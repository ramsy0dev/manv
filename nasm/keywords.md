# NASM Keywords and Directives

NASM (Netwide Assembler) provides a variety of **keywords**, **directives**, and **mnemonics** for assembling x86/x86-64 programs. Here’s a **comprehensive list**:

---

## **1. Sections & Segments**
Used to define different parts of an ELF or PE executable.

| **Directive** | **Description** |
|--------------|---------------|
| `section .text` | Code section (for executable instructions) |
| `section .data` | Initialized data section (global/static variables) |
| `section .bss` | Uninitialized data section (zeroed at runtime) |
| `segment` | Alternative to `section`, mainly used in DOS/Windows |

---

## **2. Symbol Definitions & Scope**
Used for declaring global and local symbols.

| **Directive** | **Description** |
|--------------|---------------|
| `global` | Makes a symbol available to the linker |
| `extern` | Declares symbols from another file |
| `%define` | Defines a macro (like `#define` in C) |
| `equ` | Assigns a constant value to a symbol |

Example:
```assembly
msg_len equ 13   ; Define a constant
global _start    ; Export `_start` to the linker
```

---

## **3. Data Definition Directives**
Used to declare variables in memory.

| **Directive** | **Description** |
|--------------|---------------|
| `db` | Define byte (8-bit) |
| `dw` | Define word (16-bit) |
| `dd` | Define double word (32-bit) |
| `dq` | Define quad word (64-bit) |
| `dt` | Define ten bytes (80-bit, for FPU) |

Example:
```assembly
msg db "Hello, World!", 0  ; Null-terminated string
num dw 100                 ; 16-bit integer
```

---

## **4. CPU Instructions (Mnemonics)**
These are common x86-64 instructions.

| **Category** | **Instructions** |
|-------------|----------------|
| **Data Movement** | `mov`, `push`, `pop`, `lea`, `xchg` |
| **Arithmetic** | `add`, `sub`, `mul`, `div`, `inc`, `dec` |
| **Bitwise Ops** | `and`, `or`, `xor`, `not`, `shl`, `shr` |
| **Control Flow** | `jmp`, `call`, `ret`, `loop` |
| **Comparison** | `cmp`, `test` |
| **Conditional Jumps** | `je`, `jne`, `jg`, `jl`, `jge`, `jle` |
| **System Calls** | `syscall`, `int 0x80` |

Example:
```assembly
mov rax, 1   ; Load syscall number for sys_write
mov rdi, 1   ; File descriptor (stdout)
mov rsi, msg ; Pointer to message
mov rdx, msg_len ; Message length
syscall
```

---

## **5. Macros & Conditional Assembly**
NASM allows preprocessor macros and conditional compilation.

| **Directive** | **Description** |
|--------------|---------------|
| `%macro` | Defines a macro |
| `%endmacro` | Ends a macro definition |
| `%if`, `%elif`, `%else`, `%endif` | Conditional assembly |
| `%ifdef`, `%ifndef` | Checks if a symbol is defined |

Example:
```assembly
%macro PRINT 2
    mov rax, 1
    mov rdi, 1
    mov rsi, %1
    mov rdx, %2
    syscall
%endmacro

PRINT msg, msg_len
```

---

## **6. Debugging & Alignment**
| **Directive** | **Description** |
|--------------|---------------|
| `align` | Aligns data to a specific byte boundary |
| `nop` | No operation (used for padding) |
| `times` | Repeats an instruction multiple times |

Example:
```assembly
align 16   ; Ensure next instruction is at a 16-byte boundary
times 4 db 0  ; Reserve 4 bytes filled with 0
```

---

## **7. Stack Operations**
| **Instruction** | **Description** |
|---------------|---------------|
| `push` | Push value onto stack |
| `pop` | Pop value from stack |
| `call` | Call a function |
| `ret` | Return from function |

Example:
```assembly
push rax
call my_function
pop rax
```

---

## **8. System Calls (Linux)**
When working with **ELF64**, system calls are made using `syscall` and **register-based calling convention**.

| **Syscall** | **rax** | **rdi** | **rsi** | **rdx** |
|------------|--------|--------|--------|--------|
| `sys_write` | `1` | fd (1 = stdout) | buffer | size |
| `sys_exit` | `60` | exit_code | — | — |

Example:
```assembly
mov rax, 60  ; sys_exit
mov rdi, 0   ; Exit code 0
syscall
```

---

## **Final Notes**
This list covers **most** of the NASM keywords and features. If you're writing a **compiled language**, focus on:
- **`section .text`** for code
- **`global` & `extern`** for symbol linking
- **`syscall`** for interacting with Linux
- **Macros (`%macro`)** for abstraction

