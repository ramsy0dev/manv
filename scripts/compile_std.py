#!/usr/bin/python3

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

import os
import subprocess

from rich import print

LIBS_OBJECTS_DIR_PATH = "std/libs"

ASM_LIBS_PATHS = [
    "std/core.asm",
    "std/io.asm"
]

def compile_libs_to_object() -> None:
    """
    Compile libraries into object files.
    """
    for path in ASM_LIBS_PATHS:
        print(
            f"[bold green][INFO][reset]: Compiling lib '{path}'..."
        )
        
        out = subprocess.run(
            ["nasm", "-f", "elf64", path, "-o", f"std/libs/{path.split('/')[-1].replace('asm', 'o')}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if out.stderr:
            print(f"[bold red][ERROR][reset]: Caught the following error \n{out.stderr.decode()}")
            
        if 'command not found' in out.stderr.decode():
            print(f"[bold red][ERROR][reset]: nasm is not installed")
            exit(1)

def run() -> None:
    if not os.path.exists(LIBS_OBJECTS_DIR_PATH):
        print(f"[bold green][INFO][reset]: Creating directory '{LIBS_OBJECTS_DIR_PATH}'...")

        os.mkdir(LIBS_OBJECTS_DIR_PATH)

    print(
        f"[bold green][INFO][reset]: Compiling std libraries"
    )
    compile_libs_to_object()

if __name__ == "__main__":
    run()
