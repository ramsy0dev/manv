"""WGSL emission from ManV Kernel IR for the WebGPU backend.

Key WGSL constraints vs CUDA:
- No 64-bit integers or floats; i64/f64 are lowered to i32/f32 with a warning.
- bool arrays are forbidden; bool params use u32 arrays.
- var<workgroup> must be at module scope (not inside a function).
- select() argument order is reversed vs C ternary: select(false_val, true_val, cond).
- Math intrinsics have no type suffix: sqrt(), abs(), etc.
- Float literals need an explicit 'f' suffix for f32: 1.0f.
"""

from __future__ import annotations

from typing import Any

from ...kernel_ir import KIRModule, parse_kir_module


DTYPE_TO_WGSL = {
    "i32": "i32", "int": "i32",
    "i64": "i32",   # WebGPU lacks 64-bit integers; emits warning comment
    "f32": "f32", "float": "f32",
    "f64": "f32",   # WebGPU lacks 64-bit floats; emits warning comment
    "bool": "bool",
}

DTYPE_TO_WGSL_ARRAY = {**DTYPE_TO_WGSL, "bool": "u32"}  # WGSL forbids bool arrays

_DTYPE_LOSSY = {"i64", "f64"}


def emit_wgsl(module: KIRModule | dict[str, Any], *, workgroup_size: int = 64) -> str:
    """Emit a complete WGSL source string for every kernel in *module*."""
    parsed = module if isinstance(module, KIRModule) else parse_kir_module(module)

    parts: list[str] = [
        "// ManV WebGPU backend",
        f"// source: {parsed.source}",
        f"// hash: {parsed.canonical_hash()}",
        "",
    ]

    for kernel in parsed.kernels:
        parts.extend(_emit_wgsl_kernel(kernel.to_dict(), workgroup_size=workgroup_size))
        parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _emit_wgsl_kernel(kernel: dict[str, Any], *, workgroup_size: int) -> list[str]:
    debug_meta = kernel.get("debug_meta", {}) if isinstance(kernel.get("debug_meta"), dict) else {}
    kernel_kind = str(debug_meta.get("kernel_kind", "elementwise"))
    if kernel_kind.startswith("reduction_"):
        return _emit_wgsl_reduction_kernel(kernel, workgroup_size=workgroup_size)
    return _emit_wgsl_elementwise_kernel(kernel, workgroup_size=workgroup_size)


def _lossy_comment(dtype: str) -> str:
    if dtype in _DTYPE_LOSSY:
        mapped = DTYPE_TO_WGSL.get(dtype, "f32")
        return f" /* WARNING: {dtype} lowered to {mapped} — WebGPU lacks native {dtype} */"
    return ""


def _emit_wgsl_elementwise_kernel(kernel: dict[str, Any], *, workgroup_size: int) -> list[str]:
    name = str(kernel.get("kernel_name", "manv_kernel"))
    params = list(kernel.get("signature", {}).get("params", []))
    blocks = list(kernel.get("blocks", []))
    ops = blocks[0].get("ops", []) if blocks else list(kernel.get("ops", []))

    lines: list[str] = []

    lines.append("struct ManvUniforms { manv_n: u32, }")
    lines.append("")

    for i, param in enumerate(params):
        dtype = str(param.get("dtype", "f32"))
        wgsl_arr = DTYPE_TO_WGSL_ARRAY.get(dtype, "f32")
        comment = _lossy_comment(dtype)
        lines.append(f"@group(0) @binding({i}) var<storage, read_write> {param.get('name')}: array<{wgsl_arr}>;{comment}")

    lines.append("@group(1) @binding(0) var<uniform> manv_uniforms: ManvUniforms;")
    lines.append("")

    lines.append(f"@compute @workgroup_size({workgroup_size}, 1, 1)")
    lines.append(f"fn {name}(")
    lines.append("    @builtin(global_invocation_id) global_id: vec3<u32>,")
    lines.append("    @builtin(num_workgroups) num_wgs: vec3<u32>")
    lines.append(") {")
    lines.append(f"    let stride: u32 = num_wgs.x * {workgroup_size}u;")
    lines.append("    var i: u32 = global_id.x;")
    lines.append("    loop {")
    lines.append("        if i >= manv_uniforms.manv_n { break; }")

    emitted, _value_exprs = _emit_wgsl_ops(ops)
    for line in emitted:
        lines.append(f"        {line}")

    lines.append("        i += stride;")
    lines.append("    }")
    lines.append("}")

    return lines


def _wgsl_neutral(op: str, wgsl_type: str) -> str:
    is_float = wgsl_type == "f32"
    is_int = wgsl_type == "i32"
    if op == "+":
        return "0.0f" if is_float else "0i"
    if op == "*":
        return "1.0f" if is_float else "1i"
    if op == "min":
        return "3.402823466e+38f" if is_float else ("2147483647i" if is_int else "0u")
    if op == "max":
        return "-3.402823466e+38f" if is_float else ("-2147483648i" if is_int else "0u")
    return "0.0f" if is_float else "0i"


def _wgsl_combine(op: str, acc: str, val: str) -> str:
    if op == "+":
        return f"{acc} = {acc} + {val}"
    if op == "*":
        return f"{acc} = {acc} * {val}"
    if op in {"min", "max"}:
        return f"{acc} = {op}({acc}, {val})"
    return f"{acc} = {acc} + {val}"


def _emit_wgsl_reduction_kernel(kernel: dict[str, Any], *, workgroup_size: int) -> list[str]:
    name = str(kernel.get("kernel_name", "manv_kernel"))
    params = list(kernel.get("signature", {}).get("params", []))
    blocks = list(kernel.get("blocks", []))
    ops = blocks[0].get("ops", []) if blocks else list(kernel.get("ops", []))
    debug_meta = kernel.get("debug_meta", {}) if isinstance(kernel.get("debug_meta"), dict) else {}

    kernel_kind = str(debug_meta.get("kernel_kind", "reduction_partial"))
    value_dtype = str(debug_meta.get("value_dtype", "f32"))
    wgsl_type = DTYPE_TO_WGSL.get(value_dtype, "f32")
    output_buffer = str(debug_meta.get("output_buffer", "out"))
    reduction_op = str(debug_meta.get("reduction_op", "+"))
    value_name = str(debug_meta.get("reduction_value", ""))
    neutral = _wgsl_neutral(reduction_op, wgsl_type)

    lines: list[str] = []

    lines.append("struct ManvUniforms { manv_n: u32, }")
    lines.append("")

    for i, param in enumerate(params):
        dtype = str(param.get("dtype", "f32"))
        wgsl_arr = DTYPE_TO_WGSL_ARRAY.get(dtype, "f32")
        comment = _lossy_comment(dtype)
        lines.append(f"@group(0) @binding({i}) var<storage, read_write> {param.get('name')}: array<{wgsl_arr}>;{comment}")

    lines.append("@group(1) @binding(0) var<uniform> manv_uniforms: ManvUniforms;")
    lines.append("")

    # WGSL requires var<workgroup> at module scope
    lines.append(f"var<workgroup> shared_acc_{name}: array<{wgsl_type}, {workgroup_size}>;")
    lines.append("")

    lines.append(f"@compute @workgroup_size({workgroup_size}, 1, 1)")
    lines.append(f"fn {name}(")
    lines.append("    @builtin(global_invocation_id) global_id: vec3<u32>,")
    lines.append("    @builtin(workgroup_id) wg_id: vec3<u32>,")
    lines.append("    @builtin(num_workgroups) num_wgs: vec3<u32>")
    lines.append(") {")
    lines.append(f"    let tid: u32 = global_id.x % {workgroup_size}u;")
    lines.append(f"    let stride: u32 = num_wgs.x * {workgroup_size}u;")
    lines.append("    var i: u32 = global_id.x;")
    lines.append(f"    var acc: {wgsl_type} = {neutral};")
    lines.append("    loop {")
    lines.append("        if i >= manv_uniforms.manv_n { break; }")

    emitted, value_exprs = _emit_wgsl_ops(ops)
    for line in emitted:
        lines.append(f"        {line}")

    reduction_expr = value_exprs.get(value_name, value_name or "acc")
    lines.append(f"        {_wgsl_combine(reduction_op, 'acc', reduction_expr)};")
    lines.append("        i += stride;")
    lines.append("    }")

    lines.append(f"    shared_acc_{name}[tid] = acc;")
    lines.append("    workgroupBarrier();")
    lines.append(f"    var offset: u32 = {workgroup_size}u / 2u;")
    lines.append("    loop {")
    lines.append("        if offset == 0u { break; }")
    lines.append("        if tid < offset {")
    lines.append(f"            {_wgsl_combine(reduction_op, f'shared_acc_{name}[tid]', f'shared_acc_{name}[tid + offset]')};")
    lines.append("        }")
    lines.append("        workgroupBarrier();")
    lines.append("        offset = offset / 2u;")
    lines.append("    }")

    lines.append("    if tid == 0u {")
    if kernel_kind == "reduction_partial":
        lines.append(f"        {output_buffer}[wg_id.x] = shared_acc_{name}[0u];")
    else:
        lines.append(f"        {output_buffer}[0u] = shared_acc_{name}[0u];")
    lines.append("    }")
    lines.append("}")

    return lines


def _emit_wgsl_ops(ops: list[dict[str, Any]]) -> tuple[list[str], dict[str, str]]:
    value_exprs: dict[str, str] = {"i": "i", "idx": "i"}
    lines: list[str] = []

    for op in ops:
        opcode = str(op.get("opcode", op.get("op", "")))
        outputs = [str(x) for x in op.get("outputs", [])]
        inputs = [str(x) for x in op.get("inputs", [])]
        attrs = op.get("attrs", {}) if isinstance(op.get("attrs"), dict) else {}
        op_dtype = str(op.get("dtype", "f32"))

        if opcode == "thread_id_x":
            if outputs:
                value_exprs[outputs[0]] = "i"
            continue

        if opcode == "const":
            if outputs:
                value = attrs.get("value", 0)
                if isinstance(value, float) or op_dtype in {"f32", "float", "f64"}:
                    value_exprs[outputs[0]] = f"{float(value)}f"
                else:
                    value_exprs[outputs[0]] = repr(value)
            continue

        if opcode == "buffer_load" and outputs:
            buffer_name = str(attrs.get("buffer", "arg0"))
            index_expr = value_exprs.get(inputs[0], "i") if inputs else "i"
            value_exprs[outputs[0]] = f"{buffer_name}[{index_expr}]"
            continue

        if opcode.startswith("binary::") and outputs:
            token = opcode.split("::", 1)[1]
            if token == "and":
                token = "&&"
            elif token == "or":
                token = "||"
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
            if token in {"not", "!"}:
                value_exprs[outputs[0]] = f"(!{operand})"
            else:
                value_exprs[outputs[0]] = f"({token}{operand})"
            continue

        if opcode == "cast" and outputs:
            to_dtype = str(attrs.get("to_dtype", "f32"))
            wgsl_type = DTYPE_TO_WGSL.get(to_dtype, "f32")
            operand = value_exprs.get(inputs[0], inputs[0] if inputs else "0")
            value_exprs[outputs[0]] = f"{wgsl_type}({operand})"
            continue

        if opcode == "select" and outputs:
            # WGSL: select(false_val, true_val, cond) — reversed vs C ternary
            cond = value_exprs.get(inputs[0], inputs[0] if inputs else "false")
            tval = value_exprs.get(inputs[1], inputs[1] if len(inputs) > 1 else "0")
            fval = value_exprs.get(inputs[2], inputs[2] if len(inputs) > 2 else "0")
            value_exprs[outputs[0]] = f"select({fval}, {tval}, {cond})"
            continue

        if opcode == "intrinsic_call" and outputs:
            iname = str(attrs.get("name", ""))
            args = [value_exprs.get(inp, inp) for inp in inputs]
            # WGSL built-ins have no float suffix
            if iname in {"sqrt", "abs", "floor", "ceil", "sin", "cos", "tan",
                         "exp", "log", "log2", "pow", "min", "max"}:
                value_exprs[outputs[0]] = f"{iname}({', '.join(args)})"
            elif iname == "clamp":
                value_exprs[outputs[0]] = f"clamp({', '.join(args)})"
            elif iname == "fabs":
                value_exprs[outputs[0]] = f"abs({', '.join(args)})"
            else:
                lines.append(f"// unsupported intrinsic: {iname}")
                value_exprs[outputs[0]] = "0"
            continue

        if opcode == "kernel_assert":
            lines.append("// kernel_assert omitted in WebGPU path")
            continue

        lines.append(f"// unsupported op: {opcode}")

    return lines, value_exprs
