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
import subprocess

from rich import print
from pathlib import Path
from typing import Literal

# Parser
from manv.src.parser.parser import Parser

# Lexer
from manv.src.lexer.lexer import Lexer

# Gencode
from manv.src.codegen.codegen import Codegen

# File handler
from manv.file_handler import FileHandler

# Platform type
from manv.common import PLATFORM, PL_LINUX

# Init cli
cli = typer.Typer()

@cli.command()
def compile(
    file_path: Path = typer.Argument(help="The path to the manv script file"),
    libs_dir_path: Path = typer.Option(
        Path("./stdlib/libs"), "-L", help=(
            "Specifies a directory to be added to the linker’s library search paths."
            "This allows the linker to locate libraries used with the -l option."
            "The directory is searched before the standard system library paths."
        )
    ),
    threads: int = typer.Option(3, "--threads", help="The number of threads to use."),
) -> None:
    """
    Compile a manv program source.
    """
    # Check for file existance
    if not file_path.exists():
        print(
            f"[bold red][ERROR][reset]: The provided file path '{file_path}' doesn't exists."
        )
        sys.exit(1)

    file_name = file_path.name

    file = FileHandler(file_path)
    file_content = file.read(threads=threads)

    # Generate tokens
    lexer = Lexer()

    print(
        f"[bold green][INFO][reset]: Generating tokens..."
    )

    tokens = lexer.generate_tokens(data=file_content, file_path=file_path)

    # Build an AST
    parser = Parser()

    print(
        f"[bold green][INFO][reset]: Generating an AST tree..."
    )

    program = parser.parse(tokens=tokens)

    # Generate assembly
    codegen = Codegen()

    print(
        f"[bold green][INFO][reset]: Generating assembly code..."
    )

    generated_asm_code = codegen.codegen(
        program=program
    )
    generated_asm_code = generated_asm_code.get_assembly()

    output_asm_file_name = file_name.replace(".mv", ".asm")
    output_object_file_name = file_name.replace(".mv", ".o")
    output_binary_file_name = file_name.replace(".mv", "")

    # Save the generated assembly
    with open(output_asm_file_name, "w") as output:
        output.write(generated_asm_code)

    # Compile the generated assembly
    print(
        f"[bold green][INFO][reset]: Compiling generated assembly [cyan]'{output_asm_file_name}'[reset]..."
    )

    compile_out = subprocess.run(
        [
            "nasm",
            "-f",
            "elf64",
            output_asm_file_name,
            "-o", output_object_file_name
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    exec_out = subprocess.run(
        [
            "ld",
            "-L",
            libs_dir_path,
            "-s",
            "-o",
            output_binary_file_name,
            output_object_file_name
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if compile_out.stderr != b'':
        print(f"[bold red][ERROR][reset]: Caught the following error when compiling assembly.\n{exec_out.stderr.decode()}")
        sys.exit(1)

    # Cleaning up
    print("[bold green][INFO][reset]: Cleaning up...")
    
    # subprocess.run(
    #     ["rm", output_asm_file_name, output_object_file_name]
    # )
    
@cli.command()
def build_lexer(
    file_path: Path = typer.Argument(help="The path to the manv script file"),
    threads: int = typer.Option(3, "--threads", help="The number of threads to use."),
) -> None:
    """
    Build the lexer tree.
    """
    # Check for file existance
    if not file_path.exists():
        print(
            f"[bold red][ERROR][reset]: The provided file path '{file_path}' doesn't exists."
        )
        sys.exit(1)

    file = FileHandler(file_path)
    file_content = file.read(threads=threads)

    lexer = Lexer()

    print(
        f"[bold green][INFO][reset]: Generating tokens for file [cyan]'{file_path}'[reset]"
    )

    program_tokens = lexer.generate_tokens(data=file_content, file_path=file_path)

    for token in program_tokens.tokens:
        print(
            f"[bold green][INFO][reset]: line '{token.line.line_number}': \n\t{'\n\t'.join([str(i) for i in token.tokens])}"
        )


def run():
    # Check if platform is not UNIX
    if not PLATFORM == PL_LINUX:
        print(
            "[bold red][ERROR][reset]: Platform error, only UNIX platforms are supported."
        )
        sys.exit(1)

    cli()
