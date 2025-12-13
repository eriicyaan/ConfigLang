# tests/test_parser.py
import pytest
import lark
from config_parser.parser import create_parser
from config_parser.transformer import ConfigTransformer


class TestParser:
    @pytest.fixture
    def parser(self):
        transformer = ConfigTransformer()
        return create_parser(transformer)

    def test_parse_struct_basic(self, parser):
        """Тест на парсинг простой структуры"""
        text = 'struct { Var1 = 42, Var2 = "test" };'
        result = parser.parse(text)
        assert result is not None

    def test_parse_struct_empty(self, parser):
        """Тест на парсинг пустой структуры"""
        text = 'struct {};'
        result = parser.parse(text)
        assert result is not None

    def test_parse_struct_nested(self, parser):
        """Тест на парсинг вложенной структуры"""
        text = 'struct { Var1 = struct { Nested = 100 } };'
        result = parser.parse(text)
        assert result is not None

    def test_parse_const_expr(self, parser):
        """Тест на парсинг константного выражения"""
        text = '.[ 5 3 + ].;'
        result = parser.parse(text)
        assert result is not None

    def test_parse_multiple_statements(self, parser):
        """Тест на парсинг нескольких выражений"""
        text = """
            Var1 := 10;
            struct { 
                Value = .[ Var1 5 + ]. 
            };
        """
        result = parser.parse(text)
        assert result is not None

    def test_parse_with_comments(self, parser):
        """Тест на парсинг с комментариями"""
        text = """
            <# Это комментарий #>
            struct {
                Name = "value"  <# Еще комментарий #>
            };
        """
        result = parser.parse(text)
        assert result is not None

    def test_parse_negative_numbers(self, parser):
        """Тест на парсинг отрицательных чисел"""
        text = 'struct { Value = -15.5 };'
        result = parser.parse(text)
        assert result is not None

    def test_parse_scientific_notation(self, parser):
        """Тест на парсинг чисел в научной нотации"""
        text = 'struct { Value = 1.5e-10 };'
        result = parser.parse(text)
        assert result is not None

    def test_invalid_syntax(self, parser):
        """Тест на обработку неверного синтаксиса"""
        text = 'struct { = 5 };'
        with pytest.raises(lark.exceptions.LarkError):
            parser.parse(text)

    def test_parse_string_with_escapes(self, parser):
        """Тест на парсинг строк с экранированием"""
        text = 'struct { Text = "Hello \\"world\\"" };'
        result = parser.parse(text)
        assert result is not None

    def test_variable_name_capital_letter(self, parser):
        """Тест на проверку, что переменные начинаются с заглавной буквы"""
        text = 'struct { VarName = 100 };'
        result = parser.parse(text)
        assert result is not None

        # Проверка, что переменная с маленькой буквы вызовет ошибку
        text_invalid = 'struct { varname = 100 };'
        with pytest.raises(lark.exceptions.LarkError):
            parser.parse(text_invalid)