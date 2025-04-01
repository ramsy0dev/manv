
section .data
    msg db "Hello World!", 0xA

section .text
    global _start

_start:
    mov rax, 1      ; sys_write
    mov rdi, 1      ; STDOUT
    mov rsi, msg    ; data to write to STDOUT
    mov rdx, 13     ; Length of the data
    syscall

    mov rax, 60 ; sys_exit
    mov rdi, 0  ; exit code 0, we can also do: xor rdi, rdi
    syscall

