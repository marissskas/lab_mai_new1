"""Модульное тестирование FileDatabase."""
import unittest
import tempfile
import shutil
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.file import FileDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)


class TestFileDatabase(unittest.TestCase):
    """Тесты для FileDatabase."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_create_table_success(self):
        """Тест успешного создания таблицы."""
        self.db.create_table("users", ("id", "name"))
        self.assertTrue(self.db._table_exists("users"))
        
        # Проверяем, что файл создан
        file_path = self.db._get_table_path("users")
        self.assertTrue(file_path.exists())

    def test_create_table_duplicate(self):
        """Тест создания дублирующей таблицы."""
        self.db.create_table("users", ("id", "name"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("users", ("id", "name"))

    def test_insert_record_success(self):
        """Тест успешной вставки записи."""
        self.db.create_table("users", ("id", "name", "age"))
        self.db.insert_record("users", {"id": "1", "name": "Alice", "age": "30"})
        
        records = self.db.select_records("users")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Alice")

    def test_insert_missing_column(self):
        """Тест вставки с отсутствующим полем."""
        self.db.create_table("users", ("id", "name"))
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("users", {"id": "1"})

    def test_insert_extra_column(self):
        """Тест вставки с лишним полем."""
        self.db.create_table("users", ("id", "name"))
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("users", {"id": "1", "name": "Alice", "extra": "value"})

    def test_data_persistence_between_instances(self):
        """Тест: данные сохраняются между экземплярами."""
        # Первый экземпляр - создаём таблицу и добавляем запись
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        # Второй экземпляр - загружаем данные
        db2 = FileDatabase(self.temp_dir)
        records = db2.select_records("users")
        
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["name"], "Alice")
        self.assertEqual(records[1]["name"], "Bob")

    def test_select_with_filters(self):
        """Тест выборки с фильтрами."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        records = self.db.select_records("users", name="Bob")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], "2")

    def test_select_with_multiple_filters(self):
        """Тест выборки с несколькими фильтрами."""
        self.db.create_table("users", ("id", "name", "age"))
        self.db.insert_record("users", {"id": "1", "name": "Alice", "age": "30"})
        self.db.insert_record("users", {"id": "2", "name": "Bob", "age": "25"})
        self.db.insert_record("users", {"id": "3", "name": "Alice", "age": "25"})
        
        records = self.db.select_records("users", name="Alice", age="25")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], "3")

    def test_select_with_unknown_filter(self):
        """Тест выборки с неизвестным полем фильтра."""
        self.db.create_table("users", ("id", "name"))
        with self.assertRaises(UnknownColumnError):
            self.db.select_records("users", unknown="value")

    def test_select_from_missing_table(self):
        """Тест выборки из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")

    def test_update_records_success(self):
        """Тест успешного обновления записей."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        count = self.db.update_records("users", {"name": "Updated"}, id="1")
        self.assertEqual(count, 1)
        
        records = self.db.select_records("users", id="1")
        self.assertEqual(records[0]["name"], "Updated")

    def test_update_records_without_filters(self):
        """Тест обновления всех записей."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        count = self.db.update_records("users", {"name": "Updated"})
        self.assertEqual(count, 2)
        
        records = self.db.select_records("users")
        for record in records:
            self.assertEqual(record["name"], "Updated")

    def test_update_records_persistence(self):
        """Тест: обновления сохраняются в файл."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        
        self.db.update_records("users", {"name": "Updated"}, id="1")
        
        # Проверяем через новый экземпляр
        db2 = FileDatabase(self.temp_dir)
        records = db2.select_records("users", id="1")
        self.assertEqual(records[0]["name"], "Updated")

    def test_delete_records_success(self):
        """Тест успешного удаления записей."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        count = self.db.delete_records("users", id="1")
        self.assertEqual(count, 1)
        
        records = self.db.select_records("users")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Bob")

    def test_delete_records_without_filters(self):
        """Тест удаления всех записей."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        count = self.db.delete_records("users")
        self.assertEqual(count, 2)
        
        records = self.db.select_records("users")
        self.assertEqual(len(records), 0)

    def test_delete_records_persistence(self):
        """Тест: удаления сохраняются в файл."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        
        self.db.delete_records("users", id="1")
        
        # Проверяем через новый экземпляр
        db2 = FileDatabase(self.temp_dir)
        records = db2.select_records("users")
        self.assertEqual(len(records), 0)

    def test_invalid_json_handling(self):
        """Тест обработки повреждённого JSON-файла."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        
        # Повреждаем файл
        file_path = self.db._get_table_path("users")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("{invalid json}")
        
        db2 = FileDatabase(self.temp_dir)
        with self.assertRaises(InvalidStorageDataError):
            db2.select_records("users")

    def test_directory_created_automatically(self):
        """Тест: директория создаётся автоматически."""
        new_dir = os.path.join(self.temp_dir, "new_data_dir")
        db = FileDatabase(new_dir)
        self.assertTrue(os.path.exists(new_dir))

    def test_get_table_names(self):
        """Тест получения списка таблиц."""
        self.db.create_table("users", ("id", "name"))
        self.db.create_table("products", ("id", "title"))
        
        # Проверяем через прямой доступ к директории
        files = os.listdir(self.temp_dir)
        self.assertIn("users.json", files)
        self.assertIn("products.json", files)


class TestFileDatabaseWithStudentTable(unittest.TestCase):
    """Тесты FileDatabase с таблицей студентов (русские поля)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_create_student_table(self):
        """Тест создания таблицы студентов."""
        columns = ("id", "имя", "фамилия", "возраст", "пол")
        self.db.create_table("студенты", columns)
        
        self.assertTrue(self.db._table_exists("студенты"))
        
        # Проверяем структуру в файле
        file_path = self.db._get_table_path("студенты")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["columns"], ["id", "имя", "фамилия", "возраст", "пол"])

    def test_insert_and_select_cyrillic(self):
        """Тест вставки и выборки кириллических данных."""
        self.db.create_table("студенты", ("id", "имя", "фамилия"))
        self.db.insert_record("студенты", {"id": "1", "имя": "Иван", "фамилия": "Петров"})
        
        records = self.db.select_records("студенты", имя="Иван")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["фамилия"], "Петров")


if __name__ == "__main__":
    unittest.main()
