# evaluator.py
from lexer import Lexer
from parser import Parser
from ast_1 import (BinOp, Number, UnaryOp, Boolean, Var, VarAssign, VarReassign, Block, If, While, For, Read, Print)
import traceback
import sys

class Interpreter:
    def __init__(self):
        self.env = {}

    def visit_BinOp(self, node: BinOp):
        if node.op == '+':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == '-':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == '*':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == '/':
            right = self.visit(node.right)
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return self.visit(node.left) / right
        elif node.op == '**':
            return self.visit(node.left) ** self.visit(node.right)
        elif node.op == 'rem':
            right = self.visit(node.right)
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return self.visit(node.left) % right
        elif node.op == 'quot':
            right = self.visit(node.right)
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return self.visit(node.left) // right
        elif node.op == '<':
            return self.visit(node.left) < self.visit(node.right)
        elif node.op == '>':
            return self.visit(node.left) > self.visit(node.right)
        elif node.op == '<=':
            return self.visit(node.left) <= self.visit(node.right)
        elif node.op == '>=':
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op == '==':
            return self.visit(node.left) == self.visit(node.right)
        elif node.op == '!=':
            return self.visit(node.left) != self.visit(node.right)
        elif node.op == 'and':
            return self.visit(node.left) and self.visit(node.right)
        elif node.op == 'or':
            return self.visit(node.left) or self.visit(node.right)
        else:
            raise Exception(f"Unknown binary operator {node.op}")

    def visit_Number(self, node: Number):
        return node.value

    def visit_UnaryOp(self, node: UnaryOp):
        if node.op == '+':
            return +self.visit(node.expr)
        elif node.op == '-':
            return -self.visit(node.expr)
        elif node.op == 'not':
            return not self.visit(node.expr)
        else:
            raise Exception(f"Unknown unary operator {node.op}")

    def visit_Boolean(self, node: Boolean):
        return node.value

    def visit_Var(self, node: Var):
        if node.name in self.env:
            return self.env[node.name]
        else:
            raise Exception(f"Undefined variable '{node.name}'")

    def visit_VarAssign(self, node: VarAssign):
        value = self.visit(node.value)
        self.env[node.name] = value
        return value

    def visit_VarReassign(self, node: VarReassign):
        if node.name not in self.env:
            raise Exception(f"Variable '{node.name}' is not declared.")
        self.env[node.name] = self.visit(node.value)
        return self.env[node.name]

    def visit_Block(self, node: Block):
        result = None
        for stmt in node.statements:
            result = self.visit(stmt)
        return result

    def visit_If(self, node: If):
        if self.visit(node.condition):
            return self.visit(node.then_branch)
        elif node.else_branch:
            return self.visit(node.else_branch)
        return None

    def visit_While(self, node: While):
        result = None
        while self.visit(node.condition):
            result = self.visit(node.body)
        return result

    def visit_For(self, node: For):
        start = self.visit(node.start)
        end = self.visit(node.end)
        result = None
        self.env[node.var] = start
        while self.env[node.var] <= end:
            result = self.visit(node.body)
            self.env[node.var] += 1
        return result

    def visit_Read(self, node: Read):
        # If a target is provided, use it in the prompt; otherwise, use a generic prompt.
        prompt = f"Enter value for {node.target}:" if node.target else "Enter value:"
        value = int(input(prompt + " "))
        # If using read as an expression in an assignment, just return the value.
        return value

    def visit_Print(self, node: Print):
        value = self.visit(node.expr)
        print(value)
        return value

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, None)
        if visitor is None:
            raise Exception(f"No visitor found for {type(node).__name__}")
        return visitor(node)

    def interpret(self, tree):
        return self.visit(tree)

class Calculator:
    def __init__(self):
        self.interpreter = Interpreter()

    def calculate(self, expression: str):
        try:
            lexer = Lexer(expression)
            parser = Parser(lexer)
            tree = parser.parse()
            result = self.interpreter.interpret(tree)
            return result
        except Exception as e:
            traceback.print_exc()
            raise

def run_file(filename: str):
    calculator = Calculator()
    try:
        with open(filename, 'r') as file:
            program = file.read()
        result = calculator.calculate(program)
        if result is not None:
            print(f"Final result: {result}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluator.py <filename.myprog>")
        sys.exit(1)
    filename = sys.argv[1]
    if not filename.endswith('.og'):
        print("Error: File must have a .og extension.")
        sys.exit(1)
    run_file(filename)