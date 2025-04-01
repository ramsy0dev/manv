# NASM Syntax Guide

## 1️⃣ Basic NASM Syntax
```assembly
section .text  ; Code section (required)
global _start  ; Entry point (needed for linking)

_start:
    ; Your assembly code here
```

---

## 2️⃣ NASM Sections
### 🔹 Code Section (`.text`)
The **`.text` section** contains the actual program code.
```assembly
section .text
global _start

_start:
    ; sys_exit
    mov rax, 60  
    xor rdi, rdi
    syscall      
```

### 🔹 Data Section (`.data`)
The **`.data` section** stores **initialized variables**.
```assembly
section .data
message db "Hello, NASM!", 0xA  ; Null-terminated string
```

### 🔹 BSS Section (`.bss`)
The **`.bss` section** is for **uninitialized variables**.
```assembly
section .bss
buffer resb 256  ; Reserve 256 bytes
```

---

## 3️⃣ Declaring Constants & Variables
### 🔹 Constants (`equ`)
```assembly
BUFFER_SIZE equ 1024
mov rax, BUFFER_SIZE
```

### 🔹 Variables (`db`, `dw`, `dd`, `dq`)
```assembly
section .data
myByte  db  10       ; 1 byte
myWord  dw  1000     ; 2 bytes
myDword dd  12345678 ; 4 bytes
myQword dq  1234567890123456789  ; 8 bytes
```

---

## 4️⃣ NASM Instructions
### 🔹 Moving Data (`mov`)
```assembly
mov rax, 5    ; Move 5 into RAX
mov rbx, rax  ; Copy value of RAX into RBX
```

### 🔹 Arithmetic (`add`, `sub`, `mul`, `div`)
```assembly
add rax, 10  ; rax = rax + 10
sub rbx, 2   ; rbx = rbx - 2
```

### 🔹 Multiplication & Division
```assembly
mov rax, 10
mov rbx, 5
mul rbx   ; RAX = RAX * RBX (10 * 5 = 50)
div rbx   ; RAX = RAX / RBX (50 / 5 = 10)
```

### 🔹 Logical Operations (`and`, `or`, `xor`, `not`)
```assembly
and rax, rbx  ; Bitwise AND
or rax, rbx   ; Bitwise OR
xor rax, rbx  ; Bitwise XOR
not rax       ; Bitwise NOT
```

---

## 5️⃣ Control Flow (Jumps & Loops)
### 🔹 Unconditional Jump (`jmp`)
```assembly
jmp my_label

my_label:
    ; Code continues here
```

### 🔹 Conditional Jumps
```assembly
cmp rax, rbx  ; Compare RAX and RBX
je equal      ; Jump if equal
jne not_equal ; Jump if not equal
jg greater    ; Jump if greater
jl less       ; Jump if less
```

### 🔹 Loop Example
```assembly
section .bss
counter resb 1  ; Reserve 1 byte for counter

section .text
global _start

_start:
    mov byte [counter], 5  ; Store 5 in counter

loop_start:
    dec byte [counter]     ; Decrease counter
    cmp byte [counter], 0
    jne loop_start         ; Loop if not zero

    mov rax, 60  ; sys_exit
    xor rdi, rdi
    syscall
```

---

## 6️⃣ Calling Linux Syscalls
### 🔹 Writing to STDOUT (`sys_write`)
```assembly
section .data
message db "Hello, NASM!", 0xA
message_len equ $ - message  ; Calculate string length

section .text
global _start

_start:
    mov rax, 1       ; sys_write
    mov rdi, 1       ; File descriptor: STDOUT
    mov rsi, message ; Message to print
    mov rdx, message_len ; Message length
    syscall

    mov rax, 60  ; sys_exit
    xor rdi, rdi
    syscall
```

---

## 7️⃣ Compiling & Running NASM Code
### 🔹 Compiling on Linux (ELF64)
```sh
nasm -f elf64 program.asm -o program.o
ld program.o -o program
./program
```

### 🔹 Compiling on Windows (PE64)
```sh
nasm -f win64 program.asm -o program.obj
golink /entry:_start /console program.obj kernel32.dll
```

---

## 🛠 Summary
| Syntax Element  | NASM Syntax |
|----------------|------------|
| **Code Section** | `section .text` |
| **Data Section** | `section .data` |
| **BSS Section**  | `section .bss` |
| **Define Constant** | `equ` (`BUFFER_SIZE equ 1024`) |
| **Define Variable** | `db`, `dw`, `dd`, `dq` |
| **Move Data** | `mov rax, 5` |
| **Math Operations** | `add`, `sub`, `mul`, `div` |
| **Jump Instructions** | `jmp`, `je`, `jne`, `jg`, `jl` |
| **Syscalls** | `mov rax, syscall_number`, `syscall` |

---

Would you like me to generate **example code** that your compiler can output? 🚀


