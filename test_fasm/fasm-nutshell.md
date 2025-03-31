
# Boilerplate ASM

```asm
format ELF64 executable 3

segment readable executable
; ----------------------- ;
;     Code to execute     ;
; ----------------------- ;

exit:
  mov rax, 60 ; sys_exit
  mov rdi, 0  ; exit code 0
  syscall

segment readable writable
; ----------------------- ;
;      Data to store      ;
; ----------------------- ;


```


# Registers

# Registers roles

* RAX is used to specify the syscall number.

* RDI, RSI, RDX, R10, R8, and R9 are used for passing arguments (in order).

* RAX also stores the return value of the syscall.

