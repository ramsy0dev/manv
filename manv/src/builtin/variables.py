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
    "Variable",
    "VariableDict",
    "TYPE_INT",
    "TYPE_FLOAT",
    "VARIABLE_TYPES"
]

# Exceptions
from manv.src.parser.exceptions import (
    NSizeToDecreaseIsLarge,
    InvalidVariableType
)

TYPE_INT    : str = "INT"
TYPE_FLOAT  : str = "FLOAT"
TYPE_STRING : str = "STRING"
TYPE_VECTOR : str = "VECTOR"

VARIABLE_TYPES: dict[str, int|float|str|list] ={
    TYPE_INT: int,
    TYPE_FLOAT: float,
    TYPE_STRING: str,
    TYPE_VECTOR: list
}

DEFAULT_VARIABLE_SIZE: int = 255

MAX_VARIABLE_LENGTH: int = 255

CRA_ALLOWED_SYMBOLS: list[str] = [
    "[", "]", ":", "="
]

SIZE_INC_ALLOWED_SYMBOLS: list[str] = [
    ","
]

SIZE_DEC_ALLOWED_SYMBOLS: list[str] = SIZE_INC_ALLOWED_SYMBOLS

# Declars
class Variable: ...
class VariableDict: ...

def is_variable_name_valid(variable_name: str) -> bool: ...
def check_variable_bounds(variable_value: str, variable_size: int) -> bool: ...
def convert_to_variable_type(variable_value: str, variable_type: str) -> str|int|float|list: ...

# Implementation
class Variable:
    """
    A variable representation
    """
    def __init__(self, name: str, size: int, type: str, value: str | None = None) -> None:
        self.name   =   name
        self.size   =   size
        self.type   =   type
        self.value  =   value
    
    def __repr__(self):
        return f"<Variable: name={self.name!r}, size={self.size!r}, type={self.type!r}, value={self.value!r}>"
    

class VariableDict:
    """
    A dictionary for the Variable class
    """
    dictionary: dict[str, Variable] = dict()
    
    def __init__(self) -> None:
        pass
    
    def add(self, variable: Variable) -> None:
        """
        Add a Variable object to the dictionary.
        
        Args:
            variable (Variable): A Variable object.
        
        Returns:
            None.
        """
        self.dictionary[variable.name] = variable
    
    def get(self, variable_name: str) -> Variable | None:
        """
        Fetch a variable from the dictionary by their name.
        
        Args:
            variable_name (str): The variable's name.
            
        Returns:
            Variable: A Variable object if it does exists,
            otherwise None is returned
        """
        if not self.is_exist(variable_name):
            return None
        
        return self.dictionary[variable_name]

    def update(self, variable_name: str, variable: Variable) -> None:
        """
        Update a variable.
        
        Args:
            variable_name (str): The variable's name.
            variable (Variable): The variable object.
        
        Returns:
            None.
        """
        self.dictionary[variable_name] = variable
    
    def is_exist(self, variable_name: str) -> bool:
        """
        Check if a variable exists or not.
        
        Args:
            variable_name (str): The variable's name.
        
        Returns:
            True if it exists, otherwise False.
        """
        try:
            self.dictionary[variable_name]
            return True
        except:
            return False

def convert_to_variable_type(variable_value: str, variable_type: str) -> str|int|float|list:
    """
    Convert variable values into their corresponding type.
    
    Args:
        variable_value (str): The variable's value.
        variable_type (str): The variable's type.
    
    Returns:
        str|int|float|list: The variable's value in its corresponding type.
    """
    try:
        if not isinstance(variable_value, VARIABLE_TYPES[variable_type]):
            variable_value = VARIABLE_TYPES[variable_type](variable_value)
    except Exception as e:
        raise InvalidVariableType

    return variable_value
