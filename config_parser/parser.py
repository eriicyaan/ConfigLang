import lark

GRAMMAR = r"""
    ?start: statement*

    ?statement: struct
              | const_declaration
              | const_expr

    struct: "struct" "{" pair_list? "}" [";"]

    pair_list: pair ("," pair)* [","]?

    pair: NAME "=" value

    ?value: NUMBER
          | STRING
          | struct
          | const_expr
          | NAME -> constant_ref

    const_declaration: NAME ":=" value [";"]

    const_expr: ".[" expr_items "]" "." [";"]

    expr_items: expr_item+

    ?expr_item: NUMBER
              | NAME
              | OP
              | FUNCTION

    OP: "+" | "-" | "*" | "/"
    FUNCTION: "mod" | "sqrt"

    NAME: /[_A-Z][_a-zA-Z0-9]*/
    NUMBER: /[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/
    STRING: /"(?:[^"\\]|\\.)*"/

    %import common.WS
    %ignore WS
    %ignore /<#[\s\S]*?#>/
"""

def create_parser(transformer):
    return lark.Lark(
        GRAMMAR,
        parser='lalr',
        transformer=transformer,
        propagate_positions=True,
        debug=False
    )
