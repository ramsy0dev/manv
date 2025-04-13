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
    "Codegen"
]

import sys
from rich import print

# Base
from manv.src.ast.base import ASTNode

# Nodes
from manv.src.ast.nodes import *

# Builtin functions
from manv.src.builtin.functions import *

# Builtin Literals
from manv.src.builtin.literals import *

# Builtin Types
from manv.src.builtin.types import *

from manv.src.codegen.asm import *

# Sections
TEXT_SECTION = "text"
DATA_SECTION = "data"
BSS_SECTIOn  = "bss"

# Labels
MAIN_FUNC_LABEL = "main"

# Arguments registers for Unix x86-64
ARGS_REGISTERS = [
    "rdi",
    "rsi",
    "rdx",
    "rcx",
    "r8",
    "r9"
]

class Codegen:
    """
    Generate assembly code
    """
    def __init__(self) -> None:
        self.asm = ASM()

    def codegen(self, program: Program) -> ASM:
        """
        Generate assembly code based on the program's AST tree.
        """
        # Exit out if no main function was given
        # if program.main is None:
        #     print(f"[bold red][ERROR][reset]: No main function was declared.")
        #     exit(1)

        # Dump builtin functions
        self.dump_builtin_funcs()

        program.main = Function(
            identifier=Identifier(name="main"),
            arguments=NULL(),
            statements=[
                # Call PRINT
                CallFunction(
                    identifier=Identifier(name="prints"),
                    args_list=[
                        ArgumentValue(
                           identifier=Identifier(name="char_seq"),
                           value=CallConstant(
                            identifier=Identifier(name="text")
                           ),
                           reg_label="rsi",
                        ),
                        ArgumentValue(
                            identifier=Identifier(name="length"),
                            value=NumberLiteral(
                                value=11
                            ),
                            reg_label="rdx"
                        ),
                    ]
                ),
                # Call EXIT
                CallFunction(
                    identifier=Identifier(name="exit")),
                ],
            return_type=IntType(),
        )

        entries = [
            program,
            program.main
        ]

        for i, entry in enumerate(entries):
            # Main function
            if i == 1:
                self.asm.add_to_section(
                    section=TEXT_SECTION,
                    label=MAIN_FUNC_LABEL,
                    code=[
                        "global _start\n",
                        ("_start:\n" if len(entry.statements) != 0 else "")
                    ]
                )

            for statement in entry.statements:
                self.process_statement(
                    statement=statement
                )
                
        return self.asm

    def process_statement(self, statement: ASTNode) -> str:
        """
        Process a single statement
        """
        # Constant declaration
        if isinstance(statement, Constant):
            self.asm.add_to_section(
                section=DATA_SECTION,
                label=statement.identifier.name + "_const",
                code=f"{statement.identifier.name} {'db'  if isinstance(statement.typ, (CharType, StrType)) else 'dq'} {statement.value.value}\n"
            )
            
        # Function
        if isinstance(statement, Function):
            # Baked in assembly implementation
            if statement.asm_code is not None:
                for section in statement.asm_code:
                    self.asm.add_to_section(
                        section=section,
                        label=statement.identifier.name + "_func",
                        code=statement.asm_code[section]
                    )
        
        # Call Function
        if isinstance(statement, CallFunction):
            # Pass arguments
            # NOTE: Max args number is 6
            if statement.args_list is not None:
                for i, arg in enumerate(statement.args_list):
                    reg = ARGS_REGISTERS[i]
                    
                    if arg.reg_label is not None:
                        reg = arg.reg_label
                    
                    value = None

                    # CallConstant
                    if isinstance(arg.value, CallConstant):
                        value = arg.value.identifier.name
                    else:
                        value = arg.value.value
                    
                    self.asm.add_to_section(
                        section=TEXT_SECTION,
                        label=statement.identifier.name + "_call_func",
                        code=f"mov {reg}, {value}\n"
                    )

            self.asm.add_to_section(
                section=TEXT_SECTION,
                label=statement.identifier.name + "_call_func",
                code=f"call {statement.identifier.name}\n"
            )
    
    def dump_builtin_funcs(self) -> None:
        """
        Dump builtin functions into the output source code.
        """
        for builtin_func in BUILTIN_FUNCTIONS:
            self.process_statement(
                statement=builtin_func
            )
        
    def get_size_of_obj(self, obj, seen=None) -> int:
        """
        Recursively find the true size of an object including its references
        """
        if seen is None:
            seen = set()

        obj_id = id(obj)
        if obj_id in seen:
            return 0  # Avoid infinite recursion for circular references

        seen.add(obj_id)
        size = sys.getsizeof(obj)

        if isinstance(obj, dict):
            size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set, frozenset)):
            size += sum(deep_getsizeof(i, seen) for i in obj)

        return size
    