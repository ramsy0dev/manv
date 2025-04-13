; Test file for testing io::print

section .data
    msg db "Hello World!", 0xA
    msg_len equ $ - msg

section .text
global _start

extern print  ; print function from the IO library

_start:
    ; Test with invalid text error (null)
    xor rdi, rdi           ; rdi = 0 (Null pointer)
    mov rsi, msg_len
    call print

    ; Exit program normally
    mov rax, 60            ; sys_exit
    xor rdi, rdi           ; Return code 0
    syscall

