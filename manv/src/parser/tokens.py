
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

# Token type
KEYWORD_TOKEN        = iota.new() # Represents a language keyword.
WORD_TOKEN           = iota.new() # Reperesents any kind a instruction that doesn't use any of the language's keyword.
IDENTIFIER_TOKEN     = iota.new() # Name of a variable, constants, function, structure...
DYNAMIC_SIZE_TOKEN   = iota.new() # Dynamic size
TYPE_TOKEN           = iota.new() # Type literal
VALUE_TOKEN          = iota.new() # Representing constant, variable... value

# Literals
SIZE_LITERAL            = iota.new() # Size to allocat for any type of data.
DYNAMIC_SIZE_LITERAL    = iota.new()
NUMBER_LITERAL          = iota.new()
FLOAT_LITERAL           = iota.new()
BIN_LITERAL             = iota.new() # A binary literal, ex: 0b0001, 0b0010, ...
HEX_LITERAL             = iota.new() # A hexadecimal literal, ex: 0xFF, 0x1A3F ...
TRUE_LITERAL            = iota.new()
FALSE_LITERAL           = iota.new()

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
