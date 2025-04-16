import pytest

# Lexer
from manv.src.lexer.lexer import Lexer

# Init lexer
lexer = Lexer()

# Test units
def test_constant_declaration():
    """
    Test constant declaration.
    
    A constant declaration in ManV is like so:
    
    ```
    >>> const x[10]: int = 3;
    ```
    
    the other variation of it, is making the size dynamic
    to the value.

    ```
    >>> const x: int = 3;
    ```
    """
    raw_code_tokens_map = {
        "const p[100]: int = 100;\n": [
            {"KEYWORD_TOKEN": "CONST_KEYWORD"},
            {"WORD_TOKEN": "p"},
            {"SIZE_LITERAL": "100"},
            {"TYPE_TOKEN": "int"},
            {"VALUE_TOKEN": "100"},
            {"SEMICOLON_SYMBOL": ";"}
        ],
        "const x: int = 100;\n": [
            {"KEYWORD_TOKEN": "CONST_KEYWORD"},
            {"WORD_TOKEN": "x"},
            {"DYNAMIC_SIZE_LITERAL": 0},
            {"TYPE_TOKEN": "int"},
            {"VALUE_TOKEN": "100"},
            {"SEMICOLON_SYMBOL": ";"}
        ]
    }
    tokens_obj = lexer.generate_tokens(
        data=[i for i in raw_code_tokens_map]
    )

    actual_tokens = [
        token.tokens for token in tokens_obj.tokens
    ]
    expected_tokens = [
        raw_code_tokens_map[token] for token in raw_code_tokens_map
    ]

    assert actual_tokens == expected_tokens

def test_variable_declaration() -> None:
    """
    Test variable declaration
    """
    raw_code_tokens_map = {
        "var p[100]: int;\n": [
            {"KEYWORD_TOKEN": "VAR_KEYWORD"},
            {"WORD_TOKEN": "p"},
            {"SIZE_LITERAL": "100"},
            {"TYPE_TOKEN": "int"},
            {"SEMICOLON_SYMBOL": ";"}
        ],
        "var x: int = 100;\n": [
            {"KEYWORD_TOKEN": "VAR_KEYWORD"},
            {"WORD_TOKEN": "x"},
            {"DYNAMIC_SIZE_LITERAL": 0},
            {"TYPE_TOKEN": "int"},
            {"VALUE_TOKEN": "100"},
            {"SEMICOLON_SYMBOL": ";"}
        ]
    }
    tokens_obj = lexer.generate_tokens(
        data=[i for i in raw_code_tokens_map]
    )

    actual_tokens = [
        token.tokens for token in tokens_obj.tokens
    ][2:]
    expected_tokens = [
        raw_code_tokens_map[token] for token in raw_code_tokens_map
    ]

    assert actual_tokens == expected_tokens
