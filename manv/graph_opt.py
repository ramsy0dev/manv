from __future__ import annotations

from typing import Any


SIDE_EFFECT_OPS = {
    "return",
    "call",
    "assign",
    "set_attr",
    "set_index",
    "raise",
    "break",
    "continue",
    "if_region",
    "while_region",
    "try_region",
    "import",
    "from_import",
}


def optimize_graph_ir(graph_ir: dict[str, Any]) -> dict[str, Any]:
    constant_folding = 0
    dead_nodes_removed = 0
    cse_total = 0
    fusion_total = 0
    memory_reuse_total = 0

    for fn in graph_ir.get("functions", []):
        nodes = fn.get("nodes", [])
        fold_count = _constant_fold(nodes)
        cse_count = _common_subexpression_elimination(fn)
        fusion_count = _effect_safe_fusion(fn)
        prune_count = _dead_node_elimination(fn)
        reuse_count = _memory_reuse(fn)
        fn["optimization"] = {
            "constant_folding": fold_count,
            "cse": cse_count,
            "fusion": fusion_count,
            "layout_normalization": 0,
            "memory_reuse": reuse_count,
            "dead_nodes_removed": prune_count,
        }
        constant_folding += fold_count
        cse_total += cse_count
        fusion_total += fusion_count
        dead_nodes_removed += prune_count
        memory_reuse_total += reuse_count

    graph_ir["optimization"] = {
        "constant_folding": constant_folding,
        "cse": cse_total,
        "fusion": fusion_total,
        "layout_normalization": 0,
        "memory_reuse": memory_reuse_total,
        "dead_nodes_removed": dead_nodes_removed,
    }
    return graph_ir


def _constant_fold(nodes: list[dict[str, Any]]) -> int:
    folded = 0
    node_by_id = {node.get("id"): node for node in nodes}

    for node in nodes:
        op = str(node.get("op", ""))
        if op.startswith("binary::"):
            inputs = node.get("inputs", [])
            if len(inputs) != 2:
                continue
            left = _const_value(node_by_id.get(inputs[0]))
            right = _const_value(node_by_id.get(inputs[1]))
            if left is None or right is None:
                continue
            value = _eval_binary(op.split("::", 1)[1], left, right)
            if value is None:
                continue
            node["op"] = "const"
            node["inputs"] = []
            node["dtype"] = _dtype_of(value)
            node["attrs"] = {"value": value, "folded_from": op}
            folded += 1
            continue

        if op.startswith("unary::"):
            inputs = node.get("inputs", [])
            if len(inputs) != 1:
                continue
            value = _const_value(node_by_id.get(inputs[0]))
            if value is None:
                continue
            unary_op = op.split("::", 1)[1]
            if unary_op == "-":
                value = -value
            else:
                continue
            node["op"] = "const"
            node["inputs"] = []
            node["dtype"] = _dtype_of(value)
            node["attrs"] = {"value": value, "folded_from": op}
            folded += 1

    return folded


def _common_subexpression_elimination(function_graph: dict[str, Any]) -> int:
    nodes: list[dict[str, Any]] = function_graph.get("nodes", [])
    edges: list[dict[str, Any]] = function_graph.get("edges", [])

    seen: dict[tuple[str, tuple[str, ...], tuple[tuple[str, Any], ...]], str] = {}
    replace: dict[str, str] = {}
    removed = 0

    for node in nodes:
        op = str(node.get("op", ""))
        if op in SIDE_EFFECT_OPS or op.startswith("stub::"):
            continue
        key = (
            op,
            tuple(str(x) for x in node.get("inputs", [])),
            _cse_attrs_key(dict(node.get("attrs", {}))),
        )
        node_id = str(node.get("id"))
        if key in seen:
            replace[node_id] = seen[key]
            removed += 1
        else:
            seen[key] = node_id

    if not replace:
        return 0

    for node in nodes:
        node["inputs"] = [replace.get(str(inp), str(inp)) for inp in node.get("inputs", [])]

    function_graph["edges"] = [
        {
            "from": replace.get(str(edge.get("from")), str(edge.get("from"))),
            "to": replace.get(str(edge.get("to")), str(edge.get("to"))),
        }
        for edge in edges
        if str(edge.get("from")) not in replace
    ]

    function_graph["nodes"] = [node for node in nodes if str(node.get("id")) not in replace]
    return removed


def _effect_safe_fusion(function_graph: dict[str, Any]) -> int:
    nodes: list[dict[str, Any]] = function_graph.get("nodes", [])
    fused = 0
    for idx in range(len(nodes) - 1):
        a = nodes[idx]
        b = nodes[idx + 1]
        op_a = str(a.get("op", ""))
        op_b = str(b.get("op", ""))
        if op_a.startswith("binary::") and op_b.startswith("binary::"):
            if not a.get("effectful") and not b.get("effectful"):
                b_attrs = dict(b.get("attrs", {}))
                b_attrs["fused_with"] = str(a.get("id"))
                b["attrs"] = b_attrs
                fused += 1
    return fused


def _dead_node_elimination(function_graph: dict[str, Any]) -> int:
    nodes: list[dict[str, Any]] = function_graph.get("nodes", [])
    edges: list[dict[str, Any]] = function_graph.get("edges", [])
    node_by_id = {node.get("id"): node for node in nodes}

    roots: list[str] = []
    for node in nodes:
        op = str(node.get("op", ""))
        if op in SIDE_EFFECT_OPS or op.startswith("stub::"):
            roots.append(str(node.get("id")))

    reachable: set[str] = set()
    stack = roots[:]
    while stack:
        current = stack.pop()
        if current in reachable:
            continue
        reachable.add(current)
        node = node_by_id.get(current)
        if not node:
            continue
        for source in node.get("inputs", []):
            if source in node_by_id:
                stack.append(source)

    before = len(nodes)
    function_graph["nodes"] = [node for node in nodes if node.get("id") in reachable]
    keep_ids = {str(node.get("id")) for node in function_graph["nodes"]}
    function_graph["edges"] = [
        edge for edge in edges if str(edge.get("from")) in keep_ids and str(edge.get("to")) in keep_ids
    ]
    after = len(function_graph["nodes"])
    return max(0, before - after)


def _memory_reuse(function_graph: dict[str, Any]) -> int:
    """Identify same-dtype, same-size alloc nodes that can reuse a freed buffer.

    Walk nodes in declaration order (which approximates topological order for
    straight-line code).  Once the last consumer of an alloc has been passed,
    mark the buffer as free.  When a later alloc with identical dtype and size
    appears, re-use the free slot and record the reuse in the node's attrs so
    downstream passes can skip redundant allocations.
    """
    nodes: list[dict[str, Any]] = function_graph.get("nodes", [])
    reused = 0

    # Collect alloc nodes: op starts with "alloc"
    alloc_ids: list[str] = [
        str(node.get("id"))
        for node in nodes
        if str(node.get("op", "")).startswith("alloc")
    ]
    if len(alloc_ids) < 2:
        return 0

    # Index nodes by id for quick lookup.
    node_by_id: dict[str, dict[str, Any]] = {str(n.get("id")): n for n in nodes}

    # Compute last-use position for each alloc.
    last_use: dict[str, int] = {}
    for pos, node in enumerate(nodes):
        for inp in node.get("inputs", []):
            inp_str = str(inp)
            if inp_str in alloc_ids:
                last_use[inp_str] = pos

    # Free-list: maps (dtype, size) -> list of alloc_ids that are now free.
    free_pool: dict[tuple[str, Any], list[str]] = {}

    freed_at: dict[str, int] = {}
    for alloc_id in alloc_ids:
        freed_at[alloc_id] = last_use.get(alloc_id, -1)

    for pos, node in enumerate(nodes):
        node_id = str(node.get("id"))
        op = str(node.get("op", ""))

        # Release buffers whose last use was before this position.
        for alloc_id, last_pos in list(freed_at.items()):
            if last_pos < pos and alloc_id not in {
                v for vals in free_pool.values() for v in vals
            }:
                alloc_node = node_by_id.get(alloc_id)
                if alloc_node is not None:
                    dtype = str(alloc_node.get("dtype", "dynamic"))
                    size = alloc_node.get("attrs", {}).get("size")
                    free_pool.setdefault((dtype, size), []).append(alloc_id)

        if op.startswith("alloc") and node_id not in alloc_ids[:alloc_ids.index(node_id)]:
            dtype = str(node.get("dtype", "dynamic"))
            size = node.get("attrs", {}).get("size")
            key = (dtype, size)
            if key in free_pool and free_pool[key]:
                donor_id = free_pool[key].pop()
                attrs = dict(node.get("attrs", {}))
                attrs["reuse_of"] = donor_id
                node["attrs"] = attrs
                reused += 1

    return reused


def _cse_attrs_key(attrs: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    # Ignore non-semantic metadata so equivalent compute ops can fold together.
    ignored = {"result", "provenance", "hlir_id", "fn", "block"}
    items: list[tuple[str, Any]] = []
    for key, value in attrs.items():
        normalized_key = str(key)
        if normalized_key in ignored:
            continue
        items.append((normalized_key, _freeze_attr(value)))
    return tuple(sorted(items))


def _freeze_attr(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(sorted((str(k), _freeze_attr(v)) for k, v in value.items()))
    if isinstance(value, list):
        return tuple(_freeze_attr(v) for v in value)
    if isinstance(value, set):
        return tuple(sorted(_freeze_attr(v) for v in value))
    return value


def _const_value(node: dict[str, Any] | None) -> Any | None:
    if not node:
        return None
    if node.get("op") != "const":
        return None
    attrs = node.get("attrs", {})
    if not isinstance(attrs, dict):
        return None
    return attrs.get("value")


def _dtype_of(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return "dynamic"


def _eval_binary(op: str, left: Any, right: Any) -> Any | None:
    try:
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "%":
            return left % right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
    except Exception:
        return None
    return None

