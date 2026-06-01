"""Модуль текстового пользовательского интерфейса."""

from typing import Optional
from .backend.memory import MemoryDatabase
from .backend.file import FileDatabase
from .backend.errors import DatabaseError


class DatabaseApp:
    """Главное приложение."""
    
    def __init__(self):
        self.db = self._select_database()
        self.running = True
    
    def _select_database(self):
        """Выбор типа базы данных."""
        print("\n" + "=" * 50)
        print("ВЫБОР ТИПА БАЗЫ ДАННЫХ")
        print("=" * 50)
        print("1. In-memory (данные в оперативной памяти)")
        print("2. File JSON (сохранение в JSON-файлы)")
        
        choice = input("\nВведите номер (1-2): ").strip()
        
        if choice == "2":
            print("\nИспользуется файловая база данных (данные сохраняются в папке data/)")
            return FileDatabase()
        else:
            print("\nИспользуется in-memory база данных (данные не сохраняются)")
            return MemoryDatabase()
    
    def print_menu(self):
        print("\n" + "=" * 50)
        print("      БАЗА ДАННЫХ СТУДЕНТОВ")
        print("=" * 50)
        print("1. Создать таблицу")
        print("2. Показать таблицы")
        print("3. Добавить студента")
        print("4. Показать всех студентов")
        print("5. Найти студентов")
        print("6. Обновить данные студента")
        print("7. Удалить студента")
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
    
    def read_int(self, prompt: str) -> int:
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Введите целое число")
    
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
    
    def create_table(self):
        print("\n--- СОЗДАНИЕ ТАБЛИЦЫ ---")
        name = self.read_string("Имя таблицы: ")
        
        print("\nСтандартные поля: id, имя, фамилия, возраст, пол")
        use_default = input("Использовать стандартные поля? (y/n): ").strip().lower()
        
        if use_default == 'y':
            columns = ("id", "имя", "фамилия", "возраст", "пол")
        else:
            cols_input = input("Колонки (через пробел): ").strip()
            if not cols_input:
                print("Ошибка. Нужно указать хотя бы одну колонку")
                return
            columns = tuple(cols_input.split())
        
        try:
            self.db.create_table(name, columns)
            print(f"Таблица '{name}' создана")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def show_tables(self):
        print("\n--- ВСЕ ТАБЛИЦЫ ---")
        tables = self.db.get_table_names()
        if not tables:
            print("Нет таблиц")
            return
        for name in tables:
            info = self.db.get_table_info(name)
            print(f"{name}: {info['columns']} ({info['records_count']} записей)")
    
    def insert_record(self):
        table_name = self.select_table()
        if not table_name:
            return
        
        info = self.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
        
        print(f"\n--- ДОБАВЛЕНИЕ ЗАПИСИ В ТАБЛИЦУ '{table_name}' ---")
        record = {}
        
        for col in info['columns']:
            if col == "id":
                value = self.read_string(f"{col}: ")
            elif col == "возраст":
                value = str(self.read_int(f"{col}: "))
            elif col == "пол":
                value = self.read_string(f"{col} (М/Ж): ")
                value = value.upper()
                if value not in ("М", "Ж"):
                    print("Пол должен быть М или Ж. Установлено значение по умолчанию: М")
                    value = "М"
            else:
                value = self.read_string(f"{col}: ")
            record[col] = value
        
        try:
            self.db.insert(table_name, record)
            print("Запись добавлена")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def select_all(self):
        table_name = self.select_table()
        if not table_name:
            return
        print(f"\n--- ВСЕ ЗАПИСИ ТАБЛИЦЫ '{table_name}' ---")
        try:
            records = self.db.select(table_name)
            if not records:
                print("Нет записей")
                return
            
            if "id" in records[0] and "имя" in records[0] and "фамилия" in records[0]:
                print("\n{:<5} {:<15} {:<15} {:<6} {:<3}".format("ID", "Имя", "Фамилия", "Возраст", "Пол"))
                print("-" * 50)
                for rec in records:
                    print("{:<5} {:<15} {:<15} {:<6} {:<3}".format(
                        rec.get("id", ""),
                        rec.get("имя", ""),
                        rec.get("фамилия", ""),
                        rec.get("возраст", ""),
                        rec.get("пол", ""),
                    ))
            else:
                for i, rec in enumerate(records, 1):
                    print(f"{i}. {rec}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def search_records(self):
        table_name = self.select_table()
        if not table_name:
            return
        info = self.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
        
        print(f"\n--- ПОИСК ЗАПИСЕЙ В ТАБЛИЦЕ '{table_name}' ---")
        filters = {}
        for col in info['columns']:
            value = self.read_optional(f"{col} (Enter чтобы пропустить): ")
            if value is not None:
                filters[col] = value
        
        try:
            records = self.db.select(table_name, **filters)
            print(f"\nНайдено: {len(records)}")
            for i, rec in enumerate(records, 1):
                print(f"{i}. {rec}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def update_records(self):
        table_name = self.select_table()
        if not table_name:
            return
        info = self.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
        
        print(f"\n--- ОБНОВЛЕНИЕ ЗАПИСЕЙ В ТАБЛИЦЕ '{table_name}' ---")
        
        print("Введите фильтры (поля для поиска записей):")
        filters = {}
        for col in info['columns']:
            value = self.read_optional(f"  {col} (Enter чтобы пропустить): ")
            if value is not None:
                filters[col] = value
        
        print("\nВведите новые значения:")
        updates = {}
        for col in info['columns']:
            value = self.read_optional(f"  {col} (Enter чтобы не менять): ")
            if value is not None:
                updates[col] = value
        
        if not updates:
            print("Нет полей для обновления")
            return
        
        try:
            count = self.db.update(table_name, updates, **filters)
            print(f"Обновлено записей: {count}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def delete_records(self):
        table_name = self.select_table()
        if not table_name:
            return
        info = self.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
        
        print(f"\n--- УДАЛЕНИЕ ЗАПИСЕЙ ИЗ ТАБЛИЦЫ '{table_name}' ---")
        
        filters = {}
        for col in info['columns']:
            value = self.read_optional(f"{col} (Enter чтобы пропустить): ")
            if value is not None:
                filters[col] = value
        
        if not filters:
            confirm = input("Удалить ВСЕ записи? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Отменено")
                return
        
        try:
            count = self.db.delete(table_name, **filters)
            print(f"Удалено записей: {count}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def table_info(self):
        table_name = self.select_table()
        if not table_name:
            return
        info = self.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
        
        print(f"\n--- ИНФОРМАЦИЯ О ТАБЛИЦЕ '{table_name}' ---")
        print(f"Колонки: {info['columns']}")
        print(f"Количество записей: {info['records_count']}")
    
    def sort_records(self):
        table_name = self.select_table()
        if not table_name:
            return
        info = self.db.get_table_info(table_name)
        if not info:
            print("Ошибка: таблица не найдена")
            return
        
        print(f"\n--- СОРТИРОВКА ЗАПИСЕЙ В ТАБЛИЦЕ '{table_name}' ---")
        print(f"Доступные поля: {info['columns']}")
        
        field = self.read_string("Поле для сортировки: ")
        rev_input = self.read_optional("По убыванию? (y/n): ")
        reverse = rev_input == 'y'
        
        try:
            records = self.db.sort_records(table_name, field, reverse)
            order = "по убыванию" if reverse else "по возрастанию"
            print(f"\nСортировка по полю '{field}' {order}:")
            for i, rec in enumerate(records, 1):
                print(f"{i}. {rec}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def run(self):
        # Автоматически создаём таблицу студентов при запуске
        try:
            from .backend.memory import init_student_table
            init_student_table()
            print("Таблица 'студенты' создана (поля: id, имя, фамилия, возраст, пол)")
        except Exception as e:
            print(f"При создании таблицы студентов: {e}")
        
        while self.running:
            try:
                self.print_menu()
                choice = input("Выберите действие: ").strip()
                
                if choice == "1":
                    self.create_table()
                elif choice == "2":
                    self.show_tables()
                elif choice == "3":
                    self.insert_record()
                elif choice == "4":
                    self.select_all()
                elif choice == "5":
                    self.search_records()
                elif choice == "6":
                    self.update_records()
                elif choice == "7":
                    self.delete_records()
                elif choice == "8":
                    self.table_info()
                elif choice == "9":
                    self.sort_records()
                elif choice == "0":
                    print("\nДо свидания!")
                    self.running = False
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
