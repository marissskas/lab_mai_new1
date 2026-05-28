# src/db/tui.py
"""Модуль текстового пользовательского интерфейса."""

from typing import Optional
from abc import ABC, abstractmethod

from .backend.memory_db import MemoryDatabase
from .backend.file_db import FileDatabase
from .backend.errors import DatabaseError


class Menu(ABC):
    @abstractmethod
    def execute(self, app: "DatabaseApp") -> None:
        pass


class CreateTableMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        print("\n--- СОЗДАНИЕ ТАБЛИЦЫ ---")
        name = app.read_string("Имя таблицы: ")
        cols_input = input("Колонки (через пробел): ").strip()
        if not cols_input:
            print("Ошибка. Нужно указать хотя бы одну колонку")
            return
        columns = tuple(cols_input.split())
        try:
            app.db.create_table(name, columns)
            print(f"Таблица '{name}' создана")
        except Exception as e:
            print(f"Ошибка: {e}")


class ShowTablesMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        print("\n--- ВСЕ ТАБЛИЦЫ ---")
        tables = app.db.get_table_names()
        if not tables:
            print("Нет таблиц")
            return
        for name in tables:
            info = app.db.get_table_info(name)
            print(f"{name}: {info['columns']} ({info['records_count']} записей)")


class InsertRecordMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        table_name = app.select_table()
        if not table_name:
            return
        
        info = app.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
        
        print(f"\n--- ДОБАВЛЕНИЕ ЗАПИСИ В ТАБЛИЦУ '{table_name}' ---")
        record = {}
        for col in info['columns']:
            value = app.read_string(f"{col}: ")
            record[col] = value
        
        try:
            app.db.insert(table_name, record)
            print("Запись добавлена")
        except Exception as e:
            print(f"Ошибка: {e}")


class SelectAllMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        table_name = app.select_table()
        if not table_name:
            return
        print(f"\n--- ВСЕ ЗАПИСИ ТАБЛИЦЫ '{table_name}' ---")
        try:
            records = app.db.select(table_name)
            if not records:
                print("Нет записей")
                return
            for i, rec in enumerate(records, 1):
                print(f"{i}. {rec}")
        except Exception as e:
            print(f"Ошибка: {e}")


class SearchRecordsMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        table_name = app.select_table()
        if not table_name:
            return
        info = app.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
            
        print(f"\n--- ПОИСК В ТАБЛИЦЕ '{table_name}' ---")
        filters = {}
        for col in info['columns']:
            value = app.read_optional(f"{col} (Enter чтобы пропустить): ")
            if value is not None:
                filters[col] = value
        
        try:
            records = app.db.select(table_name, **filters)
            print(f"\nНайдено: {len(records)}")
            for i, rec in enumerate(records, 1):
                print(f"{i}. {rec}")
        except Exception as e:
            print(f"Ошибка: {e}")


class UpdateRecordsMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        table_name = app.select_table()
        if not table_name:
            return
        info = app.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
            
        print(f"\n--- ОБНОВЛЕНИЕ В ТАБЛИЦЕ '{table_name}' ---")
        
        print("Введите фильтры (поля для поиска записей):")
        filters = {}
        for col in info['columns']:
            value = app.read_optional(f"  {col} (Enter чтобы пропустить): ")
            if value is not None:
                filters[col] = value
        
        print("\nВведите новые значения:")
        updates = {}
        for col in info['columns']:
            value = app.read_optional(f"  {col} (Enter чтобы не менять): ")
            if value is not None:
                updates[col] = value
        
        if not updates:
            print("Нет полей для обновления")
            return
        
        try:
            count = app.db.update(table_name, updates, **filters)
            print(f"Обновлено записей: {count}")
        except Exception as e:
            print(f"Ошибка: {e}")


class DeleteRecordsMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        table_name = app.select_table()
        if not table_name:
            return
        info = app.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
            
        print(f"\n--- УДАЛЕНИЕ ИЗ ТАБЛИЦЫ '{table_name}' ---")
        
        filters = {}
        for col in info['columns']:
            value = app.read_optional(f"{col} (Enter чтобы пропустить): ")
            if value is not None:
                filters[col] = value
        
        if not filters:
            confirm = input("Удалить ВСЕ записи? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Отменено")
                return
        
        try:
            count = app.db.delete(table_name, **filters)
            print(f"Удалено записей: {count}")
        except Exception as e:
            print(f"Ошибка: {e}")


class TableInfoMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        table_name = app.select_table()
        if not table_name:
            return
        info = app.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
            
        print(f"\n--- ИНФОРМАЦИЯ О ТАБЛИЦЕ '{table_name}' ---")
        print(f"Колонки: {info['columns']}")
        print(f"Записей: {info['records_count']}")


class SortRecordsMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        table_name = app.select_table()
        if not table_name:
            return
        info = app.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
            
        print(f"\n--- СОРТИРОВКА ТАБЛИЦЫ '{table_name}' ---")
        print(f"Доступные поля: {info['columns']}")
        
        field = app.read_string("Поле для сортировки: ")
        rev_input = app.read_optional("По убыванию? (y/n): ")
        reverse = rev_input == 'y'
        
        try:
            records = app.db.sort_records(table_name, field, reverse)
            order = "по убыванию" if reverse else "по возрастанию"
            print(f"\nСортировка по '{field}' {order}:")
            for i, rec in enumerate(records, 1):
                print(f"{i}. {rec}")
        except Exception as e:
            print(f"Ошибка: {e}")


class ExitMenu(Menu):
    def execute(self, app: "DatabaseApp") -> None:
        print("\nДо свидания!")
        app.running = False


class DatabaseApp:
    def __init__(self):
        self.db = self._select_database()
        self.running = True
        self.menus = {
            "1": CreateTableMenu(),
            "2": ShowTablesMenu(),
            "3": InsertRecordMenu(),
            "4": SelectAllMenu(),
            "5": SearchRecordsMenu(),
            "6": UpdateRecordsMenu(),
            "7": DeleteRecordsMenu(),
            "8": TableInfoMenu(),
            "9": SortRecordsMenu(),
            "0": ExitMenu(),
        }

    def _select_database(self):
        """Выбор типа базы данных при запуске."""
        print("\n" + "=" * 50)
        print("ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ")
        print("=" * 50)
        print("\nВыберите тип базы данных:")
        print("1. In-memory (данные не сохраняются после выхода)")
        print("2. File database (JSON) (данные сохраняются)")

        choice = input("\nВведите номер (1 или 2): ").strip()

        if choice == "2":
            print("\nИнициализация файловой базы данных...")
            return FileDatabase()
        else:
            print("\nИнициализация in-memory базы данных...")
            return MemoryDatabase()

    def print_menu(self):
        print("\n" + "=" * 50)
        print("      БАЗА ДАННЫХ")
        print("=" * 50)
        print("1. Создать таблицу")
        print("2. Показать таблицы")
        print("3. Добавить запись")
        print("4. Показать все записи")
        print("5. Найти записи")
        print("6. Обновить записи")
        print("7. Удалить записи")
        print("8. Информация о таблице")
        print("9. Сортировка")
        print("0. Выход")
        print("-" * 50)

    def read_string(self, prompt: str) -> str:
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Поле не может быть пустым")

    def read_optional(self, prompt: str) -> Optional[str]:
        value = input(prompt).strip()
        return value if value else None

    def select_table(self) -> Optional[str]:
        tables = self.db.get_table_names()
        if not tables:
            print("Нет таблиц. Сначала создайте таблицу.")
            return None
        print("\nДоступные таблицы:")
        for i, name in enumerate(tables, 1):
            info = self.db.get_table_info(name)
            if info:
                print(f"  {i}. {name} ({info['records_count']} записей)")
            else:
                print(f"  {i}. {name}")
        try:
            choice = input("Выберите номер: ").strip()
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(tables):
                return tables[idx]
            print("Неверный номер")
            return None
        except ValueError:
            print("Введите число")
            return None

    def run(self):
        while self.running:
            try:
                self.print_menu()
                choice = input("Выберите действие: ").strip()
                if choice in self.menus:
                    self.menus[choice].execute(self)
                elif choice:
                    print("Неизвестная команда. Введите номер от 0 до 9.")
            except KeyboardInterrupt:
                print("\n\nДо свидания!")
                break
            except Exception as e:
                print(f"Непредвиденная ошибка: {e}")


def run():
    app = DatabaseApp()
    app.run()
