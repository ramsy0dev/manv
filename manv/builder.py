"""Builds ManV build artifacts for the selected host backend.

Why this module exists:
- `manv build` now targets a one-file runnable artifact rather than a copied
  source tree.
- The builder owns the transition from compiler artifacts + project metadata to
  an embedded runtime payload.

Current scope:
- Emits a deterministic native executable under `.manv/target/<host-target>/`
  when the host backend resolves to LLVM.
- Preserves the existing `.mvz` bundle path for explicit `--host interp`.
- Writes build metadata next to native artifacts so later packaging and
  reporting phases do not need to rediscover how the executable was produced.
"""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys

from . import __version__
from .build_manifest import (
    BuildManifest,
    MANIFEST_VERSION,
    collect_input_files,
    fingerprint_file,
    is_up_to_date,
    load_manifest,
    save_manifest,
)
from .compiler import compile_pipeline_full, compile_target
from .host import HostSelectionRequest, resolve_host_selection
from .packaging import EmbeddedBuildMetadata, write_python_bundle
from .project import discover_target


@dataclass
class BuildResult:
    path: Path
    was_rebuilt: bool
    reason: str


def host_target_name() -> str:
    machine = platform.machine().lower()
    if sys.platform == "win32":
        return "x86_64-win64" if machine in {"amd64", "x86_64"} else "aarch64-aapcs64"
    if machine in {"arm64", "aarch64"}:
        return "aarch64-aapcs64"
    return "x86_64-sysv"


def default_bundle_path(context, out_dir: Path | None = None) -> Path:
    host_target = host_target_name()
    if out_dir is not None:
        return out_dir / f"{context.name}.mvz"
    return context.build_dir / host_target / f"{context.name}.mvz"


def default_native_path(context, out_dir: Path | None = None) -> Path:
    host_target = host_target_name()
    suffix = ".exe" if sys.platform == "win32" else ""
    if out_dir is not None:
        return out_dir / f"{context.name}{suffix}"
    return context.build_dir / host_target / f"{context.name}{suffix}"


def build_target(
    path: str | Path | None,
    out_dir: Path | None = None,
    *,
    portable_cache: bool = False,
    host_backend: str = "auto",
    device_backend: str = "auto",
) -> BuildResult:
    context = discover_target(path)
    host_selection = resolve_host_selection(
        HostSelectionRequest(
            requested_host_backend=host_backend,
            policy="build",
        )
    )
    resolved_host = host_selection.resolved_host_backend
    host_target = host_target_name()

    manifest_dir = out_dir if out_dir is not None else context.build_dir
    input_files = collect_input_files(context.root, context.entry, context.config_path)
    manifest = load_manifest(manifest_dir)
    up_to_date, reason = is_up_to_date(
        manifest, context.root, input_files,
        host_target, resolved_host, device_backend, optimize=True,
    )

    if up_to_date:
        assert manifest is not None
        out_path_str = manifest.outputs.get("native_exe") or manifest.outputs.get("bundle", "")
        return BuildResult(path=Path(out_path_str), was_rebuilt=False, reason=reason)

    if resolved_host == "interp":
        artifact = _build_interpreter_bundle(context, out_dir=out_dir, portable_cache=portable_cache)
        output_key = "bundle"
    else:
        artifact = _build_native_executable(
            context,
            out_dir=out_dir,
            host_backend=host_backend,
            device_backend=device_backend,
        )
        output_key = "native_exe"

    inputs_records = {}
    for file_path in input_files:
        try:
            rel = str(file_path.relative_to(context.root))
        except ValueError:
            rel = str(file_path)
        if file_path.exists():
            inputs_records[rel] = fingerprint_file(file_path)

    new_manifest = BuildManifest(
        format_version=MANIFEST_VERSION,
        manv_version=__version__,
        last_built_at=datetime.now(timezone.utc).isoformat(),
        target=host_target,
        host_backend=resolved_host,
        device_backend=device_backend,
        optimize=True,
        inputs=inputs_records,
        outputs={output_key: str(artifact)},
    )
    save_manifest(manifest_dir, new_manifest)

    return BuildResult(path=artifact, was_rebuilt=True, reason=reason)


def _build_interpreter_bundle(context, *, out_dir: Path | None, portable_cache: bool) -> Path:
    source = context.entry.read_text(encoding="utf-8")
    host_target = host_target_name()
    artifacts = compile_pipeline_full(
        source,
        str(context.entry),
        optimize=True,
        target_name=host_target,
        capture_graph=False,
    )

    payload_files = _embedded_program_files(context, source, artifacts)
    metadata = EmbeddedBuildMetadata(
        format_version=1,
        manv_version=__version__,
        project_name=context.name,
        entry_module="src/main.mv",
        host_target=host_target,
        build_mode="single-file-mvz",
        selection_policy="auto",
        default_backend="auto",
        portable_cache_mode=portable_cache,
        embedded_artifacts=tuple(sorted(path.removeprefix("manv_embedded/program/") for path in payload_files)),
        source_hash=_sha256_text(source),
        hlir_hash=_sha256_json(artifacts["hlir"]),
        kernel_hash=_sha256_json(artifacts["kernel"]),
        build_flags={"portable_cache": portable_cache},
    )

    package_root = Path(__file__).resolve().parent
    bundle_path = default_bundle_path(context, out_dir)
    return write_python_bundle(bundle_path, package_root=package_root, metadata=metadata, embedded_files=payload_files)


def _build_native_executable(
    context,
    *,
    out_dir: Path | None,
    host_backend: str,
    device_backend: str,
) -> Path:
    source = context.entry.read_text(encoding="utf-8")
    host_target = host_target_name()
    artifacts = compile_pipeline_full(
        source,
        str(context.entry),
        optimize=True,
        target_name=host_target,
        capture_graph=False,
    )

    native_out_dir = out_dir if out_dir is not None else context.build_dir / host_target
    try:
        written = compile_target(
            context.entry,
            native_out_dir,
            emit=["native_exe", *context.build_emit],
            backend=device_backend if device_backend != "auto" else "none",
            optimize=True,
            target_name=host_target,
            capture_graph=False,
            host_backend=host_backend,
            stem_override=context.name,
        )
    except Exception:
        raise

    if "native_exe" not in written:
        raise RuntimeError("native build requested but no executable artifact was produced")
    executable = written["native_exe"]

    metadata_path = native_out_dir / f"{context.name}.build.json"
    metadata_path.write_text(
        json.dumps(
            {
                "format_version": 1,
                "manv_version": __version__,
                "project_name": context.name,
                "entry_module": "src/main.mv",
                "host_target": host_target,
                "host_backend": "llvm",
                "device_backend_policy": device_backend,
                "portable_cache_mode": False,
                "source_hash": _sha256_text(source),
                "hlir_hash": _sha256_json(artifacts["hlir"]),
                "kernel_hash": _sha256_json(artifacts["kernel"]),
                "build_flags": {},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return executable


def _embedded_program_files(context, source: str, artifacts: dict[str, object]) -> dict[str, bytes]:
    files: dict[str, bytes] = {
        "manv_embedded/program/src/main.mv": source.encode("utf-8"),
    }
    if context.config_path and context.config_path.exists():
        files["manv_embedded/program/project.toml"] = context.config_path.read_bytes()

    json_artifacts = {
        "entry.mv.json": {
            "entry": "src/main.mv",
            "project_name": context.name,
        },
        "program.hlir.json": artifacts["hlir"],
        "program.graph.json": artifacts["graph"],
        "program.kernel.json": artifacts["kernel"],
        "program.gpu_report.json": artifacts["gpu_report"],
        "metadata.json": {
            "project_name": context.name,
            "source_name": str(context.entry),
        },
    }
    for name, payload in json_artifacts.items():
        files[f"manv_embedded/program/{name}"] = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return files


def _sha256_text(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sha256_json(payload: object) -> str:
    packed = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(packed).hexdigest()
