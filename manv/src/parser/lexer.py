
import sys

from rich import print
from typing import Generator

from manv.models.line_model import LineModel

# Tokens
from manv.src.parser.tokens import *

# Tokens types
TOKENS: dict[int, str] = {
    KEYWORD_TOKEN       : "KEYWORD_TOKEN",
    WORD_TOKEN          : "WORD_TOKEN", 
    IDENTIFIER_TOKEN    : "IDENTIFIER_TOKEN",
    DYNAMIC_SIZE_TOKEN  : "DYNAMIC_SIZE_TOKEN",
    TYPE_TOKEN          : "TYPE_TOKEN",
    VALUE_TOKEN         : "VALUE_TOKEN"
}

# Keywords binded to their string representation
KEYWORDS: dict[int, str] = {
    # Operations keywords
    MUL_KEYWORD: "MUL_KEYWORD",
    ADD_KEYWORD: "ADD_KEYWORD",
    DIV_KEYWORD: "DIV_KEYWORD",
    SUB_KEYWORD: "SUB_KEYWORD",

    # Variables/Constants keywords
    CONST_KEYWORD: "CONST_KEYWORD",
    VAR_KEYWORD: "VAR_KEYWORD",
    SIZE_INC_KEYWORD: "SIZE_INC_KEYWORD",
    SIZE_DEC_KEYWORD: "SIZE_DEC_KEYWORD",
    EMT_KEYWORD: "EMT_KEYWORD",
    DEL_KEYWORD: "DEL_KEYWORD"
}

# Types binded to their string representation
TYPE_SYNTAX_MAP: dict[int, str] = {
    INT_TYPE: "INT_TYPE",
    FLOAT_TYPE: "FLOAT_TYPE",
    STR_TYPE: "STR_TYPE",
    CHAR_TYPE: "CHAR_TYPE"
}

TYPES: dict[str, int] = {
    "int": INT_TYPE,
    "float": FLOAT_TYPE,
    "str": STR_TYPE,
    "char": CHAR_TYPE,
}

# Literals binded to their string respresentation
LITERALS: dict[int, str] = {
    SIZE_LITERAL: "SIZE_LITERAL",
    DYNAMIC_SIZE_LITERAL: "DYNAMIC_SIZE_LITERAL",
    NUMBER_LITERAL: "NUMBER_LITERAL",
    FLOAT_LITERAL: "FLOAT_LITERAL",
    BIN_LITERAL: "BIN_LITERAL",
    HEX_LITERAL: "HEX_LITERAL",
    TRUE_LITERAL: "TRUE_LITERAL",
    FALSE_LITERAL: "FALSE_LITERAL"
}

# MAP_LITERALS: dict[int, str] = {
#     TRUE_LITERAL: "TRUE",
#     FALSE_LITERAL: "FAlSE"
# }

# Symbols binded to their string representation
SYMBOLS: dict[int, str] = {
    SEMICOLON_SYMBOL: "SEMICOLON_SYMBOL",
    COLON_SYMBOL: "COLON_SYMBOL",
    COMMA_SYMBOL: "COMMA_SYMBOL",
    DOT_SYMBOL: "DOT_SYMBOL",
    LPAREN_SYMBOL: "LPAREN_SYMBOL",
    RPAREN_SYMBOL: "RPAREN_SYMBOL",
    LBRACE_SYMBOL: "LBRACE_SYMBOL",
    RBRACE_SYMBOL: "RBRACE_SYMBOL",
    LBRACKET_SYMBOL: "LBRACKET_SYMBOL",
    RBRACKET_SYMBOL: "RBRACKET_SYMBOL",
    PLUS_SYMBOL: "PLUS_SYMBOL",
    MINUS_SYMBOL: "MINUS_SYMBOL",
    ASTERISK_SYMBOL: "ASTERISK_SYMBOL",
    SLASH_SYMBOL: "SLASH_SYMBOL",
    PERCENT_SYMBOL: "PERCENT_SYMBOL",
    AMPERSAND_SYMBOL: "AMPERSAND_SYMBOL",
    PIPE_SYMBOL: "PIPE_SYMBOL",
    CARET_SYMBOL: "CARET_SYMBOL",
    TILDE_SYMBOL: "TILDE_SYMBOL",
    EXCLAMATION_SYMBOL: "EXCLAMATION_SYMBOL",
    QUESTION_SYMBOL: "QUESTION_SYMBOL",
    EQUALS_SYMBOL: "EQUALS_SYMBOL",
    LESS_THAN_SYMBOL: "LESS_THAN_SYMBOL",
    GREATER_THAN_SYMBOL: "GREATER_THAN_SYMBOL",
    DOUBLE_EQUALS_SYMBOL: "DOUBLE_EQUALS_SYMBOL",
    NOT_EQUALS_SYMBOL: "NOT_EQUALS_SYMBOL",
    LESS_THAN_EQUALS_SYMBOL: "LESS_THAN_EQUALS_SYMBOL",
    GREATER_THAN_EQUALS_SYMBOL: "GREATER_THAN_EQUALS_SYMBOL",
    PLUS_EQUALS_SYMBOL: "PLUS_EQUALS_SYMBOL",
    MINUS_EQUALS_SYMBOL: "MINUS_EQUALS_SYMBOL",
    ASTERISK_EQUALS_SYMBOL: "ASTERISK_EQUALS_SYMBOL",
    SLASH_EQUALS_SYMBOL: "SLASH_EQUALS_SYMBOL",
    PERCENT_EQUALS_SYMBOL: "PERCENT_EQUALS_SYMBOL",
    AMPERSAND_EQUALS_SYMBOL: "AMPERSAND_EQUALS_SYMBOL",
    PIPE_EQUALS_SYMBOL: "PIPE_EQUALS_SYMBOL",
    CARET_EQUALS_SYMBOL: "CARET_EQUALS_SYMBOL",
    LEFT_SHIFT_SYMBOL: "LEFT_SHIFT_SYMBOL",
    RIGHT_SHIFT_SYMBOL: "RIGHT_SHIFT_SYMBOL",
    LEFT_SHIFT_EQUALS_SYMBOL: "LEFT_SHIFT_EQUALS_SYMBOL",
    RIGHT_SHIFT_EQUALS_SYMBOL: "RIGHT_SHIFT_EQUALS_SYMBOL",
    DOUBLE_PIPE_SYMBOL: "DOUBLE_PIPE_SYMBOL",
    DOUBLE_AMPERSAND_SYMBOL: "DOUBLE_AMPERSAND_SYMBOL",
    DOUBLE_PLUS_SYMBOL: "DOUBLE_PLUS_SYMBOL",
    DOUBLE_MINUS_SYMBOL: "DOUBLE_MINUS_SYMBOL",
    ARROW_SYMBOL: "ARROW_SYMBOL",
    DOUBLE_ARROW_SYMBOL: "DOUBLE_ARROW_SYMBOL",
    ELLIPSIS_SYMBOL: "ELLIPSIS_SYMBOL",
    HASHTAG_SYMBOL: "HASHTAG_SYMBOL",
    BACKSLASH_SYMBOL: "BACKSLASH_SYMBOL",
    AT_SYMBOL: "AT_SYMBOL",
    DOLLAR_SYMBOL: "DOLLAR_SYMBOL",
}

# Lexer rules
LEXER_RULES: dict[int, str] = {
    CONST_KEYWORD: r""
}

class Tokens:
    """
    Class for representing the tokens generated
    by the Lexer.
    """
    file_path: str | None = None
    lines_count: int  = 0
    tokens: list[dict] = list()

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
            
            # line = self.remove_comments_from_line(data=line.strip())
            line = LineModel(content=line, line_number=i)
            split_line_content = [
                i  for i in line.content.split(" ") if i != ""
            ]

            print(
                f"[bold blue][DEBUG][reset]: Current line '{line.line_number+1}'\n"
                f"\t   {line.line_number+1!r} | {line.content!r}\n"
            ) 
            
            token: dict = {
                "line_n": line.line_number+1,
                "tokens": list()
            }
            
            # Emtpy line
            if len(line.content) == 0:
                continue
            
            token_construct = ""
            last_char = None
            skip_indexes_list        = None
            skip_indexes_list_mirror = None # Mirror of skip_indexes_list

            for i, char in enumerate(line.content):
                # Skip processed indexes
                if skip_indexes_list is not None and len(skip_indexes_list) > 0:
                    skip_indexes_list_mirror = skip_indexes_list

                    for x, index in enumerate(skip_indexes_list_mirror):
                        if i == index:
                            skip_indexes_list.pop(x)

                            last_char = char
                            last_line = line

                            continue

                next_char = line.content[i+1] if i+1 < len(line.content) else None

                # Empty space
                if char == ' ':
                    last_char = char
                    last_line = line
                    
                    continue
                
                # Comment line
                if char == "/" and next_char == "/":
                    print(f"[bold blue][DEBUG][reset]: Skipping line '{line.line_number+1}', line contains a comment.")
                    break

                # End-Of-Line without a semicolon
                if i != 0:      # Ignore EOF in empty lines
                    if char != ";" and next_char == "\n":
                        print(f"{char = }, {next_char = }, {last_char = }")
                        print(
                        f"[bold red][ERROR][reset]: Expected a semicolon at end of line '{line.line_number+1}'"
                        )
                        sys.exit(1)
                
                # End-Of-Line
                is_eof = False
                if char == ";":
                    if next_char == "\n":
                        is_eof = True
                    else:
                        text = line.content[i+1:]
                        for _, x in enumerate(text):
                            if x == "/" and text[_+1] == "/":
                                is_eof = True
                if is_eof:
                    print(
                        f"[bold blue][DEBUG][reset]: Reached EOF of line '{line.line_number+1}'."
                    )
                    
                    token["tokens"].append({SYMBOLS[SEMICOLON_SYMBOL]: ";"})
                    token_construct = ""
                    is_eof = False
                
                token_construct += char
                
                print(
                    f"[bold blue][DEBUG][reset]: Last char {last_char!r}, current char {char!r}, next char {next_char!r},constructed token {token_construct!r}"
                )
                
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
                        (f"constant identifier '{constant_identifier[TOKENS[WORD_TOKEN]]}'" if constant_identifier is not None else f"variable identifier '{variable_identifier[TOKENS[WORD_TOKEN]]}'") + \
                        (f"in line '{line.line_number+1}'.")
                    
                    print(log_msg)
                    
                    if constant_identifier is not None:
                        token["tokens"].append(constant_identifier)
                    else:
                        token["tokens"].append(variable_identifier)
                    
                    token_construct = ""

                # Constant/Variable size
                size, skip_indexes_list = self.extract_constant_variable_size(
                    token_construct=token_construct,
                    current_index=i,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    line_content=line.content,
                    token=token
                )

                if size is not None:
                    size_n = size[LITERALS[SIZE_LITERAL]] if LITERALS[SIZE_LITERAL] in size else size[LITERALS[DYNAMIC_SIZE_LITERAL]]
                    is_dynamic = LITERALS[DYNAMIC_SIZE_LITERAL] in size

                    log_msg = f"[bold blue][DEBUG][reset]: Found size literal '{size_n}' in line '{line.line_number+1}'." \
                        if not is_dynamic else f"[bold blue][DEBUG][reset]: Found dynamic size in line '{line.line_number+1}'." \
                    
                    print(log_msg)
                    
                    token["tokens"].append(size)
                    token_construct = ""
                
                # Constant/Variable type
                _type, skip_indexes_list = self.extract_constant_variable_type(
                    token_construct=token_construct,
                    current_index=i,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    line_content=line.content,
                    token=token
                )

                if _type is not None:
                    print(f"[bold blue][DEBUG][reset]: Found type literal '{_type[TOKENS[TYPE_TOKEN]]}' in line '{line.line_number}'.")
                    
                    token["tokens"].append(_type)
                    token_construct = ""
                
                value, skip_indexes_list = self.extract_constant_variable_value(
                    token_construct=token_construct,
                    current_index=i,
                    current_char=char,
                    last_char=last_char,
                    next_char=next_char,
                    line_content=line.content,
                    token=token
                )

                if value is not None:
                    log_msg = ""
                    if TOKENS[VALUE_TOKEN] in value:
                        log_msg = f"[bold blue][DEBUG][reset]: Found value '{value[TOKENS[VALUE_TOKEN]]}' in line '{line.line_number}'."
                    else:
                        log_msg = f"[bold blue][DEBUG][reset]: No value set in line '{line.line_number}'."
                    
                    print(log_msg)

                    token["tokens"].append(value)
                    token_construct = ""
                
            
                # Keyword: CONST_KEYWORD
                if token_construct == "const":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[CONST_KEYWORD]})
                    token_construct = ""
                
                # Keyword: VAR_KEYWORD
                if token_construct == "var":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] :  KEYWORDS[VAR_KEYWORD]})
                    token_construct = ""

                # Keyword: MUL_KEYWORD
                if token_construct == "mul":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[MUL_KEYWORD]})
                    token_construct = ""

                # Keyword: SIZE_INC_KEYWORD
                if token_construct == "size_inc":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[SIZE_INC_KEYWORD]})
                    token_construct = ""

                # Keyword: SIZE_DEC_KEYWORD
                if token_construct == "size_dec":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[SIZE_DEC_KEYWORD]})
                    token_construct = ""

                # Keyword: EMT_KEYWORD
                if token_construct == "emt":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[EMT_KEYWORD]})
                    token_construct = ""
                
                # Keyword: DEL_KEYWORD
                if token_construct == "del":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[DEL_KEYWORD]})
                    token_construct = ""
                
                # Keyword: MUL_KEYWORD
                if token_construct == "mul":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[MUL_KEYWORD]})
                    token_construct = ""
                
                # Keyword: ADD_KEYWORD
                if token_construct == "add":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[ADD_KEYWORD]})
                    token_construct = ""
                
                # Keyword: DIV_KEYWORD
                if token_construct == "div":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[DIV_KEYWORD]})
                    token_construct = ""

                # Keyword: SUB_KEYWORD
                if token_construct == "sub":
                    print(
                        f"[bold blue][DEBUG][reset]: Found token '{token_construct}' in line '{line.line_number+1}'."
                    )

                    token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[SUB_KEYWORD]})
                    token_construct = ""
                
            # # Keyword: CONST_KEYWORD 
            # if split_line_content[0] == KEYWORDS[CONST_KEYWORD]:    
            #     token["tokens"].append({TOKENS[KEYWORD_TOKEN] : KEYWORDS[CONST_KEYWORD]})

            #     # -- Syntax variations:
            #     #   >>> const x[n]: INT = y; 
            #     #             ^ ^   ^^^ ^ ^  

            #     # Check if the syntax is correct
            #     if len(split_line_content) > 5 or len(split_line_content) < 5:
            #         print(
            #             f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': Invalid syntax.\n" +
            #             (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #             f"\t-> {line.line_number+1} | {line.content}"
            #         )
            #         exit(1)

            #     constant_identifier = split_line_content[1].split("[")[0]
                
            #     # Check if the identifier is unique
            #     if constant_identifier in self.global_identifiers:
            #         print(
            #             f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': Constant identifier '{constant_identifier}' is already declared.\n" +
            #             (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #             f"\t-> {line.line_number+1} | {line.content}"
            #         )
            #         exit(1)

            #     # Check if the identifier contains illegal symbols
            #     for symbol in SYMBOLS:
            #         if SYMBOLS[symbol] in ["_"]:
            #             continue
                    
            #         if SYMBOLS[symbol] in constant_identifier:
            #             print(
            #                 f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': Illegal symbol '{SYMBOLS[symbol]}' found in constant identifier.\n" +
            #                 (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #                 f"\t-> {line.line_number+1} | {line.content}"
            #             )
            #             exit(1)

            #     # Check if the identifier contains integers and not sequence of chars
            #     for char in constant_identifier:
            #         try:
            #             char = int(char)
            #             print(
            #                 f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': Constant identifier '{constant_identifier}' can't contain integers, only strings.\n" +
            #                 (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #                 f"\t-> {line.line_number+1} | {line.content}"
            #             )
            #             exit(1)
            #         except Exception as e:
            #             continue
                
            #     constant_size = split_line_content[1].split("[")[1][:-2]
                
            #     # Check if the size contains illegal symbols
            #     for symbol in SYMBOLS:
            #         if SYMBOLS[symbol] in ["-"]:
            #             continue

            #         if SYMBOLS[symbol] in constant_size:
            #             print(
            #                 f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': Illegal symbol '{SYMBOLS[symbol]}' found in constant's size.\n" +
            #                 (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #                 f"\t-> {line.line_number+1} | {line.content}"
            #             )
            #             exit(1)
                
            #     # Check if the size contains any characters and not integers
            #     if self.contains_characters(data=constant_size, ignore_chars=["-"]):
            #         print(
            #             f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': size should contain integers and not characters.\n" +
            #             (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #             f"\t-> {line.line_number+1} | {line.content}"
            #         )
            #         exit(1)
            #     else:
            #         if len(constant_size) == 0:
            #             constant_size = None
            #         else:
            #             constant_size = int(constant_size)

            #     # check if the size is negative
            #     if constant_size is not None:
            #         if constant_size < 0:
            #             print(
            #                 f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': Constant's size '{constant_size}' can't be negative.\n" +
            #                 (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #                 f"\t-> {line.line_number+1} | {line.content}"
            #             )
            #             exit(1)
                    
            #     constant_type = split_line_content[2]
            #     constant_value = split_line_content[4][:-1] # Skip index [3], contains '='
            #     end_of_line = split_line_content[4][-1]

            #     # Check if the constant_value's type correspondes with the constant_type
            #     if not self.check_value_type(constant_type, constant_value):
            #         print(
            #             f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': Constant's value's type doesn't match the declared type.\n" +
            #             (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #             f"\t-> {line.line_number+1} | {line.content}"
            #         )
            #         exit(1)

            #     constant_value = self.convert_value_type(constant_value, _type=constant_type)

            #     # Check if the size is empty, if true then we auto set it
            #     if constant_size is None:
            #         if constant_type in [STR_TYPE, CHAR_TYPE]:
            #             constant_size = len(constant_value.encode("utf-8"))
            #         else:
            #             constant_size = self.get_size_of_obj(obj=constant_value)
            #     else:
            #         constant_size = int(constant_size)
                
            #     # Check if the initial size is bigger then the size of the constant's value
            #     if constant_size < sys.getsizeof(constant_value):
            #         print(
            #             f"[bold red][ERROR][reset] [cyan]File<{file_path}>[reset] in line '{line.line_number+1}': Not enough size '{constant_size}' for value '{constant_value}'.\n" +
            #             (f"\t   {last_line.line_number+1} | {last_line.content}\n" if last_line is not None else "") +
            #             f"\t-> {line.line_number+1} | {line.content}"
            #         )
            #         exit(1)
                
            #     # Register tokens
            #     token["tokens"].append({IDENTIFIER: constant_identifier})
            #     token["tokens"].append({SIZE_LITERAL: constant_size})
            #     token["tokens"].append({COLON_SYMBOL: SYMBOLS[COLON_SYMBOL]})
                
            #     _key = None
            #     for key, value in TYPE_SYNTAX_MAP.items():
            #         if value == constant_type:
            #             _key = key
                
            #     token["tokens"].append({_key: constant_type})
            #     token["tokens"].append({EQUALS_SYMBOL: SYMBOLS[EQUALS_SYMBOL]})
            #     token["tokens"].append({NUMBER_LITERAL: constant_value})
            #     token["tokens"].append({SEMICOLON_SYMBOL: end_of_line})
                
            #     self.global_identifiers.append(constant_identifier) # Saving the identifier

            tokens.tokens.append(token)

            last_line = line
            last_char = char
            
        return tokens

    def is_last_token_const(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a constant keyword
        """
        const_token = {TOKENS[KEYWORD_TOKEN]: KEYWORDS[CONST_KEYWORD]}

        last_token = list(token.items())[1][1][index]

        return const_token == last_token

    def is_last_token_var(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a variable keyword
        """
        var_token = {TOKENS[KEYWORD_TOKEN]: KEYWORDS[VAR_KEYWORD]}

        last_token = list(token.items())[1][1][index]

        return var_token == last_token

    def is_last_token_word(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a word (identifier)
        """
        last_token = list(token.items())[1][1][index]

        return list(last_token.items())[0][0] == TOKENS[WORD_TOKEN]

    def is_last_token_size(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a size or dynamic size.
        """
        last_token = list(token.items())[1][1][index]

        return list(last_token.items())[0][0] in [LITERALS[SIZE_LITERAL], LITERALS[DYNAMIC_SIZE_LITERAL]]
    
    def is_last_token_type(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a type.
        """
        last_token = list(token.items())[1][1][index]

        return list(last_token.items())[0][0] == TOKENS[TYPE_TOKEN]
    
    def is_last_token_semicolon(self, token: dict, index: int | None = -1) -> bool:
        """
        Is the last token a semicolon (EOF)
        """
        last_token = list(token.items())[1][1][index]

        return list(last_token.items())[0][0] == SYMBOLS[SEMICOLON_SYMBOL]
    
    def extract_constant_identifier(self, token_construct: str, current_char: str, last_char: str, next_char: str, token: dict) -> dict:
        """
        Extract the constant's identifier
        """
        if len(list(token.items())[1][1]) == 0:
            return None

        if self.is_last_token_const(token=token) and next_char in ["[", ":"]:
            return {
                TOKENS[WORD_TOKEN]: token_construct,
            }
    
    def extract_variable_identifier(self, token_construct: str, current_char: str, last_char: str, next_char: str, token: dict) -> dict:
        """
        Extract variable's identifier.
        """
        if len(list(token.items())[1][1]) == 0:
            return None
        
        if self.is_last_token_var(token=token) and next_char in ["[", ":"]:
            return {
                TOKENS[WORD_TOKEN]: token_construct,
            }
    
    def extract_constant_variable_size(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: dict) -> tuple[dict, list[int]]:
        """
        Extract the constant/variable 's size.
        """
        size = ""
        skip_indexes_list = []

        if len(list(token.items())[1][1]) == 0:
            return None, None
        
        if self.is_last_token_word(token=token) and current_char == "[":
            split_line = [_ for _ in line_content[current_index:]]
            for i, char in enumerate(split_line):
                if char == "]":
                    # skip_indexes_list.append(
                    #     current_index + i
                    # )
                    break
                
                if char == "[":
                    continue

                size += char
                
                skip_indexes_list.append(
                    current_index + i
                )
        # Check if no fixed size was declared
        elif self.is_last_token_word(token=token) and current_char == ":":
            return {LITERALS[DYNAMIC_SIZE_LITERAL]: 0}, skip_indexes_list
        
        if len(size) != 0:
            return {LITERALS[SIZE_LITERAL]: size}, skip_indexes_list
        
        return None, skip_indexes_list

    def extract_constant_variable_type(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: dict) -> tuple[dict, list[int]]:
        """
        Extract constant/variable 's type.
        """
        _type = ""
        skip_indexes_list = []

        if len(list(token.items())[1][1]) == 0:
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

            return {TOKENS[TYPE_TOKEN]: _type}, skip_indexes_list
        
        return None, None

    def extract_constant_variable_value(self, token_construct: str, current_index: int, current_char: str, last_char: str, next_char: str, line_content: str, token: dict) -> tuple[dict, list[int]]:
        """
        Extract constant/variable 's value
        """
        value = ""
        skip_indexes_list = []

        if len(list(token.items())[1][1]) == 0:
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
            
            return {TOKENS[VALUE_TOKEN]: value}, skip_indexes_list

        return None, None
    
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
