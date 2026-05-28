# tests/test_database.py
"""Тесты для абстрактного класса Database."""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.database import Database
from src.db.backend.errors import TableAlreadyExistsError, TableNotFoundError
from src.db.backend.table import Table


class ConcreteDatabase(Database):
    """Конкретная реализация Database для тестирования."""
    
    def __init__(self):
        self._tables = {}
    
    def _table_exists(self, table_name: str) -> bool:
        return table_name in self._tables
    
    def _load_table(self, table_name: str) -> Table:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        return self._tables[table_name]
    
    def _save_table(self, table_name: str, table: Table) -> None:
        self._tables[table_name] = table


class TestDatabase(unittest.TestCase):
    """Тесты для абстрактного класса Database."""
    
    def setUp(self):
        self.db = ConcreteDatabase()
    
    def test_create_table_success(self):
        """Тест успешного создания таблицы."""
        self.db.create_table("users", ("id", "name"))
        self.assertTrue(self.db._table_exists("users"))
    
    def test_create_table_already_exists(self):
        """Тест создания уже существующей таблицы."""
        self.db.create_table("users", ("id", "name"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("users", ("id", "name"))
    
    def test_insert_record(self):
        """Тест вставки записи через абстрактный интерфейс."""
        self.db.create_table("users", ("id", "name"))
        record = {"id": "1", "name": "Alice"}
        self.db.insert_record("users", record)
        
        table = self.db._load_table("users")
        records = table.select()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Alice")
    
    def test_insert_record_table_not_exists(self):
        """Тест вставки в несуществующую таблицу."""
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("nonexistent", {"id": "1"})
    
    def test_select_records(self):
        """Тест выборки записей."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        records = self.db.select_records("users", name="Alice")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], "1")
    
    def test_select_records_table_not_exists(self):
        """Тест выборки из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")
    
    def test_update_records(self):
        """Тест обновления записей."""
        self.db.create_table("users", ("id", "name", "age"))
        self.db.insert_record("users", {"id": "1", "name": "Alice", "age": "20"})
        
        updated = self.db.update_records("users", {"age": "21"}, id="1")
        self.assertEqual(updated, 1)
        
        records = self.db.select_records("users", id="1")
        self.assertEqual(records[0]["age"], "21")
    
    def test_delete_records(self):
        """Тест удаления записей."""
        self.db.create_table("users", ("id", "name"))
        self.db.insert_record("users", {"id": "1", "name": "Alice"})
        self.db.insert_record("users", {"id": "2", "name": "Bob"})
        
        deleted = self.db.delete_records("users", name="Alice")
        self.assertEqual(deleted, 1)
        
        records = self.db.select_records("users")
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
