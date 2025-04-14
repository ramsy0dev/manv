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
    "Lexer"
]

import sys

from rich import print
from typing import Generator

# Models
from manv.models.line_model import LineModel

# Tokens
from manv.src.parser.tokens import *

class Token:
    """
    Class representing a single token
    """
    line: LineModel
    tokens: dict

    def __init__(self, line: LineModel, tokens: dict) -> None:
        self.line = line
        self.tokens = tokens

class Tokens:
    """
    Class for representing the tokens generated
    by the Lexer.
    """
    file_path: str | None = None
    lines_count: int  = 0
    tokens: list[Token] = list()

    def __init__(self, file_path: str | None = None) -> None:
        self.file_path = file_path

class Lexer:
    """
    Lexer for manv language.
    """
    def __init__(self) -> None:
        self.global_identifiers = list() # Identifiers for variables, constants, functions that are globally available.

    def generate_tokens(self, data: Generator, file_path: str | None = None) -> Tokens:
        """
        Generates tokens from a program source code.
        """
        tokens = Tokens(
            file_path=file_path
        )
        
        last_line: LineModel | None = None

        for i, line in enumerate(data):
            tokens.lines_count += 1
            
            current_line = LineModel(
                content=line,
                line_number=i+1,
                last_line=last_line
            )

            if last_line is not None:
                last_line.next_line = current_line
            

            # print(f"[bold blue][DEBUG][reset]: {current_line}")
            split_line_content = [
                i  for i in current_line.content.split(" ") if i != ""
            ]

            # print(
            #     f"[bold blue][DEBUG][reset]: Current line '{current_line.line_number}'\n"
            #     f"\t   {current_line.line_number!r} | {current_line.content!r}\n"
            # )
            
            token = Token(
                line=current_line,
                tokens=list()
            )

            # Emtpy line
            if len(current_line.content) == 0:
                continue
            
            token_construct = ""
            last_char = None
            skip_indexes_list        = None
            skip_indexes_list_mirror = None # Mirror of skip_indexes_list

            for i, char in enumerate(current_line.content):
                # Skip processed indexes
                if skip_indexes_list is not None and len(skip_indexes_list) > 0:
                    skip_indexes_list_mirror = skip_indexes_list

                    for x, index in enumerate(skip_indexes_list_mirror):
                        if i == index:
                            skip_indexes_list.pop(x)

                            last_char = char
                            last_line = current_line

                            continue

                next_char = current_line.content[i+1] if i+1 < len(current_line.content) else None

                # Empty space
                # if char == ' ':
                #     last_char = char
                #     last_line = current_line

                #     # token.tokens.append({LITERALS_SYNTAX_MAP[SPACE_LITERAL]: " "})

                #     continue
                
                # Comment line
                if char == "/" and next_char == "/":
                    token.tokens.append({KEYWORDS_SYNTAX_MAP[COMMENT_KEYWORD]: KEYWORDS[COMMENT_KEYWORD]})
                    token.tokens.append({TOKENS_SYNTAX_MAP[COMMENT_TOKEN]: current_line.content[i+2:]})

                    break

                # End-Of-Line without a semicolon
                if i != 0:                              # Ignore EOF in empty lines
                    if char != ";" and next_char == "\n":
                        print(f"{char = }, {next_char = }, {last_char = }")
                        print(
                            f"[bold red][ERROR][reset]: Expected a semicolon at end of line '{token.line.line_number}'"
                        )
                        sys.exit(1)
                
                # End-Of-Line
                is_eof = False
                if char == ";":
                    if next_char == "\n":
                        is_eof = True
                    else:
                        text = current_line.content[i+1:]
                        for _, x in enumerate(text):
                            if x == "/" and text[_+1] == "/":
                                is_eof = True
                if is_eof:
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Reached EOF of line '{current_line.line_number}'."
                    # )
                    
                    token.tokens.append({SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]: SYMBOLS[SEMICOLON_SYMBOL]})
                    token_construct = ""
                    is_eof = False
                
                token_construct += char
                
                # print(
                #     f"[bold blue][DEBUG][reset]: Last char {last_char!r}, current char {char!r}, next char {next_char!r},constructed token {token_construct!r}"
                # )
                
                # Constant/Variable name
                constant_identifier = self.extract_constant_identifier(
                    token_construct=token_construct,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    token=token
                )

                variable_identifier = self.extract_variable_identifier(
                    token_construct=token_construct,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    token=token
                )

                if constant_identifier is not None or variable_identifier is not None:
                    log_msg = (f"[bold blue][DEBUG][reset]: Found ") + \
                        (f"constant identifier '{constant_identifier[TOKENS_SYNTAX_MAP[WORD_TOKEN]]}'" if constant_identifier is not None else f"variable identifier '{variable_identifier[TOKENS_SYNTAX_MAP[WORD_TOKEN]]}'") + \
                        (f"in line '{current_line.line_number}'.")
                    
                    # print(log_msg)
                    
                    if constant_identifier is not None:
                        token.tokens.append(constant_identifier)
                    if variable_identifier is not None:
                        token.tokens.append(variable_identifier)
                    
                    token_construct = ""

                # Constant/Variable size
                size, skip_indexes_list = self.extract_constant_variable_size(
                    token_construct=token_construct,
                    current_index=i,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    line_content=current_line.content,
                    token=token
                )

                if size is not None:
                    size_n = size[LITERALS_SYNTAX_MAP[SIZE_LITERAL]] if LITERALS_SYNTAX_MAP[SIZE_LITERAL] in size else size[LITERALS_SYNTAX_MAP[DYNAMIC_SIZE_LITERAL]]
                    is_dynamic = LITERALS_SYNTAX_MAP[DYNAMIC_SIZE_LITERAL] in size

                    log_msg = f"[bold blue][DEBUG][reset]: Found size literal '{size_n}' in line '{current_line.line_number}'." \
                        if not is_dynamic else f"[bold blue][DEBUG][reset]: Found dynamic size in line '{current_line.line_number}'." \
                    
                    # print(log_msg)
                    
                    token.tokens.append(size)
                    token_construct = ""
                
                # Constant/Variable type
                _type, skip_indexes_list = self.extract_constant_variable_type(
                    token_construct=token_construct,
                    current_index=i,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    line_content=current_line.content,
                    token=token
                )

                if _type is not None:
                    # print(f"[bold blue][DEBUG][reset]: Found type literal '{_type[TOKENS_SYNTAX_MAP[TYPE_TOKEN]]}' in line '{current_line.line_number}'.")
                    
                    token.tokens.append(_type)
                    token_construct = ""
                
                value, skip_indexes_list = self.extract_constant_variable_value(
                    token_construct=token_construct,
                    current_index=i,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    line_content=current_line.content,
                    token=token
                )

                if value is not None:
                    log_msg = ""
                    if TOKENS_SYNTAX_MAP[VALUE_TOKEN] in value:
                        log_msg = f"[bold blue][DEBUG][reset]: Found value '{value[TOKENS_SYNTAX_MAP[VALUE_TOKEN]]}' in line '{current_line.line_number}'."
                    else:
                        log_msg = f"[bold blue][DEBUG][reset]: No value set in line '{current_line.line_number}'."
                    
                    # print(log_msg)

                    token.tokens.append(value)
                    token_construct = ""
                
                
                # Math operation elements
                extract_op_elements, skip_indexes_list = self.extract_op_elements(
                    token_construct=token_construct,
                    current_index=i,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    line_content=current_line.content,
                    token=token
                )

                if extract_op_elements is not None:
                    for element in extract_op_elements:
                        token.tokens.append(
                            element
                        )
                    
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found math operation elements '{extract_op_elements}' in line '{current_line.line_number}'"
                    # )
                    token_constrruct = ""
                
                # Keyword: CONST_KEYWORD
                if token_construct == "const":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[CONST_KEYWORD]})
                    token_construct = ""
                
                # Keyword: VAR_KEYWORD
                if token_construct == "var":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] :  KEYWORDS_SYNTAX_MAP[VAR_KEYWORD]})
                    token_construct = ""

                # Keyword: MUL_KEYWORD
                if token_construct == "mul":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[MUL_KEYWORD]})
                    token_construct = ""

                # Keyword: SIZE_INC_KEYWORD
                if token_construct == "size_inc":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[SIZE_INC_KEYWORD]})
                    token_construct = ""

                # Keyword: SIZE_DEC_KEYWORD
                if token_construct == "size_dec":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[SIZE_DEC_KEYWORD]})
                    token_construct = ""

                # Keyword: EMT_KEYWORD
                if token_construct == "emt":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[EMT_KEYWORD]})
                    token_construct = ""
                
                # Keyword: DEL_KEYWORD
                if token_construct == "del":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[DEL_KEYWORD]})
                    token_construct = ""
                
                # Keyword: MUL_KEYWORD
                if token_construct == "mul":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[MUL_KEYWORD]})
                    token_construct = ""
                
                # Keyword: ADD_KEYWORD
                if token_construct == "add":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[ADD_KEYWORD]})
                    token_construct = ""
                
                # Keyword: DIV_KEYWORD
                if token_construct == "div":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[DIV_KEYWORD]})
                    token_construct = ""

                # Keyword: SUB_KEYWORD
                if token_construct == "sub":
                    # print(
                    #     f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{current_line.line_number}'."
                    # )

                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[SUB_KEYWORD]})
                    token_construct = ""

            tokens.tokens.append(token)

            last_line = current_line
            last_char = char
            
        return tokens

    def is_last_token_const(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a constant keyword
        """
        const_token = {TOKENS_SYNTAX_MAP[KEYWORD_TOKEN]: KEYWORDS_SYNTAX_MAP[CONST_KEYWORD]}

        last_token = token.tokens[index]

        return const_token == last_token

    def is_last_token_var(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a variable keyword
        """
        var_token = {TOKENS_SYNTAX_MAP[KEYWORD_TOKEN]: KEYWORDS_SYNTAX_MAP[VAR_KEYWORD]}

        last_token = token.tokens[index]

        return var_token == last_token

    def is_last_token_word(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a word (identifier)
        """
        last_token = token.tokens[index]
        
        return list(last_token.items())[0][0] == TOKENS_SYNTAX_MAP[WORD_TOKEN]

    def is_last_token_size(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a size or dynamic size.
        """
        last_token = token.tokens[index]

        return list(last_token.items())[0][0] in [LITERALS_SYNTAX_MAP[SIZE_LITERAL], LITERALS_SYNTAX_MAP[DYNAMIC_SIZE_LITERAL]]
    
    def is_last_token_type(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a type.
        """
        last_token = token.tokens[index]

        return list(last_token.items())[0][0] == TOKENS_SYNTAX_MAP[TYPE_TOKEN]
    
    def is_last_token_semicolon(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a semicolon (EOF)
        """
        last_token = token.tokens[index]

        return list(last_token.items())[0][0] == SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]
    
    def is_line_context_op(self, token: Token) -> bool:
        """
        Is the line context a mathematical operation (mul, div, sub, add)
        """
        first_token = token.tokens[0]
        ops = [pair[1] for pair in list(KEYWORDS_SYNTAX_MAP.items())[:4]]

        return list(first_token.items())[0][1] in ops

    def extract_constant_identifier(self, token_construct: str, current_char: str, last_char: str, next_char: str, token: Token) -> dict:
        """
        Extract the constant's identifier
        """
        if len(token.tokens) == 0:
            return None

        if self.is_last_token_const(token=token) and next_char in ["[", ":"]:
            return {
                TOKENS_SYNTAX_MAP[WORD_TOKEN]: token_construct,
            }
    
    def extract_variable_identifier(self, token_construct: str, current_char: str, last_char: str, next_char: str, token: Token) -> dict:
        """
        Extract variable's identifier.
        """
        if len(token.tokens) == 0:
            return None
        
        if self.is_last_token_var(token=token) and next_char in ["[", ":"]:
            return {
                TOKENS_SYNTAX_MAP[WORD_TOKEN]: token_construct,
            }
    
    def extract_constant_variable_size(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token) -> tuple[dict, list[int]]:
        """
        Extract the constant/variable 's size.
        """
        size = ""
        skip_indexes_list = []

        if len(token.tokens) == 0:
            return None, None
        
        if self.is_last_token_word(token=token) and current_char == "[":
            split_line = [_ for _ in line_content[current_index:]]
            for i, char in enumerate(split_line):
                if char == "]":
                    break
                
                if char == "[":
                    continue

                size += char
                
                skip_indexes_list.append(
                    current_index + i
                )
        # Check if no fixed size was declared
        elif self.is_last_token_word(token=token) and current_char == ":":
            return {LITERALS_SYNTAX_MAP[DYNAMIC_SIZE_LITERAL]: 0}, skip_indexes_list
        
        if len(size) != 0:
            return {LITERALS_SYNTAX_MAP[SIZE_LITERAL]: size}, skip_indexes_list
        
        return None, skip_indexes_list

    def extract_constant_variable_type(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token) -> tuple[dict, list[int]]:
        """
        Extract constant/variable 's type.
        """
        _type = ""
        skip_indexes_list = []

        if len(token.tokens) == 0:
            return None, None
        
        if self.is_last_token_size(token=token) and current_char == ":":
            for i, char in enumerate(line_content[current_index+1:]):
                # Ignore spaces
                if char == ' ':
                    continue
                
                # Stop at semicolon in case no value was given to the constant/variable
                # or at EQUAL_SYMBOL if otherwise.
                if char in [";", "="]:
                    break

                _type += char

                skip_indexes_list.append(
                    current_index + i
                )

            return {TOKENS_SYNTAX_MAP[TYPE_TOKEN]: _type}, skip_indexes_list
        
        return None, None

    def extract_constant_variable_value(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token) -> tuple[dict, list[int]]:
        """
        Extract constant/variable 's value
        """
        value = ""
        skip_indexes_list = []

        if len(token.tokens) == 0:
            return None, None
        
        if self.is_last_token_type(token=token) and current_char == "=":
            in_string = False
            string_char = None  # to track whether it's " or '
            
            for i, char in enumerate(line_content[current_index + 1:]):
                absolute_index = current_index + 1 + i

                # Skip leading spaces
                if char == ' ' and len(value) == 0:
                    continue

                # Handle string start/end
                if char in {'"', "'"}:
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif string_char == char:
                        in_string = False  # closing the string

                # Stop at semicolon only if not inside a string
                if char == ';' and not in_string:
                    break
                
                value += char

                skip_indexes_list.append(
                    current_index + i
                )
            
            return {TOKENS_SYNTAX_MAP[VALUE_TOKEN]: value}, skip_indexes_list

        return None, None
    
    def extract_op_elements(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token) -> tuple[dict, list[int]]:
        """
        Extract the elements (left, right) in a mathematical operation.
        """
        elements = list()
        skip_indexes_list = [i for i in range(current_index, len(line_content))]

        if len(token.tokens) == 0:
            return None, None
        
        def is_identifier(elem) -> bool:
            for i in elem:
                try:
                    int(i)
                except:
                    return True
            return False

        # Check if the line context is an operation (mul, div, add, sub)
        if self.is_line_context_op(token=token):
            left_element = ""
            right_element = ""
            result_var_identifier = ""

            split_line_content = line_content.split(" ")    # Spliting the line is more convenient

            # Operation keywords mul, div, add, sub
            op_keywords = list()
            for pair in list(KEYWORDS.items())[:4]:
                op_keywords.append(pair[1])
            
            for i, char in enumerate(split_line_content):
                # Skip the operation keyword (mul, add, div, sub)
                if char in op_keywords:
                    continue
                
                # Left element
                if char.startswith("("):
                    left_element = char[1:-1] # Remove '(', ','
                    
                    elements.append(
                        {(LITERALS_SYNTAX_MAP[OP_LEFT_ELEMENT_LITERAL] if not is_identifier(left_element) else TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]): left_element}
                    )

                # Right element
                if char.endswith(")"):
                    right_element = char[:-1] # Remove ')'
                    
                    elements.append(
                        {(LITERALS_SYNTAX_MAP[OP_LEFT_ELEMENT_LITERAL] if not is_identifier(right_element) else TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]) : right_element}
                    )
                
                # into keyword
                if char == "into":
                    elements.append(
                        {KEYWORDS_SYNTAX_MAP[INTO_KEYWORD]: "into"}
                    )
                
                # Result identifier
                if split_line_content[i-1] == "into" and char.endswith(";\n"):
                    result_var_identifier = char[:-2] # Remove ';\n'

                    elements.append({TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]: result_var_identifier})
                    elements.append({SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]: ";"})

        return elements, skip_indexes_list

    def check_value_type(self, _type: str, value: str) -> bool:
        """
        Check if the value of a constant/variable correspond to the type.
        """
        _type = self.get_type_from_source(_type)
        
        if _type == INT_TYPE:
            try:
                int(value)
                return True
            except:
             return False
        elif _type == FLOAT_TYPE:
            try:
                float(value)
                return True
            except:
                return False
        elif _type == STR_TYPE:
            try:
                str(value)
                return True
            except:
                return False
        elif _type == CHAR_TYPE:
            try:
                return len(str(value)) == 1
            except:
                return False
        else:
            return None

    def get_size_of_obj(self, obj, seen=None) -> int:
        """
        Recursively find the true size of an object including its references
        """
        if seen is None:
            seen = set()

        obj_id = id(obj)
        if obj_id in seen:
            return 0  # Avoid infinite recursion for circular references

        seen.add(obj_id)
        size = sys.getsizeof(obj)

        if isinstance(obj, dict):
            size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set, frozenset)):
            size += sum(deep_getsizeof(i, seen) for i in obj)

        return size
    
    def contains_characters(self, data: str, ignore_chars: list[str] | None = list()) -> bool:
        """
        Check if a sequence of data contains integers or not.
        """
        for char in data:
            try:
                if char in ignore_chars:
                    continue
                int(char)
            except Exception as e:
                return True
    
    def convert_value_type(self, value: str, _type: int) -> int | str | float:
        """
        Convert a given value into its type.
        """
        _type = self.get_type_from_source(_type)

        if _type == INT_TYPE:
            return int(value)
        elif _type == FLOAT_TYPE:
            return float(value)
        elif _type == STR_TYPE:
            str(value)
        elif _type == CHAR_TYPE:
            str(value)

    def get_type_from_source(self, _type: str) -> int:
        """
        Get type from the declared source code.
        """
        for i in TYPE_SYNTAX_MAP:
            if TYPE_SYNTAX_MAP[i] == _type:
                return i

    def remove_comments_from_line(self, data: str) -> str:
        """
        Remove comments from a line.
        
        Args:
            data (str): The line's data.
        
        Returns:
            str: The clean line, without comments
        """
        if "//" in data:
            data = data.split("//")[0][0:-1] # NOTE: [0:-1] is for removing the last space between the size and the '//'
    
        return data
