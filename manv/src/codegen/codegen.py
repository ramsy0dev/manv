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
import random
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
BSS_SECTION  = "bss"

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
        self.asm.add_to_section(
            section=TEXT_SECTION,
            label=MAIN_FUNC_LABEL,
            code=[
                "global _start\n",
                ("_start:\n" if len(program.statements) != 0 else "")
            ]
        )

        for statement in program.statements:
            self.process_statement(
                statement=statement
            )
        
        # Exit syscall
        self.asm.add_to_section(
            section=TEXT_SECTION,
            label="exit_syscall",
            code=[
                "\t" + f"mov rax, 60\n",
                "\t" + f"mov rsi, 0\n",
                "\t" + f"syscall\n"
            ]
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

        # Variable declaration
        if isinstance(statement, Variable):
            # Determine which section to use
            section = None
            asm_code = ""

            if statement.value is None:
                section = BSS_SECTION
                asm_code = "\t" + f"{statement.identifier.name} resq {statement.size.value}\n"
            else:
                section = DATA_SECTION
                if isinstance(statement.typ, (CharType, StrType)): # Use 'db'
                    asm_code = "\t" + f"{statement.identifier.name} db {statement.value.value}"
                else:   # Use 'dq'
                    asm_code = "\t" + f"{statement.identifier.name} dq {statement.value.value}"
            
            self.asm.add_to_section(
                section=section,
                label=statement.identifier.name + "_var",
                code=asm_code
            )
    
        # Operations
        if isinstance(statement, (MultiplyOp, DivideOp, AdditionOp, SubtractionOp)):
            asm_code = list()

            if isinstance(statement, MultiplyOp):
                regs = ["rax", "rbx"]
                left = None
                right = None
                
                if isinstance(statement.left, Identifier):
                    left = f"[{statement.left.name}]"
                else:
                    left = statement.left.value
                
                if isinstance(statement.right, Identifier):
                    right = f"[{statement.right.name}]"
                else:
                    right = statement.right.value
                
                # Load values from memory
                asm_code.append(
                    "\t" + f"mov {regs[0]}, {left}\n"
                )
                asm_code.append(
                    "\t" + f"mov {regs[1]}, {right}\n"
                )

                # Preform the multiplication
                asm_code.append(
                    "\t" + f"imul {regs[0]}, {regs[1]}\n"
                )

                # Store the result in the result identifier
                asm_code.append(
                    "\t" + f"mov [{statement.assign.identifier.name}], {regs[0]}\n"
                )

                # asm_code.append(
                #     "\t" + f"mov rax, [{statement.assign.identifier.name}]\n"
                # )
                # asm_code.append(
                #     "\t" + f"call printi\n"
                # )
            elif isinstance(statement, DivideOp):
                regs = ["rax", "rdx", "rcx"]
                left = None
                right = None
                
                if isinstance(statement.left, Identifier):
                    left = f"[{statement.left.name}]"
                else:
                    left = statement.left.value
                
                if isinstance(statement.right, Identifier):
                    right = f"[{statement.right.name}]"
                else:
                    left = statement.right.value
                
                asm_code.append(
                    "\t" + f"mov {regs[0]}, {left}\n"
                )

                # Clear rdx (high bits of dividend)
                asm_code.append(
                     "\t" + f"xor {regs[1]}, {regs[1]}\n"
                )

                asm_code.append(
                     "\t" + f"mov {regs[2]}, {right}\n"
                )

                # Preform the division
                asm_code.append(
                     "\t" + f"idiv {regs[2]}\n"
                )

                # Store the result in the result identifier
                asm_code.append(
                    "\t" + f"mov [{statement.assign.identifier.name}], {regs[0]}\n"
                )
            elif isinstance(statement, AdditionOp):
                regs = ["rax"]
                left = None
                right = None

                if isinstance(statement.left, Identifier):
                    left = f"[{statement.left.name}]"
                else:
                    left = statement.left.value
                
                if isinstance(statement.right, Identifier):
                    right = f"[{statement.right.name}]"
                else:
                    left = statement.right.value
                
                asm_code.append(
                    "\t" + f"mov {regs[0]}, {left}\n"
                )

                # Perform the addition
                asm_code.append(
                    "\t" + f"add {regs[0]}, {right}\n"
                )

                # Store the result in the result identifier
                asm_code.append(
                    "\t" + f"mov [{statement.assign.identifier.name}], {regs[0]}\n"
                )
            elif isinstance(statement, SubtractionOp):
                regs = ["rbx"]
                left = None
                right = None

                if isinstance(statement.left, Identifier):
                    left = f"[{statement.left.name}]"
                else:
                    left = statement.left.value
                
                if isinstance(statement.right, Identifier):
                    right = f"[{statement.right.name}]"
                else:
                    left = statement.right.value
                
                asm_code.append(
                    "\t" + f"mov {regs[0]}, {left}\n",
                )

                # Perform the subtraction
                asm_code.append(
                    "\t" + f"sub {regs[0]}, {right}\n"
                )

                # Store the result in the result identifier
                asm_code.append(
                    "\t" + f"mov [{statement.assign.identifier.name}], {regs[0]}\n"
                )

            # For now we are adding every instruction into the main function
            # label _start
            self.asm.add_to_section(
                section=TEXT_SECTION,
                label=MAIN_FUNC_LABEL,
                code=asm_code
            )

        # syscall
        if isinstance(statement, Syscall):
            label = "syscall_" + str(random.choice(range(999, 9999)))
            syscall_number = statement.syscall_number
            args = statement.args
            error_identifier = statement.error.name

            syscall_regs_list = [
                "rdi",
                "rsi",
                "rdx",
                "r10",
                "r8",
                "r9",
            ]

            # Move the syscall number to the RAX register
            self.asm.add_to_section(
                section=TEXT_SECTION,
                label=label,
                code=[
                    "\t" + f"mov rax, {syscall_number}\n",
                ]
            )
            
            # Move arguments value into the registers
            for i, arg in enumerate(args):
                self.asm.add_to_section(
                    section=TEXT_SECTION,
                    label=label,
                    code=[
                        "\t" + f"mov {syscall_regs_list[i]}, {arg}\n"
                    ]
                )
            
            # Call syscall
            self.asm.add_to_section(
                section=TEXT_SECTION,
                label=label,
                code=[
                    "\t" + "syscall\n"
                ]
            )

            # Move the error raised by the syscall to the provided identifier
            self.asm.add_to_section(
                section=TEXT_SECTION,
                label=label,
                code=[
                    "\t" + f"mov [{error_identifier}], rax\n"
                ]
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
                        code="\t" + f"mov {reg}, {value}\n"
                    )

            self.asm.add_to_section(
                section=TEXT_SECTION,
                label=statement.identifier.name + "_call_func",
                code="\t" + f"call {statement.identifier.name}\n"
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
    