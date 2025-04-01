# NASM Registers Guide

## 1️⃣ General-Purpose Registers (64-bit)
### 🔹 RAX (Accumulator Register)
- Used for arithmetic, multiplication, division, and syscall return values.
- Example: Multiplication using `rax`.
```assembly
mov rax, 10
mov rbx, 5
mul rbx   ; RAX = RAX * RBX (10 * 5 = 50)
```

### 🔹 RBX (Base Register)
- Typically used as a base pointer for memory access.
- Example: Using `rbx` as a loop counter.
```assembly
mov rbx, 5
loop_start:
    dec rbx
    cmp rbx, 0
    jne loop_start
```

### 🔹 RCX (Counter Register)
- Used in loops and `rep` string operations.
- Example: Looping `5` times using `rcx`.
```assembly
mov rcx, 5
loop_start:
    dec rcx
    jnz loop_start
```

### 🔹 RDX (Data Register)
- Used for I/O operations and as a high-order register for division/multiplication.
- Example: Division with `rdx`.
```assembly
mov rax, 100
mov rbx, 10
div rbx   ; RAX = RAX / RBX, remainder stored in RDX
```

### 🔹 RSI (Source Index)
- Used for string operations and memory addressing.
- Example: Copying data from `rsi`.
```assembly
mov rsi, message
mov rdi, buffer
mov rcx, message_len
rep movsb  ; Copy `message` to `buffer`
```

### 🔹 RDI (Destination Index)
- Used as a destination pointer in string operations.
- Example: Writing to memory using `rdi`.
```assembly
mov rdi, buffer
mov byte [rdi], 'A'
```

---

## 2️⃣ Stack and Base Registers
### 🔹 RBP (Base Pointer)
- Holds the base address of the stack frame.
- Example: Function call using `rbp`.
```assembly
push rbp
mov rbp, rsp  ; Set new stack frame
; Function body
mov rsp, rbp  ; Restore stack
pop rbp
```

### 🔹 RSP (Stack Pointer)
- Points to the top of the stack.
- Example: Pushing and popping values from the stack.
```assembly
push rax   ; Save RAX on the stack
pop rax    ; Restore RAX from the stack
```

---

## 3️⃣ Special Registers
### 🔹 RIP (Instruction Pointer)
- Holds the address of the next instruction to execute.
- Example: Jumping to a label.
```assembly
jmp my_label
my_label:
    nop  ; Do nothing
```

### 🔹 RFLAGS (Flags Register)
- Stores status flags after operations (e.g., zero flag, carry flag).
- Example: Conditional jump using `ZF` (zero flag).
```assembly
cmp rax, rbx
je equal_label
```

---

## 4️⃣ Segment Registers (Rarely Used in x86-64)
- **CS** (Code Segment) - Points to code segment.
- **DS** (Data Segment) - Points to data segment.
- **ES, FS, GS, SS** - Used for system and thread-specific data.

---

## 🛠 Summary Table
| Register | Purpose |
|----------|---------|
| **RAX**  | Accumulator (arithmetic, return values) |
| **RBX**  | Base register (memory access) |
| **RCX**  | Counter register (loops, `rep` operations) |
| **RDX**  | Data register (multiplication, division) |
| **RSI**  | Source index (string/memory operations) |
| **RDI**  | Destination index (string/memory operations) |
| **RBP**  | Base pointer (stack frame) |
| **RSP**  | Stack pointer (top of stack) |
| **RIP**  | Instruction pointer (next instruction) |
| **RFLAGS** | Status flags (zero flag, carry flag, etc.) |

Would you like any additional details? 🚀


