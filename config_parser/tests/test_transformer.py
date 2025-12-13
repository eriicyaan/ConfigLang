# tests/test_transformer.py
import pytest
import math
from config_parser.parser import create_parser
from config_parser.transformer import ConfigTransformer


class TestConfigTransformer:
    @pytest.fixture
    def transformer(self):
        return ConfigTransformer()

    @pytest.fixture
    def parser(self):
        return create_parser(ConfigTransformer())

    def test_transform_struct(self, transformer, parser):
        """Тест трансформации структуры"""
        text = 'struct { Var1 = 42, Var2 = 3.14 };'
        result = parser.parse(text)
        assert result == {"Var1": 42.0, "Var2": 3.14}

    def test_transform_empty_struct(self, transformer, parser):
        """Тест трансформации пустой структуры"""
        text = 'struct {};'
        result = parser.parse(text)
        assert result == {}

    def test_transform_nested_struct(self, transformer, parser):
        """Тест трансформации вложенной структуры"""
        text = 'struct { Outer = struct { Inner = 100 } };'
        result = parser.parse(text)
        assert result == {"Outer": {"Inner": 100.0}}

    def test_transform_const_declaration(self, transformer, parser):
        """Тест трансформации объявления константы"""
        text = 'Const1 := 10; struct { Value = Const1 };'
        result = parser.parse(text)
        assert result == [{"Value": 10.0}]

    def test_transform_const_expr_basic(self, transformer, parser):
        """Тест трансформации базового константного выражения"""
        text = '.[ 5 3 + ].;'
        result = parser.parse(text)
        assert result == 8.0

    def test_transform_const_expr_complex(self, transformer, parser):
        """Тест трансформации сложного константного выражения"""
        text = '.[ 10 2 * 4 / 1 + ].;'
        result = parser.parse(text)
        # (10 * 2) / 4 + 1 = 20 / 4 + 1 = 5 + 1 = 6
        assert result == 6.0

    def test_transform_math_operations(self, transformer, parser):
        """Тест трансформации математических операций"""
        text = '.[ 15 7 - ].;'
        result = parser.parse(text)
        assert result == 8.0

    def test_transform_mod_function(self, transformer, parser):
        """Тест трансформации функции mod"""
        text = '.[ 10 3 mod ].;'
        result = parser.parse(text)
        assert result == 1.0

    def test_transform_sqrt_function(self, transformer, parser):
        """Тест трансформации функции sqrt"""
        text = '.[ 16 sqrt ].;'
        result = parser.parse(text)
        assert result == 4.0

    def test_transform_with_constants(self, transformer, parser):
        """Тест трансформации с использованием констант"""
        text = """
            Pi := 3.14159;
            Radius := 5;
            struct {
                Area = .[ Pi Radius Radius * * ].
            };
        """
        result = parser.parse(text)
        area = 3.14159 * 5 * 5
        assert pytest.approx(result[0]["Area"], 0.0001) == area

    def test_transform_string(self, transformer, parser):
        """Тест трансформации строк"""
        text = 'struct { Message = "Hello World" };'
        result = parser.parse(text)
        assert result == {"Message": "Hello World"}

    def test_transform_string_with_escape(self, transformer, parser):
        """Тест трансформации строк с экранированием"""
        text = 'struct { Text = "Line 1\nLine 2" };'
        result = parser.parse(text)
        assert result == {"Text": "Line 1\nLine 2"}

    def test_transform_negative_sqrt(self, transformer, parser):
        """Тест на ошибку при извлечении корня из отрицательного числа"""
        text = '.[ -1 sqrt ].;'
        with pytest.raises(ValueError, match="Square root of negative number"):
            parser.parse(text)

    def test_transform_division_by_zero(self, transformer, parser):
        """Тест на ошибку деления на ноль"""
        text = '.[ 5 0 / ].;'
        with pytest.raises(ValueError, match="Division by zero"):
            parser.parse(text)

    def test_transform_undefined_constant(self, transformer, parser):
        """Тест на ошибку при использовании неопределенной константы"""
        text = 'struct { Value = UndefinedConst };'
        with pytest.raises(ValueError, match="Undefined constant"):
            parser.parse(text)

    def test_transform_invalid_expression(self, transformer, parser):
        """Тест на ошибку в невалидном выражении"""
        text = '.[ 5 + ].;'
        with pytest.raises(ValueError, match="Not enough operands"):
            parser.parse(text)

    def test_transform_multiple_results(self, transformer, parser):
        """Тест на ошибку при нескольких результатах выражения"""
        text = '.[ 5 3 ].;'
        with pytest.raises(ValueError, match="Invalid expression result count"):
            parser.parse(text)
