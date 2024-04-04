# mfti_test

## Overview

`mfti_test` is a Python project designed to simplify complex expressions in source code by transforming them into an Abstract Syntax Tree (AST), using a custom transformer to unnest these expressions, and then converting the modified AST back into source code. This process introduces temporary variables for complex expressions, ensuring that function calls and operations are simplified and more readable.

## Features

- **Unnesting Complex Expressions**: The core functionality of `mfti_test` is to unnest complex expressions in Python code. This includes binary operations, unary operations, function calls, and return statements.
- **Simplification of Source Code**: By introducing temporary variables for complex expressions, the transformed code becomes more readable and easier to understand.
- **Custom Transformer**: The project includes a custom `UnnestTransformer` class that extends `ast.NodeTransformer`. This transformer is responsible for traversing the AST and applying the unnesting logic.
- **Example Usage**: The project includes an example of how to use the `unnest_code` function to simplify complex expressions in a given source code string.

## Usage

To use `mfti_test`, simply import the `unnest_code` function and pass a string containing the Python code you wish to simplify. The function will return a string with the simplified code.

```python
from master import unnest_code

code = """
def foo(a, b, c, d):
    return baz(-a, c**(a - b) + d, k=A + 123)

def bar(x):
    a = x * 2 + sin(x)
    b = a
    return a, b, x + 1
"""

print(unnest_code(code))
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or find bugs, please open an issue or submit a pull request.

## License

This project is open source and available under the [MIT License](LICENSE).
