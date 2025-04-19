# Introduction

ManV is an SCL (Structured Calculations Language) inspired by SQL (Structured Query Language), made for creating complex structured calculations.

# Development plan

- [X] Make ManV a compiled language (By generating assembly code)
- [X] Implement Constant/Variable declaration
- [X] Implement basic math operations (mul, div, add, sub)
- [X] Implement syscall keyword for interacting the system
- [X] Implement a basic pointer
- [ ] Implement memory manipulation keywords like pop, push...
- [ ] Implement if-else conditions
- [ ] Implement while loops
- [ ] Implement functions
- [ ] Implement the 'include' keyword
- [ ] Write the ManV stdlib
- [ ] Port some C libraries (raylib) to ManV

# Syntax

* ## Basic data types

```
int     // Integer type
float   // Float type
str     // String sequence
char    // Char
```

* ## Declare variables

```
const x[10]: int = 1;      // Variable named 'x' of type int, with the value of '1'
const y[10]: float = 0.1;  // Variable named 'y' of type float, with the value of '0.1'
const c: int;              // Variable named 'c' of type int, with a dynamic size and with no value assigned

// If we want to increase or decrease the variable's size
// we do the following:

size_inc x, 10;  // Increase the size by 10
size_dec y, 10; // Decrease the size by 10

// To empty or delete a variable from memory
emt x // Empty the variable x from its value
del x // Delete the variable x from memory
```

* ## Basic operations

```
const x: int = 10;
const y: int = 2;

var mul_res: int;
var add_res: int;
var div_res: float;
var sub_res: int;

mul (x, y) into mul_res;     // Multiplication
add (x, y) into add_res;     // Addition
div (x, y) into div_res;     // Division
sub (x, y) into sub_res;     // Subtraction
```

* ## Direct syscalls

ManV provides a keyword called `syscall` which you can use to directly make syscalls.
the syntax for `syscall` is the following:


```
syscall $RAX, $RSI, $RDI, ..., $ERR;
```

An example usage, this is a simple call to sys_exit:
```

const EXIT_OK: int = 0; // Exit code 0
var errno: int;         // Error reporting

syscall 60, EXIT_OK, errno;

```

