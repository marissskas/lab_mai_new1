"""Модульное тестирование текстового пользовательского интерфейса."""

import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.memory_db import MemoryDatabase


class TestDatabaseApp(unittest.TestCase):
    """Тесты для DatabaseApp."""

    def setUp(self):
        from src.db.tui import DatabaseApp
        self.app = DatabaseApp()
        self.app.db = MemoryDatabase()

    def test_read_string_valid(self):
        with patch('builtins.input', return_value="тест"):
            result = self.app.read_string("Введите: ")
            self.assertEqual(result, "тест")

    def test_read_optional_empty(self):
        with patch('builtins.input', return_value=""):
            result = self.app.read_optional("Введите: ")
            self.assertIsNone(result)

    def test_select_table_no_tables(self):
        result = self.app.select_table()
        self.assertIsNone(result)

    def test_exit_menu(self):
        from src.db.tui import ExitMenu
        menu = ExitMenu()
        menu.execute(self.app)
        self.assertFalse(self.app.running)


if __name__ == "__main__":
    unittest.main()
