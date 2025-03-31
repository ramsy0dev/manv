format ELF64 executable 3

segment readable executable

entry main

main:
  lea rdi, [text] ;; Load the address of text into rdi
  mov rax, 14     ;; Length of text
  mov rdx, rax
  mov rsi, rdi
  mov rdi, 1
  mov rax, 1
  syscall
  
  xor rdi, rdi    ;; exit code 0
  mov rax, 60     ;; sys_exit
  syscall

segment readable writable

text db 'Hello World', 10, 0 ;; 10 -> \n, 0 -> EOF
