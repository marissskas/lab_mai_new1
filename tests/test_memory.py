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
        # Все значения хранятся как строки
        expected = {"id": "1", "имя": "Иван", "возраст": "20"}
        self.assertEqual(result, expected)

    def test_insert_missing_column(self):
        """Тест вставки с отсутствующим полем."""
        self.db.create_table("студенты", ("id", "имя", "email"))
        record = {"id": "1", "имя": "Иван"}
        with self.assertRaises(MissingColumnError):
            self.db.insert("студенты", record)

    def test_insert_extra_column(self):
        """Тест вставки с лишним полем."""
        self.db.create_table("студенты", ("id", "имя"))
        record = {"id": "1", "имя": "Иван", "лишнее": "поле"}
        with self.assertRaises(UnknownColumnError):
            self.db.insert("студенты", record)

    def test_select_all(self):
        """Тест выборки всех записей."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        result = self.db.select("студенты")
        self.assertEqual(len(result), 2)

    def test_select_with_filters(self):
        """Тест выборки с фильтрами."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        result = self.db.select("студенты", id="1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["имя"], "Анна")

    def test_select_with_unknown_filter(self):
        """Тест выборки с неизвестным полем фильтра."""
        self.db.create_table("студенты", ("id", "имя"))
        with self.assertRaises(UnknownColumnError):
            self.db.select("студенты", неизвестное="значение")

    def test_update_success(self):
        """Тест успешного обновления."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        
        count = self.db.update("студенты", {"имя": "Борис"}, id="1")
        self.assertEqual(count, 1)
        
        result = self.db.select("студенты", id="1")
        self.assertEqual(result[0]["имя"], "Борис")

    def test_update_with_unknown_field(self):
        """Тест обновления с неизвестным полем."""
        self.db.create_table("студенты", ("id", "имя"))
        with self.assertRaises(UnknownColumnError):
            self.db.update("студенты", {"неизвестное": "значение"}, id="1")

    def test_delete_success(self):
        """Тест успешного удаления."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        count = self.db.delete("студенты", id="1")
        self.assertEqual(count, 1)
        
        records = self.db.select("студенты")
        self.assertEqual(len(records), 1)

    def test_delete_all(self):
        """Тест удаления всех записей."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        count = self.db.delete("студенты")
        self.assertEqual(count, 2)
        
        records = self.db.select("студенты")
        self.assertEqual(len(records), 0)

    def test_sort_records_ascending(self):
        """Тест сортировки по возрастанию (строковая сортировка)."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "3", "имя": "Вера"})
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        
        sorted_records = self.db.sort_records("студенты", "id", reverse=False)
        # ID хранятся как строки, поэтому сортируются строки
        expected_ids = ["1", "2", "3"]
        result_ids = [r["id"] for r in sorted_records]
        self.assertEqual(result_ids, expected_ids)

    def test_sort_records_descending(self):
        """Тест сортировки по убыванию (строковая сортировка)."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        self.db.insert("студенты", {"id": "2", "имя": "Борис"})
        self.db.insert("студенты", {"id": "3", "имя": "Вера"})
        
        sorted_records = self.db.sort_records("студенты", "id", reverse=True)
        # ID хранятся как строки, поэтому сортируются строки
        expected_ids = ["3", "2", "1"]
        result_ids = [r["id"] for r in sorted_records]
        self.assertEqual(result_ids, expected_ids)

    def test_sort_records_numeric_field_as_string(self):
        """Тест сортировки числового поля, хранящегося как строка."""
        self.db.create_table("товары", ("id", "цена"))
        self.db.insert("товары", {"id": "1", "цена": "100"})
        self.db.insert("товары", {"id": "2", "цена": "20"})
        self.db.insert("товары", {"id": "3", "цена": "300"})
        
        # Строковая сортировка: "100", "20", "300" (а не числовая)
        sorted_records = self.db.sort_records("товары", "цена", reverse=False)
        expected_prices = ["100", "20", "300"]
        result_prices = [r["цена"] for r in sorted_records]
        self.assertEqual(result_prices, expected_prices)

    def test_sort_with_unknown_field(self):
        """Тест сортировки по неизвестному полю."""
        self.db.create_table("студенты", ("id", "имя"))
        with self.assertRaises(UnknownColumnError):
            self.db.sort_records("студенты", "неизвестное")

    def test_get_table_info(self):
        """Тест получения информации о таблице."""
        self.db.create_table("студенты", ("id", "имя"))
        self.db.insert("студенты", {"id": "1", "имя": "Анна"})
        
        info = self.db.get_table_info("студенты")
        self.assertEqual(info["name"], "студенты")
        self.assertEqual(info["columns"], ("id", "имя"))
        self.assertEqual(info["records_count"], 1)

    def test_get_nonexistent_table_info(self):
        """Тест получения информации о несуществующей таблице."""
        info = self.db.get_table_info("несуществующая")
        self.assertIsNone(info)

    def test_select_from_nonexistent_table(self):
        """Тест выборки из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.select("несуществующая")

    def test_insert_into_nonexistent_table(self):
        """Тест вставки в несуществующую таблицу."""
        with self.assertRaises(TableNotFoundError):
            self.db.insert("несуществующая", {"id": "1"})


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

    def test_select_record_with_id_filter(self):
        """Тест выборки записей с фильтром по ID."""
        create_record(1, "Иван", "Петров", 20, "М")
        create_record(2, "Мария", "Иванова", 19, "Ж")
        
        result = select_record(student_id=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Иван")
        self.assertEqual(result[0][0], 1)  # ID как int

    def test_select_record_with_first_name_filter(self):
        """Тест выборки записей с фильтром по имени."""
        create_record(1, "Иван", "Петров", 20, "М")
        create_record(2, "Мария", "Иванова", 19, "Ж")
        
        result = select_record(first_name="Иван")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Иван")

    def test_select_record_with_second_name_filter(self):
        """Тест выборки записей с фильтром по фамилии."""
        create_record(1, "Иван", "Петров", 20, "М")
        create_record(2, "Мария", "Иванова", 19, "Ж")
        
        result = select_record(second_name="Иванова")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], "Иванова")

    def test_select_record_with_age_filter(self):
        """Тест выборки записей с фильтром по возрасту."""
        create_record(1, "Иван", "Петров", 20, "М")
        create_record(2, "Мария", "Иванова", 19, "Ж")
        
        result = select_record(age=19)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Мария")
        self.assertEqual(result[0][3], 19)  # Возраст как int

    def test_select_record_with_sex_filter(self):
        """Тест выборки записей с фильтром по полу."""
        create_record(1, "Иван", "Петров", 20, "М")
        create_record(2, "Мария", "Иванова", 19, "Ж")
        
        result = select_record(sex="Ж")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Мария")

    def test_select_record_multiple_filters(self):
        """Тест выборки записей с несколькими фильтрами."""
        create_record(1, "Иван", "Петров", 20, "М")
        create_record(2, "Иван", "Сидоров", 22, "М")
        
        result = select_record(first_name="Иван", second_name="Петров")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], "Петров")

    def test_select_record_no_filters(self):
        """Тест выборки всех записей."""
        create_record(1, "Иван", "Петров", 20, "М")
        create_record(2, "Мария", "Иванова", 19, "Ж")
        
        result = select_record()
        self.assertEqual(len(result), 2)

    def test_student_len(self):
        """Тест получения количества записей."""
        Student.clear()
        self.assertEqual(len(Student()), 0)
        
        create_record(1, "Иван", "Петров", 20, "М")
        self.assertEqual(len(Student()), 1)
        
        create_record(2, "Мария", "Иванова", 19, "Ж")
        self.assertEqual(len(Student()), 2)

    def test_student_clear(self):
        """Тест очистки таблицы студентов."""
        create_record(1, "Иван", "Петров", 20, "М")
        self.assertEqual(len(Student()), 1)
        
        Student.clear()
        self.assertEqual(len(Student()), 0)


if __name__ == "__main__":
    unittest.main()
