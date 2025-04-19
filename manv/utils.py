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

__all__ = [
    "get_platform",
    "create_path",
    "random_ascii_str",
    "random_int",
    "iota"
]

import os
import sys
import string
import random

from rich import print
from pathlib import Path

# Constants
PL_WINDOWS = 0x01
PL_LINUX   = 0x02

# Defines
def get_platform() -> str: ...
def create_path(path: str) -> str: ...
def random_ascii_str(len: int | None = 1) -> str: ...
def random_int(int_range: tuple[int, int] | None = (999, 9999)) -> str: ...

class iota: ...

# Implementations
def get_platform() -> int:
    """
    Returns the platform type
    """
    return PL_LINUX if sys.platform == "linux" else PL_WINDOWS

def create_path(path: str) -> str:
    """
    Create a path
    """
    platform = get_platform()
    slash = "/" if platform == PL_LINUX else "\\"
    
    dirs = path.split(slash)
    
    root_dir = os.getcwd()

    print(f"[bold blue][DEBUG][reset]: Current working directory '{root_dir}'")

    last_dir = root_dir
    
    for i in range(len(dirs)):
        directory = ""
        
        if dirs[i] == "":
            continue
        
        directory = last_dir + slash + dirs[i]
        
        print(f"[bold blue][DEBUG][reset]Processing directory '{directory}'")

        directory = Path(directory)

        is_file_format = i == len(dirs) - 1
        
        if not is_file_format and not directory.exists():
            directory.mkdir()
        elif is_file_format and not directory.exists():
            directory.touch()
    
        last_dir += slash + dirs[i]
    
    return last_dir


def random_ascii_str(len: int | None = 1) -> str:
    """
    Generate a random ascii string sequence.
    """    
    ascii_list = [char for char in string.ascii_lowercase + string.ascii_uppercase]

    ascii_str = random.choices(ascii_list, k=len)

    return ''.join(ascii_str)

def random_int(int_range: tuple[int, int] | None = (999, 9999)) -> str:
    """
    Generate a random integer.
    """
    return random.choice([i for i in range(int_range[0], int_range[1])])

class iota:
    """
    Simple implementation of iota.
    """
    current_n: int = 0
    
    def new(self) -> int:
        self.current_n += 1

        return self.current_n

