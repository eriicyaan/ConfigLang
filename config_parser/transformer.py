import math
import lark


def get_value(item):
    """Универсальный метод получения значения из токена или объекта"""
    if hasattr(item, 'value'):
        return item.value
    return item


class ConfigTransformer(lark.Transformer):
    def __init__(self):
        self.constants = {}

    def start(self, items):
        return [item for item in items if item is not None]

    def struct(self, items):
        if items and items[0]:
            return dict(items[0])
        return {}

    def pair_list(self, items):
        return [item for item in items if item is not None]

    def pair(self, items):
        name = get_value(items[0])
        value = items[1]
        return (name, value)

    def constant_ref(self, items):
        name = get_value(items[0])
        if name not in self.constants:
            raise ValueError(f"Undefined constant: {name}")
        return self.constants[name]

    def const_declaration(self, items):
        name = get_value(items[0])
        value = items[1]
        self.constants[name] = value
        return None

    def const_expr(self, items):
        return self._evaluate_postfix(items[0])

    def expr_items(self, items):
        return items

    def NUMBER(self, token):
        return float(token.value)

    def STRING(self, token):
        raw = token.value[1:-1]
        return raw.replace('\\"', '"').replace('\\\\', '\\')

    def NAME(self, token):
        return token.value

    def OP(self, token):
        return token.value

    def FUNCTION(self, token):
        return token.value

    def _evaluate_postfix(self, tokens):
        stack = []
        for token in tokens:
            value = get_value(token)

            # Если это число или строковое представление числа
            if isinstance(value, (int, float)):
                stack.append(float(value))
            elif isinstance(value, str) and value.replace('.', '', 1).lstrip('-').isdigit():
                stack.append(float(value))
            elif value in ['+', '-', '*', '/']:
                if len(stack) < 2:
                    raise ValueError(f"Not enough operands for {value}")
                b = stack.pop()
                a = stack.pop()
                if value == '+':
                    stack.append(a + b)
                elif value == '-':
                    stack.append(a - b)
                elif value == '*':
                    stack.append(a * b)
                elif value == '/':
                    if abs(b) < 1e-9:
                        raise ValueError("Division by zero")
                    stack.append(a / b)
            elif value == 'mod':
                if len(stack) < 2:
                    raise ValueError("Not enough operands for mod")
                b = stack.pop()
                a = stack.pop()
                stack.append(a % b)
            elif value == 'sqrt':
                if not stack:
                    raise ValueError("Not enough operands for sqrt")
                a = stack.pop()
                if a < 0:
                    raise ValueError("Square root of negative number")
                stack.append(math.sqrt(a))
            else:
                # Пытаемся найти как константу
                if value in self.constants:
                    stack.append(self.constants[value])
                else:
                    raise ValueError(f"Unknown token in expression: {value}")

        if len(stack) != 1:
            raise ValueError(f"Invalid expression result count: {len(stack)}")
        return stack[0]
