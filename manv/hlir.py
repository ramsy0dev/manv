from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceSpan:
    uri: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "start_line": self.start_line,
            "start_col": self.start_col,
            "end_line": self.end_line,
            "end_col": self.end_col,
        }


@dataclass
class Provenance:
    primary_span: SourceSpan | None = None
    inlined_chain: list[SourceSpan] = field(default_factory=list)
    ast_id: str | None = None
    hlir_id: str | None = None
    graph_id: str | None = None
    kir_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary_span": self.primary_span.to_dict() if self.primary_span else None,
            "inlined_chain": [span.to_dict() for span in self.inlined_chain],
            "ast_id": self.ast_id,
            "hlir_id": self.hlir_id,
            "graph_id": self.graph_id,
            "kir_id": self.kir_id,
        }


@dataclass
class HInstruction:
    op: str
    dest: str | None = None
    type_name: str | None = None
    args: list[str] = field(default_factory=list)
    attrs: dict[str, Any] = field(default_factory=dict)
    effectful: bool = False
    effects: list[str] = field(default_factory=list)
    instr_id: str | None = None
    provenance: Provenance | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.instr_id,
            "op": self.op,
            "dest": self.dest,
            "type": self.type_name,
            "args": self.args,
            "attrs": self.attrs,
            "effectful": self.effectful,
            "effects": list(self.effects),
            "provenance": self.provenance.to_dict() if self.provenance else None,
        }


@dataclass
class HTerminator:
    op: str
    args: list[str] = field(default_factory=list)
    attrs: dict[str, Any] = field(default_factory=dict)
    term_id: str | None = None
    provenance: Provenance | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.term_id,
            "op": self.op,
            "args": self.args,
            "attrs": self.attrs,
            "provenance": self.provenance.to_dict() if self.provenance else None,
        }


@dataclass
class HBasicBlock:
    label: str
    instructions: list[HInstruction] = field(default_factory=list)
    terminator: HTerminator | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "instructions": [i.to_dict() for i in self.instructions],
            "terminator": self.terminator.to_dict() if self.terminator else None,
        }


@dataclass
class HFunction:
    name: str
    params: list[dict[str, Any]]
    return_type: str | None
    entry: str
    blocks: list[HBasicBlock]
    attrs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "params": self.params,
            "return_type": self.return_type,
            "entry": self.entry,
            "blocks": [b.to_dict() for b in self.blocks],
            "attrs": self.attrs,
        }


@dataclass
class HExternDecl:
    """Metadata for a single C extern function declaration.

    Carried on HModule so LLVM codegen can emit ``declare`` lines and the
    linker step can collect ``-l`` flags without re-scanning the AST.
    """

    manv_name: str
    c_name: str
    lib: str
    param_types: list[str | None]
    return_type: str | None
    varargs: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "manv_name": self.manv_name,
            "c_name": self.c_name,
            "lib": self.lib,
            "param_types": self.param_types,
            "return_type": self.return_type,
            "varargs": self.varargs,
        }


@dataclass
class HModule:
    version: str
    source: str
    functions: list[HFunction]
    attrs: dict[str, Any] = field(default_factory=dict)
    extern_fns: list[HExternDecl] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "source": self.source,
            "functions": [f.to_dict() for f in self.functions],
            "attrs": self.attrs,
            "extern_fns": [e.to_dict() for e in self.extern_fns],
        }
