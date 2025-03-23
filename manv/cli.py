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

from loguru import logger

# Parser
from manv.parser import Parser

# File handler
from manv.file_handler import FileHandler

cli = typer.Typer()

@cli.command()
def run(
    file_path: str = typer.Option(None, "--file-path", help="The path to the manv script file."),
    threads: int = typer.Option(3, "--threads", help="The number of threads to use.")
    ) -> None:
    """
    Run a manv file source code.
    """
    if not pathlib.Path(file_path).exists():
        logger.error(f"The provided file path '{file_path}' doesn't exists.")
        sys.exit(1)
    
    file = FileHandler(file_path)
    file_content = file.read(
        threads=threads
    )
    
    parser = Parser()
    parser.parse(
        data=file_content
    )

def run():
    cli()
