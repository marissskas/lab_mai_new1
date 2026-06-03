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

    def test_table_not_found_error(self):
        """Тест ошибки при обращении к несуществующей таблице."""
        with self.assertRaises(TableNotFoundError):
            self.db.select("несуществующая_таблица")
        
        with self.assertRaises(TableNotFoundError):
            self.db.insert("несуществующая_таблица", {"id": "1"})
        
        with self.assertRaises(TableNotFoundError):
            self.db.update("несуществующая_таблица", {"field": "value"})
        
        with self.assertRaises(TableNotFoundError):
            self.db.delete("несуществующая_таблица")
        
        with self.assertRaises(TableNotFoundError):
            self.db.sort_records("несуществующая_таблица", "id")

    def test_insert_success(self):
        """Тест успешной вставки записи (с учётом преобразования типов)."""
        self.db.create_table("студенты", ("id", "имя", "возраст"))
        record = {"id": "1", "имя": "Иван", "возраст": "20"}
        result = self.db.insert("студенты", record)
        
        # После вставки числа должны стать int
        expected = {"id": 1, "имя": "Иван", "возраст": 20}
        self.assertEqual(result, expected)
        
        # Проверяем, что запись действительно сохранилась с правильными типами
        records = self.db.select("студенты")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 1)
        self.assertEqual(records[0]["возраст"], 20)

    def test_insert_missing_column(self):
        """Тест вставки с отсутствующим полем."""
        self.db.create_table("студенты", ("id", "имя", "email"))
        record = {"id": "1", "имя": "Иван"}
        with self.assertRaises(MissingColumnError):
            self.db.insert("студенты", record)

    def test_insert_extra_column(self):
        """Тест вставки с лишним полем."""
        self.db.create_table("студенты", ("id", "имя"))
        record = {"id": "1", "имя": "Иван", "лишнее": "значение"}
        with self.assertRaises(UnknownColumnError):
            self.db.insert("студенты", record)

    def test_select_with_filters(self):
        """Тест выборки с фильтрами (фильтры работают со строковыми значениями)."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        # Фильтр по id как строке (так работает ввод пользователя)
        result = self.db.select("студенты", id="1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["имя"], "Анна")
        
        # Фильтр по id как числу (тоже должно работать)
        result = self.db.select("студенты", id=1)
        self.assertEqual(len(result), 1)

    def test_select_invalid_filter_column(self):
        """Тест выборки с несуществующим полем фильтра."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        
        # Должен быть выброшен UnknownColumnError
        with self.assertRaises(UnknownColumnError):
            self.db.select("студенты", несуществующее="значение")

    def test_update_success(self):
        """Тест успешного обновления."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        
        count = self.db.update("студенты", {"имя": "Борис"}, id="1")
        self.assertEqual(count, 1)
        
        result = self.db.select("студенты", id="1")
        self.assertEqual(result[0]["имя"], "Борис")

    def test_update_invalid_column(self):
        """Тест обновления с несуществующим полем."""
        self.db.create_table("студенты", ("id", "имя"))
        with self.assertRaises(UnknownColumnError):
            self.db.update("студенты", {"несуществующее": "значение"})

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
        """Тест сортировки по возрастанию (числовая сортировка)."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "3", "имя": "Вера"})
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        sorted_records = self.db.sort_records("студенты", "id", reverse=False)
        # После преобразования типов id должны быть int, а не str
        expected_ids = [1, 2, 3]
        result_ids = [r["id"] for r in sorted_records]
        self.assertEqual(result_ids, expected_ids)

    def test_sort_records_descending(self):
        """Тест сортировки по убыванию."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "3", "имя": "Вера"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        sorted_records = self.db.sort_records("студенты", "id", reverse=True)
        expected_ids = [3, 2, 1]
        result_ids = [r["id"] for r in sorted_records]
        self.assertEqual(result_ids, expected_ids)

    def test_sort_invalid_field(self):
        """Тест сортировки по несуществующему полю."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        
        with self.assertRaises(UnknownColumnError):
            self.db.sort_records("студенты", "несуществующее_поле")


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
        
        result = select_record(first_name="Иван")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Иван")

    def test_student_len(self):
        """Тест получения количества записей."""
        Student.clear()
        self.assertEqual(len(Student()), 0)
        
        create_record(1, "Иван", "Петров", 20, "М")
        self.assertEqual(len(Student()), 1)


if __name__ == "__main__":
    unittest.main()
