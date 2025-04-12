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
    "Number",
    "Float",
    "String",
    "Char",
    "BinaryOp",
    "Identifier",
    "Constant",
    "Assignment"
]

from typing import List
from dataclasses import dataclass, field

# Base
from manv.src.ast.base import ASTNode

# Types
from manv.src.builtin.types import *

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

    def __init__(self) -> None:
        self.statements = list()
    
    def __repr__(self) -> str:
        return f"Program(statements={self.statements!r})"

@dataclass
class Number(ASTNode):
    value: int
    typ: Type = field(default_factory=IntType)

@dataclass
class Float(ASTNode):
    value: float
    typ: Type = field(default_factory=FloatType)

@dataclass
class String(ASTNode):
    value: str
    typ: Type = field(default_factory=StrType)

@dataclass
class Char(ASTNode):
    value: str
    typ: Type = field(default_factory=CharType)

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class Constant(ASTNode):
    identifier: Identifier
    size: Number
    typ: Type
    value: ASTNode

    def __repr__(self) -> str:
        return f"Constant(identifier={self.identifier!r}, size={self.size!r}, typ={self.typ!r}, value={self.value!r})"

@dataclass
class BinaryOp(ASTNode):
    op: int
    left: ASTNode
    right: ASTNode

@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode
