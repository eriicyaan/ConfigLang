import pytest
import subprocess
import json
import tempfile
import os
import sys
from pathlib import Path


class TestIntegration:
    def get_cli_path(self):
        """Получаем путь к cli.py"""
        # Путь к директории проекта
        project_root = Path(__file__).parent.parent
        cli_path = project_root / "cli.py"
        return str(cli_path)

    def test_end_to_end_simple_config(self):
        """Интеграционный тест: от ввода до JSON файла"""
        config_text = """
            <# Простая конфигурация сервера #>
            MAXCONNECTIONS := 100;
            TIMEOUT := 30;

            struct {
                Server = struct {
                    Port = 8080,
                    Host = "localhost",
                    MaxUsers = MAXCONNECTIONS,
                    Settings = struct {
                        Timeout = .[ TIMEOUT 5 + ].
                    }
                },
                Database = struct {
                    Host = "db.local",
                    Port = 5432
                }
            };
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            output_file = tmp.name

        try:
            # Запускаем CLI как скрипт python
            cli_path = self.get_cli_path()
            result = subprocess.run(
                [sys.executable, cli_path, '-o', output_file],
                input=config_text,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )

            # Проверяем успешное выполнение
            assert result.returncode == 0, f"CLI failed: {result.stderr}"

            # Проверяем, что файл не пустой
            assert os.path.getsize(output_file) > 0

            # Читаем результат
            with open(output_file, 'r', encoding='utf-8') as f:
                output = json.load(f)

            # Проверяем структуру результата
            assert len(output) == 1
            config = output[0]

            assert "Server" in config
            assert "Database" in config

            server = config["Server"]
            assert server["Port"] == 8080.0
            assert server["Host"] == "localhost"
            assert server["MaxUsers"] == 100.0
            assert server["Settings"]["Timeout"] == 35.0  # 30 + 5

            db = config["Database"]
            assert db["Host"] == "db.local"
            assert db["Port"] == 5432.0

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_end_to_end_complex_expressions(self):
        config_text = """
            Pi := 3.1415926535;
            Radius := 10;

            struct {
                Circle = struct {
                    Radius = Radius,
                    Area = .[ Pi Radius Radius * * ].,
                    Circumference = .[ 2 Pi Radius * * ].
                },
                Math = struct {
                    SqrtExample = .[ 256 sqrt ].,
                    ModExample = .[ 17 5 mod ].
                }
            };
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            output_file = tmp.name

        try:
            cli_path = self.get_cli_path()
            result = subprocess.run(
                [sys.executable, cli_path, '-o', output_file],
                input=config_text,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )

            assert result.returncode == 0, f"CLI failed: {result.stderr}"

            with open(output_file, 'r', encoding='utf-8') as f:
                output = json.load(f)

            circle = output[0]["Circle"]
            math = output[0]["Math"]

            # Проверяем вычисления
            expected_area = 3.1415926535 * 10 * 10
            expected_circumference = 2 * 3.1415926535 * 10

            assert pytest.approx(circle["Area"], 0.0001) == expected_area
            assert pytest.approx(circle["Circumference"], 0.0001) == expected_circumference
            assert math["SqrtExample"] == 16.0
            assert math["ModExample"] == 2.0

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


    def test_end_to_end_error_handling(self):
        """Интеграционный тест обработки ошибок"""
        config_text = 'struct { Value = UndefinedConstant };'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            output_file = tmp.name

        try:
            cli_path = self.get_cli_path()
            result = subprocess.run(
                [sys.executable, cli_path, '-o', output_file],
                input=config_text,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )

            # Должна быть ошибка
            assert result.returncode == 1
            # Проверяем, что в stderr есть сообщение об ошибке
            assert len(result.stderr) > 0

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_end_to_end_multiple_structures(self):
        """Интеграционный тест с несколькими структурами"""
        config_text = """
            struct { First = 1 };
            struct { Second = 2 };
            Const := 3;
            .[ Const 5 * ].;
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            output_file = tmp.name

        try:
            cli_path = self.get_cli_path()
            result = subprocess.run(
                [sys.executable, cli_path, '-o', output_file],
                input=config_text,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )

            assert result.returncode == 0, f"CLI failed: {result.stderr}"

            with open(output_file, 'r', encoding='utf-8') as f:
                output = json.load(f)

            # Проверяем все три элемента
            assert len(output) == 3
            assert output[0] == {"First": 1.0}
            assert output[1] == {"Second": 2.0}
            assert output[2] == 15.0  # 3 * 5

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)