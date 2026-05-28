# tests/test_memory.py
"""Модульное тестирование MemoryDatabase."""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.memory_db import MemoryDatabase
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
)


class TestMemoryDatabase(unittest.TestCase):
    """Тесты для MemoryDatabase."""

    def setUp(self):
        """Подготовка перед каждым тестом."""
        self.db = MemoryDatabase()

    def test_create_table_success(self):
        """Тест успешного создания таблицы."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        tables = self.db.get_table_names()
        self.assertIn("студенты", tables)
        
        info = self.db.get_table_info("студенты")
        self.assertIsNotNone(info)
        self.assertEqual(info["columns"], ("id", "имя", "возраст"))
        self.assertEqual(info["records_count"], 0)

    def test_create_table_duplicate(self):
        """Тест создания дублирующей таблицы."""
        self.db.create_table("студенты", ("id", "имя"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("студенты", ("id", "имя"))

    def test_get_table_names_empty(self):
        """Тест получения списка таблиц из пустой БД."""
        self.assertEqual(self.db.get_table_names(), [])

    def test_get_table_names_with_tables(self):
        """Тест получения списка таблиц, когда они есть."""
        self.db.create_table("users", ("id", "name"))
        self.db.create_table("products", ("id", "title"))
        tables = self.db.get_table_names()
        self.assertEqual(len(tables), 2)
        self.assertIn("users", tables)
        self.assertIn("products", tables)

    def test_get_table_info_nonexistent(self):
        """Тест получения информации о несуществующей таблице."""
        self.assertIsNone(self.db.get_table_info("несуществующая"))

    def test_get_table_info_existing(self):
        """Тест получения информации о существующей таблице."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна", "возраст": "16"})
        
        info = self.db.get_table_info("студенты")
        self.assertEqual(info["name"], "студенты")
        self.assertEqual(info["columns"], ("id", "имя", "возраст"))
        self.assertEqual(info["records_count"], 1)

    def test_insert_success(self):
        """Тест успешной вставки записи."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        record = {"id": "1", "имя": "Иван Петров", "возраст": "17"}
        result = self.db.insert("студенты", record)
        self.assertEqual(result, record)

        records = self.db.select("студенты")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], record)

    def test_insert_table_not_exists(self):
        """Тест вставки в несуществующую таблицу."""
        with self.assertRaises(TableNotFoundError):
            self.db.insert("несуществующая", {"id": "1"})

    def test_insert_missing_column(self):
        """Тест вставки с отсутствующим полем."""
        self.db.create_table("студенты", ("id", "имя", "email"))
        record = {"id": "1", "имя": "Иван Петров"}
        with self.assertRaises(MissingColumnError):
            self.db.insert("студенты", record)

    def test_insert_extra_column(self):
        """Тест вставки с лишним полем."""
        self.db.create_table("студенты", ("id", "имя"))
        record = {"id": "1", "имя": "Иван Петров", "лишнее": "значение"}
        with self.assertRaises(UnknownColumnError):
            self.db.insert("студенты", record)

    def test_select_no_filters(self):
        """Тест выборки без фильтров."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна Иванова"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис Смирнов"})

        records = self.db.select("студенты")
        self.assertEqual(len(records), 2)

    def test_select_with_filters(self):
        """Тест выборки с фильтрами."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна Иванова", "возраст": "16"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис Смирнов", "возраст": "17"})
        self.db.insert("студенты", {"id": "3", "имя": "Вера Козлова", "возраст": "18"})

        result = self.db.select("студенты", id="1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["имя"], "Анна Иванова")

        result = self.db.select("студенты", имя="Вера Козлова")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["возраст"], "18")

    def test_select_table_not_exists(self):
        """Тест выборки из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.select("несуществующая")

    def test_update_success(self):
        """Тест успешного обновления."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна Иванова", "возраст": "16"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис Смирнов", "возраст": "17"})

        count = self.db.update("студенты", {"возраст": "18"}, id="1")
        self.assertEqual(count, 1)

        result = self.db.select("студенты", id="1")
        self.assertEqual(result[0]["возраст"], "18")

    def test_update_no_matches(self):
        """Тест обновления без совпадений."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна Иванова"})

        count = self.db.update("студенты", {"имя": "Петр Сидоров"}, id="999")
        self.assertEqual(count, 0)

    def test_update_multiple_records(self):
        """Тест обновления нескольких записей одновременно."""
        self.db.create_table("студенты", ("id", "имя", "группа"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна Иванова", "группа": "113А"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис Смирнов", "группа": "113А"})
        self.db.insert("студенты", {"id": "3", "имя": "Вера Козлова", "группа": "113Б"})

        count = self.db.update("студенты", {"группа": "113В"}, группа="113А")
        self.assertEqual(count, 2)

        result = self.db.select("студенты", группа="113В")
        self.assertEqual(len(result), 2)

    def test_update_table_not_exists(self):
        """Тест обновления в несуществующей таблице."""
        with self.assertRaises(TableNotFoundError):
            self.db.update("несуществующая", {"field": "value"})

    def test_delete_success(self):
        """Тест успешного удаления."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна Иванова"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис Смирнов"})
        self.db.insert("студенты", {"id": "3", "имя": "Вера Козлова"})

        count = self.db.delete("студенты", id="1")
        self.assertEqual(count, 1)

        records = self.db.select("студенты")
        self.assertEqual(len(records), 2)

    def test_delete_no_matches(self):
        """Тест удаления без совпадений."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна Иванова"})

        count = self.db.delete("студенты", id="999")
        self.assertEqual(count, 0)

        records = self.db.select("студенты")
        self.assertEqual(len(records), 1)

    def test_delete_all_records(self):
        """Тест удаления всех записей (без фильтров)."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна Иванова"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис Смирнов"})

        count = self.db.delete("студенты")
        self.assertEqual(count, 2)

        records = self.db.select("студенты")
        self.assertEqual(len(records), 0)

    def test_delete_table_not_exists(self):
        """Тест удаления из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.delete("несуществующая")

    def test_sort_records_ascending(self):
        """Тест сортировки по возрастанию."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "3", "имя": "Вера"})
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})

        sorted_records = self.db.sort_records("студенты", "id", reverse=False)
        expected_ids = ["1", "2", "3"]
        result_ids = [r["id"] for r in sorted_records]
        self.assertEqual(result_ids, expected_ids)

    def test_sort_records_descending(self):
        """Тест сортировки по убыванию."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "3", "имя": "Вера"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})

        sorted_records = self.db.sort_records("студенты", "id", reverse=True)
        expected_ids = ["3", "2", "1"]
        result_ids = [r["id"] for r in sorted_records]
        self.assertEqual(result_ids, expected_ids)

    def test_sort_invalid_field(self):
        """Тест сортировки по несуществующему полю."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})

        with self.assertRaises(UnknownColumnError):
            self.db.sort_records("студенты", "несуществующее_поле")

    def test_sort_table_not_exists(self):
        """Тест сортировки в несуществующей таблице."""
        with self.assertRaises(TableNotFoundError):
            self.db.sort_records("несуществующая", "field")

    def test_sort_does_not_modify_original(self):
        """Тест: сортировка не меняет оригинальный порядок."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "3", "имя": "Вера"})
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})

        original_ids = [r["id"] for r in self.db.select("студенты")]

        self.db.sort_records("студенты", "id")
        current_ids = [r["id"] for r in self.db.select("студенты")]

        self.assertEqual(original_ids, current_ids)


if __name__ == "__main__":
    unittest.main()
