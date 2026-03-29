"""Tests for the CUDA C++ codegen layer (manv.backends.cuda.codegen)."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from manv.backends.cuda.codegen import emit_cuda_cpp
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
                    "block_x": 256, "block_y": 1, "block_z": 1, "shared_bytes": 0,
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

def test_math_h_include_always_present() -> None:
    module = _make_module([], [])
    src = emit_cuda_cpp(parse_kir_module(module))
    assert "#include <math.h>" in src


def _with_store(ops: list[dict], buf_name: str = "out") -> tuple[list[dict], list[dict]]:
    """Add a thread_id + buffer_store so expression ops get emitted into the kernel body."""
    tid = _op("t0", "thread_id_x", [], ["t0"], {}, "i32")
    # Use the last output from ops as the stored value; fall back to a const
    last_out = ops[-1]["outputs"][0] if ops and ops[-1]["outputs"] else "t0"
    store = _op("ws", "buffer_store", ["t0", last_out], [], {"buffer": buf_name}, "void")
    return [_buf_param(buf_name, "f32")], [tid] + ops + [store]


def test_cast_op_f32_target() -> None:
    params, ops = _with_store([
        _op("v0", "const", [], ["v0"], {"value": 3}, "i32"),
        _op("c0", "cast", ["v0"], ["c0"], {"to_dtype": "f32"}, "f32"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "((float)" in src


def test_cast_op_f64_target() -> None:
    params, ops = _with_store([
        _op("v0", "const", [], ["v0"], {"value": 3}, "i32"),
        _op("c0", "cast", ["v0"], ["c0"], {"to_dtype": "f64"}, "f64"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "((double)" in src


def test_select_op_ternary_syntax() -> None:
    params, ops = _with_store([
        _op("cond", "const", [], ["cond"], {"value": 1}, "bool"),
        _op("tv", "const", [], ["tv"], {"value": 2}, "f32"),
        _op("fv", "const", [], ["fv"], {"value": 3}, "f32"),
        _op("s0", "select", ["cond", "tv", "fv"], ["s0"], {}, "f32"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "?" in src
    assert ":" in src


def test_intrinsic_sqrt_f32_uses_sqrtf() -> None:
    params, ops = _with_store([
        _op("v0", "const", [], ["v0"], {"value": 4.0}, "f32"),
        _op("r0", "intrinsic_call", ["v0"], ["r0"], {"name": "sqrt"}, "f32"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "sqrtf(" in src


def test_intrinsic_sqrt_f64_uses_sqrt_not_sqrtf() -> None:
    params, ops = _with_store([
        _op("v0", "const", [], ["v0"], {"value": 4.0}, "f64"),
        _op("r0", "intrinsic_call", ["v0"], ["r0"], {"name": "sqrt"}, "f64"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "sqrt(" in src
    assert "sqrtf(" not in src


def test_intrinsic_pow_two_args() -> None:
    params, ops = _with_store([
        _op("base", "const", [], ["base"], {"value": 2.0}, "f32"),
        _op("exp_", "const", [], ["exp_"], {"value": 3.0}, "f32"),
        _op("r0", "intrinsic_call", ["base", "exp_"], ["r0"], {"name": "pow"}, "f32"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "powf(" in src


def test_intrinsic_min_int_uses_min_not_fminf() -> None:
    params, ops = _with_store([
        _op("a", "const", [], ["a"], {"value": 2}, "i32"),
        _op("b", "const", [], ["b"], {"value": 3}, "i32"),
        _op("r0", "intrinsic_call", ["a", "b"], ["r0"], {"name": "min"}, "i32"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "min(" in src
    assert "fminf(" not in src


def test_intrinsic_clamp_f32_nested_fminf_fmaxf() -> None:
    params, ops = _with_store([
        _op("v", "const", [], ["v"], {"value": 1.0}, "f32"),
        _op("lo", "const", [], ["lo"], {"value": 0.0}, "f32"),
        _op("hi", "const", [], ["hi"], {"value": 2.0}, "f32"),
        _op("r0", "intrinsic_call", ["v", "lo", "hi"], ["r0"], {"name": "clamp"}, "f32"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "fminf(fmaxf(" in src


def test_intrinsic_abs_int_uses_abs() -> None:
    params, ops = _with_store([
        _op("v", "const", [], ["v"], {"value": -5}, "i32"),
        _op("r0", "intrinsic_call", ["v"], ["r0"], {"name": "abs"}, "i32"),
    ])
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, ops)))
    assert "abs(" in src
    assert "fabsf(" not in src


def test_f64_param_emits_double_pointer() -> None:
    params = [_buf_param("data", "f64", 0)]
    src = emit_cuda_cpp(parse_kir_module(_make_module(params, [])))
    assert "double* data" in src


def test_reduction_kernel_block_x_128_shared_size() -> None:
    launch = {"grid_x": 1, "grid_y": 1, "grid_z": 1, "block_x": 128, "block_y": 1, "block_z": 1, "shared_bytes": 0}
    debug_meta = {
        "kernel_kind": "reduction_partial",
        "value_dtype": "f32",
        "output_buffer": "out",
        "reduction_op": "+",
        "reduction_value": "",
    }
    params = [_buf_param("out", "f32", 0), _buf_param("inp", "f32", 1)]
    module = _make_module(params, [], debug_meta=debug_meta, launch=launch)
    src = emit_cuda_cpp(parse_kir_module(module))
    assert "shared_acc[128]" in src


def test_unknown_intrinsic_emits_stub() -> None:
    ops = [
        _op("r0", "intrinsic_call", [], ["r0"], {"name": "totally_unknown_fn"}, "f32"),
    ]
    src = emit_cuda_cpp(parse_kir_module(_make_module([], ops)))
    assert "unsupported intrinsic" in src
