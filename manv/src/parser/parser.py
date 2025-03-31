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
    "Parser"
]

import os
import sys

from loguru import logger

# Variables
from manv.src.builtin.variables import (
    Variable,
    VariableDict,
    is_variable_name_valid,
    check_variable_bounds,
    convert_to_variable_type,
    VARIABLE_TYPES,
    TYPE_INT,
    DEFAULT_VARIABLE_SIZE,
    MAX_VARIABLE_LENGTH,
    CRA_ALLOWED_SYMBOLS,
    SIZE_INC_ALLOWED_SYMBOLS,
    SIZE_DEC_ALLOWED_SYMBOLS
)
from manv.src.parser.exceptions import (
    NSizeToDecreaseIsLarge,
    InvalidVariableType
)

# Models
from manv.models.line_model import LineModel

class Parser:
    """
    The manv structured calculation language parser.
    """
    VARIABLES: list[Variable] = list()
    VARIABLE_DICT: VariableDict = VariableDict()
    
    def __init__(self) -> None:
        pass
    
    def parse(self, tokens) -> list:
        """
        Parse the provided data.
        """
        line_n: int = 0
        last_line: LineModel = None
        
        for line in data:    
            line_n += 1 # increment the line number
        
            line = LineModel(
                content=line.strip(),
                line_number=line_n
            )
            
            # Skip empty line
            if len(line.content) == 0:
                logger.debug(f"Current line in process '{line.line_number}' is empty, skipping it.")
                last_line = line
                continue
            
            logger.debug(f"Current line in proccess \n{line.line_number} | {line.content}")
            
            # Ignore comments
            if line.content.startswith("//"):
                logger.debug(f"Ignoring comment on line number '{line.line_number}'.")
                last_line = line
                continue
            
            # Invalid comment syntax
            if line.content.startswith("/"):
                logger.error(
                    f"Invalid syntax found in line '{line.line_number}'. Did you mean '//', instead of '/' ?\n"
                    " -- Call Stack:\n"
                    f"\t   {line.line_number-1} | {last_line.content}\n"
                    f"\t-> {line.line_number} | {line.content}"
                )
                sys.exit(1)
            
            # -- Syntax: CRA
            # Creating a variable
            if line.content.startswith("CRA"):
                line_content = self.__remove_comments_from_line__(
                    data=line.content
                )
                
                line_content = line_content.split(" ")
                
                # Check the space number
                space_n = len(line_content)
                
                # The variable declaration part contains four parts
                # -- First part: CRA
                #           CRA x[n]: TYPE = VALUE
                #           ^^^
                # -- Second part: variable_name + variable_size
                #           CRA x[n]: TYPE = VALUE
                #               ^^^^
                # -- Third part: variable_type
                #           CRA x[n]: TYPE = VALUE
                #                     ^^^^
                # -- Fourth part (optional): equal symbol
                #           CRA x[n]: TYPE = VALUE
                #                          ^
                # -- Fifth part (optional): variable_value
                #           CRA x[n]: TYPE = VALUE
                #                            ^^^^^
                # So when spliting by space, space_n should be:
                #   >>> space_n = 3 (Meaning no value was sat)
                #   >>> space_n = 5 (Meaning a value was sat)
                if space_n != 5 and space_n != 3:
                    logger.debug(f"{space_n = }, {line_content = }")
                    logger.error(
                        f"Invalid syntax in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Check unwanted symbols
                is_symbols, symbol = self.__is_exists_symbols__(
                    data=line.content,
                    allowed_symbols=CRA_ALLOWED_SYMBOLS
                )
                
                if is_symbols:
                    # Exception for negative size
                    if symbol == "-":
                        if "[-" in line.content:
                            continue
                    
                    # Exception for comments
                    if symbol == "/":
                        if "//" in line.content:
                            continue
                    
                    logger.error(
                        f"Invalid syntax in line '{line.line_number}'.a\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Parse the variable_name
                variable_name = line_content[1].split("[")[0]
                
                # Parse the variable_size and check if its an INT
                variable_size = line_content[1].split("[")[1][:-2] # Removing the _[x]: and leaving only the value
                
                # Check if the variable name is of type INT
                try:
                    convert_to_variable_type(
                        variable_value=variable_name,
                        variable_type=TYPE_INT
                    )
                    logger.error(
                        f"Variable name shouldn't be an integer in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                except InvalidVariableType:
                    pass
                
                # Check if the variable_size's type is INT and converting it
                # to type INT
                try:
                    if variable_size != "":
                        variable_size = convert_to_variable_type(
                            variable_value=variable_size,
                            variable_type=TYPE_INT
                        )
                except InvalidVariableType:
                    logger.error(
                        f"Invalid size value type in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Parse the variable_type
                variable_type = line_content[2]
                
                # Parse the variable_value
                variable_value = None
                if space_n == 5:
                    variable_value = line_content[4]

                    try:
                        variable_value = convert_to_variable_type(
                            variable_value=variable_value,
                            variable_type=variable_type
                        )
                    except InvalidVariableType:
                        logger.error(
                            f"Variable value's type doesn't correspond to the variable's declared type in line '{line.line_number}'.\n"
                            " -- Call Stack:\n"
                            f"\t   {line.line_number-1} | {last_line.content}\n"
                            f"\t-> {line.line_number} | {line.content}"
                        )
                        sys.exit(1)

                # Check if the variable size is empty, this means
                # we will auto assign a size based on the value.
                if variable_size == "":
                    logger.debug("variable_size is emtpyyy")
                    if variable_value is not None:
                        variable_size = sys.getsizeof(variable_value)
                        
                        logger.debug(f"Dynamicly sat {variable_size = }")
                    else:
                        variable_size = DEFAULT_VARIABLE_SIZE
                
                # check if the variable_name's lenght hit the max
                if len(variable_name) > MAX_VARIABLE_LENGTH:
                    logger.error(
                        f"The variable name is too long in line '{line.line_number}', maximum variable name length is '{MAX_VARIABLE_LENGTH = }'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Check if the variable_name is duplicate
                if self.VARIABLE_DICT.is_exist(variable_name=variable_name):
                    logger.error(
                        f"Variable with duplicate name '{variable_name}' in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                logger.debug(f"Create new variable: {variable_name = }, {variable_size = }, {variable_type = }, {variable_value = }")
                
                # Check if the variable_type is valid
                if variable_type not in VARIABLE_TYPES:
                    logger.error(
                        f"Unknown variable type '{variable_type}' in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Check if the size is not negative
                if variable_size < 0:
                    logger.error(
                        f"The size of the variable can't be negative, in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                variable = Variable(
                    name=variable_name,
                    size=variable_size,
                    type=variable_type,
                    value=variable_value
                )
                
                self.VARIABLE_DICT.add(
                    variable=variable
                )
                self.VARIABLES.append(
                    variable
                )
                
                logger.debug(f"Appending variable \"{variable}\" to the stack")
                logger.debug(f"Variables in the stack:\n{self.VARIABLES = }")
            
            # -- Syntax: SIZE_INC
            if line.content.startswith("SIZE_INC"):
                line_content = self.__remove_comments_from_line__(
                    data=line.content
                )
                
                line_content = line_content.split(" ")
                
                # check for the space number
                space_n = len(line_content)
                
                if space_n > 3 or space_n < 3:
                    logger.error(
                        f"Invalid syntax in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Check for unwanted symbols
                is_symbols, symbol = self.__is_exists_symbols__(
                    data=line.content,
                    allowed_symbols=SIZE_INC_ALLOWED_SYMBOLS
                )
                
                if is_symbols:
                    if symbol == "/":
                        if "//" in line.content:
                            continue
                    
                    logger.error(
                            f"Invalid syntax in line '{line.line_number}'.a\n"
                            " -- Call Stack:\n"
                            f"\t   {line.line_number-1} | {last_line.content}\n"
                            f"\t-> {line.line_number} | {line.content}"
                        )
                    sys.exit(1)
                
                # Parse the variable_name
                variable_name = line_content[1][0:-1]
                
                # Parse the size_to_increase
                size_to_increase = line_content[2]
                
                # Check if the variable exists or not.
                if not self.VARIABLE_DICT.is_exist(variable_name=variable_name):
                    logger.error(
                        f"Undeclared reference to variable '{variable_name}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Check if size_to_increase is negative
                if size_to_increase.startswith("-"):
                    logger.error(
                        f"The size to increase can't be negative in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                logger.debug(f"Increasing variable '{variable_name}' size by {size_to_increase}.")
                variable = self.VARIABLE_DICT.get(
                    variable_name=variable_name
                )
                
                # Check if the size's type is INT
                try:
                    size_to_increase = convert_to_variable_type(
                        variable_value=size_to_increase,
                        variable_type=TYPE_INT
                    )
                except InvalidVariableType:
                    logger.error(
                        f"Invalid size value type in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                variable.size += size_to_increase
                
                self.VARIABLE_DICT.update(
                    variable_name=variable_name,
                    variable=variable
                )
            
            # -- Syntax: SIZE_DEC
            if line.content.startswith("SIZE_DEC"):
                line_content = self.__remove_comments_from_line__(
                    data=line.content
                )
                
                line_content = line_content.split(" ")
                
                # check for the space number
                space_n = len(line_content)
                
                if space_n > 3 or space_n < 3:
                    logger.error(
                        f"Invalid syntax in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Check for unwanted symbols
                is_symbols, symbol = self.__is_exists_symbols__(
                    data=line.content,
                    allowed_symbols=SIZE_DEC_ALLOWED_SYMBOLS
                )
                
                if is_symbols:
                    if symbol == "/":
                        if "//" in line.content:
                            continue
                    
                    logger.error(
                        f"Invalid syntax in line '{line.line_number}'.a\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Parse the variable_name
                variable_name = line_content[1][0:-1]
                
                # Parse the size_to_decrease
                size_to_decrease = line_content[2]
                
                # Check if the variable exists or not.
                if not self.VARIABLE_DICT.is_exist(variable_name=variable_name):
                    logger.error(
                        f"Undeclared reference to variable '{variable_name}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Check if the size's type is INT
                try:
                    size_to_decrease = convert_to_variable_type(
                        variable_value=size_to_decrease,
                        variable_type=TYPE_INT
                    )
                except InvalidVariableType:
                    logger.error(
                        f"Invalid size value type in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Check if size_to_decrease is negative
                if size_to_decrease < 0:
                    logger.error(
                        f"The size to decrease can't be negative in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                # Fetch the variable from the stack
                variable = self.VARIABLE_DICT.get(
                    variable_name=variable_name
                )
                
                # Check if the variable_size will become zero after the decrease
                if size_to_decrease > variable.size:
                    logger.error(
                        f"Size to decrease is larger then the variable's size in line '{line.line_number}'.\n"
                        " -- Call Stack:\n"
                        f"\t   {line.line_number-1} | {last_line.content}\n"
                        f"\t-> {line.line_number} | {line.content}"
                    )
                    sys.exit(1)
                
                logger.debug(f"Decreasing variable '{variable_name}' size by {size_to_increase}.")
                
                variable.size -= size_to_decrease
                
                self.VARIABLE_DICT.update(
                    variable_name=variable_name,
                    variable=variable
                )
            # -- Syntax: EMT
            # -- Syntax: DEL
            
            last_line = line
        
        logger.debug(
            "Variables dictionary:\n"
            f"\t>>> {self.VARIABLE_DICT = }"
        )
    
    def __remove_comments_from_line__(self, data: str) -> str:
        """
        Remove comments from a line.
        
        Args:
            data (str): The line's data.
        
        Returns:
            str: The clean line, without comments
        """
        if "//" in data:
            data = data.split("//")[0][0:-1] # NOTE: [0:-1] is for removing the last space between the size and the '//'
    
        return data
        
    def __is_exists_symbols__(self, data: str, allowed_symbols: list[str]) -> bool:
        """
        Check for unwanted symbols in data.
        
        Args:
            data (str): The line's data.
            allowed_symbols (list[str]): The allowed symbols.
        
        Returns:
            True if is exists, otherwise False.
        """
        unwanted_symbols = [
            "(", ")", "=", ",", ".", "\\", "|",
            "-", ";", "%", "@", "!", "#", "/"
            "^", "&", "*", "{", "}", "?", "<",
            ">", ":"
        ]
        
        for symbol in unwanted_symbols:
            if symbol in data:
                # Exception for negative size
                if symbol in allowed_symbols:
                    continue
                
                return (True, symbol)

        return (False, None)
