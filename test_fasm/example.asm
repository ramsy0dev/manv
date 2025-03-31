
format ELF64 executable 3

segment readable executable

entry main

main:
    ; Pass arguments (5, 10, 15) to the function
    mov rdi, 5        ; First argument
    mov rsi, 10       ; Second argument
    mov rdx, 15       ; Third argument
    call compute_result  ; Call function

    ; Convert integer result (in RAX) to string
    mov rdi, rax      ; Move result to RDI for conversion
    call int_to_string

    ; Print the result
    mov rax, 1        ; sys_write syscall
    mov rdi, 1        ; File descriptor 1 (stdout)
    mov rsi, buffer   ; Address of string buffer
    mov rdx, buffer_len ; Length of string
    syscall           ; Print result

    ; Exit program
    xor rdi, rdi      ; Exit code 0
    mov rax, 60       ; sys_exit syscall
    syscall

; Function: compute_result(int a, int b, int c)
; Adds a, b, and c, then multiplies by 2
compute_result:
    push rbp          ; Save base pointer
    mov rbp, rsp      ; Set new base pointer

    mov rax, rdi      ; RAX = first argument
    add rax, rsi      ; RAX += second argument
    add rax, rdx      ; RAX += third argument
    imul rax, 2       ; RAX *= 2  (Multiply by 2)

    pop rbp           ; Restore base pointer
    ret               ; Return (RAX holds result)

; Function: int_to_string(int num)
; Converts integer in RDI to string in 'buffer'
int_to_string:
    mov rbx, buffer + 19  ; Point RBX to end of buffer
    mov byte [rbx], 0xA   ; Store newline character
    dec rbx               ; Move back for digits

.loop:
    mov rax, rdi          ; Copy number into RAX
    mov rdx, 0            ; Clear RDX for division
    mov rcx, 10           ; Divisor (base 10)
    div rcx               ; RAX = RAX / 10, RDX = RAX % 10
    add dl, '0'           ; Convert remainder to ASCII
    mov [rbx], dl         ; Store ASCII digit in buffer
    dec rbx               ; Move left
    test rax, rax         ; Check if RAX == 0
    jnz .loop             ; If not, continue

    inc rbx               ; Adjust pointer
    mov buffer, rbx       ; Store pointer to start of number
    ret                   ; Return

segment readable writable

buffer rb 20             ; Buffer for storing integer string
buffer_len equ 20        ; Max buffer length
