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
from typing import Generator, List, Dict

# Models
from manv.models.line_model import LineModel

# Tokens
from manv.src.parser.tokens import *

class Token:
    """
    Class representing a line's tokens
    """
    line: LineModel
    tokens: Dict

    def __init__(self, line: LineModel, tokens: Dict) -> None:
        self.line = line
        self.tokens = tokens

class Tokens:
    """
    Class for representing the tokens generated
    by the Lexer.
    """
    file_path: str | None = None
    lines_count: int  = 0
    tokens: List[Token] = list()
    const_identifiers: List[str] = list()
    var_identifiers: List[str] = list()
    ptr_identifiers: List[str] = list()
    functions_identifiers: List[str] = list()

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


        # if-else condition blocks
        is_if_condition_block = False
        is_else_condition_block = False
        if_condition_block_count = 0
        else_condition_block_count = 0
        is_last_block_if_block = False
        
        for i, line in enumerate(data):
            tokens.lines_count += 1
            
            current_line = LineModel(
                content=line,
                line_number=i+1,
                last_line=last_line
            )

            if last_line is not None:
                last_line.next_line = current_line
            
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
            
            # NOTE: Instead of looping through each character, we 
            # need to create seperate functions to detect what instruction
            # is being given in the current line and generate tokens based off 
            # of it, this way we can have controll over the syntax of each individual
            # keyword
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
                if char == ' ':
                    last_char = char
                    last_line = current_line

                    continue
                
                # Comment line
                if char == "/" and next_char == "/":
                    token.tokens.append({KEYWORDS_SYNTAX_MAP[COMMENT_KEYWORD]: KEYWORDS[COMMENT_KEYWORD]})
                    token.tokens.append({TOKENS_SYNTAX_MAP[COMMENT_TOKEN]: current_line.content[i+2:]})
                    break

                # End-Of-Line without a semicolon
                if i != 0:                              # Ignore EOF in empty lines
                    if char != ";" and next_char == "\n":
                        # No semicolon needed at the EOF of an if-else block.
                        if char == "{":
                            continue

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
                    print(
                        f"[bold blue][DEBUG][reset]: Reached EOF of line '{current_line.line_number}'."
                    )
                    
                    token.tokens.append({TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS[SEMICOLON_SYMBOL]})
                    token_construct = ""
                    is_eof = False
                
                # Symbol '{' start of if-else block, function block, struct block...
                if char == "{":
                    token.tokens.append(
                        {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[LBRACE_SYMBOL]}
                    )
                    continue
                
                # Symbol '}' end if or else block
                if char == "}":
                    # End if condition block
                    if is_if_condition_block:
                        token.tokens.append(
                            {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[RBRACE_SYMBOL]}
                        )
                        is_if_condition_block = False
                        is_last_block_if_block = True
                        if_condition_block_count -= 1

                        continue
                    
                    # End else condition block
                    elif is_else_condition_block:
                        token.tokens.append(
                            {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[RBRACE_SYMBOL]}
                        )
                        is_else_condition_block = False
                        else_condition_block_count -= 1
                        
                        continue

                token_construct += char
                
                # Keyword: CONST_KEYWORD
                if token_construct == "const":
                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[CONST_KEYWORD]})
                    
                    const_declaration = self.parse_constant_declaration(
                        token_construct=token_construct,
                        current_index=i,
                        current_char=char,
                        line_content=current_line.content,
                        token=token
                    )

                    for tok in const_declaration:
                        token.tokens.append(
                            tok
                        )

                        # Save the constant identifier
                        if list(tok.items())[0][0] == TOKENS_SYNTAX_MAP[WORD_TOKEN]:
                            tokens.const_identifiers.append(
                                list(tok.items())[0][1]
                            )
                    
                    token_construct = ""
                    break
                
                # Keyword: VAR_KEYWORD
                if token_construct == "var":
                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] :  KEYWORDS_SYNTAX_MAP[VAR_KEYWORD]})

                    var_declaration = self.parse_variable_declaration(
                        token_construct=token_construct,
                        current_index=i,
                        current_char=char,
                        line_content=current_line.content,
                        token=token
                    )

                    for tok in var_declaration:
                        token.tokens.append(tok)

                        # Save the variable identifier
                        if list(tok.items())[0][0] == TOKENS_SYNTAX_MAP[WORD_TOKEN]:
                            tokens.var_identifiers.append(
                                list(tok.items())[0][1]
                            )
                        
                    
                    token_construct = ""
                    break
                
                # Keyword: PTR_KEYWORD
                if token_construct == "ptr":
                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] :  KEYWORDS_SYNTAX_MAP[PTR_KEYWORD]})

                    ptr_declaration = self.parse_pointer_declaration(
                        token_construct=token_construct,
                        current_index=i,
                        current_char=char,
                        line_content=current_line.content,
                        token=token
                    )

                    for tok in ptr_declaration:
                        token.tokens.append(tok)

                        # Save the pointer identifier
                        if list(tok.items())[0][0] == TOKENS_SYNTAX_MAP[WORD_TOKEN]:
                            tokens.ptr_identifiers.append(
                                list(tok.items())[0][1]
                            )
                        
                    token_construct = ""
                    break

                # Keyword: SIZE_INC_KEYWORD
                if token_construct == "size_inc":
                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[SIZE_INC_KEYWORD]})
                    token_construct = ""

                # Keyword: SIZE_DEC_KEYWORD
                if token_construct == "size_dec":
                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[SIZE_DEC_KEYWORD]})
                    token_construct = ""

                # Keyword: EMT_KEYWORD
                if token_construct == "emt":
                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[EMT_KEYWORD]})
                    token_construct = ""
                
                # Keyword: DEL_KEYWORD
                if token_construct == "del":
                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[DEL_KEYWORD]})
                    token_construct = ""
                
                # Keyword: MUL_KEYWORD, ADD_KEYWORD, SUB_KEYWORD, DIV_KEYWORD
                if token_construct in ["mul", "add", "sub", "div"]:
                    token.tokens.append({TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] : KEYWORDS_SYNTAX_MAP[MUL_KEYWORD]})
                    
                    parsed_op_elements, skip_indexes_list = self.parse_op_elements(
                        token_construct=token_construct,
                        current_index=i,
                        current_char=char,
                        last_char=last_char,
                        next_char=next_char,
                        line_content=current_line.content,
                        token=token
                    )

                    if parsed_op_elements is not None:
                        for element in parsed_op_elements:
                            token.tokens.append(
                                element
                            )
                        
                    token_construct = ""
                    break
                
                # Keyword: SYSCALL_KEYWORD
                if token_construct == "syscall":
                    token.tokens.append(
                        {TOKENS_SYNTAX_MAP[KEYWORD_TOKEN]: KEYWORDS_SYNTAX_MAP[SYSCALL_KEYWORD]}
                    )

                    syscall = self.parse_syscall_elements(
                        token_construct=token_construct,
                        current_index=i,
                        current_char=char,
                        last_char=last_char,
                        next_char=next_char,
                        line_content=current_line.content,
                        token=token
                    )

                    for tok in syscall:
                        token.tokens.append(tok)
                    
                    token_construct = ""
                    break
                
                # Keyword: IF_KEYWORD
                if token_construct == "if":
                    if_condition_block_count += 1
                    is_if_condition_block = True
                    
                    token.tokens.append(
                        {TOKENS_SYNTAX_MAP[KEYWORD_TOKEN]: KEYWORDS_SYNTAX_MAP[IF_KEYWORD]}
                    )

                    if_condition_tokens = self.parse_if_condition(
                        token_construct=token_construct,
                        current_index=i,
                        current_char=char,
                        last_char=last_char,
                        next_char=next_char,
                        line_content=current_line.content,
                        token=token
                    )

                    if if_condition_tokens is not None:
                        for tok in if_condition_tokens:
                            token.tokens.append(tok)
                        
                        token_construct = ""
                        break
                        
                # Keyword: ELSE_KEYWORD
                if token_construct == "else":
                    if not is_last_block_if_block:
                        print(f"[bold red][ERROR][reset]: Can't use else-condition without an if-condition in line '{token.line.line_number}'.")
                        sys.exit(1)
                    
                    token.tokens.append(
                        {TOKENS_SYNTAX_MAP[KEYWORD_TOKEN]: KEYWORDS_SYNTAX_MAP[ELSE_KEYWORD]}
                    )
                    token_construct = ""

                    else_condition_block_count += 1
                    is_else_condition_block = True

                    is_if_condition_block = False
                    is_last_block_if_block = False
                    if_condition_block_count -= 1
                
                # Constant identifier
                if token_construct in tokens.const_identifiers:
                    token.tokens.append(
                        {TOKENS_SYNTAX_MAP[CONST_IDENTIFIER_TOKEN]: token_construct}
                    )
                
                # Variable indentifier
                if token_construct in tokens.var_identifiers:
                    token.tokens.append(
                        {TOKENS_SYNTAX_MAP[VAR_IDENTIFIER_TOKEN]: token_construct}
                    )

                    # Change the variable's value
                    parsed_elements = self.parse_reasign_variable(
                        token_construct=token_construct,
                        current_index=i,
                        current_char=char,
                        last_char=last_char,
                        next_char=next_char,
                        line_content=current_line.content,
                        token=token
                    )

                    if parsed_elements is not None:
                        for tok in parsed_elements:
                            token.tokens.append(tok)

                # Pointer identifier
                if token_construct in tokens.ptr_identifiers:
                    token.tokens.append(
                        {TOKENS_SYNTAX_MAP[PTR_IDENTIFIER_TOKEN]: token_construct}
                    )
                
                # Function identifier
                if token_construct in tokens.functions_identifiers:
                    token.tokens.append(
                        {TOKENS_SYNTAX_MAP[FUNCTION_IDENTIFIER_TOKEN]: token_construct}
                    )

            tokens.tokens.append(token)

            last_line = current_line
            last_char = char
            
        return tokens

    def strip_line_from_comments(self, line_content: str) -> str:
        """
        Stip the line from comments and new line escape character.
        """
        in_string = False
        escaped = False
        result = []

        i = 0
        while i < len(line_content):
            char = line_content[i]

            # Handle escape characters
            if char == "\\" and not escaped:
                escaped = True
                result.append(char)
                i += 1
                continue

            # Toggle string context
            if char == '"' and not escaped:
                in_string = not in_string

            # Handle comment only if we're not in a string
            if not in_string and char == "/" and i + 1 < len(line_content) and line_content[i + 1] == "/":
                break  # Stop here — comment starts

            result.append(char)
            escaped = False
            i += 1

        # Join and strip trailing whitespace
        clean_line = ''.join(result).rstrip(" \t\r\n")

        return clean_line + "\n"

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

        return list(last_token.items())[0][0] == TOKENS_SYNTAX_MAP[SYMBOL_TOKEN] and list(last_token.items())[0][1] == SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL] 
    
    def is_last_token_ptr(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a ptr.
        """
        last_token = token.tokens[index]

        return list(last_token.items())[0][0] == TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] and list(last_token.items())[0][1] == KEYWORDS_SYNTAX_MAP[PTR_KEYWORD]

    def is_last_token_syscall(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a syscall.
        """
        last_token = token.tokens[index]

        return list(last_token.items())[0][0] == TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] and list(last_token.items())[0][1] == KEYWORDS_SYNTAX_MAP[SYSCALL_KEYWORD]
    
    def is_last_token_if(self, token: Tokens, index: int) -> bool:
        """
        Is the last token (or block) is an if-condition
        """
        last_token = token.tokens[index]
        
        return list(last_token.items())[0][0] == TOKENS_SYNTAX_MAP[KEYWORD_TOKEN] and list(last_token.items())[0][1] == KEYWORDS_SYNTAX_MAP[IF_KEYWORD]
    
    def is_line_context_op(self, token: Token) -> bool:
        """
        Is the line context a mathematical operation (mul, div, sub, add)
        """
        first_token = token.tokens[0]
        ops = [pair[1] for pair in list(KEYWORDS_SYNTAX_MAP.items())[:4]]

        return list(first_token.items())[0][1] in ops

    def is_line_context_const(self, token: Token) -> bool:
        """
        Is the current line context a constant declaration keyword.
        """
        return self.is_last_token_const(token=token, index=0)
    
    def is_line_context_var(self, token: Token) -> bool:
        """
        Is the current line context a variable declaration keyword.
        """
        return self.is_last_token_var(token=token, index=0)
    
    def is_line_context_ptr(self, token: Token) -> bool:
        """
        Is the current line context a pointer declaration keyword.
        """
        return self.is_last_token_ptr(token=token, index=0)
    
    def is_line_context_syscall(self, token: Token) -> bool:
        """
        Is the current line context a syscall.
        """
        return self.is_last_token_syscall(token=token, index=0)

    def is_line_context_if(self, token: Token) -> bool:
        """
        Is the current line context an if condition.
        """
        return self.is_last_token_if(token=token, index=0)

    def parse_constant_declaration(self, token_construct: str, current_index: int, current_char: str, line_content: str, token: Token) -> list:
        """
        Parse constant declaration elements: identifier, size, type, value.
        """
        elements = list()
        
        default_dynamic_size = 8   # 8 byte for 64 bit
        if self.is_line_context_const(token=token):
            line_content = line_content[current_index+1:]   # Ignore the 'const' keyword
            line_content = self.strip_line_from_comments(line_content=line_content)
            
            word = ""

            is_size_context = False     # Mark True when we encounter '['
                                        # Because that will be the start
                                        # of the constant's size
            for i, char in enumerate(line_content):
                next_char = None
                last_char = None
                
                if (i + 1) < len(line_content):
                    next_char = line_content[i+1]
                if (i - 1) >= 0:
                    last_char = line_content[i-1]

                # Ignore spaces
                if char == " ":
                    continue

                # Constant identifier
                #        x: or x[...]:        |        x :  or x [...]:
                if char in [":", "["] and len(elements) == 0: # Add length so we won't be adding everything
                    elements.append(
                        {TOKENS_SYNTAX_MAP[WORD_TOKEN]: word}
                    )
                    
                    # Size context
                    if char == "[":
                        is_size_context = True

                    word = ""
                
                # Constant Size
                if is_size_context:
                    # Depending on if the last character
                    # was '[' or the current character
                    # the sequence we are going to loop through
                    # is different.
                    sequence = None
                    if char == "[":
                        sequence = line_content[i+1:]
                    elif last_char == "[":
                        sequence = line_content[i:]

                    for x, size_n in enumerate(sequence):
                        if size_n == "]" and sequence[x+1] == ":":
                            break
                        
                        # Ignore spaces
                        if size_n == " ":
                            continue
                    
                        word += size_n
                    
                    elements.append(
                        {
                            LITERALS_SYNTAX_MAP[SIZE_LITERAL]: word
                        }
                    )

                    is_size_context = False
                    word = ""

                # Constant type
                if char == ":":
                    sequence = line_content[i+1:]

                    typ = ""
                    for x, type_char in enumerate(sequence):
                        if type_char == "=":
                            # Check if no size was given, meaning dynamic size
                            if len(elements) == 1:  # DO NOT CHANGE THIS PLS
                                elements.append(
                                    {LITERALS_SYNTAX_MAP[DYNAMIC_SIZE_LITERAL]: default_dynamic_size}
                                )
                            
                            elements.append(
                                {TOKENS_SYNTAX_MAP[TYPE_TOKEN]: typ}
                            )
                            typ = ""

                            break

                        # Ignore the spaces between ':' and the actual type
                        # :   int   =
                        #  ^^^   ^^^   <- Ignore them
                        if type_char == " ":
                            continue

                        typ += type_char
                    
                # Constant value
                if char == "=":
                    sequence = line_content[i + 1:]

                    value = ""
                    string_char = None
                    in_string = False

                    for x, value_char in enumerate(sequence):
                        # Start or end of string
                        if value_char in {'"', "'"}:
                            if not in_string:
                                in_string = True
                                string_char = value_char
                            elif value_char == string_char:
                                in_string = False

                        # End of value — only if NOT in a string
                        if not in_string and (value_char == ';' or value_char == '\n'):
                            elements.append({TOKENS_SYNTAX_MAP[VALUE_TOKEN]: value.strip()})
                            
                            # Append the semicolon if it's present
                            if value_char == ";":
                                elements.append({TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]})
                            break

                        value += value_char
                    
                # Break the loop in case all elements are lexed
                if len(elements) in [4, 5]:
                    break

                if char not in [" ", "[", "]", ":"]:
                    word += char
                
        return elements
    
    def parse_variable_declaration(self, token_construct: str, current_index: int, current_char: str, line_content: str, token: Token) -> tuple[dict, list[int]]:
        """
        Parse the variable declaration elements.
        """
        elements = list()

        default_dynamic_size = 8   # 8 byte for 64 bit
        if self.is_line_context_var(token=token):
            line_content = line_content[current_index+1:]   # Ignore the 'const' keyword
            line_content = self.strip_line_from_comments(line_content=line_content)
            word = ""

            is_size_context = False     # Mark True when we encounter '['
                                        # Because that will be the start
                                        # of the constant's size
            for i, char in enumerate(line_content):
                next_char = None
                last_char = None
                
                if (i + 1) < len(line_content):
                    next_char = line_content[i+1]
                if (i - 1) >= 0:
                    last_char = line_content[i-1]

                # Ignore spaces
                if char == " ":
                    continue

                # Variable identifier
                #        x: or x[...]:        |        x :  or x [...]:
                if char in [":", "["] and len(elements) == 0: # Add length so we won't be adding everything
                    elements.append(
                        {TOKENS_SYNTAX_MAP[WORD_TOKEN]: word}
                    )
                    
                    # Size context
                    if char == "[":
                        is_size_context = True

                    word = ""
                
                # Variable Size
                if is_size_context:
                    # Depending on if the last character
                    # was '[' or the current character
                    # the sequence we are going to loop through
                    # is different.
                    sequence = None

                    if char == "[":
                        sequence = line_content[i+1:]
                    elif last_char == "[":
                        sequence = line_content[i:]

                    for x, size_n in enumerate(sequence):
                        if size_n == "]" and sequence[x+1] == ":":
                            break
                        
                        # Ignore spaces
                        if size_n == " ":
                            continue
                    
                        word += size_n
                    
                    elements.append(
                        {
                            LITERALS_SYNTAX_MAP[SIZE_LITERAL]: word
                        }
                    )

                    is_size_context = False
                    word = ""

                # Variable type
                if char == ":":
                    sequence = line_content[i+1:]

                    typ = ""
                    for x, type_char in enumerate(sequence):
                        if type_char in ["=", ";", "\n"]:
                            # Check if no size was given, meaning dynamic size
                            if len(elements) == 1:  # DO NOT CHANGE THIS PLS
                                elements.append(
                                    {LITERALS_SYNTAX_MAP[DYNAMIC_SIZE_LITERAL]: default_dynamic_size}
                                )
                            
                            elements.append(
                                {TOKENS_SYNTAX_MAP[TYPE_TOKEN]: typ}
                            )

                            if type_char == ";" and sequence[x+1:x+2] == "\n":
                                elements.append(
                                    {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]}
                                )
                                
                            typ = ""

                            break

                        # Ignore the spaces between ':' and the actual type
                        # :   int   =
                        #  ^^^   ^^^   <- Ignore them
                        if type_char == " ":
                            continue

                        typ += type_char
                
                # Variable value
                if char == "=":
                    sequence = line_content[i + 1:]

                    value = ""
                    string_char = None
                    in_string = False

                    for x, value_char in enumerate(sequence):
                        # Start or end of string
                        if value_char in {'"', "'"}:
                            if not in_string:
                                in_string = True
                                string_char = value_char
                            elif value_char == string_char:
                                in_string = False

                        # End of value — only if NOT in a string
                        if not in_string and (value_char == ';' or value_char == '\n'):
                            elements.append({TOKENS_SYNTAX_MAP[VALUE_TOKEN]: value.strip()})
                            
                            # Append the semicolon if it's present
                            if value_char == ";":
                                elements.append({TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]})
                            break

                        value += value_char

                # Break the loop in case all elements are lexed
                if len(elements) in [4, 5]:
                    break

                if char not in [" ", "[", "]", ":"]:
                    word += char
        
        return elements

    def parse_pointer_declaration(self, token_construct: str, current_index: int, current_char: str, line_content: str, token: Token) -> tuple[dict, list[int]]:
        """
        Parse a pointer declaration elements.
        """
        elements = list()

        if self.is_line_context_ptr(token=token):
            line_content = line_content[current_index+1:]   # Ignore the 'const' keyword
            line_content = self.strip_line_from_comments(line_content=line_content)
            word = ""

            is_size_context = False     # Mark True when we encounter '['
                                        # Because that will be the start
                                        # of the constant's size
            for i, char in enumerate(line_content):
                next_char = None
                last_char = None
                
                if (i + 1) < len(line_content):
                    next_char = line_content[i+1]
                if (i - 1) >= 0:
                    last_char = line_content[i-1]

                # Ignore spaces
                if char == " ":
                    continue

                # Pointer identifier
                #        x: or x[...]:        |        x :  or x [...]:
                if char in [":", "["] and len(elements) == 0: # Add length so we won't be adding everything
                    elements.append(
                        {TOKENS_SYNTAX_MAP[WORD_TOKEN]: word}
                    )
                    
                    # Size context
                    if char == "[":
                        is_size_context = True

                    word = ""

                # Pointer type
                if char == ":":
                    sequence = line_content[i+1:]

                    typ = ""
                    for x, type_char in enumerate(sequence):
                        if type_char in ["=", ";", "\n"]:                       
                            elements.append(
                                {TOKENS_SYNTAX_MAP[TYPE_TOKEN]: typ}
                            )

                            if type_char == ";" and sequence[x+1:x+2] == "\n":
                                elements.append(
                                    {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]}
                                )
                                
                            typ = ""

                            break

                        # Ignore the spaces between ':' and the actual type
                        # :   int   =
                        #  ^^^   ^^^   <- Ignore them
                        if type_char == " ":
                            continue

                        typ += type_char
                
                # Pointer value
                if char == "=":
                    sequence = line_content[i + 1:]

                    value = ""
                    string_char = None
                    in_string = False

                    for x, value_char in enumerate(sequence):
                        # Start or end of string
                        if value_char in {'"', "'"}:
                            if not in_string:
                                in_string = True
                                string_char = value_char
                            elif value_char == string_char:
                                in_string = False

                        # End of value — only if NOT in a string
                        if not in_string and (value_char == ';' or value_char == '\n'):
                            elements.append({TOKENS_SYNTAX_MAP[VALUE_TOKEN]: value.strip()})
                            
                            # Append the semicolon if it's present
                            if value_char == ";":
                                elements.append({TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]})
                            break

                        value += value_char

                # Break the loop in case all elements are lexed
                if len(elements) in [3, 4]:
                    break

                if char not in [" ", ":"]:
                    word += char
        
        return elements

    def parse_op_elements(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token) -> tuple[dict, list[int]]:
        """
        Parse the elements (left, right) in a mathematical operation.
        """
        elements = list()
        skip_indexes_list = [i for i in range(current_index+1, len(line_content))]
        
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
                    elements.append({TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]})
                
                if len(elements) == 5:
                    break

        return elements, skip_indexes_list

    def parse_syscall_elements(self,  token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token) -> dict:
        """
        Parse syscall elements.
        """
        elements = list()

        max_syscall_idx = 456   # Source: https://filippo.io/linux-syscall-table/
        max_syscall_regs_n = 6
        
        if self.is_line_context_syscall(token=token):
            line_content = line_content[current_index+1:]
            line_content = self.strip_line_from_comments(line_content=line_content)
            line_content = line_content.split(",")

            # syscall number
            syscall_number = line_content[0]
            if not self.is_seq_char_int(seq_char=syscall_number):
                elements.append(
                    {TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]: syscall_number.strip()}
                )
            else:
                # The given syscall number is higher then 'max_syscall_idx'
                if int(syscall_number) > max_syscall_idx:
                    print(f"[bold red][ERROR][reset]: Invalid syscall number, in line '{token.line.line_number}'")
                    sys.exit(1)
                
                elements.append(
                    {LITERALS_SYNTAX_MAP[NUMBER_LITERAL]: int(syscall_number)}
                )
            
            # Registers value
            regs_values = line_content[1:-1]

            # Handle too many arguments passed
            if len(regs_values) > max_syscall_regs_n:
                print(f"[bold red][ERROR][reset]: syscall only supports up to 6 arguments (found 8), in line '{token.line.line_number}'.")
                sys.exit(1)
            
            for reg_value in regs_values:
                element = None
                reg_value = reg_value.strip()

                if reg_value.startswith("*"):
                    elements.append(
                        {TOKENS_SYNTAX_MAP[DEREFERENCE_PTR_TOKEN]: "*"}
                    )
                
                    reg_value = reg_value[1:]
                
                if self.is_seq_char_int(seq_char=reg_value):
                    element = {
                        LITERALS_SYNTAX_MAP[NUMBER_LITERAL]: int(reg_value)
                    }
                elif self.is_seq_char_float(seq_char=reg_value):
                    element = {
                        LITERALS_SYNTAX_MAP[FLOAT_LITERAL]: float(reg_value)
                    }
                else:
                    element = {
                        LITERALS_SYNTAX_MAP[STRING_LITERAL]: reg_value
                    }

                elements.append(element)

            # Error identifier
            error_identifier = line_content[-1]
            error_identifier = error_identifier.strip()

            if error_identifier[-1] == ";" or error_identifier[-2:] == ";\n":
                elements.append(
                    {TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]: error_identifier[:-1].strip()}
                )
                elements.append(
                    {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[SEMICOLON_SYMBOL]}
                )
            else:
                elements.append(
                    {TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]: error_identifier}
                )
        
        return elements

    def parse_condition(self,  token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token ) -> dict | None:
        """
        Parse conditions: '==', '!=', '>', '<', '>=', '=<'
        """
        elements = list()
        left_element = ""
        right_element = ""
        condition_symbol = ""
        is_left_element = True

        compare_map = {
            "==": EQUAL_TOKEN,
            "!=": NOT_EQUAL_TOKEN,
            ">": GREATER_THAN_TOKEN,
            ">=": GREATER_THAN_OR_EQUAL_TOKEN,
            "<": SMALLER_THAN_TOKEN,
            "=<": SMALLER_THAN_OR_EQUAL_TOKEN
        }
        index_0_list = [i[0] for i in compare_map]

        for i, char in enumerate(line_content):
            # Skip spaces
            if char == " ":
                continue
            
            if char in index_0_list and len(condition_symbol)  == 0:
                # Append the left element
                if self.is_seq_char_int(seq_char=left_element):
                    elements.append(
                        {LITERALS_SYNTAX_MAP[NUMBER_LITERAL]: left_element}
                    )
                elif self.is_seq_char_float(seq_char=left_element):
                    elements.append(
                        {LITERALS_SYNTAX_MAP[FLOAT_LITERAL]: left_element}
                    )
                else:
                    elements.append(
                        {TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]: left_element}
                    )
                
                is_left_element = False # Move to the right element
                condition_symbol += char

                # The condition symbols shouldn't contain a space
                # in between:
                # Example:
                #       10 = = 10;  // Should throw an error.
                #       10 == 10; // Should work
                if line_content[i+1] == " " and char not in [">", "<"]: # Characters like >, < will expect '=' after.
                    print(f"[bold red][ERROR][reset]: Invalid syntax in line '{token.line.line_number}'.")
                    sys.exit(1)
                elif line_content[i+1] == " " and char in [">", "<"]:
                     pass
                else:
                    condition_symbol += line_content[i+1]

                # Invalid compare token
                if condition_symbol not in compare_map:
                    print(f"[bold red][ERROR][reset]: Invalid compare symbol '{condition_symbol}' in line '{token.line.line_number}'")
                    sys.exit(1)
                else:
                    elements.append(
                        {TOKENS_SYNTAX_MAP[compare_map[condition_symbol]]: condition_symbol}
                    )
                
                # Skip this char so it won't be added to right or left element
                continue
            elif char in index_0_list and len(condition_symbol) == 2:
                continue
            
            # Append the char to right or left element
            if not is_left_element:
                right_element += char
            else:
                left_element += char
            
            # End of the right element
            if i == len(line_content)-1:
                if self.is_seq_char_int(seq_char=right_element):
                    elements.append(
                        {LITERALS_SYNTAX_MAP[NUMBER_LITERAL]: right_element}
                    )
                elif self.is_seq_char_float(seq_char=right_element):
                    elements.append(
                        {LITERALS_SYNTAX_MAP[FLOAT_LITERAL]: right_element}
                    )
                else:
                    elements.append(
                        {TOKENS_SYNTAX_MAP[IDENTIFIER_TOKEN]: right_element}
                    )

        return elements

    def parse_if_condition(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token ) -> dict | None:
        """
        Parse the condition in if-condition-block
        """
        elements = list()

        if self.is_line_context_if(token=token):
            condition = ""                  # Conditions for now are just comparison
            is_in_condition_block = False   # Track if we are inside of '()'
            rparen_symbol = False           # Track the '(' symbol
            is_rbrace_symbol = False        # Track the '{' symbol

            line_content = self.strip_line_from_comments(line_content=line_content)
            for char in line_content:
                if char == "(":
                    is_in_condition_block = True
                    elements.append(
                        {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[LPAREN_SYMBOL]}
                    )
                    continue
                elif char == ")":
                    is_in_condition_block = False
                    rparen_symbol = True
                elif char == "{":
                    is_rbrace_symbol = True
                
                if is_in_condition_block:
                    condition += char

            condition_elements = self.parse_condition(
                token_construct=token_construct,
                current_index=current_index,
                current_char=current_char,
                last_char=last_char,
                next_char=next_char,
                line_content=condition,
                token=token
            )

            for element in condition_elements:
                elements.append(element)
            
            if rparen_symbol:
                elements.append(
                    {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[RPAREN_SYMBOL]}
                )
            if is_rbrace_symbol:
                elements.append(
                    {TOKENS_SYNTAX_MAP[SYMBOL_TOKEN]: SYMBOLS_SYNTAX_MAP[LBRACE_SYMBOL]}
                )

            return elements

        return None

    def parse_reasign_variable(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: Token ) -> dict | None:
        """
        Parse reasign/asign a new value to a variable.
        """
        return None

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

    def escape_spaces_at_zero_idx(self, seq_char: str) -> str:
        """
        Escape spaces at index zero in sequence of characters.
        """
        def strip_space(seq_char: str) -> str:
            x = ""
            for char in seq_char:
                if char == " " and len(x) == 0:
                    continue

                x += char
            
            return x

        clean_seq_char = ""

        # From right-to-left
        right_seq_char = strip_space(seq_char=seq_char)
        
        # From left-to-right
        left_seq_char = strip_space(seq_char=right_seq_char[::-1])

        clean_seq_char = left_seq_char[::-1]

        return clean_seq_char
     
    def is_seq_char_int(self, seq_char: str) -> bool:
        """
        Check if a sequence of characters
        is actualy an integer
        """
        try:
            int(seq_char)
            return True
        except:
            return False
    
    def is_seq_char_float(self, seq_char: str) -> bool:
        """
        Check if a sequence of characters
        is actually a float.
        """
        try:
            float(seq_char)
            # If data is a number it can be both
            # an int and a float, so eliminate this
            # by checking if the string representation 
            # of the data contains a '.' which is only
            # found in floats.
            if "." not in str(seq_char):
                return False
            return True
        except:
            return False
        
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
