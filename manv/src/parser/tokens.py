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

# Utils
from manv.utils import iota

iota = iota()

# keywords
# ------------------------------------- #
# -------- Operations keywords -------- #
# ------------------------------------- #
MUL_KEYWORD = iota.new()  # Multiplication
ADD_KEYWORD = iota.new()  # Addition
DIV_KEYWORD = iota.new()  # Division
SUB_KEYWORD = iota.new()  # Substitution

# ------------------------------------- #
# ---- Variable/Constants keywords ---- #
# ------------------------------------- #
CONST_KEYWORD       =   iota.new()  # Declare a constant
VAR_KEYWORD         =   iota.new()  # Declare a variable
PTR_KEYWORD         =   iota.new()  # Declare a pointer
SIZE_INC_KEYWORD    =   iota.new()  # Increase the size of a variable
SIZE_DEC_KEYWORD    =   iota.new()  # Decrease the size of a variable
EMT_KEYWORD         =   iota.new()  # Empty a variable from its value
DEL_KEYWORD         =   iota.new()  # Delete a variable/constant from memory.
INTO_KEYWORD        =   iota.new()  # Direct result into a variable.
SYSCALL_KEYWORD     =   iota.new()  # Make syscall
IF_KEYWORD          = iota.new()
ELSE_KEYWORD        = iota.new()
COMMENT_KEYWORD     =   iota.new()  # The double forward-slash for comments

# Builtin types
INT_TYPE = iota.new()
FLOAT_TYPE = iota.new()
STR_TYPE = iota.new()
CHAR_TYPE = iota.new()
BOOL_TRUE_TYPE = iota.new()
BOOL_FALSE_TYPE = iota.new()

# Token type
KEYWORD_TOKEN               = iota.new()  # Represents a language keyword.
WORD_TOKEN                  = iota.new()  # Reperesents any kind a instruction that doesn't use any of the language's keyword.
SYMBOL_TOKEN                = iota.new()
IDENTIFIER_TOKEN            = iota.new()  # Name of a variable, constants, function, structure...
TYPE_TOKEN                  = iota.new()  # Type literal
VALUE_TOKEN                 = iota.new()  # Representing constant, variable... value
DEREFERENCE_PTR_TOKEN       = iota.new()
CONST_IDENTIFIER_TOKEN      = iota.new()
VAR_IDENTIFIER_TOKEN        = iota.new()
PTR_IDENTIFIER_TOKEN        = iota.new()
FUNCTION_IDENTIFIER_TOKEN   = iota.new()
EQUAL_TOKEN                 = iota.new()
NOT_EQUAL_TOKEN             = iota.new()
GREATER_THAN_TOKEN          = iota.new()
SMALLER_THAN_TOKEN          = iota.new()
GREATER_THAN_OR_EQUAL_TOKEN = iota.new()
SMALLER_THAN_OR_EQUAL_TOKEN = iota.new()
COMMENT_TOKEN               = iota.new()

# Literals
SIZE_LITERAL            =   iota.new()  # Size to allocat for any type of data.
DYNAMIC_SIZE_LITERAL    =   iota.new()
NUMBER_LITERAL          =   iota.new()
FLOAT_LITERAL           =   iota.new()
STRING_LITERAL          =   iota.new()
BIN_LITERAL             =   iota.new()  # A binary literal, ex: 0b0001, 0b0010, ...
HEX_LITERAL             =   iota.new()  # A hexadecimal literal, ex: 0xFF, 0x1A3F ...
TRUE_LITERAL            =   iota.new()
FALSE_LITERAL           =   iota.new()
NULL_LITERAL            =   iota.new()
SPACE_LITERAL           =   iota.new()

OP_RIGHT_ELEMENT_LITERAL    =   iota.new() 
OP_LEFT_ELEMENT_LITERAL     =   iota.new()
UNINITIALIZED_VAR_LITERAL   =   iota.new()

# Symbols
SEMICOLON_SYMBOL = iota.new()
COLON_SYMBOL = iota.new()
COMMA_SYMBOL = iota.new()
DOT_SYMBOL = iota.new()
LPAREN_SYMBOL = iota.new()
RPAREN_SYMBOL = iota.new()
LBRACE_SYMBOL = iota.new()
RBRACE_SYMBOL = iota.new()
LBRACKET_SYMBOL = iota.new()
RBRACKET_SYMBOL = iota.new()
PLUS_SYMBOL = iota.new()
MINUS_SYMBOL = iota.new()
ASTERISK_SYMBOL = iota.new()
SLASH_SYMBOL = iota.new()
PERCENT_SYMBOL = iota.new()
AMPERSAND_SYMBOL = iota.new()
PIPE_SYMBOL = iota.new()
CARET_SYMBOL = iota.new()
TILDE_SYMBOL = iota.new()
EXCLAMATION_SYMBOL = iota.new()
QUESTION_SYMBOL = iota.new()
EQUALS_SYMBOL = iota.new()
LESS_THAN_SYMBOL = iota.new()
GREATER_THAN_SYMBOL = iota.new()
DOUBLE_EQUALS_SYMBOL = iota.new()
NOT_EQUALS_SYMBOL = iota.new()
LESS_THAN_EQUALS_SYMBOL = iota.new()
GREATER_THAN_EQUALS_SYMBOL = iota.new()
PLUS_EQUALS_SYMBOL = iota.new()
MINUS_EQUALS_SYMBOL = iota.new()
ASTERISK_EQUALS_SYMBOL = iota.new()
SLASH_EQUALS_SYMBOL = iota.new()
PERCENT_EQUALS_SYMBOL = iota.new()
AMPERSAND_EQUALS_SYMBOL = iota.new()
PIPE_EQUALS_SYMBOL = iota.new()
CARET_EQUALS_SYMBOL = iota.new()
LEFT_SHIFT_SYMBOL = iota.new()
RIGHT_SHIFT_SYMBOL = iota.new()
LEFT_SHIFT_EQUALS_SYMBOL = iota.new()
RIGHT_SHIFT_EQUALS_SYMBOL = iota.new()
DOUBLE_PIPE_SYMBOL = iota.new()
DOUBLE_AMPERSAND_SYMBOL = iota.new()
DOUBLE_PLUS_SYMBOL = iota.new()
DOUBLE_MINUS_SYMBOL = iota.new()
ARROW_SYMBOL = iota.new()
DOUBLE_ARROW_SYMBOL = iota.new()
ELLIPSIS_SYMBOL = iota.new()
HASHTAG_SYMBOL = iota.new()
BACKSLASH_SYMBOL = iota.new()
AT_SYMBOL = iota.new()
DOLLAR_SYMBOL = iota.new()

# Tokens types
TOKENS_SYNTAX_MAP: dict[int, str] = {
    KEYWORD_TOKEN: "KEYWORD_TOKEN",
    WORD_TOKEN: "WORD_TOKEN",
    SYMBOL_TOKEN: "SYMBOL_TOKEN",
    IDENTIFIER_TOKEN: "IDENTIFIER_TOKEN",
    TYPE_TOKEN: "TYPE_TOKEN",
    VALUE_TOKEN: "VALUE_TOKEN",
    DEREFERENCE_PTR_TOKEN: "DEREFERENCE_PTR_TOKEN",
    CONST_IDENTIFIER_TOKEN: "CONST_IDENTIFIER_TOKEN",
    VAR_IDENTIFIER_TOKEN: "VAR_IDENTIFIER_TOKEN",
    PTR_IDENTIFIER_TOKEN: "PTR_IDENTIFIER_TOKEN",
    FUNCTION_IDENTIFIER_TOKEN: "FUNCTION_IDENTIFIER_TOKEN",
    EQUAL_TOKEN: "EQUAL_TOKEN",
    NOT_EQUAL_TOKEN: "NOT_EQUAL_TOKEN",
    GREATER_THAN_TOKEN: "GREATER_THAN_TOKEN",
    SMALLER_THAN_TOKEN: "SMALLER_THAN_TOKEN",
    GREATER_THAN_OR_EQUAL_TOKEN: "GREATER_THAN_OR_EQUAL_TOKEN",
    SMALLER_THAN_OR_EQUAL_TOKEN: "SMALLER_THAN_OR_EQUAL_TOKEN",
    COMMENT_TOKEN: "COMMENT_TOKEN"
}

# Keywords binded to their string representation
KEYWORDS_SYNTAX_MAP: dict[int, str] = {
    MUL_KEYWORD: "MUL_KEYWORD",
    ADD_KEYWORD: "ADD_KEYWORD",
    PTR_KEYWORD: "PTR_KEYWORD",
    DIV_KEYWORD: "DIV_KEYWORD",
    SUB_KEYWORD: "SUB_KEYWORD",
    CONST_KEYWORD: "CONST_KEYWORD",
    VAR_KEYWORD: "VAR_KEYWORD",
    SIZE_INC_KEYWORD: "SIZE_INC_KEYWORD",
    SIZE_DEC_KEYWORD: "SIZE_DEC_KEYWORD",
    EMT_KEYWORD: "EMT_KEYWORD",
    DEL_KEYWORD: "DEL_KEYWORD",
    INTO_KEYWORD: "INTO_KEYWORD",
    SYSCALL_KEYWORD: "SYSCALL_KEYWORD",
    IF_KEYWORD: "IF_KEYWORD",
    ELSE_KEYWORD: "ELSE_KEYWORD",
    COMMENT_KEYWORD: "COMMENT_KEYWORD"
}

KEYWORDS: dict[int, str] = {
    MUL_KEYWORD: "mul",
    ADD_KEYWORD: "add",
    DIV_KEYWORD: "div",
    SUB_KEYWORD: "sub",
    CONST_KEYWORD: "const",
    VAR_KEYWORD: "var",
    PTR_KEYWORD: "ptr",
    SIZE_INC_KEYWORD: "size_inc",
    SIZE_DEC_KEYWORD: "size_inc",
    EMT_KEYWORD: "emt",
    DEL_KEYWORD: "del",
    INTO_KEYWORD: "into",
    SYSCALL_KEYWORD: "syscall",
    IF_KEYWORD: "if",
    ELSE_KEYWORD: "else",
    COMMENT_KEYWORD: "//"
}

# Types binded to their string representation
TYPE_SYNTAX_MAP: dict[int, str] = {
    INT_TYPE: "INT_TYPE",
    FLOAT_TYPE: "FLOAT_TYPE",
    STR_TYPE: "STR_TYPE",
    CHAR_TYPE: "CHAR_TYPE",
}

TYPES: dict[str, int] = {
    INT_TYPE: "int",
    FLOAT_TYPE: "float",
    STR_TYPE: "str",
    CHAR_TYPE: "char",
}

# Literals binded to their string respresentation
LITERALS_SYNTAX_MAP: dict[int, str] = {
    SIZE_LITERAL: "SIZE_LITERAL",
    DYNAMIC_SIZE_LITERAL: "DYNAMIC_SIZE_LITERAL",
    NUMBER_LITERAL: "NUMBER_LITERAL",
    FLOAT_LITERAL: "FLOAT_LITERAL",
    STRING_LITERAL: "STR_LITERAL",
    BIN_LITERAL: "BIN_LITERAL",
    HEX_LITERAL: "HEX_LITERAL",
    TRUE_LITERAL: "TRUE_LITERAL",
    FALSE_LITERAL: "FALSE_LITERAL",
    OP_LEFT_ELEMENT_LITERAL: "OP_LEFT_ELEMENT_LITERAL",
    OP_RIGHT_ELEMENT_LITERAL: "OP_RIGHT_ELEMENT_LITERAL",
    UNINITIALIZED_VAR_LITERAL: "UNINITIALIZED_VAR_LITERAL",
    SPACE_LITERAL: "SPACE_LITERAL"
}

LITERALS: dict[str, int] = {
    "TRUE": TRUE_LITERAL,
    "FALSE": FALSE_LITERAL,
    "NULL": NULL_LITERAL,
    " ": SPACE_LITERAL
}

# Symbols binded to their string representation
SYMBOLS_SYNTAX_MAP: dict[int, str] = {
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

SYMBOLS: dict[str, int] = {
    SEMICOLON_SYMBOL: ";" ,
    COLON_SYMBOL: ":" ,
    COMMA_SYMBOL: "," ,
    DOT_SYMBOL: "." ,
    LPAREN_SYMBOL: "(" ,
    RPAREN_SYMBOL: ")" ,
    LBRACE_SYMBOL: "{" ,
    RBRACE_SYMBOL: "}" ,
    LBRACKET_SYMBOL: "[" ,
    RBRACKET_SYMBOL: "]" ,
    PLUS_SYMBOL: "+" ,
    MINUS_SYMBOL: "-" ,
    ASTERISK_SYMBOL: "*" ,
    SLASH_SYMBOL: "/" ,
    PERCENT_SYMBOL: "%" ,
    AMPERSAND_SYMBOL: "&" ,
    PIPE_SYMBOL: "|" ,
    CARET_SYMBOL: "^" ,
    TILDE_SYMBOL: "~" ,
    EXCLAMATION_SYMBOL: "!" ,
    QUESTION_SYMBOL: "?" ,
    EQUALS_SYMBOL: "=" ,
    LESS_THAN_SYMBOL: "<" ,
    GREATER_THAN_SYMBOL: ">" ,
    DOUBLE_EQUALS_SYMBOL: "==" ,
    NOT_EQUALS_SYMBOL: "!=" ,
    LESS_THAN_EQUALS_SYMBOL: "<=" ,
    GREATER_THAN_EQUALS_SYMBOL: ">=" ,
    PLUS_EQUALS_SYMBOL: "+=" ,
    MINUS_EQUALS_SYMBOL: "-=" ,
    ASTERISK_EQUALS_SYMBOL: "*=" ,
    SLASH_EQUALS_SYMBOL: "/=" ,
    PERCENT_EQUALS_SYMBOL: "%=" ,
    AMPERSAND_EQUALS_SYMBOL: "&=" ,
    PIPE_EQUALS_SYMBOL: "|=" ,
    CARET_EQUALS_SYMBOL: "^=" ,
    LEFT_SHIFT_SYMBOL: "<<" ,
    RIGHT_SHIFT_SYMBOL: ">>" ,
    LEFT_SHIFT_EQUALS_SYMBOL: "<<=" ,
    RIGHT_SHIFT_EQUALS_SYMBOL: ">>=" ,
    DOUBLE_PIPE_SYMBOL: "||" ,
    DOUBLE_AMPERSAND_SYMBOL: "&&" ,
    DOUBLE_PLUS_SYMBOL: "++" ,
    DOUBLE_MINUS_SYMBOL: "--" ,
    ARROW_SYMBOL: "->" ,
    DOUBLE_ARROW_SYMBOL: "=>" ,
    ELLIPSIS_SYMBOL: "..." ,
    HASHTAG_SYMBOL: "#" ,
    BACKSLASH_SYMBOL: "\\" ,
    AT_SYMBOL: "@" ,
    DOLLAR_SYMBOL: "$" 
}

def get_reverse_key_value(value, dict_obj: dict) -> any:
    """
    Get the key from the value.
    """
    _ = value
    for key, value in dict_obj.items():
        if _ == value:
            return key
