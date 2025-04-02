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
import sys
import tomllib
import subprocess

from rich import print
from pathlib import Path

class Test:
    """
    Test class for holding info about each test
    """
    test_file_path          : str
    test_file_object_path   : str
    binary_file_path        : str
    lib_file_path           : str
    lib_object_path         : str
    
    stdout                  : str | None = None
    stderr                  : str | None = None

    def load_toml(self, toml: dict) -> None:
        """
        Load attributes value from toml.
        """
        for att in self.__annotations__:
            setattr(self, att, toml["Test"][att])
          
def list_files_in_directory(directory: str) -> list[str]:
    return [str(file) for file in Path(directory).rglob('*') if file.is_file()]

TESTS_PATH = "./tests"

TESTS: list[Test] = list()

def generate_test_objects() -> None:
    """
    Generate Test objects
    """
    files = list_files_in_directory(directory=TESTS_PATH)
    
    for file in files:
        # Skip asm files
        if file.endswith(".asm") or file.endswith(".o"):
          continue
        
        # Skip binary files
        try:
            open(file, "rb").readline().decode('utf-8')
        except Exception as e:
          continue
        
        with open(file, "rb") as f:
            test_config = tomllib.load(f)
            
            test = Test()
            test.load_toml(test_config)

            TESTS.append(test)
      
def compile_test_file_to_object(test_file_path: str, test_file_object_path: str) -> None:
    """
    Compile the test file into an object file
    """
    out = subprocess.run(
      ["nasm", "-f", "elf64", test_file_path, "-o", test_file_object_path]
    )

    if out.stderr:
        print(f"[bold red][ERROR][reset]: Caught the following error while trying to compile '{test_file_path}' \n{out.stderr.decode()}")
        sys.exit(1)

def compile_lib_file_to_object(lib_file_path: str, lib_object_path: str) -> None:
    """
    Compile the test file into an object file
    """
    out = subprocess.run(
      ["nasm", "-f", "elf64", lib_file_path, "-o", lib_object_path]
    )

    if out.stderr:
        print(f"[bold red][ERROR][reset]: Caught the following error while trying to compile '{lib_file_path}' \n{out.stderr.decode()}")
        sys.exit(1)
    
def link_test_file_with_lib(test_file_object_path: str, lib_object_path: str, binary_file_path: str) -> None:
    """
    Link the test file object with the library object file.
    """
    out = subprocess.run(
      ["ld", "-s", "-o", binary_file_path, test_file_object_path, lib_object_path]
    )

    if out.stderr:
        print(f"[bold red][ERROR][reset]: Caught the following error while trying to link '{test_file_object_path}' and '{lib_object_path}' \n{out.stderr.decode()}")
        sys.exit(1)

def run_test_file(test: Test) -> None:
    """
    Run a test file
    """
    # Compile the test file into an object file
    compile_test_file_to_object(
      test_file_path=test.test_file_path,
      test_file_object_path=test.test_file_object_path
    )

    # Compile the lib
    compile_lib_file_to_object(
      lib_file_path=test.lib_file_path,
      lib_object_path=test.lib_object_path
    )

    # Link with library
    link_test_file_with_lib(
      test_file_object_path=test.test_file_object_path,
      lib_object_path=test.lib_object_path,
      binary_file_path=test.binary_file_path
    )

    # Run the test file
    print(f"[bold green][INFO][reset]: Running test '{test.test_file_path}'...", end=" ")
    
    out = subprocess.run(
      [f"{test.binary_file_path}"],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )

    # Check the stderr
    for i, x in zip(test.stderr, out.stderr.decode().split("\n")):
        if i != x:
            print("[bold red]FAILD[reset]")
            print(
                f"[bold green][INFO][reset]: Expected stderr from test '{test.test_file_path}'\n"
                f"\t STDERR = {out.stderr.decode() if out.stderr.decode() != '' else None}"
            )
            sys.exit(1)
    
    # Check the stdout
    for i, x in zip(test.stdout, out.stdout.decode().split("\n")):
        if i != x:
            print("[bold red]FAILD[reset]")
            print(
                f"[bold green][INFO][reset]: Expected stdout from test '{test.test_file_path}'\n"
                f"\t STDOUT = {out.stdout.decode() if out.stdout.decode() != '' else None}"
            )
            sys.exit(1)
    
    print("[bold green]PASS[reset]")

def run() -> None:
    # Generate test objects
    print(f"[bold green][INFO][reset]: Generating tests objects...")
    generate_test_objects()

    # Run tests
    for test in TESTS:
        run_test_file(test=test)

if __name__ == "__main__":
  run()
