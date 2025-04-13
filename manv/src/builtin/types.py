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
    "Type",
    "MultiType",
    "StrType",
    "IntType",
    "CharType",
    "FloatType",
    "CallType",
    "BUILTIN_TYPES"
]

from dataclasses import dataclass

class Type:
    pass

class MultiType:
    type_list: list[Type]

    def __init__(self, type_list: list[Type]) -> None:
        self.type_list = type_list

@dataclass
class StrType(Type):
    bits: int = 16

@dataclass
class CharType(Type):
    bits: int = 2

@dataclass
class IntType(Type):
    bits: int = 32

@dataclass
class FloatType(Type):
    bits: int = 64

@dataclass
class CallType(Type):
    bits: int = 22

BUILTIN_TYPES: dict[str, Type] = {
    "int": IntType,
    "float": FloatType,
    "str": StrType,
    "char": CharType,
}
