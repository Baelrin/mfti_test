import ast
from typing import Union

import astor


class UnnestTransformer(ast.NodeTransformer):
    def __init__(self):
        self.var_counter = 0
        self.assignments = []

    def visit_FunctionDef(
        self, node: ast.FunctionDef
    ) -> Union[ast.FunctionDef, ast.AST]:
        self.var_counter = 0
        self.assignments = []
        return self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> Union[ast.BinOp, ast.Name]:
        if not isinstance(node.left, (ast.Name, ast.Constant)) or not isinstance(
            node.right, (ast.Name, ast.Constant)
        ):
            return self.extract_complex_expression(node)
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Union[ast.UnaryOp, ast.Name]:
        if not isinstance(node.operand, (ast.Name, ast.Constant)):
            return self.extract_complex_expression(node)
        return node

    def visit_Call(self, node: ast.Call) -> Union[ast.Call, ast.Name]:
        new_args = []
        for arg in node.args:
            if not isinstance(arg, (ast.Name, ast.Constant)):
                new_var = ast.Name(id=f"v{self.var_counter}", ctx=ast.Store())
                self.var_counter += 1
                assign = ast.Assign(targets=[new_var], value=arg)
                self.assignments.append(assign)
                new_args.append(new_var)
            else:
                new_args.append(arg)
        node.args = new_args
        return node

    def visit_Return(self, node: ast.Return) -> ast.Return:
        if not isinstance(node.value, (ast.Name, ast.Constant)):
            new_var = ast.Name(id=f"v{self.var_counter}", ctx=ast.Store())
            self.var_counter += 1
            assign = ast.Assign(targets=[new_var], value=node.value)
            self.assignments.append(assign)
            node.value = new_var
        return node

    def extract_complex_expression(self, node: ast.AST) -> ast.Name:
        new_var = ast.Name(id=f"v{self.var_counter}", ctx=ast.Store())
        self.var_counter += 1
        assign = ast.Assign(targets=[new_var], value=node)
        self.assignments.append(assign)
        return new_var

    def post_visit(self, node: ast.AST) -> ast.AST:
        if isinstance(node, ast.FunctionDef):
            node.body = self.assignments + node.body
        return node


def unnest_code(code: str) -> str:
    try:
        tree = ast.parse(code)
        transformer = UnnestTransformer()
        new_tree = transformer.visit(tree)
        new_tree = transformer.post_visit(new_tree)
        return astor.to_source(new_tree)
    except Exception as e:
        print(f"Ошибка при обработке кода: {e}")
        return ""


# Пример использования
code = """
def foo(a, b, c, d):
    return baz(-a, c**(a - b) + d, k=A + 123)

def bar(x):
    a = x * 2 + sin(x)
    b = a
    return a, b, x + 1
"""

print(unnest_code(code))
