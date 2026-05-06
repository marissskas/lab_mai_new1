"""Модульное тестирование базы данных Database."""

import unittest
import sys
import os

# Добавляем путь к src для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.memory import Database


class TestDatabase(unittest.TestCase):
    """Класс для тестирования Database."""
    
    def setUp(self):
        """Подготовка тестовой среды перед каждым тестом."""
        self.db = Database()
    
    def test_create_table_success(self):
        """Тест успешного создания таблицы."""
        self.db.create_table("users", ("id", "name", "email"))
        
        tables = self.db.get_table_names()
        self.assertIn("users", tables)
        
        info = self.db.get_table_info("users")
        self.assertEqual(info["columns"], ("id", "name", "email"))
        self.assertEqual(info["records_count"], 0)
    
    def test_create_table_empty_name(self):
        """Тест создания таблицы с пустым именем."""
        with self.assertRaises(ValueError) as context:
            self.db.create_table("", ("id", "name"))
        self.assertEqual(str(context.exception), "Имя таблицы не может быть пустым")
    
    def test_create_table_no_columns(self):
        """Тест создания таблицы без колонок."""
        with self.assertRaises(ValueError) as context:
            self.db.create_table("users", ())
        self.assertEqual(str(context.exception), "Таблица должна содержать хотя бы одну колонку")
    
    def test_create_table_duplicate(self):
        """Тест создания дублирующей таблицы."""
        self.db.create_table("users", ("id", "name"))
        
        with self.assertRaises(ValueError) as context:
            self.db.create_table("users", ("id", "name"))
        self.assertEqual(str(context.exception), "Таблица 'users' уже существует")
    
    def test_get_table_names_empty(self):
        """Тест получения списка таблиц для пустой БД."""
        self.assertEqual(self.db.get_table_names(), [])
    
    def test_get_table_info_nonexistent(self):
        """Тест получения информации о несуществующей таблице."""
        self.assertIsNone(self.db.get_table_info("nonexistent"))
    
    def test_insert_success(self):
        """Тест успешной вставки записи."""
        self.db.create_table("users", ("id", "name", "age"))
        
        record = {"id": "1", "name": "John Doe", "age": "25"}
        result = self.db.insert("users", record)
        
        self.assertEqual(result, record)
        
        records = self.db.select("users")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], record)
    
    def test_insert_table_not_exists(self):
        """Тест вставки в несуществующую таблицу."""
        with self.assertRaises(ValueError) as context:
            self.db.insert("nonexistent", {"id": "1"})
        self.assertEqual(str(context.exception), "Таблица 'nonexistent' не существует")
    
    def test_insert_missing_field(self):
        """Тест вставки записи с отсутствующим полем."""
        self.db.create_table("users", ("id", "name", "email"))
        
        record = {"id": "1", "name": "John"}
        
        with self.assertRaises(ValueError) as context:
            self.db.insert("users", record)
        self.assertEqual(str(context.exception), "Отсутствует поле 'email'")
    
    def test_insert_extra_field(self):
        """Тест вставки записи с лишним полем."""
        self.db.create_table("users", ("id", "name"))
        
        record = {"id": "1", "name": "John", "extra": "value"}
        
        with self.assertRaises(ValueError) as context:
            self.db.insert("users", record)
        self.assertEqual(str(context.exception), "Поле 'extra' не определено в таблице")
    
    def test_select_no_filters(self):
        """Тест выборки без фильтров."""
        self.db.create_table("users", ("id", "name"))
        
        records_data = [
            {"id": "1", "name": "Alice"},
            {"id": "2", "name": "Bob"},
        ]
        
        for record in records_data:
            self.db.insert("users", record)
        
        result = self.db.select("users")
        self.assertEqual(len(result), 2)
        self.assertEqual(result, records_data)
    
    def test_select_with_filters(self):
        """Тест выборки с фильтрами."""
        self.db.create_table("users", ("id", "name", "age"))
        
        records_data = [
            {"id": "1", "name": "АЛИСА", "age": "19"},
            {"id": "2", "name": "Кирилл", "age": "17"},
            {"id": "3", "name": "Егор", "age": "18"},
        ]
        
        for record in records_data:
            self.db.insert("users", record)
        
        # Фильтр по имени
        result = self.db.select("users", name="Alice")
        self.assertEqual(len(result), 2)
        
        # Фильтр по имени и возрасту
        result = self.db.select("users", name="Alice", age="25")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "1")
    
    def test_select_invalid_filter_field(self):
        """Тест выборки с несуществующим полем фильтра."""
        self.db.create_table("users", ("id", "name"))
        
        with self.assertRaises(ValueError) as context:
            self.db.select("users", invalid_field="value")
        self.assertEqual(str(context.exception), "Поле 'invalid_field' не существует в таблице")
    
    def test_update_success(self):
        """Тест успешного обновления записей."""
        self.db.create_table("users", ("id", "name", "age"))
        
        records_data = [
            {"id": "1", "name": "АЛИСА", "age": "19"},
            {"id": "2", "name": "Кирилл", "age": "17"},
        ]
        
        for record in records_data:
            self.db.insert("users", record)
        
        # Обновление по фильтру
        count = self.db.update("users", {"age": "15"}, name="Alice")
        self.assertEqual(count, 1)
        
        # Проверка результата
        result = self.db.select("users", name="Alice")
        self.assertEqual(result[0]["age"], "15")
        
        # Обновление без фильтра (все записи)
        count = self.db.update("users", {"age": "99"})
        self.assertEqual(count, 2)
        
        result = self.db.select("users")
        for record in result:
            self.assertEqual(record["age"], "99")
    
    def test_update_table_not_exists(self):
        """Тест обновления в несуществующей таблице."""
        with self.assertRaises(ValueError) as context:
            self.db.update("nonexistent", {"field": "value"})
        self.assertEqual(str(context.exception), "Таблица 'nonexistent' не существует")
    
    def test_update_invalid_field(self):
        """Тест обновления несуществующего поля."""
        self.db.create_table("users", ("id", "name"))
        
        with self.assertRaises(ValueError) as context:
            self.db.update("users", {"invalid": "value"})
        self.assertEqual(str(context.exception), "Поле 'invalid' не существует в таблице")
    
    def test_delete_success(self):
        """Тест успешного удаления записей."""
        self.db.create_table("users", ("id", "name", "age"))
        
        records_data = [
            {"id": "1", "name": "АЛИСА", "age": "19"},
            {"id": "2", "name": "Кирилл", "age": "17"},
            {"id": "3", "name": "Егор", "age": "18"},
        ]
        
        for record in records_data:
            self.db.insert("users", record)
        
        # Удаление по фильтру
        count = self.db.delete("users", name="АЛИСА")
        self.assertEqual(count, 2)
        
        result = self.db.select("users")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Кирилл")
        
        # Удаление всех записей
        count = self.db.delete("users")
        self.assertEqual(count, 1)
        
        result = self.db.select("users")
        self.assertEqual(len(result), 0)
    
    def test_delete_table_not_exists(self):
        """Тест удаления из несуществующей таблицы."""
        with self.assertRaises(ValueError) as context:
            self.db.delete("nonexistent")
        self.assertEqual(str(context.exception), "Таблица 'nonexistent' не существует")
    
    def test_delete_invalid_filter_field(self):
        """Тест удаления с несуществующим полем фильтра."""
        self.db.create_table("users", ("id", "name"))
        
        with self.assertRaises(ValueError) as context:
            self.db.delete("users", invalid_field="value")
        self.assertEqual(str(context.exception), "Поле 'invalid_field' не существует в таблице")
    
    def test_multiple_tables(self):
        """Тест работы с несколькими таблицами."""
        # Создаем первую таблицу
        self.db.create_table("users", ("id", "name"))
        self.db.insert("users", {"id": "1", "name": "АЛИСА"})
        
        # Создаем вторую таблицу
        self.db.create_table("products", ("id", "title", "price"))
        self.db.insert("products", {"id": "1", "title": "Book", "price": "100"})
        
        # Проверяем независимость таблиц
        users = self.db.select("users")
        products = self.db.select("products")
        
        self.assertEqual(len(users), 1)
        self.assertEqual(len(products), 1)
        
        # Обновление не влияет на другую таблицу
        self.db.update("users", {"name": "Кирилл"})
        
        users = self.db.select("users")
        products = self.db.select("products")
        
        self.assertEqual(users[0]["name"], "Кирилл")
        self.assertEqual(products[0]["title"], "Book")


if __name__ == "__main__":
    unittest.main()

class TestDatabaseSorting(unittest.TestCase):
    """Тесты для метода сортировки."""
    
    def setUp(self):
        """Подготовка тестовой среды."""
        self.db = Database()
        self.db.create_table("users", ("id", "name", "age"))
        
        self.records = [
            {"id": "3", "name": "АЛИСА", "age": "19"},
            {"id": "1", "name": "Кирилл", "age": "17"},
            {"id": "2", "name": "Егор", "age": "18"},
        ]
        
        for record in self.records:
            self.db.insert("users", record)
    
    def test_sort_by_id_ascending(self):
        """Тест сортировки по ID по возрастанию."""
        sorted_records = self.db.sort_records("users", "id", reverse=False)
        
        expected_ids = ["1", "2", "3"]
        result_ids = [r["id"] for r in sorted_records]
        
        self.assertEqual(result_ids, expected_ids)
    
    def test_sort_by_id_descending(self):
        """Тест сортировки по ID по убыванию."""
        sorted_records = self.db.sort_records("users", "id", reverse=True)
        
        expected_ids = ["3", "2", "1"]
        result_ids = [r["id"] for r in sorted_records]
        
        self.assertEqual(result_ids, expected_ids)
    
    def test_sort_by_name_ascending(self):
        """Тест сортировки по имени по возрастанию."""
        sorted_records = self.db.sort_records("users", "name", reverse=False)
        
        expected_names = ["АЛИСА", "Кирилл", "Егор"]
        result_names = [r["name"] for r in sorted_records]
        
        self.assertEqual(result_names, expected_names)
    
    def test_sort_by_name_descending(self):
        """Тест сортировки по имени по убыванию."""
        sorted_records = self.db.sort_records("users", "name", reverse=True)
        
        expected_names = ["Егор", "Кирилл", "АЛИСА"]
        result_names = [r["name"] for r in sorted_records]
        
        self.assertEqual(result_names, expected_names)
    
    def test_sort_by_age_ascending(self):
        """Тест сортировки по возрасту по возрастанию."""
        sorted_records = self.db.sort_records("users", "age", reverse=False)
        
        expected_ages = ["17", "18", "19"]
        result_ages = [r["age"] for r in sorted_records]
        
        self.assertEqual(result_ages, expected_ages)
    
    def test_sort_by_age_descending(self):
        """Тест сортировки по возрасту по убыванию."""
        sorted_records = self.db.sort_records("users", "age", reverse=True)
        
        expected_ages = ["19", "18", "17"]
        result_ages = [r["age"] for r in sorted_records]
        
        self.assertEqual(result_ages, expected_ages)
    
    def test_sort_table_not_exists(self):
        """Тест сортировки в несуществующей таблице."""
        with self.assertRaises(ValueError) as context:
            self.db.sort_records("nonexistent", "id")
        self.assertEqual(str(context.exception), "Таблица 'nonexistent' не существует")
    
    def test_sort_invalid_field(self):
        """Тест сортировки по несуществующему полю."""
        with self.assertRaises(ValueError) as context:
            self.db.sort_records("users", "invalid_field")
        self.assertEqual(str(context.exception), "Поле 'invalid_field' не существует в таблице")
    
    def test_sort_does_not_modify_original(self):
        """Тест проверяет, что сортировка не изменяет оригинальный порядок записей."""
        # Сохраняем оригинальный порядок
        original_ids = [r["id"] for r in self.db.select("users")]
        
        # Выполняем сортировку
        sorted_records = self.db.sort_records("users", "id", reverse=False)
        
        # Проверяем, что оригинальный порядок не изменился
        current_ids = [r["id"] for r in self.db.select("users")]
        self.assertEqual(original_ids, current_ids)
        