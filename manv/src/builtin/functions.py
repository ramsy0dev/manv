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
    "exit_func",
    "printi_func",
    "prints_func",
    "BUILTIN_FUNCTIONS"
]

# Types
from manv.src.builtin.types import *

# Nodes
from manv.src.ast.nodes import *

# Literals
from manv.src.builtin.literals import *

# Exit function
exit_func = Function(
    identifier=Identifier(name="exit"),
    arguments=[NULL()],
    statements=[NULL()],
    return_type=NULL(),
    asm_code={
        "text": [
            "exit:\n",
            "\t" + "mov rax, 60\n",
            "\t" + "mov rdi, 0\n",
            "\t" + "syscall\n"
        ]
    }
)

# print integers func
printi_func = Function(
    identifier=Identifier(name="printi"),
    arguments=Arguments(
        args_list=[
            Argument(
                identifier=Identifier(name="n"),
                typ=MultiType(
                    type_list=[
                        IntType,
                        FloatType,
                        CallType
                    ]
                ),
                default_value=NULL(),
                reg_label="rsi"
            )
        ]
    ),
    statements=[NULL()],
    return_type=NULL(),
    asm_code={
        "text": [
            "printi:\n",
            "\t" + "mov     r9, -3689348814741910323\n",
            "\t" + "sub     rsp, 40\n",
            "\t" + "mov     BYTE [rsp+31], 10\n",
            "\t" + "lea     rcx, [rsp+30]\n",
            ".L2:\n",
            "\t" + "mov     rax, rdi\n",
            "\t" + "lea     r8, [rsp+32]\n",
            "\t" + "mul     r9\n",
            "\t" + "mov     rax, rdi\n",
            "\t" + "sub     r8, rcx\n",
            "\t" + "shr     rdx, 3\n",
            "\t" + "lea     rsi, [rdx+rdx*4]\n",
            "\t" + "add     rsi, rsi\n",
            "\t" + "sub     rax, rsi\n",
            "\t" + "add     eax, 48\n",
            "\t" + "mov     BYTE [rcx], al\n",
            "\t" + "mov     rax, rdi\n",
            "\t" + "mov     rdi, rdx\n",
            "\t" + "mov     rdx, rcx\n",
            "\t" + "sub     rcx, 1\n",
            "\t" + "cmp     rax, 9\n",
            "\t" + "ja      .L2\n",
            "\t" + "lea     rax, [rsp+32]\n",
            "\t" + "mov     edi, 1\n",
            "\t" + "sub     rdx, rax\n",
            "\t" + "xor     eax, eax\n",
            "\t" + "lea     rsi, [rsp+32+rdx]\n",
            "\t" + "mov     rdx, r8\n",
            "\t" + "mov     rax, 1\n",
            "\t" + "syscall\n",
            "\t" + "add     rsp, 40\n",
            "\t" + "ret\n",
        ]
    },
    is_syscall=True
)

# print strings func
prints_func = Function(
    identifier=Identifier(
        name="prints"
    ),
    arguments=Arguments(
        args_list=[
            Argument(
                identifier=Identifier(name="char_seq"),
                typ=MultiType(
                    type_list=[
                        StrType,
                        CharType,
                        CallType
                    ]
                ),
                reg_label="rsi",  # sys_write expects buffer in rsi
                default_value=NULL()
            ),
            Argument(
                identifier=Identifier(name="length"),
                typ=MultiType(
                    type_list=[
                        IntType,
                        CallType
                    ]
                ),
                reg_label="rdx",  # sys_write expects length in rdx
                default_value=NULL()
            )
        ]
    ),
    statements=[NULL()],
    return_type=NULL(),
    asm_code={
        "text": [
            "prints:\n",
            "\t" + "mov     rax, 1          ; syscall: write\n",
            "\t" + "mov     rdi, 1          ; stdout\n",
            "\t" + "syscall\n",
            "\t" + "ret\n",
        ]
    },
    is_syscall=True
)

BUILTIN_FUNCTIONS = [
    exit_func,
    printi_func,
    prints_func
]
