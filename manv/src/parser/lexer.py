from enum import auto 

from loguru import logger
from typing import Generator


from manv.models.line_model import LineModel

# Utils
from manv.utils import iota

iota = iota()

# keywords
# ------------------------------------- #
# -------- Operations keywords -------- #
# ------------------------------------- #
MUL_KEYWORD  = iota.new() # Multiplication
ADD_KEYWORD  = iota.new() # Addition
DIV_KEYWORD  = iota.new() # Division
SUB_KEYWORD  = iota.new() # Substitution 


# ------------------------------------- #
# ---- Variable/Constants keywords ---- #
# ------------------------------------- #
CONST_KEYWORD     = iota.new()    # Declare a constant
VAR_KEYWORD       = iota.new()    # Declare a variable
SIZE_INC_KEYWORD  = iota.new()    # Increase the size of a variable
SIZE_DEC_KEYWORD  = iota.new()    # Decrease the size of a variable
EMT_KEYWORD       = iota.new()    # Empty a variable from its value
DEL_KEYWORD       = iota.new()    # Delete a variable/constant from memory.

# Builtin types
INT_TYPE         = iota.new()
FLOAT_TYPE       = iota.new()
STR_TYPE         = iota.new()
CHAR_TYPE        = iota.new()
BOOL_TRUE_TYPE   = iota.new()
BOOL_FALSE_TYPE  = iota.new()
VECTOR_TYPE      = iota.new()

# Literals
SIZE_LITERAL     = iota.new() # Size to allocat for any type of data.
NUMBER_LITERAL   = iota.new()
FLOAT_LITERAL    = iota.new()
BIN_LITERAL      = iota.new() # A binary literal, ex: 0b0001, 0b0010, ...
HEX_LITERAL      = iota.new() # A hexadecimal literal, ex: 0xFF, 0x1A3F ...
TRUE_LITERAL     = iota.new()
FALSE_LITERAL    = iota.new()

# Symbols
SEMICOLON_SYMBOL                =    iota.new()
COLON_SYMBOL                    =    iota.new()
COMMA_SYMBOL                    =    iota.new()
DOT_SYMBOL                      =    iota.new()
LPAREN_SYMBOL                   =    iota.new()
RPAREN_SYMBOL                   =    iota.new()
LBRACE_SYMBOL                   =    iota.new()
RBRACE_SYMBOL                   =    iota.new()
LBRACKET_SYMBOL                 =    iota.new()
RBRACKET_SYMBOL                 =    iota.new()
PLUS_SYMBOL                     =    iota.new()
MINUS_SYMBOL                    =    iota.new()
ASTERISK_SYMBOL                 =    iota.new()
SLASH_SYMBOL                    =    iota.new()
PERCENT_SYMBOL                  =    iota.new()
AMPERSAND_SYMBOL                =    iota.new()
PIPE_SYMBOL                     =    iota.new()
CARET_SYMBOL                    =    iota.new()
TILDE_SYMBOL                    =    iota.new()
EXCLAMATION_SYMBOL              =    iota.new() 
QUESTION_SYMBOL                 =    iota.new()
EQUALS_SYMBOL                   =    iota.new()
LESS_THAN_SYMBOL                =    iota.new()
GREATER_THAN_SYMBOL             =    iota.new()
DOUBLE_EQUALS_SYMBOL            =    iota.new()
NOT_EQUALS_SYMBOL               =    iota.new()
LESS_THAN_EQUALS_SYMBOL         =    iota.new()
GREATER_THAN_EQUALS_SYMBOL      =    iota.new()
PLUS_EQUALS_SYMBOL              =    iota.new()
MINUS_EQUALS_SYMBOL             =    iota.new()
ASTERISK_EQUALS_SYMBOL          =    iota.new()
SLASH_EQUALS_SYMBOL             =    iota.new()
PERCENT_EQUALS_SYMBOL           =    iota.new()
AMPERSAND_EQUALS_SYMBOL         =    iota.new()
PIPE_EQUALS_SYMBOL              =    iota.new()
CARET_EQUALS_SYMBOL             =    iota.new()
LEFT_SHIFT_SYMBOL               =    iota.new()
RIGHT_SHIFT_SYMBOL              =    iota.new()
LEFT_SHIFT_EQUALS_SYMBOL        =    iota.new()
RIGHT_SHIFT_EQUALS_SYMBOL       =    iota.new()
DOUBLE_PIPE_SYMBOL              =    iota.new()
DOUBLE_AMPERSAND_SYMBOL         =    iota.new()
DOUBLE_PLUS_SYMBOL              =    iota.new()
DOUBLE_MINUS_SYMBOL             =    iota.new()
ARROW_SYMBOL                    =    iota.new()
DOUBLE_ARROW_SYMBOL             =    iota.new()
ELLIPSIS_SYMBOL                 =    iota.new()
HASHTAG_SYMBOL                  =    iota.new()
BACKSLASH_SYMBOL                =    iota.new()
AT_SYMBOL                       =    iota.new()
DOLLAR_SYMBOL                   =    iota.new()

# Keywords binded to their string representation
KEYWORDS: dict[int, str] = {
    # Operations keywords
    MUL_KEYWORD: "MUL",
    ADD_KEYWORD: "ADD",
    DIV_KEYWORD: "DIV",
    SUB_KEYWORD: "SUB",

    # Variables/Constants keywords
    CONST_KEYWORD: "CONST",
    VAR_KEYWORD: "VAR",
    SIZE_INC_KEYWORD: "SIZE_INC",
    SIZE_DEC_KEYWORD: "SIZE_DEC",
    EMT_KEYWORD: "EMT",
    DEL_KEYWORD: "DEL"
}

# Types binded to their string representation
BUILTIN_TYPES: dict[int, str] = {
    INT_TYPE: "INT",
    FLOAT_TYPE: "FLOAT",
    STR_TYPE: "STR",
    CHAR_TYPE: "CHAR",
    VECTOR_TYPE: "VECTOR"
}

# Literals binded to their string respresentation
LITERALS: dict[int, str] = {
    SIZE_LITERAL: "SIZE_LITERAL",
    NUMBER_LITERAL: "NUMBER_LITERAL",
    FLOAT_LITERAL: "FLOAT_LITERAL",
    BIN_LITERAL: "BIN_LITERAL",
    HEX_LITERAL: "HEX_LITERAL",
    TRUE_LITERAL: "TRUE_LITERAL",
    FALSE_LITERAL: "FALSE_LITERAL"
}

# Symbols binded to their string representation
SYMBOLS: dict[int, str] = {
    SEMICOLON_SYMBOL: ";",
    COLON_SYMBOL: ":",
    COMMA_SYMBOL: ",",
    DOT_SYMBOL: ".",
    LPAREN_SYMBOL: "(", 
    RPAREN_SYMBOL: ")",    
    LBRACE_SYMBOL: "{",
    RBRACE_SYMBOL: "}",
    LBRACKET_SYMBOL: "[",
    RBRACKET_SYMBOL: "]",
    PLUS_SYMBOL: "+",
    MINUS_SYMBOL: "-",   
    ASTERISK_SYMBOL: "*",
    SLASH_SYMBOL: "/",
    PERCENT_SYMBOL: "%", 
    AMPERSAND_SYMBOL: "&",   
    PIPE_SYMBOL: "|",    
    CARET_SYMBOL: "^",  
    TILDE_SYMBOL: "~", 
    EXCLAMATION_SYMBOL: "!",  
    QUESTION_SYMBOL: "?",  
    EQUALS_SYMBOL: "=",   
    LESS_THAN_SYMBOL: "<",   
    GREATER_THAN_SYMBOL: ">",   
    DOUBLE_EQUALS_SYMBOL: "==",
    NOT_EQUALS_SYMBOL: "!=",
    LESS_THAN_EQUALS_SYMBOL: "<=",    
    GREATER_THAN_EQUALS_SYMBOL: ">=",   
    PLUS_EQUALS_SYMBOL: "+=",    
    MINUS_EQUALS_SYMBOL: "-=",
    ASTERISK_EQUALS_SYMBOL: "*=", 
    SLASH_EQUALS_SYMBOL: "/=",
    PERCENT_EQUALS_SYMBOL: "%=",
    AMPERSAND_EQUALS_SYMBOL: "&=", 
    PIPE_EQUALS_SYMBOL: "|=",  
    CARET_EQUALS_SYMBOL: "^=",  
    LEFT_SHIFT_SYMBOL: "<<",  
    RIGHT_SHIFT_SYMBOL: ">>",  
    LEFT_SHIFT_EQUALS_SYMBOL: "<<=",
    RIGHT_SHIFT_EQUALS_SYMBOL: ">>=",  
    DOUBLE_PIPE_SYMBOL: "||",    
    DOUBLE_AMPERSAND_SYMBOL: "&&", 
    DOUBLE_PLUS_SYMBOL: "++",   
    DOUBLE_MINUS_SYMBOL: "--",
    ARROW_SYMBOL: "->", 
    DOUBLE_ARROW_SYMBOL: "=>",
    ELLIPSIS_SYMBOL: "...", 
    HASHTAG_SYMBOL: "#",  
    BACKSLASH_SYMBOL: "\\",  
    AT_SYMBOL: "@",  
    DOLLAR_SYMBOL: "$"
}

# Costum types
type KEYWORD = int # Represents a language keyword.
type WORD = str # Reperesents any kind a instruction that doesn't use any of the language's keyword.
type IDENTIFIER = str # Name of a variable, constants, function, structure...

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
        pass

    def generate_tokens(self, data: Generator, file_path: str | None = None) -> Tokens:
        """
        Generates tokens from a program source code.
        """
        tokens = Tokens(
            file_path=file_path
        )

        for i, line in enumerate(data):
            tokens.lines_count += 1
            
            line = self.remove_comments_from_line(data=line)
            line = LineModel(content=line, line_number=i)
            split_line_content = line.content.split(" ")

            logger.info(f"Current line: {line}")
            
            token: dict = {
                "line_n": line.line_number,
                "tokens": list()
            }
                
            # Keyword: CONST_KEYWORD 
            if split_line_content[0] == KEYWORDS[CONST_KEYWORD]:    
                token["tokens"].append({KEYWORD : KEYWORDS[CONST_KEYWORD]})

                # -- Syntax variations:
                #   >>> CONST x[n]: INT  = y 
                #             ^ ^   ^^^ ^ ^  
                constant_identifier = split_line_content[1].split("[")[0]
                constant_size = split_line_content[1].split("[")[1][:-2] 
                constant_type = split_line_content[2]
                constant_value = split_line_content[4] # Skip index [3], contains '='

                token["tokens"].append({IDENTIFIER: constant_identifier})
                token["tokens"].append({SIZE_LITERAL: constant_size})
                token["tokens"].append({COLON_SYMBOL: SYMBOLS[COLON_SYMBOL]})
                
                _key = None
                for key, value in BUILTIN_TYPES.items():
                    if value == constant_type:
                        _key = key
                
                token["tokens"].append({_key: constant_type})
                token["tokens"].append({EQUALS_SYMBOL: SYMBOLS[EQUALS_SYMBOL]})
                token["tokens"].append({NUMBER_LITERAL: constant_value})

            # Keyword:  VAR_KEYWORD
            if split_line_content[0] == KEYWORDS[VAR_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[VAR_KEYWORD]
                })


            # Keyword: SIZE_INC_KEYWORD
            if split_line_content[0] == KEYWORDS[SIZE_INC_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[SIZE_INC_KEYWORD]
                })

            
            # Keyword: SIZE_DEC_KEYWORD
            if split_line_content[0] == KEYWORDS[SIZE_DEC_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[SIZE_DEC_KEYWORD]
                })


            # Keyword: EMT_KEYWORD
            if split_line_content[0] == KEYWORDS[EMT_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[EMT_KEYWORD]
                })

            
            # Keyword: DEL_KEYWORD
            if split_line_content[0] == KEYWORDS[DEL_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[DEL_KEYWORD]
                })

            
            # Keyword: MUL_KEYWORD
            if split_line_content[0] == KEYWORDS[MUL_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[MUL_KEYWORD]
                })

            
            
            # Keyword: ADD_KEYWORD
            if split_line_content[0] == KEYWORDS[ADD_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[ADD_KEYWORD]
                })

            

            # Keyword: DIV_KEYWORD
            if split_line_content[0] == KEYWORDS[DIV_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[DIV_KEYWORD]
                })

            
            # Keyword: SUB_KEYWORD
            if split_line_content[0] == KEYWORDS[SUB_KEYWORD]:
                token["tokens"].append({
                    KEYWORD : KEYWORDS[SUB_KEYWORD]
                })

            tokens.tokens.append(token)
            
        return tokens

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
