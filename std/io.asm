; MIT License

; Copyright (c) 2025 ramsy0dev

; Permission is hereby granted, free of charge, to any person obtaining a copy
; of this software and associated documentation files (the "Software"), to deal
; in the Software without restriction, including without limitation the rights
; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
; copies of the Software, and to permit persons to whom the Software is
; furnished to do so, subject to the following conditions:

; The above copyright notice and this permission notice shall be included in
; all copies or substantial portions of the Software.

; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
; SOFTWARE.

; file: std/io.asm
; description: I/O Library

section .data
    ; Errors code
    invalid_text_error_code     equ 0       ; Error code for invalid text (print function)
    invalid_text_len_error_code equ 1       ; Error code for invalid text length (print function)

    ; Errors messages
    invalid_text_error_msg      db "Invalid text", 0xA         ; Error message for invalid text (print function)
    invalid_text_len_error_msg  db "Invalid text length", 0xA  ; Error message for invalid text length (print function)

section .text
global print

; ---------------------------------------------- ;
;       Builtin functions implementations        ;
; ---------------------------------------------- ;
print:
    ; manv declaration:
    ;   ``` manv
    ;   fn print(text: str, len: int) -> NONE;
    ;   ```
    ; arguments registers:
    ;   rdi -> text
    ;   rsi -> len

    ; Validate the text length
    cmp rsi, 0
    je .invalid_text_error

    ; Check if the text is a valid address
    test rdi, rdi
    jle .invalid_text_len_error

    mov rax, 1      ; sys_write
    mov rdx, rsi    ; message length
    mov rsi, rdi    ; message
    mov rdi, 1      ; STDOUT
    syscall

; ---------------------------------------------- ;
;                   Error handling               ;
; ---------------------------------------------- ;
.invalid_text_error:
    ; Write to STDOUT the error message
    mov rax, 1                          ; sys_write
    mov rdi, 1                          ; STDOUT
    mov rsi, invalid_text_error_msg     ; Error message
    mov rdx, 18                         ; Error message length
    syscall

    ; Exit
    mov rax, 60                         ; sys_exit
    mov rdi, invalid_text_error_code    ; Error code
    syscall

.invalid_text_len_error:
    ; Write to STDOUT the error message
    mov rax, 1                              ; sys_write
    mov rdi, 1                              ; STDOUT
    mov rsi, invalid_text_len_error_msg     ; Error message
    mov rdx, 20                             ; Error message length
    syscall

    ; Exit
    mov rax, 60                             ; sts_exit
    mov rdi, invalid_text_len_error_code    ; Error code
    syscall
