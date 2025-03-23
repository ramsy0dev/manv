# Introduction

ManV is an SCL (Structured Calculations Language) inspired by SQL (Structured Query Language), made for creating complex structured calculations.

# Developpement plan

* ## Implemented Syntax

|    Syntax     | Is implemented  |
|---------------|-----------------|
|   CRA         |       ✅        |
|   SIZE_INC    |       ✅        |
|   SIZE_DEC    |       ✅        |
|   EMT         |       ❌        |
|   MUL         |       ❌        |
|   ADD         |       ❌        |
|   DIV         |       ❌        |
|   SUB         |       ❌        |

* ## Implemented data types

|    Type   |  Is implemented  |
|-----------|------------------|
|   INT     |       ✅        |
|   FLOAT   |       ✅        |
|   STRING  |       ❌        |
|   VECTOR  |       ❌        |


# Syntax

* ## Basic data types

```
INT     // Integer type
FLOAT   // Float type
STRING  // String sequence
VECTOR  // Vector
```

* ## Declare variables

```
CRA x[10]: INT = 1      // Variable named 'x' of type INT, with the value of '1'
CRA y[10]: FLOAT = 0.1  // Variable named 'y' of type FLOAT, with the value of '0.1'
CRA c[]: INT            // Variable named 'c' of type INT, with a dynamic size and with no value assigned

// If we want to increase or decrease the variable's size
// we do the following:

SIZE_INC x, 10  // Increase the size by 10
SIZE_DEC y, 10  // Decrease the size by 10

// To empty or delete a variable from memory
EMT x // Empty the variable x from its value
DEL x // Delete the variable x from memory
```

* ## Basic operations

```
CRA x[]: INT = 10
CRA y[]: INT = 2

CRA mul_res[]: INT
CRA add_res[]: int
CRA div_res[]: FLOAT
CRA sub_res[]: INT

MUL x, y -> mul_res     // Multiplication
ADD x, y -> add_res     // Addition
DIV x, y -> div_res     // Division
SUB x, y -> sub_res     // Subtraction
```

* ## Symbols operations

These operations return their value instead of having to declare an other variable and store them in it to use them.

```
( a * b )        // Multiplication
( a + b )        // Addition
( a / b )        // Division
( a - b )        // Subtraction
```
