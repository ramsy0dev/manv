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
    "Parser"
]

import os
import sys

from rich import print
from typing import List, Union
from dataclasses import dataclass,field

# Models
from manv.models.line_model import LineModel

# Tokens
from manv.src.parser.tokens import *

# Builtin
from manv.src.builtin.types import *
from manv.src.builtin.literals import *

# AST
from manv.src.ast.nodes import *

BUILTIN_TYPES_OBJ_MAP =  {
    IntType: NumberLiteral,
    FloatType: FloatLiteral,
    StrType: StringLiteral,
    CharType: CharLiteral
}

# Parser
class Parser:
    """
    Parser for building AST
    """
    def __init__(self) -> None:
        pass
    
    def parse(self, tokens) -> Program:
        """
        Build an AST
        """
        program = Program()

        last_line = None

        for i, token in enumerate(tokens.tokens):
            current_line = token.line
            
            if len(tokens.tokens) - ((i+1)+1) < 0:
                next_line = None
            else:
                next_line = tokens.tokens[i+1]

            file_path = tokens.file_path
            line_tokens = token.tokens
            line_n = current_line.line_number

            # Ignore Empty lines
            if len(line_tokens) == 0:
                continue

            # Keywords
            if list(line_tokens[0].items())[0][0] == TOKENS_SYNTAX_MAP[KEYWORD_TOKEN]:
                keyword = list(line_tokens[0].items())[0][1]
                # CONST_KEYWORD
                if keyword == KEYWORDS_SYNTAX_MAP[CONST_KEYWORD]:
                    const_identifier = list(line_tokens[1].items())[0][1]
                    const_size = list(line_tokens[2].items())[0][1]
                    const_type = list(line_tokens[3].items())[0][1]
                    const_value = list(line_tokens[4].items())[0][1]
                    
                    const_declaration = Constant(
                        identifier=Identifier(
                            name=const_identifier
                        ),
                        size=NumberLiteral(
                            value=const_size
                        ),
                        typ=BUILTIN_TYPES[const_type](),
                        value=BUILTIN_TYPES_OBJ_MAP[BUILTIN_TYPES[const_type]](
                            value=const_value
                        ),
                        line=current_line
                    )

                    program.statements.append(
                        const_declaration
                    )
        
            last_line = current_line

        return program
    
    # def call_stack(self, last_line: dict, current_line: dict, next_line: dict) -> str:
    #     """
    #     Call stack trace.
    #     """
    #     last_line_source_code = last_line["source_code"]
    #     current_line_source_code = current_line["source_code"]
    #     next_line_source_code = next_line["source_code"]
        
    #     msg = (
    #         f"\t   {last_line['line_n']} | {last_line_source_code.strip()}\n"
    #         f"\t-> {current_line['line_n']} | {current_line_source_code.strip()}\n"
    #         f"\t   {next_line['line_n']} | {next_line_source_code.strip()}\n"
    #     )

    #     return msg

    # def contains_characters(self, data: str, ignore_chars: list[str] | None = list()) -> bool:
    #     """
    #     Check if a sequence of data contains integers or not.
    #     """
    #     for char in data:
    #         try:
    #             if char in ignore_chars:
    #                 continue
    #             int(char)
    #         except Exception as e:
    #             return True
    
    # def check_value_type(self, _type: str, value: str) -> bool:
    #     """
    #     Check if the value of a constant/variable correspond to the type.
    #     """
    #     _type = get_reverse_key_value(_type, TYPES)
        
    #     if _type == INT_TYPE:
    #         try:
    #             int(value)
    #             return True
    #         except:
    #          return False
    #     elif _type == FLOAT_TYPE:
    #         try:
    #             float(value)
    #             return True
    #         except:
    #             return False
    #     elif _type == STR_TYPE:
    #         try:
    #             str(value)
    #             return True
    #         except:
    #             return False
    #     elif _type == CHAR_TYPE:
    #         try:
    #             return len(str(value)) == 1
    #         except:
    #             return False
    #     else:
    #         return None
    
    # def get_type_from_source(self, _type: str) -> int:
    #     """
    #     Get type from the declared source code.
    #     """
    #     for i in TYPE_SYNTAX_MAP:
    #         if TYPE_SYNTAX_MAP[i] == _type:
    #             return i
    
    # def get_size_of_obj(self, obj, seen=None) -> int:
    #     """
    #     Recursively find the true size of an object including its references
    #     """
    #     if seen is None:
    #         seen = set()

    #     obj_id = id(obj)
    #     if obj_id in seen:
    #         return 0  # Avoid infinite recursion for circular references

    #     seen.add(obj_id)
    #     size = sys.getsizeof(obj)

    #     if isinstance(obj, dict):
    #         size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in obj.items())
    #     elif isinstance(obj, (list, tuple, set, frozenset)):
    #         size += sum(deep_getsizeof(i, seen) for i in obj)

    #     return size
    
