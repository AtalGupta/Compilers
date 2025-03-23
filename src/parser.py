# parser.py
from lexer import (Lexer, Token, LET, ASSIGN, IDENTIFIER, EQUALS, TRUE, FALSE,
                   PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, QUOT, LPAREN, RPAREN,
                   LT, LTE, GT, GTE, EQEQ, NOTEQ, AND, OR, NOT, EOF, INTEGER, FLOAT,
                   IF, ELSE, WHILE, LBRACE, RBRACE, FOR, TO, READ, PRINT,COMMA,FUNC,RETURN,STRING,LBRACKET,RBRACKET)
from ast_1 import (AST, BinOp, Number, UnaryOp, Boolean, Var, VarAssign, VarReassign,
                   Block, If, While, For, Read, Print, print_ast,FuncCall,FuncDef,Return,String,Array,ArrayAccess,ArrayAssign)

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type: str):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def block(self) -> Block:
        """Parses a block of statements within {}"""
        statements = []
        self.eat(LBRACE)
        while self.current_token.type != RBRACE and self.current_token.type != EOF:
            if self.current_token.type == RETURN:  # Handle return inside function bodies
                statements.append(self.return_statement())
            else:
                statements.append(self.statement())
        self.eat(RBRACE)
        return Block(statements)

    def statement(self) -> AST:
        """Parses a single statement: let, if, while, for, read, print, or assignment"""
        print(f"Parsing statement: {self.current_token.type,self.current_token.value }")
        if self.current_token.type == IF:
            return self.if_statement()
        elif self.current_token.type == LET:
            return self.let_statement()
        elif self.current_token.type == WHILE:
            return self.while_statement()
        elif self.current_token.type == FUNC:
            return self.function_definition()
        elif self.current_token.type == FOR:
            return self.for_statement()
        elif self.current_token.type == READ:
            self.eat(READ)
            if self.current_token.type != IDENTIFIER:
                self.error()
            target = self.current_token.value
            self.eat(IDENTIFIER)
            return Read(target)
        elif self.current_token.type == PRINT:
            self.eat(PRINT)
            expr = self.assignment()
            return Print(expr) 
        elif self.current_token.type == IDENTIFIER:
            var_name = self.current_token.value
            self.eat(IDENTIFIER)
            if self.current_token.type == LPAREN:
                return self.function_call(var_name) 
            elif self.current_token.type == LBRACKET:
                node = self.array_access(var_name)  # Parse `arr[index]`
                if self.current_token.type == ASSIGN:  # Check if it is an assignment
                    self.eat(ASSIGN)
                    value = self.assignment()
                    return ArrayAssign(node.array, node.index, value)  # Create ArrayAssign AST Node
                return node  # Just an access, not an assignment
            elif self.current_token.type == ASSIGN:
                self.eat(ASSIGN)
                expr_node = self.assignment()
                return VarReassign(var_name, expr_node)
            else:
                self.error()
        else:
            return self.assignment()
    
    def let_statement(self) -> AST:
        self.eat(LET)
        if self.current_token.type != IDENTIFIER:
            self.error()
        var_name = self.current_token.value
        self.eat(IDENTIFIER)
        self.eat(EQUALS)
        if self.current_token.type == LBRACKET:
            expr_node = self.array_literal() 
        else:
            expr_node = self.assignment()
        return VarAssign(var_name, expr_node)

    def if_statement(self) -> AST:
        self.eat(IF)
        condition = self.logical_or()
        then_branch = self.block()
        else_branch = None
        if self.current_token.type == ELSE:
            self.eat(ELSE)
            else_branch = self.block()
        return If(condition, then_branch, else_branch)

    def while_statement(self) -> AST:
        self.eat(WHILE)
        condition = self.logical_or()
        body = self.block()
        return While(condition, body)

    def for_statement(self) -> AST:
        """Parses 'for var = start to end { body }'"""
        self.eat(FOR)
        if self.current_token.type != IDENTIFIER:
            self.error()
        var_name = self.current_token.value
        self.eat(IDENTIFIER)
        self.eat(EQUALS)
        start = self.assignment()
        self.eat(TO)
        end = self.assignment()
        body = self.block()
        return For(var_name, start, end, body)
    
    def function_definition(self) -> AST:
        """Parses function definitions: func name(params) { body }"""
        self.eat(FUNC)
        
        if self.current_token.type != IDENTIFIER:
            self.error()
        func_name = self.current_token.value
        self.eat(IDENTIFIER)

        self.eat(LPAREN)
        params = []
        if self.current_token.type == IDENTIFIER:
            params.append(self.current_token.value)
            self.eat(IDENTIFIER)
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                params.append(self.current_token.value)
                self.eat(IDENTIFIER)
        self.eat(RPAREN)

        body = self.block()
        return FuncDef(func_name, params, body)

    def return_statement(self) -> AST:
        """Parses return statements"""
        self.eat(RETURN)
        return Return(self.assignment())
    
    def function_call(self, name: str) -> AST:
        """Parses function calls: name(args)"""
        self.eat(LPAREN)
        args = []
        if self.current_token.type != RPAREN:  # Ensure we allow empty argument lists
            while True:
                args.append(self.assignment())  # Correctly parse expressions as arguments
                if self.current_token.type != COMMA:
                    break
                self.eat(COMMA)
        self.eat(RPAREN)
        return FuncCall(name, args)
    
    def array_literal(self):
        elements = []
        self.eat(LBRACKET)
        
        if self.current_token.type != RBRACKET:  
            elements.append(self.assignment())
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                elements.append(self.assignment())

        self.eat(RBRACKET)
        return Array(elements)

    
    def array_access(self, var_name):
        self.eat(LBRACKET)
        index = self.assignment()
        self.eat(RBRACKET)
        return ArrayAccess(var_name, index)




    def assignment(self) -> AST:
        node = self.logical_or()
        if self.current_token.type == ASSIGN:
            if isinstance(node, ArrayAccess):  # Handle arr[index] assign value
                return ArrayAssign(node.array, node.index, self.assignment())
            elif not isinstance(node, Var):
                self.error()
            self.eat(ASSIGN)
            node = VarReassign(name=node.name, value=self.assignment())
        return node

    def logical_or(self) -> AST:
        node = self.logical_and()
        while self.current_token.type == OR:
            token = self.current_token
            self.eat(OR)
            node = BinOp(left=node, op=token.value, right=self.logical_and())
        return node

    def logical_and(self) -> AST:
        node = self.logical_not()
        while self.current_token.type == AND:
            token = self.current_token
            self.eat(AND)
            node = BinOp(left=node, op=token.value, right=self.logical_not())
        return node

    def logical_not(self) -> AST:
        if self.current_token.type == NOT:
            token = self.current_token
            self.eat(NOT)
            return UnaryOp(token.value, self.logical_not())
        return self.comparison()

    def comparison(self) -> AST:
        node = self.arithmetic()
        if self.current_token.type in (EQEQ, NOTEQ, LT, LTE, GT, GTE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token.value, right=self.arithmetic())
        return node

    def arithmetic(self) -> AST:
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token.value, right=self.term())
        return node

    def term(self) -> AST:
        node = self.power()
        while self.current_token.type in (MULTIPLY, DIVIDE, REM, QUOT):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token.value, right=self.power())
        return node

    def power(self) -> AST:
        node = self.factor()
        if self.current_token.type == EXPONENT:
            token = self.current_token
            self.eat(EXPONENT)
            node = BinOp(left=node, op=token.value, right=self.power())
        return node

    def factor(self) -> AST:
        token = self.current_token
        print(f"Parsing factor: {token.type}, value: {token.value}")
        if token.type in (PLUS, MINUS):
            self.eat(token.type)
            return UnaryOp(token.value, self.factor())
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Number(token.value)
        elif token.type == FLOAT:
            self.eat(FLOAT)
            return Number(token.value)
        elif token.type == STRING:
            string_value = token.value 
            self.eat(STRING)
            return String(string_value) 
        elif token.type == TRUE:
            self.eat(TRUE)
            return Boolean(True)
        elif token.type == FALSE:
            self.eat(FALSE)
            return Boolean(False)
        elif token.type == LBRACKET:
            return self.array_literal()
        elif token.type == IDENTIFIER:
            var_name = token.value
            self.eat(IDENTIFIER)
            if self.current_token.type == LBRACKET:  
                return self.array_access(var_name)
            elif self.current_token.type == LPAREN:  # Function call only if no brackets
                return self.function_call(var_name)

            return Var(var_name)  
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.assignment()
            self.eat(RPAREN)
            return node
        elif token.type == READ:
            self.eat(READ)
            return Read(None)  # Create a Read node without a target
        else:
            self.error()


    def parse(self) -> Block:
        statements = []
        while self.current_token.type != EOF:
            statements.append(self.statement())
        print(statements)
        return Block(statements)
