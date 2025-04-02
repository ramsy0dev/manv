; Test file for testing io::print

section .data
    msg db "Hello World!", 0xA
    msg_len equ $ - msg

section .text
global _start

extern print  ; print function from the IO library

_start:
    ; Test with valid input (normal message)
    mov rdi, msg           ; Point to the message
    mov rsi, msg_len       ; Set length of the message
    call print             ; Call the print function
    
    ; Test with invalid text (null)
    xor rdi, rdi           ; rdi = 0 (Null pointer)
    mov rsi, msg_len
    call print

    ; Test with invalid text length
    mov rdi, msg
    xor rsi, rsi
    call print
    
    ; Exit program normally
    mov rax, 60            ; sys_exit
    xor rdi, rdi           ; Return code 0
    syscall
