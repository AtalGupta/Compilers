import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

import unittest
from lexer import *
from parser import *
from ast_1 import *
test_cases = [
        ("let x = 5;", "Variable Declaration"),
        ("x = x + 1", "Variable Reassignment"),
        ("if (x > 3) { x = x - 1} else { x = x + 1 }", "If-Else Statement"),
        ("while (x < 10) { x = x + 1 }", "While Loop"),
        ("for i = 1 to 5 { print i }", "For Loop"),
        ("func add(a, b) { return a + b }", "Function Definition"),
        ("add(3, 4)", "Function Call"),
        ("return 42", "Return Statement"),
    ]
def test_parser():
    for code, description in test_cases:
        print(f"\n--- Testing: {description} ---")
        lexer = Lexer(code)

        print("Tokens:")
        while True:
            token = lexer.get_next_token()
            print(token)
            if token.type == EOF:
                break

        parser = Parser(lexer)
        ast = parser.parse()
        print_ast(ast)
if __name__== '__main__':
    test_parser()
