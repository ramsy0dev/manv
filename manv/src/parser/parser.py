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

                # VAR_KEYWORD
                if keyword == KEYWORDS_SYNTAX_MAP[VAR_KEYWORD]:
                    var_identifier = list(line_tokens[1].items())[0][1]
                    var_size = list(line_tokens[2].items())[0][1]
                    var_type = list(line_tokens[3].items())[0][1]
                    
                    # Variable can be uninitialized, so we need to check
                    # if a value is provided or not
                    var_value = None
                    if not list(line_tokens[4].items())[0][0] == SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]:
                        var_value = list(line_tokens[4].items())[0][1]

                    var_declaration = Variable(
                        identifier=Identifier(
                            name=var_identifier,
                        ),
                        size=NumberLiteral(
                            value=var_size
                        ),
                        typ=BUILTIN_TYPES[var_type](),
                        value=None,
                        line=current_line
                    )

                    program.statements.append(var_declaration)
                
                # Keyword: ptr
                if keyword == KEYWORDS_SYNTAX_MAP[PTR_KEYWORD]:
                    ptr_identifier = list(line_tokens[1].items())[0][1]
                    ptr_type = list(line_tokens[2].items())[0][1]
                    ptr_value = None

                    # The value of the pointer can be None
                    # in that case it will be 0 initialized
                    if list(line_tokens[3].items())[0][0] == TOKENS_SYNTAX_MAP[VALUE_TOKEN]:
                        ptr_value = list(line_tokens[3].items())[0][1]
                    else:
                        # 0 initialized pointer
                        ptr_value = 0

                    ptr_declaration = Pointer(
                        identifier=Identifier(
                            name=ptr_identifier,
                        ),
                        typ=BUILTIN_TYPES[ptr_type](),
                        value=MemoryAddress(
                            value=ptr_value
                        ),
                        line=current_line
                    )

                    program.statements.append(ptr_declaration)
                
                # Operations keywords (mul, div, add, sub)
                op_keywords = [
                    KEYWORDS[MUL_KEYWORD],
                    KEYWORDS[ADD_KEYWORD],
                    KEYWORDS[SUB_KEYWORD],
                    KEYWORDS[DIV_KEYWORD]
                ]

                if keyword in op_keywords:
                    left_element = list(line_tokens[1].items())[0][1]
                    left_element_literal = Identifier

                    if self.is_float(left_element):
                        left_element = float(left_element)
                        left_element_literal = FloatLiteral
                    
                    if self.is_integer(data=left_element):
                        left_element = int(left_element)
                        left_element_literal = NumberLiteral
                    
                    right_element = list(line_tokens[2].items())[0][1]
                    right_element_literal = Identifier

                    if self.is_float(data=right_element):
                        right_element = float(right_element)
                        right_element_literal = FloatLiteral
                    else:
                        if self.is_integer(data=right_element):
                            right_element = int(right_element)
                            right_element_literal = NumberLiteral
                    
                    result_var_identifier = list(line_tokens[4].items())[0][1]

                    op_class = None
                    match keyword:
                        case keyword if keyword == KEYWORDS_SYNTAX_MAP[MUL_KEYWORD]:
                            op_class = MultiplyOp
                        case keyword if keyword == KEYWORDS_SYNTAX_MAP[ADD_KEYWORD]:
                            op_class = AdditionOp
                        case keyword if keyword == KEYWORDS_SYNTAX_MAP[DIV_KEYWORD]:
                            op_class = DivideOp
                        case keyword if keyword == KEYWORDS_SYNTAX_MAP[SUB_KEYWORD]:
                            op_class = SubtractionOp
                    
                    op = op_class(
                        left=left_element_literal(left_element),
                        right=right_element_literal(right_element),
                        assign=OpResultAssignment(
                            identifier=Identifier(
                                name=result_var_identifier
                            )
                        )
                    )

                    program.statements.append(
                        op
                    )

                # keyword: syscall
                if keyword == KEYWORDS_SYNTAX_MAP[SYSCALL_KEYWORD]:
                    syscall_number = list(line_tokens[1].items())[0][1]
                    syscall_args = list()
                    error_identifier = list(line_tokens[-2].items())[0][1]

                    if list(line_tokens[1].items())[0][0] == TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]:
                        syscall_number = Identifier(name=syscall_number)
                    
                    is_dereference = False
                    for syscall_arg in line_tokens[2:-2]:
                        if list(syscall_arg.items())[0][0] == TOKENS_SYNTAX_MAP[DEREFERENCE_PTR_TOKEN]:
                            is_dereference = True
                            continue
                        
                        if is_dereference:
                            syscall_args.append(
                                DereferencePointer(
                                    identifier=Identifier(
                                        name=list(syscall_arg.items())[0][1]
                                    )
                                )
                            )
                            is_dereference = False
                            continue
                        
                        syscall_args.append(
                            list(syscall_arg.items())[0][1]
                        )

                    syscall = Syscall(
                        syscall_number=syscall_number,
                        args=syscall_args,
                        error=Identifier(name=error_identifier)
                    )

                    program.statements.append(syscall)
                
            last_line = current_line
        
        program.const_identifiers       = tokens.const_identifiers
        program.var_identifiers         = tokens.var_identifiers
        program.ptr_identifiers         = tokens.ptr_identifiers
        program.functions_identifiers   = tokens.functions_identifiers

        return program
    
    def get_type_literal(self, data):
        """
        Get the type literal of data
        """
        # Str
        if isinstance(data, str):
            return StringLiteral
        
        # Char
        if isinstance(data, str):
            if len(data) == 1:
                return CharLiteral

        # Int
        if isinstance(data, int):
            return NumberLiteral
        
        # Float
        if isinstance(data, float):
            return FloatLiteral
    
    def is_integer(self, data) -> bool:
        try:
            int(data)
            return True
        except:
            return False

    def is_float(self, data) -> bool:
        try:
            float(data)
            # If data is a number it can be both
            # an int and a float, so eliminate this
            # by checking if the string representation 
            # of the data contains a '.' which is only
            # found in floats.
            if "." not in str(data):
                return False
            return True
        except:
            return False
    

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
    
