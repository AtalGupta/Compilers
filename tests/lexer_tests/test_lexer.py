import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

import unittest
from lexer import *

class TestLexer(unittest.TestCase):
    def test_numbers(self):
        lexer = Lexer("10 3.14")
        self.assertEqual(lexer.get_next_token(), Token(INTEGER, 10))
        self.assertEqual(lexer.get_next_token(), Token(FLOAT, 3.14))
        self.assertEqual(lexer.get_next_token(), Token(EOF, None))

    def test_booleans(self):
        lexer = Lexer("True False")
        self.assertEqual(lexer.get_next_token(), Token(TRUE, True))
        self.assertEqual(lexer.get_next_token(), Token(FALSE, False))
        self.assertEqual(lexer.get_next_token(), Token(EOF, None))
    
    def test_variables(self):
        lexer = Lexer("let x = 10 \n x assign 20")
        self.assertEqual(lexer.get_next_token(), Token(LET, "let"))
        self.assertEqual(lexer.get_next_token(), Token(IDENTIFIER, "x"))
        self.assertEqual(lexer.get_next_token(), Token(EQUALS, "="))
        self.assertEqual(lexer.get_next_token(), Token(INTEGER, 10))
        self.assertEqual(lexer.get_next_token(), Token(IDENTIFIER, "x"))
        self.assertEqual(lexer.get_next_token(), Token(ASSIGN, "assign"))
        self.assertEqual(lexer.get_next_token(), Token(INTEGER, 20))
        self.assertEqual(lexer.get_next_token(), Token(EOF, None))

    def test_arithmetic_operators(self):
        lexer = Lexer("10 + 5 * 2 - 3 / 1 rem 2 quot 4 ** 3")
        expected_tokens = [
            Token(INTEGER, 10), Token(PLUS, "+"), Token(INTEGER, 5), Token(MULTIPLY, "*"), Token(INTEGER, 2),
            Token(MINUS, "-"), Token(INTEGER, 3), Token(DIVIDE, "/"), Token(INTEGER, 1), Token(REM, "rem"),
            Token(INTEGER, 2), Token(QUOT, "quot"), Token(INTEGER, 4), Token(EXPONENT, "**"), Token(INTEGER, 3),
            Token(EOF, None)
        ]
        for expected_token in expected_tokens:
            self.assertEqual(lexer.get_next_token(), expected_token)
    
    def test_comparison_operators(self):
        lexer = Lexer("10 < 20 >= 15 == 5 != 3")
        expected_tokens = [
            Token(INTEGER, 10), Token(LT, "<"), Token(INTEGER, 20), Token(GTE, ">="), Token(INTEGER, 15),
            Token(EQEQ, "=="), Token(INTEGER, 5), Token(NOTEQ, "!="), Token(INTEGER, 3), Token(EOF, None)
        ]
        for expected_token in expected_tokens:
            self.assertEqual(lexer.get_next_token(), expected_token)

    def test_logical_operators(self):
        lexer = Lexer("True and False or not True")
        expected_tokens = [
            Token(TRUE, True), Token(AND, "and"), Token(FALSE, False), Token(OR, "or"), Token(NOT, "not"), Token(TRUE, True), Token(EOF, None)
        ]
        for expected_token in expected_tokens:
            self.assertEqual(lexer.get_next_token(), expected_token)

    def test_control_flow(self):
        lexer = Lexer("if (x < y) { let z = 10 } else { z assign 20 }")
        expected_tokens = [
            Token(IF, "if"), Token(LPAREN, "("), Token(IDENTIFIER, "x"), Token(LT, "<"), Token(IDENTIFIER, "y"), Token(RPAREN, ")"),
            Token(LBRACE, "{"), Token(LET, "let"), Token(IDENTIFIER, "z"), Token(EQUALS, "="), Token(INTEGER, 10), Token(RBRACE, "}"),
            Token(ELSE, "else"), Token(LBRACE, "{"), Token(IDENTIFIER, "z"), Token(ASSIGN, "assign"), Token(INTEGER, 20), Token(RBRACE, "}"),
            Token(EOF, None)
        ]
        for expected_token in expected_tokens:
            self.assertEqual(lexer.get_next_token(), expected_token)

    def test_functions(self):
        lexer = Lexer("func add(a, b) { return a + b }")
        expected_tokens = [
            Token(FUNC, "func"), Token(IDENTIFIER, "add"), Token(LPAREN, "("), Token(IDENTIFIER, "a"), Token(COMMA, ","),
            Token(IDENTIFIER, "b"), Token(RPAREN, ")"), Token(LBRACE, "{"), Token(RETURN, "return"), Token(IDENTIFIER, "a"),
            Token(PLUS, "+"), Token(IDENTIFIER, "b"), Token(RBRACE, "}"), Token(EOF, None)
        ]
        for expected_token in expected_tokens:
            self.assertEqual(lexer.get_next_token(), expected_token)

if __name__ == "__main__":
    unittest.main()
