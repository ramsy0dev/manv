"""CUDA C++ emission from ManV Kernel IR.

Why this exists:
- NVRTC expects CUDA C++ input in this backend.
- Generated source doubles as the most readable debugging artifact, so the file
  is intentionally comment-heavy and stable.

Current scope:
- Elementwise kernels expressed through the existing KIR op set are emitted as
  grid-stride loops.
- The emitter preserves deterministic kernel naming and emits enough comments to
  connect CUDA source back to originating ManV/KIR concepts.
- Unsupported ops still emit a compilable stub body instead of failing during
  source generation. Eligibility should have filtered those cases earlier.
"""

from __future__ import annotations

import json
from typing import Any

from ...kernel_ir import KIRModule, parse_kir_module


DTYPE_TO_CUDA = {
    "i32": "int",
    "int": "int",
    "i64": "long long",
    "f32": "float",
    "float": "float",
    "bool": "bool",
}


def emit_cuda_cpp(kernel_ir: KIRModule | dict[str, Any], *, arch: str = "sm_80", debug: bool = False) -> str:
    module = kernel_ir if isinstance(kernel_ir, KIRModule) else parse_kir_module(kernel_ir)
    lines = [
        "// ManV CUDA backend",
        "// This source is generated from Kernel IR and is intentionally verbose",
        "// so dumped kernels remain useful during debugging and future backend",
        "// maintenance.",
        f"// source: {module.source}",
        f"// kir_hash: {module.canonical_hash()}",
        f"// arch: {arch}",
        "#include <stdint.h>",
        "",
    ]

    for kernel in module.kernels:
        lines.extend(_emit_kernel(module.canonical_hash(), kernel.to_dict(), debug=debug))
        lines.append("")
    return "\n".join(lines)


def _emit_kernel(module_hash: str, kernel: dict[str, Any], *, debug: bool) -> list[str]:
    name = str(kernel.get("kernel_name", "manv_kernel"))
    signature = kernel.get("signature", {})
    params = list(signature.get("params", []))
    launch = kernel.get("launch_model", {})
    blocks = list(kernel.get("blocks", []))
    ops = blocks[0].get("ops", []) if blocks else list(kernel.get("ops", []))
    debug_meta = kernel.get("debug_meta", {}) if isinstance(kernel.get("debug_meta"), dict) else {}

    arg_parts: list[str] = []
    for param in params:
        dtype = DTYPE_TO_CUDA.get(str(param.get("dtype", "i32")), "int")
        if bool(param.get("by_ref", True)) or str(param.get("kind", "buffer")) == "buffer":
            arg_parts.append(f"{dtype}* {param.get('name')}")
        else:
            arg_parts.append(f"{dtype} {param.get('name')}")
    arg_parts.append("int manv_n")

    kernel_kind = str(debug_meta.get("kernel_kind", "elementwise"))
    if kernel_kind.startswith("reduction_"):
        return _emit_reduction_kernel(name, arg_parts, launch, ops, debug_meta, module_hash=module_hash)

    lines = [
        f'extern "C" __global__ void {name}({", ".join(arg_parts)}) {{',
        "    // Kernel metadata is embedded as comments so dumped source is easy",
        "    // to correlate with ManV debug output and cache entries.",
        f"    // kernel_name: {name}",
        f"    // module_hash: {module_hash}",
        f"    // launch_model: {json.dumps(launch, sort_keys=True)}",
        f"    // lowering_mode: {debug_meta.get('lowering_mode', 'kernel')}",
        "    int idx = (int)(blockIdx.x * blockDim.x + threadIdx.x);",
        "    int stride = (int)(blockDim.x * gridDim.x);",
        "    for (int i = idx; i < manv_n; i += stride) {",
    ]

    if debug:
        lines.append("        // Debug mode preserves a direct source anchor for DAP dumps.")

    emitted, _value_exprs = _emit_ops(ops)
    if emitted:
        lines.extend(f"        {line}" for line in emitted)
    else:
        lines.append("        // No supported ops were emitted for this kernel body.")

    lines.extend(
        [
            "    }",
            "}",
        ]
    )
    return lines


def _reduction_neutral(op: str, dtype: str) -> str:
    """Return the identity element for a reduction operator as a C literal."""
    is_float = dtype in {"float", "double"}
    if op == "+":
        return "0.0f" if is_float else "0"
    if op == "*":
        return "1.0f" if is_float else "1"
    if op == "min":
        return "FLT_MAX" if is_float else "INT_MAX"
    if op == "max":
        return "-FLT_MAX" if is_float else "INT_MIN"
    return "0.0f" if is_float else "0"


def _reduction_combine(op: str, dtype: str, acc: str, val: str) -> str:
    """Return a C expression that combines *acc* and *val* using *op*."""
    if op == "+":
        return f"{acc} += {val}"
    if op == "*":
        return f"{acc} *= {val}"
    if op == "min":
        fn = "fminf" if dtype == "float" else ("fmin" if dtype == "double" else "min")
        return f"{acc} = {fn}({acc}, {val})"
    if op == "max":
        fn = "fmaxf" if dtype == "float" else ("fmax" if dtype == "double" else "max")
        return f"{acc} = {fn}({acc}, {val})"
    return f"{acc} += {val}"


def _emit_reduction_kernel(
    name: str,
    arg_parts: list[str],
    launch: dict[str, Any],
    ops: list[dict[str, Any]],
    debug_meta: dict[str, Any],
    *,
    module_hash: str,
) -> list[str]:
    emitted, value_exprs = _emit_ops(ops)
    value_name = str(debug_meta.get("reduction_value", ""))
    reduction_expr = value_exprs.get(value_name, value_name or "0")
    value_dtype = DTYPE_TO_CUDA.get(str(debug_meta.get("value_dtype", "f32")), "float")
    output_buffer = str(debug_meta.get("output_buffer", "out"))
    reduction_kind = str(debug_meta.get("kernel_kind"))
    reduction_op = str(debug_meta.get("reduction_op", "+"))
    neutral = _reduction_neutral(reduction_op, value_dtype)

    # For min/max we need the relevant header macros.
    extra_includes: list[str] = []
    if reduction_op in {"min", "max"} and value_dtype in {"float", "double"}:
        extra_includes.append("#include <math.h>")
    if reduction_op in {"min", "max"} and value_dtype in {"int", "long long"}:
        extra_includes.append("#include <limits.h>")

    lines = [*extra_includes,
        f'extern "C" __global__ void {name}({", ".join(arg_parts)}) {{',
        "    // Reduction kernels use block-local tree reduction to keep the",
        "    // generated source readable and deterministic during debugging.",
        f"    // kernel_name: {name}",
        f"    // module_hash: {module_hash}",
        f"    // launch_model: {json.dumps(launch, sort_keys=True)}",
        f"    // reduction_kind: {reduction_kind}",
        f"    // reduction_op: {reduction_op}",
        f"    __shared__ {value_dtype} shared_acc[256];",
        "    int tid = (int)threadIdx.x;",
        "    int idx = (int)(blockIdx.x * blockDim.x + threadIdx.x);",
        "    int stride = (int)(blockDim.x * gridDim.x);",
        f"    {value_dtype} acc = ({value_dtype})({neutral});",
        "    for (int i = idx; i < manv_n; i += stride) {",
    ]
    if emitted:
        lines.extend(f"        {line}" for line in emitted)
    lines.append(f"        {_reduction_combine(reduction_op, value_dtype, 'acc', reduction_expr)};")
    lines.extend(
        [
            "    }",
            "    shared_acc[tid] = acc;",
            "    __syncthreads();",
            "    for (int offset = blockDim.x / 2; offset > 0; offset >>= 1) {",
            "        if (tid < offset) {",
            f"            {_reduction_combine(reduction_op, value_dtype, 'shared_acc[tid]', 'shared_acc[tid + offset]')};",
            "        }",
            "        __syncthreads();",
            "    }",
        ]
    )

    if reduction_kind == "reduction_partial":
        lines.extend(
            [
                "    if (tid == 0) {",
                f"        {output_buffer}[blockIdx.x] = shared_acc[0];",
                "    }",
                "}",
            ]
        )
        return lines

    lines.extend(
        [
            "    if (tid == 0) {",
            f"        {output_buffer}[0] = shared_acc[0];",
            "    }",
            "}",
        ]
    )
    return lines


def _emit_ops(ops: list[dict[str, Any]]) -> tuple[list[str], dict[str, str]]:
    value_exprs: dict[str, str] = {"i": "i", "idx": "i"}
    lines: list[str] = []

    for op in ops:
        opcode = str(op.get("opcode", op.get("op", "")))
        outputs = [str(x) for x in op.get("outputs", [])]
        inputs = [str(x) for x in op.get("inputs", [])]
        attrs = op.get("attrs", {}) if isinstance(op.get("attrs"), dict) else {}

        if opcode == "thread_id_x":
            if outputs:
                value_exprs[outputs[0]] = "i"
            continue

        if opcode == "const":
            if outputs:
                value_exprs[outputs[0]] = repr(attrs.get("value", 0))
            continue

        if opcode == "buffer_load" and outputs:
            buffer_name = str(attrs.get("buffer", "arg0"))
            index_expr = value_exprs.get(inputs[0], "i") if inputs else "i"
            value_exprs[outputs[0]] = f"{buffer_name}[{index_expr}]"
            continue

        if opcode.startswith("binary::") and outputs:
            token = opcode.split("::", 1)[1]
            lhs = value_exprs.get(inputs[0], inputs[0] if inputs else "0")
            rhs = value_exprs.get(inputs[1], inputs[1] if len(inputs) > 1 else "0")
            value_exprs[outputs[0]] = f"({lhs} {token} {rhs})"
            continue

        if opcode == "buffer_store":
            buffer_name = str(attrs.get("buffer", "arg0"))
            index_expr = value_exprs.get(inputs[0], "i") if inputs else "i"
            value_expr = value_exprs.get(inputs[1], inputs[1] if len(inputs) > 1 else "0")
            lines.append(f"{buffer_name}[{index_expr}] = {value_expr};")
            continue

        if opcode.startswith("unary::") and outputs:
            token = opcode.split("::", 1)[1]
            operand = value_exprs.get(inputs[0], inputs[0] if inputs else "0")
            if token == "not" or token == "!":
                value_exprs[outputs[0]] = f"(!{operand})"
            else:
                # covers "-" and any future single-character unary ops
                value_exprs[outputs[0]] = f"({token}{operand})"
            continue

        if opcode == "kernel_assert":
            lines.append("// kernel_assert omitted in CUDA v1 runtime path")
            continue

        lines.append(f"// unsupported op: {opcode}")
    return lines, value_exprs
