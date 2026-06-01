"""Модульное тестирование MemoryDatabase."""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.memory import MemoryDatabase, create_record, select_record, Student
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidAgeError,
    DuplicateIDError,
)


class TestMemoryDatabase(unittest.TestCase):
    """Тесты для MemoryDatabase."""

    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table_success(self):
        """Тест успешного создания таблицы."""
        self.db.create_table("студенты", ("id", "имя", "фамилия", "возраст", "пол"))
        tables = self.db.get_table_names()
        self.assertIn("студенты", tables)

    def test_create_table_duplicate(self):
        """Тест создания дублирующей таблицы."""
        self.db.create_table("студенты", ("id", "имя"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("студенты", ("id", "имя"))

    def test_insert_success(self):
        """Тест успешной вставки записи."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        record = {"id": "1", "имя": "Иван", "возраст": "20"}
        result = self.db.insert("студенты", record)
        self.assertEqual(result, record)

    def test_insert_missing_column(self):
        """Тест вставки с отсутствующим полем."""
        self.db.create_table("студенты", ("id", "имя", "email"))
        record = {"id": "1", "имя": "Иван"}
        with self.assertRaises(MissingColumnError):
            self.db.insert("студенты", record)

    def test_select_with_filters(self):
        """Тест выборки с фильтрами."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        result = self.db.select("студенты", id="1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["имя"], "Анна")

    def test_update_success(self):
        """Тест успешного обновления."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        
        count = self.db.update("студенты", {"имя": "Борис"}, id="1")
        self.assertEqual(count, 1)
        
        # Проверяем, что запись обновилась
        result = self.db.select("студенты", id="1")
        self.assertEqual(result[0]["имя"], "Борис")

    def test_delete_success(self):
        """Тест успешного удаления."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        count = self.db.delete("студенты", id="1")
        self.assertEqual(count, 1)
        
        records = self.db.select("студенты")
        self.assertEqual(len(records), 1)

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


class TestStudentInterface(unittest.TestCase):
    """Тесты для интерфейса Student."""

    def setUp(self):
        Student.clear()

    def test_create_record_success(self):
        """Тест создания записи."""
        record = create_record(1, "Иван", "Петров", 20, "М")
        self.assertEqual(record, (1, "Иван", "Петров", 20, "М"))

    def test_create_record_age_negative(self):
        """Тест создания записи с отрицательным возрастом."""
        with self.assertRaises(InvalidAgeError):
            create_record(1, "Иван", "Петров", -5, "М")

    def test_create_record_duplicate_id(self):
        """Тест создания записи с дублирующим ID."""
        create_record(1, "Иван", "Петров", 20, "М")
        with self.assertRaises(DuplicateIDError):
            create_record(1, "Петр", "Сидоров", 22, "М")

    def test_select_record_with_filters(self):
        """Тест выборки записей с фильтрами."""
        create_record(1, "Иван", "Петров", 20, "М")
        create_record(2, "Мария", "Иванова", 19, "Ж")
        
        # Используем именованные аргументы на русском? Нет, функция ожидает английские.
        # Правильный вызов:
        result = select_record(first_name="Иван")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Иван")
        
        # Альтернативный тест с фильтром по фамилии
        result = select_record(second_name="Иванова")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], "Иванова")

    def test_student_len(self):
        """Тест получения количества записей."""
        Student.clear()
        self.assertEqual(len(Student()), 0)
        
        create_record(1, "Иван", "Петров", 20, "М")
        self.assertEqual(len(Student()), 1)


if __name__ == "__main__":
    unittest.main()
