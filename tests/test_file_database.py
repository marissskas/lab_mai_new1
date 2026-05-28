# tests/test_file_database.py
"""Модульное тестирование FileDatabase."""

import unittest
import tempfile
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.file_db import FileDatabase
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)


class TestFileDatabase(unittest.TestCase):
    """Тесты для FileDatabase."""

    def setUp(self):
        """Подготовка перед каждым тестом - создаём временную директорию."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = FileDatabase(self.temp_dir.name)

    def tearDown(self):
        """Очистка после каждого теста."""
        self.temp_dir.cleanup()

    def test_create_table_success(self):
        """Тест успешного создания таблицы."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        tables = self.db.get_table_names()
        self.assertIn("студенты", tables)

        # Проверка, что файл создан
        table_path = self.db._get_table_path("студенты")
        self.assertTrue(table_path.exists())

    def test_create_table_duplicate(self):
        """Тест создания дублирующей таблицы."""
        self.db.create_table("студенты", ("id", "имя"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("студенты", ("id", "имя"))

    def test_data_persists_between_instances(self):
        """Тест: данные сохраняются между разными экземплярами."""
        # Первый экземпляр - создаём данные
        first_db = FileDatabase(self.temp_dir.name)
        first_db.create_table("студенты", ("id", "имя"))
        first_db.insert("студенты", {"id": "1", "имя": "Анна"})

        # Второй экземпляр - загружаем данные
        second_db = FileDatabase(self.temp_dir.name)
        records = second_db.select("студенты")
        
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["имя"], "Анна")

    def test_insert_and_select(self):
        """Тест вставки и выборки записи."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        record = {"id": "1", "имя": "Иван Петров", "возраст": "17"}
        self.db.insert("студенты", record)

        records = self.db.select("студенты")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], record)

    def test_insert_missing_column(self):
        """Тест вставки с отсутствующим полем."""
        self.db.create_table("студенты", ("id", "имя", "email"))
        record = {"id": "1", "имя": "Иван"}
        with self.assertRaises(MissingColumnError):
            self.db.insert("студенты", record)

    def test_select_with_filters(self):
        """Тест выборки с фильтрами."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна", "возраст": "16"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис", "возраст": "17"})
        self.db.insert("студенты", {"id": "3", "имя": "Вера", "возраст": "18"})

        result = self.db.select("студенты", id="1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["имя"], "Анна")

        result = self.db.select("студенты", возраст="18")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["имя"], "Вера")

    def test_update_records(self):
        """Тест обновления записей."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна", "возраст": "16"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис", "возраст": "17"})

        count = self.db.update("студенты", {"возраст": "18"}, id="1")
        self.assertEqual(count, 1)

        result = self.db.select("студенты", id="1")
        self.assertEqual(result[0]["возраст"], "18")

    def test_delete_records(self):
        """Тест удаления записей."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})

        count = self.db.delete("студенты", id="1")
        self.assertEqual(count, 1)

        records = self.db.select("студенты")
        self.assertEqual(len(records), 1)

    def test_delete_all_records(self):
        """Тест удаления всех записей."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})

        count = self.db.delete("студенты")
        self.assertEqual(count, 2)

        records = self.db.select("студенты")
        self.assertEqual(len(records), 0)

    def test_sort_records(self):
        """Тест сортировки записей."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "3", "имя": "Вера"})
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})

        sorted_records = self.db.sort_records("студенты", "id", reverse=False)
        expected_ids = ["1", "2", "3"]
        result_ids = [r["id"] for r in sorted_records]
        self.assertEqual(result_ids, expected_ids)

    def test_load_corrupted_json(self):
        """Тест загрузки повреждённого JSON-файла."""
        self.db.create_table("студенты", ("id", "имя"))
        
        # Повреждаем JSON-файл
        table_path = self.db._get_table_path("студенты")
        with open(table_path, "w", encoding="utf-8") as f:
            f.write("{invalid json content")
        
        # Очищаем кэш
        self.db._invalidate_cache("студенты")
        
        # Попытка загрузить таблицу должна вызвать ошибку
        with self.assertRaises(InvalidStorageDataError):
            self.db.select("студенты")

    def test_get_table_info(self):
        """Тест получения информации о таблице."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна", "возраст": "16"})
        
        info = self.db.get_table_info("студенты")
        self.assertEqual(info["name"], "студенты")
        self.assertEqual(info["columns"], ("id", "имя", "возраст"))
        self.assertEqual(info["records_count"], 1)

    def test_get_table_info_nonexistent(self):
        """Тест получения информации о несуществующей таблице."""
        info = self.db.get_table_info("несуществующая")
        self.assertIsNone(info)


if __name__ == "__main__":
    unittest.main()
