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

import sys
import typer
import pathlib

from rich import print

# Parser
from manv.src.parser.parser import Parser

# Lexer
from manv.src.parser.lexer import Lexer

# File handler
from manv.file_handler import FileHandler

# Platform type
from manv.common import (
    PLATFORM,
    PL_LINUX
)

# Init cli
cli = typer.Typer()

@cli.command()
def compile(
    file_path: str = typer.Option(None, "--file-path", help="The path to the manv script file."),
    threads: int = typer.Option(3, "--threads", help="The number of threads to use.")
    ) -> None:
    """
    Compile a manv program source.
    """
    # Check for file existance
    if not pathlib.Path(file_path).exists():
        print(f"[bold red][ERROR][reset]: The provided file path '{file_path}' doesn't exists.")
        sys.exit(1)
    
    file = FileHandler(file_path)
    file_content = file.read(
        threads=threads
    )
    
    lexer = Lexer()
    program_tokens = lexer.generate_tokens(
        data=file_content
    )
    
    parser = Parser()
    parser.parse(
        tokens=program_tokens
    )

@cli.command()
def build_lexer(
    file_path: str = typer.Option(None, "--file-path", help="The path to the manv script file."),
    threads: int = typer.Option(3, "--threads", help="The number of threads to use.")
    ) -> None:
    """
    Build the lexer tree.
    """
    # Check for file existance
    if not pathlib.Path(file_path).exists():
        print(f"[bold red][ERROR][reset]: The provided file path '{file_path}' doesn't exists.")
        sys.exit(1)
    
    file = FileHandler(file_path)
    file_content = file.read(
        threads=threads
    )

    lexer = Lexer()

    program_tokens = lexer.generate_tokens(
        data=file_content,
        file_path=file_path
    )

    print(f"[bold green][INFO][reset]: Generating tokens for file [cyan]'{file_path}'[reset]")
    for token in program_tokens.tokens:
        print(
            f"[bold green][INFO][reset]: line '{token['line_n']}': \n\t{'\n\t'.join([str(i) for i in token['tokens']])}"
        )

def run():
    # Check if platform is not UNIX
    if not PLATFORM == PL_LINUX:
        print("[bold red][ERROR][reset]: Platform error, only UNIX platforms are supported.")
        sys.exit(1)

    cli()
