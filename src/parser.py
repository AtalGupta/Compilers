from lexer import (Lexer, Token, LET, IF, WHILE, FOR, FUNC, RETURN, PRINT, ELSE, ASSIGN, EQUALS,
                  PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, QUOT, LPAREN, RPAREN, LBRACE, RBRACE,
                  LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT, COMMA, LBRACKET, RBRACKET, COLON,
                  IDENTIFIER, INTEGER, FLOAT, STRING, TRUE, FALSE, EOF, TO, IN, REPEAT, UNTIL, MATCH, ARROW, QUESTION_MARK, STEP)
from ast_1 import (AST, BinOp, UnaryOp, Integer, Float, String, Boolean, Var, VarAssign, VarReassign, Block,
                  If, While, For, FuncDef, Return, FuncCall, Print, Array, Dict, ConditionalExpr,
                  RepeatUntil, Match, MatchCase, AstPrinter, Lambda,ArrayAccess,ArrayAssign)

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = self._tokenize()
        self.pos = 0

    def _tokenize(self):
        tokens = []
        while True:
            token = self.lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        return tokens

    def peek(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]

    def advance(self):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return self.tokens[-1]  # EOF

    def previous(self):
        if self.pos > 0:
            return self.tokens[self.pos - 1]
        raise ParseError("No previous token available.")
        
    def check(self, token_type):
        """Check if the current token matches the given type without advancing."""
        return self.peek().type == token_type
        
    def is_at_end(self):
        """Check if we've reached the end of the token stream."""
        return self.peek().type == EOF

    def match(self, *types):
        if self.peek().type in types:
            return self.advance()
        return None

    def consume(self, token_type: str, message: str):
        if self.peek().type == token_type:
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        error_msg = f"[line {token.line}] Error at '{token.value}': {message}"
        print(error_msg)
        return ParseError(error_msg)

    def synchronize(self):
        self.advance()
        while self.peek().type != EOF:
            if self.previous().type == RBRACE or self.peek().type in (
                LET, IF, WHILE, FOR, FUNC, RETURN, PRINT, REPEAT, MATCH
            ):
                return
            self.advance()

    def parse(self) -> Block:
        statements = []
        while self.peek().type != EOF:
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
            except ParseError:
                self.synchronize()
        return Block(statements)

    def statement(self) -> AST:
        if self.peek().type == LET:
            return self.let_statement()
        if self.peek().type == IF:
            return self.if_statement()
        if self.peek().type == WHILE:
            return self.while_statement()
        if self.peek().type == FOR:
            return self.for_statement()
        if self.peek().type == REPEAT:
            return self.repeat_statement()
        if self.peek().type == MATCH:
            return self.match_statement()
        if self.peek().type == FUNC:
            return self.function_definition()
        if self.peek().type == RETURN:
            return self.return_statement()
        if self.peek().type == PRINT:
            return self.print_statement()
        if self.peek().type == IDENTIFIER:
            var_name = self.peek().value
            token = self.consume(IDENTIFIER, "Expected an identifier")

            if self.peek().type == LBRACKET:
                node = self.array_access(var_name)  # Now node is `ArrayAccess`
                
                if self.peek().type == ASSIGN:  # Check for assignment
                    self.consume(ASSIGN, "Expected '=' in array assignment")
                    value = self.assignment()
                    return ArrayAssign(node.array, node.index, value) 
                
                return node  

            elif self.peek().type == ASSIGN: 
                self.consume(ASSIGN, "Expected '=' in variable assignment")
                value = self.assignment()
                return VarReassign(var_name, value, token)

            return Var(var_name, token) 


        return self.expression_statement()

    def let_statement(self) -> VarAssign:
        self.advance()  # Consume 'let'
        name_token = self.consume(IDENTIFIER, "Expected variable name after 'let'")
        self.consume(EQUALS, "Expected '=' after variable name")
        value = self.expression()  # Use expression for flexibility
        return VarAssign(name_token.value, value, name_token)

    def if_statement(self) -> If:
        self.advance()  # Consume 'if'
        self.consume(LPAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self.consume(RPAREN, "Expected ')' after condition")
        then_branch = self.block()
        else_branch = None
        if self.peek().type == ELSE:
            self.advance()  # Consume 'else'
            else_branch = self.block()
        return If(condition, then_branch, else_branch)

    def while_statement(self) -> While:
        self.advance()  # Consume 'while'
        self.consume(LPAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self.consume(RPAREN, "Expected ')' after condition")
        body = self.block()
        return While(condition, body)

    def for_statement(self) -> For:
        self.advance()  # Consume 'for'
        self.consume(LPAREN, "Expected '(' after 'for'")
        
        # Parse the variable declaration
        self.consume(LET, "Expected 'let' after 'for ('")
        name_token = self.consume(IDENTIFIER, "Expected variable name")
        self.consume(EQUALS, "Expected '=' after variable name")
        start = self.expression()
        
        # Parse the 'to' keyword and end expression
        self.consume(TO, "Expected 'to' after start expression")
        end = self.expression()
        
        # Handle optional step parameter
        step = None
        if self.match(STEP):
            step = self.expression()
        
        # Consume the closing parenthesis
        self.consume(RPAREN, "Expected ')' after for loop header")
        
        # Parse the body
        body = self.block()
        
        return For(name_token.value, start, end, body, step)

    def repeat_statement(self) -> RepeatUntil:
        self.advance()  # Consume 'repeat'
        body = self.block()
        self.consume(UNTIL, "Expected 'until' after repeat block")
        self.consume(LPAREN, "Expected '(' after 'until'")
        condition = self.expression()
        self.consume(RPAREN, "Expected ')' after condition")
        return RepeatUntil(body, condition)

    def match_statement(self) -> Match:
        self.advance()  # Consume 'match'
        expr = self.expression()
        self.consume(LBRACE, "Expected '{' after match expression")
        cases = []
        while self.peek().type != RBRACE:
            pattern = self.pattern()
            self.consume(ARROW, "Expected '->' after pattern")
            body = self.statement()  # Parse as statement instead of expression
            cases.append(MatchCase(pattern, body))
            if self.peek().type != RBRACE:
                self.consume(COMMA, "Expected ',' between match cases or '}' to end")
        self.consume(RBRACE, "Expected '}' after match cases")
        return Match(expr, cases)

    def function_definition(self) -> FuncDef:
        self.advance()  # Consume 'func'
        name_token = self.consume(IDENTIFIER, "Expected function name after 'func'")
        self.consume(LPAREN, "Expected '(' after function name")
        params = []
        if self.peek().type != RPAREN:
            params.append(self.consume(IDENTIFIER, "Expected parameter name").value)
            while self.match(COMMA):
                params.append(self.consume(IDENTIFIER, "Expected parameter name after ','").value)
        self.consume(RPAREN, "Expected ')' after parameters")
        body = self.block()
        return FuncDef(name_token.value, params, body, token=name_token)  # Pass token with explicit name

    def return_statement(self) -> Return:
        token = self.advance()  # Consume 'return'
        expr = self.expression()
        return Return(expr, token=token)  # Pass the return token for error reporting

    def print_statement(self) -> Print:
        self.advance()  # Consume 'print'
        expr = self.expression()
        return Print(expr)
    
    def array_literal(self):
        """Parse array literals like [1, 2, 3]"""
        elements = []
        self.consume(LBRACKET, "Expected '[' to start array")

        if self.peek().type != RBRACKET:  # If not an empty array
            elements.append(self.assignment())
            while self.match(COMMA):
                elements.append(self.assignment())

        self.consume(RBRACKET, "Expected ']' after array elements")
        return Array(elements)
    
    def array_access(self, var_name):
        """Parse array indexing like arr[0]"""
        self.consume(LBRACKET, "Expected '[' after array name")
        index = self.assignment()
        self.consume(RBRACKET, "Expected ']' after array index")
        return ArrayAccess(var_name, index) 

    def block(self) -> Block:
        self.consume(LBRACE, "Expected '{' to start block")
        statements = []
        while self.peek().type not in (RBRACE, EOF):
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        self.consume(RBRACE, "Expected '}' to end block")
        return Block(statements)

    def pattern(self) -> AST:
        if self.match(INTEGER):
            return Integer(self.previous().value)
        if self.match(FLOAT):
            return Float(self.previous().value)
        if self.match(STRING):
            return String(self.previous().value)
        if self.match(TRUE):
            return Boolean(True)
        if self.match(FALSE):
            return Boolean(False)
        if self.match(LBRACKET):
            elements = []
            if self.peek().type != RBRACKET:
                elements.append(self.expression())
                while self.match(COMMA):
                    elements.append(self.expression())
            self.consume(RBRACKET, "Expected ']' after array elements")
            return Array(elements)
        raise self.error(self.peek(), "Expected pattern (integer, float, string, boolean, or array)")
        
    def lambda_expression(self) -> Lambda:
        """Parse an anonymous function: func(param1, param2, ...) { body }"""
        token = self.previous()  # The 'func' token
        
        self.consume(LPAREN, "Expected '(' after 'func'")
        parameters = []
        
        # Parse parameters
        if not self.check(RPAREN):
            parameters.append(self.consume(IDENTIFIER, "Expected parameter name").value)
            while self.match(COMMA):
                parameters.append(self.consume(IDENTIFIER, "Expected parameter name").value)
        
        self.consume(RPAREN, "Expected ')' after parameters")
        
        # Parse body (a block)
        body = self.block()
        
        return Lambda(parameters, body, token)

    def assignment(self) -> AST:
        expr = self.conditional()
        if self.match(ASSIGN):
            assign_token = self.previous()
            if isinstance(expr, Var):
                value = self.assignment()  # Recurse for chained assignments (e.g., x = y = 5)
                return VarReassign(expr.name, value, assign_token)
            raise self.error(assign_token, "Invalid assignment target")
        return expr

    def expression_statement(self) -> AST:
        expr = self.assignment()
        return expr
    
    def conditional(self) -> AST:
        expr = self.logic_or()
        if self.match(QUESTION_MARK):
            then_expr = self.expression()
            self.consume(COLON, "Expected ':' in conditional expression")
            else_expr = self.conditional()
            return ConditionalExpr(expr, then_expr, else_expr)
        return expr

    def logic_or(self) -> AST:
        expr = self.logic_and()
        while self.match(OR):
            op = self.previous()
            right = self.logic_and()
            expr = BinOp(expr, op, right)
        return expr

    def logic_and(self) -> AST:
        expr = self.equality()
        while self.match(AND):
            op = self.previous()
            right = self.equality()
            expr = BinOp(expr, op, right)
        return expr

    def equality(self) -> AST:
        expr = self.comparison()
        while self.match(EQEQ, NOTEQ):
            op = self.previous()
            right = self.comparison()
            expr = BinOp(expr, op, right)
        return expr

    def comparison(self) -> AST:
        expr = self.term()
        while self.match(LT, GT, LTE, GTE):
            op = self.previous()
            right = self.term()
            expr = BinOp(expr, op, right)
        return expr

    def term(self) -> AST:
        expr = self.factor()
        while self.match(PLUS, MINUS):
            op = self.previous()
            right = self.factor()
            expr = BinOp(expr, op, right)
        return expr

    def factor(self) -> AST:
        expr = self.power()
        while self.match(MULTIPLY, DIVIDE, REM, QUOT):
            op = self.previous()
            right = self.power()
            expr = BinOp(expr, op, right)
        return expr

    def power(self) -> AST:
        expr = self.unary()
        while self.match(EXPONENT):
            op = self.previous()
            right = self.unary()
            expr = BinOp(expr, op, right)
        return expr

    def unary(self) -> AST:
        if self.match(MINUS, NOT):
            op = self.previous()
            right = self.unary()
            return UnaryOp(op, right)
        return self.call()

    def call(self) -> AST:
        expr = self.primary()
        while self.match(LPAREN):
            args = []
            if self.peek().type != RPAREN:
                args.append(self.expression())
                while self.match(COMMA):
                    args.append(self.expression())
            token = self.consume(RPAREN, "Expected ')' after arguments")
            expr = FuncCall(expr, args, token=token)  # Pass token for error reporting
        return expr

    def primary(self) -> AST:
        if self.match(INTEGER):
            return Integer(self.previous().value)
        if self.match(FLOAT):
            return Float(self.previous().value)
        if self.match(STRING):
            return String(self.previous().value)
        if self.match(TRUE):
            return Boolean(True)
        if self.match(FALSE):
            return Boolean(False)
        if self.match(FUNC):
            return self.lambda_expression()
        if self.match(IDENTIFIER):
            ident_token = self.previous()
            expr = Var(ident_token.value, ident_token)

            while self.match(LBRACKET):  # Handle array indexing
                index = self.expression()
                self.consume(RBRACKET, "Expected ']' after index")
                expr = ArrayAccess(expr, index)
            return expr
        if self.match(LPAREN):
            expr = self.expression()
            self.consume(RPAREN, "Expected ')' after expression")
            return expr
        if self.match(LBRACKET):
            elements = []
            if self.peek().type != RBRACKET:
                elements.append(self.expression())
                while self.match(COMMA):
                    elements.append(self.expression())
            self.consume(RBRACKET, "Expected ']' after array elements")
            return Array(elements)
        if self.match(LBRACE):
            pairs = []
            if self.peek().type != RBRACE:
                key = self.expression()
                self.consume(COLON, "Expected ':' after dict key")
                value = self.expression()
                pairs.append((key, value))
                while self.match(COMMA):
                    key = self.expression()
                    self.consume(COLON, "Expected ':' after dict key")
                    value = self.expression()
                    pairs.append((key, value))
            self.consume(RBRACE, "Expected '}' after dict pairs")
            return Dict(pairs)
        raise self.error(self.peek(), "Expected expression")

    def expression(self) -> AST:
        return self.assignment()

def parse_code(code: str) -> Block:
    lexer = Lexer(code)
    parser = Parser(lexer)
    ast = parser.parse()
    printer = AstPrinter()
    print(printer.print(ast))
    return ast

if __name__ == "__main__":
    code = """
    let x = 5
    let y = 10
    if (x > 0) {
        print x
    }
    else{
        print y
    }
    """
    parse_code(code)
