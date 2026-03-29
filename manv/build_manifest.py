"""Incremental-build manifest for ManV projects.

Tracks per-file fingerprints so unchanged projects can skip the full
compile/link cycle.  The manifest lives at build_dir/.manv.json.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANIFEST_VERSION = 1
MANIFEST_FILENAME = ".manv.json"


@dataclass
class FileRecord:
    sha256: str
    mtime: float
    size: int


@dataclass
class BuildManifest:
    format_version: int
    manv_version: str
    last_built_at: str  # ISO-8601
    target: str
    host_backend: str
    device_backend: str
    optimize: bool
    inputs: dict[str, FileRecord]   # project-relative path → record
    outputs: dict[str, str]         # artifact kind → absolute path


def fingerprint_file(path: Path) -> FileRecord:
    stat = path.stat()
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return FileRecord(sha256=sha, mtime=stat.st_mtime, size=stat.st_size)


def collect_input_files(project_root: Path, entry: Path, config_path: Path | None) -> list[Path]:
    """Return all .mv files under project_root, plus project.toml if present.

    The entry is always included even if it lives outside the project root.
    """
    seen: set[Path] = set()
    files: list[Path] = []

    def _add(p: Path) -> None:
        r = p.resolve()
        if r not in seen:
            seen.add(r)
            files.append(p)

    for mv in sorted(project_root.rglob("*.mv")):
        _add(mv)

    _add(entry)

    if config_path is not None and config_path.exists():
        _add(config_path)

    return files


def load_manifest(manifest_dir: Path) -> BuildManifest | None:
    path = manifest_dir / MANIFEST_FILENAME
    if not path.exists():
        return None
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        inputs = {k: FileRecord(**v) for k, v in data.get("inputs", {}).items()}
        return BuildManifest(
            format_version=int(data["format_version"]),
            manv_version=str(data["manv_version"]),
            last_built_at=str(data["last_built_at"]),
            target=str(data["target"]),
            host_backend=str(data["host_backend"]),
            device_backend=str(data["device_backend"]),
            optimize=bool(data["optimize"]),
            inputs=inputs,
            outputs={k: str(v) for k, v in data.get("outputs", {}).items()},
        )
    except Exception:
        return None


def save_manifest(manifest_dir: Path, manifest: BuildManifest) -> None:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / MANIFEST_FILENAME
    data: dict[str, Any] = {
        "format_version": manifest.format_version,
        "manv_version": manifest.manv_version,
        "last_built_at": manifest.last_built_at,
        "target": manifest.target,
        "host_backend": manifest.host_backend,
        "device_backend": manifest.device_backend,
        "optimize": manifest.optimize,
        "inputs": {
            k: {"sha256": v.sha256, "mtime": v.mtime, "size": v.size}
            for k, v in manifest.inputs.items()
        },
        "outputs": manifest.outputs,
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_up_to_date(
    manifest: BuildManifest | None,
    project_root: Path,
    input_files: list[Path],
    target: str,
    host_backend: str,
    device_backend: str,
    optimize: bool,
) -> tuple[bool, str]:
    """Return (up_to_date, reason_string).

    Fast path: if mtime+size unchanged, skip SHA-256.
    """
    if manifest is None:
        return False, "no manifest"

    if (
        manifest.target != target
        or manifest.host_backend != host_backend
        or manifest.device_backend != device_backend
        or manifest.optimize != optimize
    ):
        return False, "config changed"

    for kind, out_path in manifest.outputs.items():
        if not Path(out_path).exists():
            return False, f"output missing ({kind})"

    changed = 0
    existing_rels: set[str] = set()

    for file_path in input_files:
        try:
            rel = str(file_path.relative_to(project_root))
        except ValueError:
            rel = str(file_path)
        existing_rels.add(rel)

        rec = manifest.inputs.get(rel)
        if rec is None:
            changed += 1
            continue

        try:
            stat = file_path.stat()
        except OSError:
            changed += 1
            continue

        # Fast path: mtime + size match → skip SHA-256
        if stat.st_mtime == rec.mtime and stat.st_size == rec.size:
            continue

        sha = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if sha != rec.sha256:
            changed += 1

    if changed:
        return False, f"{changed} file(s) changed"

    new_files = existing_rels - set(manifest.inputs.keys())
    if new_files:
        return False, f"{len(new_files)} new file(s)"

    return True, "up to date"
