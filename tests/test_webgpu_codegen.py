"""Tests for the WebGPU WGSL codegen layer (manv.backends.webgpu.codegen)."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from manv.backends.webgpu.codegen import emit_wgsl
from manv.gpu_backends import compile_kir_backend
from manv.kernel_ir import parse_kir_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prov() -> dict:
    return {
        "graph_node_id": "g1",
        "hlir_op_id": "main.i1",
        "source_span": {"uri": "test.mv", "start_line": 1, "start_col": 1, "end_line": 1, "end_col": 10},
        "inline_chain": [],
    }


def _make_module(
    params: list[dict],
    ops: list[dict],
    *,
    kernel_name: str = "k",
    debug_meta: dict | None = None,
    launch: dict | None = None,
) -> dict:
    return {
        "version": "0.1",
        "source": "test.mv",
        "kernels": [
            {
                "kernel_name": kernel_name,
                "signature": {"params": params, "return_policy": "void"},
                "launch_model": launch or {
                    "grid_x": 1, "grid_y": 1, "grid_z": 1,
                    "block_x": 64, "block_y": 1, "block_z": 1, "shared_bytes": 0,
                },
                "memory_regions": [],
                "debug_meta": debug_meta or {},
                "blocks": [{"id": "entry", "ops": ops, "terminator": "ret"}],
            }
        ],
    }


def _buf_param(name: str, dtype: str, index: int = 0) -> dict:
    return {"index": index, "name": name, "kind": "buffer", "dtype": dtype, "by_ref": True, "alignment": 8, "address_space": "global"}


def _op(op_id: str, opcode: str, inputs: list, outputs: list, attrs: dict, dtype: str = "f32") -> dict:
    return {"id": op_id, "opcode": opcode, "inputs": inputs, "outputs": outputs, "attrs": attrs, "dtype": dtype, "memory_space": "private", "provenance": _prov()}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_compute_decorator_and_workgroup_size_present() -> None:
    src = emit_wgsl(parse_kir_module(_make_module([], [])))
    assert "@compute" in src
    assert "@workgroup_size(64, 1, 1)" in src


def test_storage_bindings_match_param_count() -> None:
    params = [_buf_param("a", "f32", 0), _buf_param("b", "f32", 1), _buf_param("c", "f32", 2)]
    src = emit_wgsl(parse_kir_module(_make_module(params, [])))
    assert src.count("var<storage, read_write>") == 3


def test_manv_uniforms_struct_and_usage() -> None:
    src = emit_wgsl(parse_kir_module(_make_module([], [])))
    assert "struct ManvUniforms" in src
    assert "manv_uniforms.manv_n" in src


def test_i64_param_lowered_to_i32_with_warning() -> None:
    params = [_buf_param("data", "i64", 0)]
    src = emit_wgsl(parse_kir_module(_make_module(params, [])))
    assert "array<i32>" in src
    assert "WARNING" in src
    assert "i64" in src


def test_f64_param_lowered_to_f32_with_warning() -> None:
    params = [_buf_param("data", "f64", 0)]
    src = emit_wgsl(parse_kir_module(_make_module(params, [])))
    assert "array<f32>" in src
    assert "WARNING" in src
    assert "f64" in src


def test_bool_array_param_uses_u32() -> None:
    params = [_buf_param("flags", "bool", 0)]
    src = emit_wgsl(parse_kir_module(_make_module(params, [])))
    assert "array<u32>" in src


def _with_store(ops: list[dict], buf_name: str = "out") -> tuple[list[dict], list[dict]]:
    """Add a thread_id + buffer_store so expression ops get emitted into the kernel body."""
    tid = _op("t0", "thread_id_x", [], ["t0"], {}, "i32")
    last_out = ops[-1]["outputs"][0] if ops and ops[-1]["outputs"] else "t0"
    store = _op("ws", "buffer_store", ["t0", last_out], [], {"buffer": buf_name}, "void")
    return [_buf_param(buf_name, "f32")], [tid] + ops + [store]


def test_select_reversed_wgsl_arg_order() -> None:
    params, ops = _with_store([
        _op("cond", "const", [], ["cond"], {"value": 1}, "bool"),
        _op("tv", "const", [], ["tv"], {"value": 2.0}, "f32"),
        _op("fv", "const", [], ["fv"], {"value": 3.0}, "f32"),
        _op("s0", "select", ["cond", "tv", "fv"], ["s0"], {}, "f32"),
    ])
    src = emit_wgsl(parse_kir_module(_make_module(params, ops)))
    # select(false_val, true_val, cond) — fv (3.0f) comes before tv (2.0f)
    assert "select(" in src
    fv_pos = src.find("3.0f")
    tv_pos = src.find("2.0f")
    select_pos = src.find("select(")
    assert select_pos != -1
    assert select_pos < fv_pos < tv_pos


def test_intrinsic_sqrt_no_suffix() -> None:
    params, ops = _with_store([
        _op("v0", "const", [], ["v0"], {"value": 4.0}, "f32"),
        _op("r0", "intrinsic_call", ["v0"], ["r0"], {"name": "sqrt"}, "f32"),
    ])
    src = emit_wgsl(parse_kir_module(_make_module(params, ops)))
    assert "sqrt(" in src
    assert "sqrtf(" not in src


def test_intrinsic_clamp_wgsl_native() -> None:
    params, ops = _with_store([
        _op("v", "const", [], ["v"], {"value": 1.0}, "f32"),
        _op("lo", "const", [], ["lo"], {"value": 0.0}, "f32"),
        _op("hi", "const", [], ["hi"], {"value": 2.0}, "f32"),
        _op("r0", "intrinsic_call", ["v", "lo", "hi"], ["r0"], {"name": "clamp"}, "f32"),
    ])
    src = emit_wgsl(parse_kir_module(_make_module(params, ops)))
    assert "clamp(" in src
    # Should NOT fall back to fminf/fmaxf
    assert "fminf" not in src
    assert "fmaxf" not in src


def test_reduction_workgroup_var_at_module_scope_and_barrier() -> None:
    debug_meta = {
        "kernel_kind": "reduction_partial",
        "value_dtype": "f32",
        "output_buffer": "out",
        "reduction_op": "+",
        "reduction_value": "",
    }
    params = [_buf_param("out", "f32", 0), _buf_param("inp", "f32", 1)]
    src = emit_wgsl(parse_kir_module(_make_module(params, [], debug_meta=debug_meta, kernel_name="red_k")))
    # var<workgroup> must appear before the fn declaration
    wg_pos = src.find("var<workgroup>")
    fn_pos = src.find("fn red_k(")
    assert wg_pos != -1
    assert fn_pos != -1
    assert wg_pos < fn_pos
    assert "workgroupBarrier()" in src


def test_reduction_partial_uses_wg_id_x() -> None:
    debug_meta = {
        "kernel_kind": "reduction_partial",
        "value_dtype": "f32",
        "output_buffer": "out",
        "reduction_op": "+",
        "reduction_value": "",
    }
    params = [_buf_param("out", "f32", 0), _buf_param("inp", "f32", 1)]
    src = emit_wgsl(parse_kir_module(_make_module(params, [], debug_meta=debug_meta)))
    assert "wg_id.x" in src


def test_compile_kir_backend_webgpu_returns_wgsl_bundle() -> None:
    params = [_buf_param("out", "f32", 0), _buf_param("inp", "f32", 1)]
    ops = [
        _op("t0", "thread_id_x", [], ["t0"], {}, "i32"),
        _op("v0", "buffer_load", ["t0"], ["v0"], {"buffer": "inp"}, "f32"),
        _op("w0", "buffer_store", ["t0", "v0"], [], {"buffer": "out"}, "void"),
    ]
    module = _make_module(params, ops)
    bundle = compile_kir_backend(module, "webgpu", target="generic")
    assert bundle.backend == "webgpu"
    assert "wgsl" in bundle.binaries
    wgsl = bundle.binaries["wgsl"]
    assert "@compute" in wgsl
