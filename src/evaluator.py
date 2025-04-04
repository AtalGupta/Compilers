from src.lexer import Lexer, Token, PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT
from src.parser import Parser
from src.ast_1 import (
    AST, BinOp, UnaryOp, Integer, Float, String, Boolean, Var, VarAssign, VarReassign, Block,
    If, While, For, RepeatUntil, Match, MatchCase, FuncDef, FuncCall, Return, Lambda,
    Array, Dict, ConditionalExpr, Print, ArrayAssign, ArrayAccess
)
import sys
import traceback
import re
from typing import Any, Dict, List, Optional
sys.setrecursionlimit(3000)

class FluxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = f"[line {token.line}] Error at '{token.value}': {message}"
        super().__init__(self.message)

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}

    def define(self, name: str, value: Any):
        self.variables[name] = value

    def get(self, name: str, token: Token) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name, token)
        raise FluxRuntimeError(token, f"Undefined variable '{name}'")

    def assign(self, name: str, value: Any, token: Token):
        if name in self.variables:
            self.variables[name] = value
            return value
        if self.parent:
            return self.parent.assign(name, value, token)
        raise FluxRuntimeError(token, f"Cannot reassign undefined variable '{name}'")

    def ancestor(self, distance: int) -> 'Environment':
        env = self
        for _ in range(distance):
            if env.parent is None:
                return env
            env = env.parent
        return env

    def get_at(self, distance: int, name: str) -> Any:
        return self.ancestor(distance).variables.get(name)

    def assign_at(self, distance: int, name: str, value: Any) -> Any:
        self.ancestor(distance).variables[name] = value
        return value

class BuiltinFunction:
    """Wrapper class for built-in functions"""
    def __init__(self, func, name):
        self.func = func
        self.name = name
        
    def __str__(self):
        return f"<built-in function {self.name}>"
    
    def call(self, evaluator, arguments, token):
        # Remove the evaluator parameter since it's not needed in the builtin_len method
        return self.func(arguments, token)  # Only pass arguments and token

class TailCall(Exception):
    """Exception used for tail call optimization"""
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

class Return(Exception):
    def __init__(self, value: Any):
        self.value = value
        super().__init__()

class Function:
    def __init__(self, declaration, closure: Environment, is_anonymous: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_anonymous = is_anonymous
        self.name = '<anonymous>' if is_anonymous else declaration.name
        self.params = declaration.params

    def __str__(self):
        params_str = ", ".join(self.params)
        if self.is_anonymous:
            return f"<anonymous function({params_str})>"
        return f"<function {self.name}({params_str})>"

    def call(self, evaluator: 'Evaluator', arguments: List[Any], token: Token) -> Any:
        if isinstance(self, BuiltinFunction):  # Handle built-in functions
            return self.call(evaluator, arguments, token)
            
        if len(arguments) != len(self.params):
            raise FluxRuntimeError(token, 
                f"Expected {len(self.params)} arguments, got {len(arguments)}")
        
        env = Environment(self.closure)
        for param, arg in zip(self.params, arguments):
            env.define(param, arg)
        
        try:
            prev_function = evaluator.current_function
            prev_env = evaluator.env
            evaluator.current_function = self
            evaluator.env = env
            
            while True:
                try:
                    result = evaluator.execute_block(self.declaration.body, env)
                    evaluator.current_function = prev_function
                    evaluator.env = prev_env
                    return result
                except TailCall as tail_call:
                    if tail_call.function != self:
                        evaluator.current_function = prev_function
                        evaluator.env = prev_env
                        return tail_call.function.call(evaluator, tail_call.arguments, token)
                    
                    if len(tail_call.arguments) != len(self.params):
                        raise FluxRuntimeError(token, 
                            f"Expected {len(self.params)} arguments, got {len(tail_call.arguments)}")
                    
                    for param, arg in zip(self.params, tail_call.arguments):
                        env.assign(param, arg, token)
        except Return as r:
            evaluator.current_function = prev_function
            evaluator.env = prev_env
            return r.value

class Evaluator:
    def __init__(self):
        self.global_env = Environment()
        self.env = self.global_env
        self.current_function = None
        self.in_tail_position = False
        self.add_builtins()

    def add_builtins(self):
        """Add built-in functions to the global environment"""
        # Add len() function
        self.global_env.define("len", BuiltinFunction(self.builtin_len, "len"))

    def builtin_len(self, arguments, token):
        """Handles len(array), len(string), and len(dict)."""
        if len(arguments) != 1:
            raise FluxRuntimeError(token, f"'len' expected 1 argument, got {len(arguments)}")
        
        arg = arguments[0]

        if arg is None:
            raise FluxRuntimeError(token, "'len' cannot be applied to 'None'")

        if isinstance(arg, (list, str, dict)):
            return len(arg)

        if hasattr(arg, '__len__'):
            return arg.__len__()

        raise FluxRuntimeError(token, f"'len' expects an array, string, or dictionary, but got {type(arg).__name__}")

    def interpret(self, tree: Block) -> Any:
        try:
            return self.execute_block(tree, self.global_env)
        except FluxRuntimeError as e:
            print(e.message)
            return None
        except Exception as e:
            print(f"Internal error: {e}")
            traceback.print_exc()
            return None

    def evaluate(self, node: AST) -> Any:
        if node is None:
            return None
        return node.accept(self)

    def execute_block(self, block: Block, env: Environment) -> Any:
        previous_env = self.env
        self.env = env
        try:
            result = None
            last_idx = len(block.statements) - 1
            
            for i, stmt in enumerate(block.statements):
                is_last = (i == last_idx)
                old_tail_pos = self.in_tail_position
                
                if is_last:
                    self.in_tail_position = self.in_tail_position or (self.current_function is not None)
                
                if isinstance(stmt, Return):
                    value = self.evaluate(stmt.value)
                    if isinstance(stmt.value, FuncCall) and self.in_tail_position:
                        callee = self.evaluate(stmt.value.callee)
                        arguments = [self.evaluate(arg) for arg in stmt.value.args]
                        if isinstance(callee, Function) and callee == self.current_function:
                            raise TailCall(callee, arguments)
                    raise Return(value)
                
                result = self.evaluate(stmt)
                self.in_tail_position = old_tail_pos
            
            return result
        finally:
            self.env = previous_env

    def visit_integer(self, node: Integer) -> Any:
        return node.value

    def visit_float(self, node: Float) -> Any:
        return node.value

    def visit_string(self, node: String) -> str:
        return node.value

    def visit_boolean(self, node: Boolean) -> bool:
        return node.value

    def visit_var(self, node: Var) -> Any:
        return self.env.get(node.name, node.token)

    def visit_var_assign(self, node: VarAssign) -> Any:
        value = self.evaluate(node.value)
        self.env.define(node.name, value)
        return value

    def visit_var_reassign(self, node: VarReassign) -> Any:
        value = self.evaluate(node.value)
        return self.env.assign(node.name, value, node.token)

    def visit_bin_op(self, node: BinOp) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op_type = node.operator.type

        if op_type == PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, str) and isinstance(right, (int, float, bool, Function)):
                return left + self.stringify(right)
            if isinstance(left, (int, float, bool, Function)) and isinstance(right, str):
                return self.stringify(left) + right
            raise FluxRuntimeError(node.operator, "Operands must be two numbers, two strings, or a string and another type for '+'")
        
        if op_type == MINUS:
            self.check_number_operands(node.operator, left, right)
            return left - right
        
        if op_type == MULTIPLY:
            self.check_number_operands(node.operator, left, right)
            return left * right
        
        if op_type == DIVIDE:
            self.check_number_operands(node.operator, left, right)
            if right == 0:
                raise FluxRuntimeError(node.operator, "Division by zero")
            return left / right
        
        if op_type == EXPONENT:
            self.check_number_operands(node.operator, left, right)
            return left ** right
        
        if op_type == REM:
            self.check_number_operands(node.operator, left, right)
            if right == 0:
                raise FluxRuntimeError(node.operator, "Remainder by zero")
            return left % right
        
        
        if op_type in (LT, GT, LTE, GTE):
            self.check_number_operands(node.operator, left, right)
            if op_type == LT: return left < right
            if op_type == GT: return left > right
            if op_type == LTE: return left <= right
            if op_type == GTE: return left >= right
        
        if op_type == EQEQ:
            return left == right
        if op_type == NOTEQ:
            return left != right
        
        if op_type == AND:
            return self.is_truthy(left) and self.is_truthy(right)
        if op_type == OR:
            return self.is_truthy(left) or self.is_truthy(right)
        
        raise FluxRuntimeError(node.operator, f"Unknown binary operator '{node.operator.value}'")

    def visit_unary_op(self, node: UnaryOp) -> Any:
        value = self.evaluate(node.right)
        if node.operator.type == MINUS:
            self.check_number_operand(node.operator, value)
            return -value
        if node.operator.type == NOT:
            return not self.is_truthy(value)
        raise FluxRuntimeError(node.operator, f"Unknown unary operator '{node.operator.type}'")

    def visit_block(self, node: Block) -> Any:
        return self.execute_block(node, Environment(self.env))

    def visit_if(self, node: If) -> Any:
        condition = self.evaluate(node.condition)
        if self.is_truthy(condition):
            return self.evaluate(node.then_branch)
        elif node.else_branch:
            return self.evaluate(node.else_branch)
        return None

    def visit_while(self, node: While) -> Any:
        result = None
        while self.is_truthy(self.evaluate(node.condition)):
            result = self.evaluate(node.body)
        return result

    def visit_for(self, node: For) -> Any:
        start = self.evaluate(node.start)
        end = self.evaluate(node.end)
        step = self.evaluate(node.step) if node.step else 1

        if not isinstance(start, (int, float)):
            raise FluxRuntimeError(Token("IDENTIFIER", node.var_name, 0), "Start value must be a number")
        if not isinstance(end, (int, float)):
            raise FluxRuntimeError(Token("IDENTIFIER", node.var_name, 0), "End value must be a number")
        if not isinstance(step, (int, float)):
            raise FluxRuntimeError(Token("IDENTIFIER", node.var_name, 0), "Step value must be a number")
        if step == 0:
            raise FluxRuntimeError(Token("IDENTIFIER", node.var_name, 0), "Step cannot be zero")

        loop_env = Environment(self.env)
        loop_env.define(node.var_name, start)
        
        result = None
        current = start
        
        while (step > 0 and current <= end) or (step < 0 and current >= end):
            body_env = Environment(loop_env)
            result = self.execute_block(node.body, body_env)
            current += step
            loop_env.assign(node.var_name, current, Token("IDENTIFIER", node.var_name, 0))
        
        return result

    def visit_repeat_until(self, node: RepeatUntil) -> Any:
        result = None
        while True:
            result = self.evaluate(node.body)
            if self.is_truthy(self.evaluate(node.condition)):
                break
        return result

    def visit_match(self, node: Match) -> Any:
        value = self.evaluate(node.expression)
        for case in node.cases:
            pattern = self.evaluate(case.pattern)
            if value == pattern:
                return self.evaluate(case.body)
        raise FluxRuntimeError(Token("MATCH", "match", 0), "No matching case found")

    def visit_match_case(self, node: MatchCase) -> Any:
        return self.evaluate(node.body)

    def visit_lambda(self, node: Lambda) -> Any:
        lambda_def = type('AnonymousFunc', (), {
            'params': node.params,
            'body': node.body,
            'name': '<anonymous>'
        })
        return Function(lambda_def, self.env, is_anonymous=True)

    def visit_func_def(self, node: FuncDef) -> None:
        func = Function(node, self.env)
        self.env.define(node.name, func)
        return func

    def visit_func_call(self, node: FuncCall) -> Any:
        callee = self.evaluate(node.callee)
        
        if not isinstance(callee, (Function, BuiltinFunction)):
            raise FluxRuntimeError(
                node.token or Token("IDENTIFIER", str(node.callee), 0), 
                f"Can only call functions, got: {type(callee).__name__}"
            )
        
        arguments = [self.evaluate(arg) for arg in node.args]
        
        if self.in_tail_position and isinstance(callee, Function) and callee == self.current_function:
            raise TailCall(callee, arguments)
        
        return callee.call(self, arguments, node.token or Token("IDENTIFIER", "function call", 0))

    def visit_return(self, node: Return) -> Any:
        was_tail = self.in_tail_position
        self.in_tail_position = self.current_function is not None
        
        try:
            value = self.evaluate(node.value)
            
            if isinstance(node.value, FuncCall) and self.in_tail_position:
                callee = self.evaluate(node.value.callee)
                arguments = [self.evaluate(arg) for arg in node.value.args]
                
                if isinstance(callee, Function) and callee == self.current_function:
                    raise TailCall(callee, arguments)
            
            raise Return(value)
        finally:
            self.in_tail_position = was_tail

    def visit_array(self, node: Array) -> List[Any]:
        return [self.evaluate(element) for element in node.elements]

    def visit_array_assign(self, node: ArrayAssign) -> Any:
        array_name = node.array if isinstance(node.array, str) else node.array.name
        array = self.env.get(array_name, node.token)
        index = self.evaluate(node.index)
        value = self.evaluate(node.value)

        if not isinstance(array, list):
            raise FluxRuntimeError(node.token, f"Cannot assign to non-array type: {type(array).__name__}")
        if not isinstance(index, int):
            raise FluxRuntimeError(node.token, f"Array index must be an integer, got {type(index).__name__}")
        if index < 0 or index >= len(array):
            raise FluxRuntimeError(node.token, f"Array index {index} out of bounds")

        array[index] = value
        self.env.assign(array_name, array, node.token)
        return value
    
    def visit_array_access(self, node: ArrayAccess) -> Any:
        array_name = node.array if isinstance(node.array, str) else node.array.name
        array = self.env.get(array_name, node.token)
        index = self.evaluate(node.index)

        if not isinstance(array, list):
            raise FluxRuntimeError(node.token, f"Cannot index non-array type: {type(array).__name__}")
        if not isinstance(index, int):
            raise FluxRuntimeError(node.token, f"Array index must be an integer, got {type(index).__name__}")
        if index < 0 or index >= len(array):
            raise FluxRuntimeError(node.token, f"Array index {index} out of bounds")

        return array[index]

    def visit_dict(self, node: Dict) -> Dict[Any, Any]:
        return {self.evaluate(k): self.evaluate(v) for k, v in node.pairs}

    def visit_conditional_expr(self, node: ConditionalExpr) -> Any:
        condition = self.evaluate(node.condition)
        if self.is_truthy(condition):
            return self.evaluate(node.then_expr)
        return self.evaluate(node.else_expr)

    def visit_print(self, node: Print) -> Any:
        value = self.evaluate(node.expression)
        print(self.stringify(value))
        return value

    def check_number_operand(self, operator: Token, operand: Any):
        if not isinstance(operand, (int, float)):
            raise FluxRuntimeError(operator, "Operand must be a number")

    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
            raise FluxRuntimeError(operator, "Operands must be numbers")

    def is_truthy(self, value: Any) -> bool:
        if value is None or value is False:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False
        if isinstance(value, str) and value == "":
            return False
        return True

    def stringify(self, value: Any) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        if isinstance(value, (Function, BuiltinFunction)):
            return str(value)
        return str(value)

def run_file(filename: str):
    evaluator = Evaluator()
    try:
        with open(filename, 'r') as file:
            program = file.read()
        lexer = Lexer(program)
        parser = Parser(lexer)
        tree = parser.parse()
        result = evaluator.interpret(tree)
        if result is not None:
            print(f"Final result: {evaluator.stringify(result)}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluator.py <filename.fs>")
        sys.exit(1)
    filename = sys.argv[1]
    run_file(filename)
