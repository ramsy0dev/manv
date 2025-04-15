import pytest
from typing import Generator

# Lexer
from manv.src.lexer.lexer import Lexer

# Init the lexer
lexer = Lexer()

# Utils
def string_generator(data: list[str]) -> Generator[str, None, None]:
    for line in data:
        yield line  # assuming generate_tokens expects character-by-character input


# Test units
def test_constant_declaration():
    raw_code_tokens_map = {
        "const p[100]: int = 100;": [
            {"KEYWORD_TOKEN": "CONST_KEYWORD"},
            {"WORD_TOKEN": "p"},
            {"SIZE_LITERAL": "100"},
            {"TYPE_TOKEN": "int"},
            {"VALUE_TOKEN": "100"},
            {"SEMICOLON_SYMBOL": ";"}
        ],
        "const x: int = 100;": [
            {"KEYWORD_TOKEN": "CONST_KEYWORD"},
            {"WORD_TOKEN": "x"},
            {"DYNAMIC_SIZE_LITERAL": 0},
            {"TYPE_TOKEN": "int"},
            {"VALUE_TOKEN": "100"},
            {"SEMICOLON_SYMBOL": ";"}
        ]
    }

    for i, raw_code in enumerate(raw_code_tokens_map):
        expected_tokens = raw_code_tokens_map[raw_code]
        tokens_obj = lexer.generate_tokens(
            data=string_generator([raw_code, ])
        )

        actual_tokens = [t.tokens for t in tokens_obj.tokens]

        assert actual_tokens[i] == expected_tokens
