"""Модульное тестирование FileDatabase."""
import unittest
import tempfile
import shutil
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
        
        # Проверяем через публичный метод
        tables = self.db.get_table_names()
        self.assertIn("users", tables)

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
        # Просто создаём экземпляр, переменная не нужна
        FileDatabase(new_dir)
        self.assertTrue(os.path.exists(new_dir))

    def test_get_table_names_public_method(self):
        """Тест публичного метода get_table_names()."""
        # Создаём несколько таблиц
        self.db.create_table("users", ("id", "name"))
        self.db.create_table("products", ("id", "title"))
        self.db.create_table("orders", ("id", "user_id"))
        
        # Получаем список таблиц через публичный метод
        tables = self.db.get_table_names()
        
        # Проверяем, что все созданные таблицы есть в списке
        self.assertEqual(len(tables), 3)
        self.assertIn("users", tables)
        self.assertIn("products", tables)
        self.assertIn("orders", tables)

    def test_get_table_names_empty(self):
        """Тест get_table_names() когда нет таблиц."""
        tables = self.db.get_table_names()
        self.assertEqual(tables, [])

    def test_get_table_info(self):
        """Тест получения информации о таблице."""
        self.db.create_table("users", ("id", "name", "age"))
        self.db.insert_record("users", {"id": "1", "name": "Alice", "age": "30"})
        self.db.insert_record("users", {"id": "2", "name": "Bob", "age": "25"})
        
        info = self.db.get_table_info("users")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "users")
        self.assertEqual(info["columns"], ("id", "name", "age"))
        self.assertEqual(info["records_count"], 2)

    def test_get_table_info_nonexistent(self):
        """Тест get_table_info() для несуществующей таблицы."""
        info = self.db.get_table_info("nonexistent")
        self.assertIsNone(info)

    def test_insert_method_alias(self):
        """Тест метода insert() (алиас для insert_record)."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert("users", {"id": "1", "name": "Alice"})
        
        records = self.db.select("users")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Alice")

    def test_select_method_alias(self):
        """Тест метода select() (алиас для select_records)."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        
        records = self.db.select("users", name="Alice")
        self.assertEqual(len(records), 1)

    def test_update_method_alias(self):
        """Тест метода update() (алиас для update_records)."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        
        count = self.db.update("users", {"name": "Updated"}, id="1")
        self.assertEqual(count, 1)
        
        records = self.db.select("users", id="1")
        self.assertEqual(records[0]["name"], "Updated")

    def test_delete_method_alias(self):
        """Тест метода delete() (алиас для delete_records)."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        
        count = self.db.delete("users", id="1")
        self.assertEqual(count, 1)
        
        records = self.db.select("users")
        self.assertEqual(len(records), 0)

    def test_sort_records(self):
        """Тест сортировки записей."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "3", "name": "Charlie"})
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        sorted_records = self.db.sort_records("users", "id", reverse=False)
        expected_ids = ["1", "2", "3"]
        result_ids = [r["id"] for r in sorted_records]
        self.assertEqual(result_ids, expected_ids)


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
        
        # Проверяем через публичный метод
        tables = self.db.get_table_names()
        self.assertIn("студенты", tables)
        
        # Проверяем структуру через get_table_info
        info = self.db.get_table_info("студенты")
        self.assertEqual(info["columns"], columns)

    def test_insert_and_select_cyrillic(self):
        """Тест вставки и выборки кириллических данных."""
        self.db.create_table("студенты", ("id", "имя", "фамилия"))
        self.db.insert_record("студенты", {"id": "1", "имя": "Иван", "фамилия": "Петров"})
        
        records = self.db.select_records("студенты", имя="Иван")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["фамилия"], "Петров")


if __name__ == "__main__":
    unittest.main()
