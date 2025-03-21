from lexer import Lexer
from parser import Parser
from ast_1 import (
    BinOp, Number, UnaryOp, Boolean, Var, VarAssign, VarReassign, Block,
    If, While, For, Read, Print, FuncDef, FuncCall, Return,String
)
import traceback
import sys

class Environment:
    """Symbol table supporting static scoping."""
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.functions = {}

    def get(self, name):
        """Retrieve variable or function from the correct scope."""
        if name in self.variables:
            return self.variables[name]
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined name: {name}")

    def set(self, name, value):
        """Set a variable in the current scope."""
        self.variables[name] = value

    def define_func(self, name, func_def):
        """Store function definition in the current scope."""
        self.functions[name] = func_def

class Interpreter:
    def __init__(self):
        self.global_env = Environment()  # Global scope

    def visit_BinOp(self, node: BinOp, env):
        left = self.visit(node.left, env)
        right = self.visit(node.right, env)
        if node.op == '+': return left + right
        if node.op == '-': return left - right
        if node.op == '*': return left * right
        if node.op == '/':
            if right == 0: raise ZeroDivisionError("Division by zero")
            return left / right
        if node.op == '**': return left ** right
        if node.op == 'rem':
            if right == 0: raise ZeroDivisionError("Division by zero")
            return left % right
        if node.op == 'quot':
            if right == 0: raise ZeroDivisionError("Division by zero")
            return left // right
        if node.op in {'<', '>', '<=', '>=', '==', '!='}:
            return eval(f"{left} {node.op} {right}")
        if node.op == 'and': return left and right
        if node.op == 'or': return left or right
        raise Exception(f"Unknown binary operator {node.op}")

    def visit_Number(self, node: Number, env):
        return node.value
    
    def visit_String(self, node: String, env):
        return node.value

    def visit_UnaryOp(self, node: UnaryOp, env):
        value = self.visit(node.expr, env)
        if node.op == '-': return -value
        if node.op == 'not': return not value
        raise Exception(f"Unknown unary operator {node.op}")

    def visit_Boolean(self, node: Boolean, env):
        return node.value

    def visit_Var(self, node: Var, env):
        return env.get(node.name)

    def visit_VarAssign(self, node: VarAssign, env):
        value = self.visit(node.value, env)
        env.set(node.name, value)
        return value

    def visit_VarReassign(self, node: VarReassign, env):
        if node.name not in env.variables:
            raise Exception(f"Variable '{node.name}' is not declared.")
        env.set(node.name, self.visit(node.value, env))
        return env.get(node.name)

    def visit_Block(self, node: Block, env):
        result = None
        for stmt in node.statements:
            result = self.visit(stmt, env)
            if isinstance(result, Return):  # Return encountered
                return result.expr
        return result

    def visit_If(self, node: If, env):
        if self.visit(node.condition, env):
            return self.visit(node.then_branch, env)
        elif node.else_branch:
            return self.visit(node.else_branch, env)
        return None

    def visit_While(self, node: While, env):
        result = None
        while self.visit(node.condition, env):
            result = self.visit(node.body, env)
        return result

    def visit_For(self, node: For, env):
        start = self.visit(node.start, env)
        end = self.visit(node.end, env)
        loop_env = Environment(parent=env)  # New scope for loop
        loop_env.set(node.var, start)
        result = None
        while loop_env.get(node.var) <= end:
            result = self.visit(node.body, loop_env)
            loop_env.set(node.var, loop_env.get(node.var) + 1)
        return result

    def visit_Read(self, node: Read, env):
        prompt = f"Enter value for {node.target}:" if node.target else "Enter value:"
        value = int(input(prompt + " "))
        return value

    def visit_Print(self, node: Print, env):
        value = self.visit(node.expr, env)
        print(value)
        return value

    def visit_FuncDef(self, node: FuncDef, env):
        """Stores function definition in the environment."""
        env.define_func(node.name, node)

    def visit_FuncCall(self, node: FuncCall, env):
        """Executes function call with static scoping."""
        func_def = env.get(node.name)
        if not isinstance(func_def, FuncDef):
            raise Exception(f"{node.name} is not a function")

        if len(node.args) != len(func_def.params):
            raise Exception(f"Expected {len(func_def.params)} arguments, got {len(node.args)}")

        # Create new local scope for function execution
        func_env = Environment(parent=env)
        for param, arg in zip(func_def.params, node.args):
            func_env.set(param, self.visit(arg, env))

        return self.visit(func_def.body, func_env)

    def visit_Return(self, node: Return, env):
        """Handles return statements by wrapping the return value."""
        return Return(self.visit(node.expr, env))

    def visit(self, node, env):
        """Dispatch method to visit the correct node type."""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, None)
        if method is None:
            raise Exception(f"No visitor found for {type(node).__name__}")
        return method(node, env)

    def interpret(self, tree):
        """Entry point to interpret the AST."""
        return self.visit(tree, self.global_env)

def run_file(filename: str):
    interpreter = Interpreter()
    try:
        with open(filename, 'r') as file:
            program = file.read()
        lexer = Lexer(program)
        parser = Parser(lexer)
        tree = parser.parse()
        result = interpreter.interpret(tree)
        if result is not None:
            print(f"Final result: {result}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        traceback.print_exc()
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
