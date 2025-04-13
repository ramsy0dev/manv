# MIT License

# Copyright (c) 2025 ramsy0dev

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__all__ = [
    "Program",
    "BinaryOp",
    "Identifier",
    "Return",
    "Arguments",
    "Argument",
    "ArgumentValue",
    "Function",
    "CallFunction",
    "CallConstant",
    "Constant",
    "Assignment"
]

from typing import List
from dataclasses import dataclass, field

# Models
from manv.models.line_model import LineModel

# Base
from manv.src.ast.base import ASTNode

# Literals
from manv.src.builtin.literals import *

# Types
from manv.src.builtin.types import *


@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class Constant(ASTNode):
    identifier: Identifier
    size: NumberLiteral
    typ: Type
    value: ASTNode
    line: LineModel

    def __repr__(self) -> str:
        return f"Constant(identifier={self.identifier!r}, size={self.size!r}, typ={self.typ!r}, value={self.value!r}, source_code={self.source_code!r})"

@dataclass
class CallConstant(ASTNode):
    identifier: Identifier

@dataclass
class Variable(ASTNode):
    identifier: Identifier
    size: NumberLiteral
    typ: Type
    value: ASTNode
    line: LineModel

@dataclass
class Return(ASTNode):
    value: ASTNode


@dataclass
class ArgumentValue(ASTNode):
    identifier: Identifier
    value: ASTNode
    reg_label: str = None   # Used in syscall function

@dataclass
class Argument(ASTNode):
    identifier: Identifier
    typ: Type
    default_value: ASTNode
    reg_label: str = None   # Used for syscall functions

@dataclass
class Arguments(ASTNode):
    args_list: list[Argument]

@dataclass
class CallArguments(ASTNode):
    name: list[ArgumentValue]

@dataclass
class Function(ASTNode):
    identifier: Identifier
    arguments: Arguments
    statements: List[ASTNode]
    return_type: Type
    asm_code: list[str] = None
    is_syscall: bool = False
    
    def __repr__(self) -> str:
        return f"Function(identifier={self.identifier!r}, arguments={self.arguments!r}, asm_code={self.asm_code!r}, statements={self.statements}, return_type={self.return_type!r}, is_syscall={self.is_syscall!r})"

@dataclass
class CallFunction(ASTNode):
    identifier: Identifier
    args_list: list[ArgumentValue] | None = None

@dataclass
class BinaryOp(ASTNode):
    op: int
    left: ASTNode
    right: ASTNode

@dataclass
class Assignment(ASTNode):
    name: StringLiteral
    value: ASTNode

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    main: Function

    def __init__(self) -> None:
        self.statements = list()
        self.main = None
    
    def __repr__(self) -> str:
        return f"Program(statements={self.statements!r}, main={self.main!r})"
