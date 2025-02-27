# ast_1.py
from dataclasses import dataclass
from typing import Union, Optional, List

@dataclass
class AST:
    """Base AST node class"""
    pass

@dataclass
class BinOp(AST):
    """Binary operation node"""
    left: AST
    op: str
    right: AST

@dataclass
class Number(AST):
    """Numeric node for both integers and floats"""
    value: Union[int, float]

@dataclass
class UnaryOp(AST):
    """Unary operation node"""
    op: str
    expr: AST

@dataclass
class Boolean(AST):
    """Boolean literal node"""
    value: bool

@dataclass
class Var(AST):
    """Variable reference node"""
    name: str

@dataclass
class VarAssign(AST):
    """Variable declaration node using 'let'"""
    name: str
    value: AST

@dataclass
class VarReassign(AST):
    """Variable reassignment node using 'assign'"""
    name: str
    value: AST

@dataclass
class Block(AST):
    """Block of statements"""
    statements: List[AST]

@dataclass
class If(AST):
    """If statement node"""
    condition: AST
    then_branch: AST
    else_branch: Optional[AST] = None

@dataclass
class While(AST):
    """While loop node"""
    condition: AST
    body: AST

@dataclass
class For(AST):
    """For loop node: for var = start to end { body }"""
    var: str          # Loop variable name
    start: AST        # Start value
    end: AST          # End value (inclusive)
    body: AST         # Block of statements

@dataclass
class Read(AST):
    """Read input into a variable"""
    target: str       # Variable to store input

@dataclass
class FuncDef(AST):
    """Function definition node"""
    name: str
    params: List[str]
    body: AST

@dataclass
class Return(AST):
    """Return statement node"""
    expr: AST


@dataclass
class Print(AST):
    """Print an expression"""
    expr: AST         # Expression to print

def print_ast(node: AST, level: int = 0) -> None:
    """Helper function to visualize AST structure"""
    indent = '  ' * level
    if isinstance(node, BinOp):
        print(f"{indent}BinOp({node.op})")
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)
    elif isinstance(node, UnaryOp):
        print(f"{indent}UnaryOp({node.op})")
        print_ast(node.expr, level + 1)
    elif isinstance(node, Number):
        print(f"{indent}Number({node.value})")
    elif isinstance(node, Boolean):
        print(f"{indent}Boolean({node.value})")
    elif isinstance(node, Var):
        print(f"{indent}Var({node.name})")
    elif isinstance(node, VarAssign):
        print(f"{indent}VarAssign({node.name})")
        print_ast(node.value, level + 1)
    elif isinstance(node, VarReassign):
        print(f"{indent}VarReassign({node.name})")
        print_ast(node.value, level + 1)
    elif isinstance(node, Block):
        print(f"{indent}Block")
        for stmt in node.statements:
            print_ast(stmt, level + 1)
    elif isinstance(node, If):
        print(f"{indent}If")
        print(f"{indent}  Condition:")
        print_ast(node.condition, level + 2)
        print(f"{indent}  Then:")
        print_ast(node.then_branch, level + 2)
        if node.else_branch:
            print(f"{indent}  Else:")
            print_ast(node.else_branch, level + 2)
    elif isinstance(node, While):
        print(f"{indent}While")
        print(f"{indent}  Condition:")
        print_ast(node.condition, level + 2)
        print(f"{indent}  Body:")
        print_ast(node.body, level + 2)
    elif isinstance(node, For):
        print(f"{indent}For({node.var})")
        print(f"{indent}  Start:")
        print_ast(node.start, level + 2)
        print(f"{indent}  End:")
        print_ast(node.end, level + 2)
        print(f"{indent}  Body:")
        print_ast(node.body, level + 2)
    elif isinstance(node, Read):
        print(f"{indent}Read({node.target})")
    elif isinstance(node, Print):
        print(f"{indent}Print")
        print_ast(node.expr, level + 1)
    elif isinstance(node, FuncDef):
        print(f"{indent}FuncDef({node.name})")
        print(f"{indent}  Params: {node.params}")
        print(f"{indent}  Body:")
        print_ast(node.body, level + 1)
    elif isinstance(node, Return):
        print(f"{indent}Return")
        print_ast(node.expr, level + 1)
