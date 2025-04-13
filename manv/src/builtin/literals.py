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
    "Literal",
    "NumberLiteral",
    "FloatLiteral",
    "StringLiteral",
    "CharLiteral",
    "TRUE",
    "FALSE",
    "NULL",
    "DynamicSize"
]

from dataclasses import dataclass, field

# AST base
from manv.src.ast.base import ASTNode

# Types
from manv.src.builtin.types import *

class Literal:
    pass

@dataclass
class NumberLiteral(ASTNode):
    value: int
    typ: Type = field(default_factory=IntType)

@dataclass
class FloatLiteral(ASTNode):
    value: float
    typ: Type = field(default_factory=FloatType)

@dataclass
class StringLiteral(ASTNode):
    value: str
    typ: Type = field(default_factory=StrType)

@dataclass
class CharLiteral(ASTNode):
    value: str
    typ: Type = field(default_factory=CharType)


@dataclass
class TRUE(Literal):
    value: int = 1

@dataclass
class FALSE(Literal):
    value: int = 0

@dataclass
class NULL(Literal):
    value: None = None

@dataclass
class DynamicSize(Literal):
    bits: 10

@dataclass
class UninitializedVariable(Literal):
    bits: 12
