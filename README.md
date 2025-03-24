# Getting Started with FS

## Overview
This guide introduces the syntax and key features of your high-level, dynamically typed, functional programming language. The language is designed for usability, expressiveness, and competitive programming, with a focus on functional programming principles.

## Data Types
### Primitive Data Types
- **Numbers**: Integers or floating-point values.
  - Example:
    ```
    let a = 10
    let b = 3.14
    ```
- **Booleans**: `True` and `False`.
  - Example:
    ```
    let is_valid = True
    ```
- **Strings**: Enclosed in double quotes.
  - Example:
    ```
    let message = "Hello, World!"
    ```
- **Arrays**: Ordered, mutable collections.
  - Example:
    ```
    let numbers = [1, 2, 3]
    ```
### Desirable Data Types
- **Dictionaries**: Key-value mappings.
  - Example:
    ```
    let person = { "name": "Alice", "age": 25 }
    ```

## Variables
- **Declaration**:
  ```
  let x = 10
  ```
- **Reassignment**:
  ```
  x assign 20
  ```
- **Scope**: Variables are lexically scoped within their block or function.

## Operators
### Arithmetic Operators
```
let sum = 10 + 5
let power = 2 ** 3
let remainder = 10 rem 3
```
### Comparison Operators
```
let result = 10 < 20  # True
```
### Logical Operators
```
let check = True and not False  # True
```
### Assignment Operators
- `let` (declaration), `assign` (reassignment)
- Example:
  ```
  let x = 10
  x assign x + 1
  ```

## Control Flow
### If Statements
```
if (x < 0) {
    print "Negative"
} else {
    print "Non-negative"
}
```
### Loops
#### While Loop
```
let x = 0
while (x < 5) {
    print x
    x assign x + 1
}
```
#### For Loop
```
for (let i = 1 to 5) {
    print i
}
```
#### Repeat Loop
```
let x = 0
repeat {
    x assign x + 1
} until (x == 5)
```

## Pattern Matching
```
let arr = [1, 2, 3]
match arr {
    [] -> "Empty",
    [head, *tail] -> head + match tail { [] -> 0, [h, *t] -> h + match t }
}
```

## Functions
### Function Definition
```
func add(a, b) {
    return a + b
}
```
### First-Class Functions
```
let double = func(x) { return x * 2 }
print double(5)  # Outputs: 10
```
### Closures
```
func counter() {
    let count = 0
    return func() {
        count assign count + 1
        return count
    }
}
let c = counter()
print c()  # 1
print c()  # 2
```
### Tail-Call Optimization
```
func factorial(n, acc = 1) {
    if (n <= 1) {
        return acc
    }
    return factorial(n - 1, n * acc)
}
print factorial(1000)  # Works without stack overflow
```

## Conditional Expressions
```
let max = a if a > b else b
```

## Error Handling
The language provides good error messages and a REPL that doesn’t crash on errors.
- Example REPL session:
  ```
  > let x = 10 / 0
  ZeroDivisionError: Division by zero at line 1. Suggestion: Ensure divisor is non-zero.
  > print x
  Undefined variable 'x' at line 2. Suggestion: Define 'x' before use.
  ```

## Compilation
The language compiles to bytecode for execution, ensuring efficient runtime performance.

## Example Program
```
func fib(n) {
    if (n <= 1) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

let x = 10
print "Fibonacci of " + x + " is " + fib(x)
```

This guide provides a comprehensive introduction to the language's syntax and features. Happy coding!

