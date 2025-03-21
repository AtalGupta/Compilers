# Compilers

## Authors
- **Atal Gupta**  
- **Ajith Boddu**  
- **Karna Pardheev Sai**  

---

## 📜 Documentation

###  Syntax
Our language provides a simple yet powerful syntax to write expressive and efficient programs.

### 🧮 Data Types
Our language has two built-in data types:
- **Numbers**: Integers or floating-point values (e.g., `10`, `3.14`).
- **Booleans**: `True` and `False`.

### 🏷️ Variables
Variables are dynamically typed and can be assigned values of any type. Use `let` to declare variables:
```plaintext
let x = 10
```

###  Operators
####  Arithmetic Operators
| Operator | Description |
|----------|------------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `**` | Exponentiation |
| `/` | Division |
| `rem` | Remainder |
| `quot` | Integer division |

Example:
```plaintext
10 + 5 * 2
```

####  Comparison Operators
| Operator | Description |
|----------|------------|
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal to |
| `>=` | Greater than or equal to |
| `==` | Equal to |
| `!=` | Not equal to |

Example:
```plaintext
10 < 20
```

####  Logical Operators
| Operator | Description |
|----------|------------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

Example:
```plaintext
True and False
```

####  Assignment Operators
| Operator | Description |
|----------|------------|
| `let` | Variable declaration |
| `assign` | Variable reassignment |

Example:
```plaintext
let x = 10
x assign 20
```

###  Control Flow
#### **If Statements**
```plaintext
if (a < b) {
    x = 10
} else {
    x = 20
}
```

#### **While Loops**
```plaintext
while (x < 10) {
    x = x + 1
}
```

#### **For Loops**
```plaintext
for (i in 1 to 10) {
    print i
}
```

#### **Repeat Loops**
```plaintext
repeat {
    x = x + 1
} until (x == 10)
```

### Print Statements
```plaintext
print("Hello, world!")
```

###  Functions
Functions are defined using the `func` keyword:
```plaintext
func add(a, b) {
    return a + b
}
```

---

##  Arithmetic Expressions

Our compiler supports:
- **Addition (`+`)**
- **Subtraction (`-`)**
- **Multiplication (`*`)**
- **Exponentiation (`**`)**
- **Division (`/`)**
- **Remainder (`rem`)**
- **Integer Division (`quot`)**

### 🔢 Operator Precedence
1. **Parentheses `()`** (Highest priority)
2. **Exponentiation `**`** (Right-associative)
3. **Multiplication `*`, Division `/`, Remainder `rem`, Integer Division `quot`** (Left to right)
4. **Addition `+`, Subtraction `-`** (Left to right)

### 🚨 Error Handling
Our compiler includes robust error handling:
- **Division by zero** → Raises `ZeroDivisionError`
- **Malformed expressions** → Flags `SyntaxError`

---



### ✅ **Feel free to contribute and improve this project!** 🚀




## Developer's Guide
Test Lexer code
go to that folder and then use command
```
python -m unittest test_lexer.py

```


normal test can be done using
```
python src/evaluator.py tests/sample_test.og
```

