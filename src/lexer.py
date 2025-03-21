# lexer.py
from dataclasses import dataclass
from typing import Optional

# Existing token types...
INTEGER    = 'INTEGER'
FLOAT      = 'FLOAT'
PLUS       = 'PLUS'
MINUS      = 'MINUS'
MULTIPLY   = 'MULTIPLY'
DIVIDE     = 'DIVIDE'
EXPONENT   = 'EXPONENT'
REM        = 'REM'
QUOT       = 'QUOT'
LPAREN     = 'LPAREN'
RPAREN     = 'RPAREN'
EQUALS     = 'EQUALS'
LET        = 'LET'
ASSIGN     = 'ASSIGN'
IDENTIFIER = 'IDENTIFIER'
TRUE       = 'TRUE'
FALSE      = 'FALSE'
LT         = 'LT'
GT         = 'GT'
LTE        = 'LTE'
GTE        = 'GTE'
EQEQ       = 'EQEQ'
NOTEQ      = 'NOTEQ'
AND        = 'AND'
OR         = 'OR'
NOT        = 'NOT'
EOF        = 'EOF'
IF         = 'IF'
ELSE       = 'ELSE'
WHILE      = 'WHILE'
LBRACE     = 'LBRACE'
RBRACE     = 'RBRACE'
COMMA      = 'COMMA'

# New tokens for for loop
FOR        = 'FOR'
TO         = 'TO'
READ       = 'READ'
PRINT      = 'PRINT'
FUNC       = 'FUNC'
STRING     = 'STRING'
RETURN     = 'RETURN'


@dataclass
class Token:
    type: str
    value: Optional[any]

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char and self.current_char != '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            self.advance()  # Skip '*'
            self.advance()  # Skip '/'
            while self.current_char and not (self.current_char == '*' and self.peek() == '/'):
                self.advance()
            self.advance()
            self.advance()
    
    def string(self):
        result = ''
        self.advance()
        while self.current_char and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()
        return Token(STRING, result)
    


    def number(self):
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token(FLOAT, float(result))
        return Token(INTEGER, int(result))

    def identifier(self):
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        if result == 'let':
            return Token(LET, result)
        elif result == 'assign':
            return Token(ASSIGN, result)
        elif result == 'True':
            return Token(TRUE, True)
        elif result == 'False':
            return Token(FALSE, False)
        elif result == 'rem':
            return Token(REM, result)
        elif result == 'quot':
            return Token(QUOT, result)
        elif result == 'and':
            return Token(AND, result)
        elif result == 'or':
            return Token(OR, result)
        elif result == 'not':
            return Token(NOT, result)
        elif result == 'if':
            return Token(IF, result)
        elif result == 'else':
            return Token(ELSE, result)
        elif result == 'while':
            return Token(WHILE, result)
        elif result == 'for':
            return Token(FOR, result)
        elif result == 'to':
            return Token(TO, result)
        elif result == 'read':
            return Token(READ, result)
        elif result == 'print':
            return Token(PRINT, result)
        elif result == 'func':
            return Token(FUNC, result)
        elif result == 'return':
            return Token(RETURN, result)
        else:
            return Token(IDENTIFIER, result)

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return self.number()
            if self.current_char.isalpha():
                return self.identifier()
            if self.current_char == '/' and self.peek() in ['/','*']:
                self.skip_comment()
                continue
            if self.current_char == '"':
                return self.string()
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            if self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    return Token(EXPONENT, '**')
                return Token(MULTIPLY, '*')
            if self.current_char == '/':
                self.advance()
                return Token(DIVIDE, '/')
            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            if self.current_char == '{':
                self.advance()
                return Token(LBRACE, '{')
            if self.current_char == '}':
                self.advance()
                return Token(RBRACE, '}')
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LTE, '<=')
                return Token(LT, '<')
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(GTE, '>=')
                return Token(GT, '>')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(EQEQ, '==')
                return Token(EQUALS, '=')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(NOTEQ, '!=')
                self.error()
            self.error()
        return Token(EOF, None)