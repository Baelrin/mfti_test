import ast
from typing import Union

import astor


class UnnestTransformer(ast.NodeTransformer):
    """
    A transformer that traverses an AST (Abstract Syntax Tree) and unnests complex expressions by introducing
    temporary variables. This simplifies function calls and operations by ensuring their arguments are
    simple names or constants.
    """

    def __init__(self):
        """
        Initializes the UnnestTransformer with a counter for generating unique temporary variable names
        and a list to hold assignments of complex expressions to these temporary variables.
        """
        self.var_counter = 0
        self.assignments = []

    def visit_FunctionDef(
        self, node: ast.FunctionDef
    ) -> Union[ast.FunctionDef, ast.AST]:
        """
        Resets the temporary variable counter and the list of assignments for each function definition encountered.
        This ensures that each function's transformations are local to that function.
        """
        self.var_counter = 0
        self.assignments = []
        return self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> Union[ast.BinOp, ast.Name]:
        """
        Visits binary operations, checks if either operand is a complex expression, and replaces it with a
        temporary variable if necessary.
        """
        if not isinstance(node.left, (ast.Name, ast.Constant)) or not isinstance(
            node.right, (ast.Name, ast.Constant)
        ):
            return self.extract_complex_expression(node)
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Union[ast.UnaryOp, ast.Name]:
        """
        Visits unary operations, checks if the operand is a complex expression, and replaces it with a
        temporary variable if necessary.
        """
        if not isinstance(node.operand, (ast.Name, ast.Constant)):
            return self.extract_complex_expression(node)
        return node

    def visit_Call(self, node: ast.Call) -> Union[ast.Call, ast.Name]:
        """
        Visits function calls, replaces any complex expressions in the arguments with temporary variables,
        and generates the necessary assignments for these replacements.
        """
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
        """
        Visits return statements, checks if the return value is a complex expression, and replaces it with a
        temporary variable if necessary.
        """
        if not isinstance(node.value, (ast.Name, ast.Constant)):
            new_var = ast.Name(id=f"v{self.var_counter}", ctx=ast.Store())
            self.var_counter += 1
            assign = ast.Assign(targets=[new_var], value=node.value)
            self.assignments.append(assign)
            node.value = new_var
        return node

    def extract_complex_expression(self, node: ast.AST) -> ast.Name:
        """
        Handles the extraction of a complex expression by assigning it to a temporary variable and replacing
        the expression with this variable.
        """
        new_var = ast.Name(id=f"v{self.var_counter}", ctx=ast.Store())
        self.var_counter += 1
        assign = ast.Assign(targets=[new_var], value=node)
        self.assignments.append(assign)
        return new_var

    def post_visit(self, node: ast.AST) -> ast.AST:
        """
        A post-processing step that inserts the assignments of complex expressions into the beginning of
        the function body, making the temporary variables available for use within the function.
        """
        if isinstance(node, ast.FunctionDef):
            node.body = self.assignments + node.body
        return node


def unnest_code(code: str) -> str:
    """
    Unnests complex expressions in the given source code string by transforming it into an AST,
    using UnnestTransformer to simplify the expressions, and then converting it back to source code.
    """
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
