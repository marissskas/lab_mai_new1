import os
import sys
from typing import Optional

from .backend.memory import Database
from .backend.exceptions import DatabaseError, RecordNotFoundError, TableNotFoundError

class ConsoleInterface:
    def __init__(self):
        self.db = Database()
        self.current_table: Optional[str] = None
        self.running = True
    
    def _clear_screen(self):
        """Очистка экрана."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self):
        """Вывод заголовка."""
        self._clear_screen()
        print("=" * 60)
        print("УПРАВЛЕНИЕ БАЗОЙ ДАННЫХ СТУДЕНТОВ")
        print("=" * 60)
        print(f"Текущая таблица: {self.current_table or 'не выбрана'}")
        print("-" * 60)
    
    def _print_main_menu(self):
        """Главное меню."""
        print("\nГЛАВНОЕ МЕНЮ:")
        print(" 1. Управление таблицами")
        print(" 2. Работа с записями")
        print(" 0. Выход")
        print("-" * 60)
    
    def _print_table_menu(self):
        """Меню таблиц."""
        print("\nМЕНЮ ТАБЛИЦ:")
        print(" 1. Создать таблицу")
        print(" 2. Выбрать таблицу")
        print(" 3. Список таблиц")
        print(" 4. Переименовать таблицу")
        print(" 5. Удалить таблицу")
        print(" 6. Очистить таблицу")
        print(" 0. Назад")
        print("-" * 60)
    
    def _print_record_menu(self):
        """Меню записей."""
        print("\nМЕНЮ ЗАПИСЕЙ:")
        print(" 1. Добавить запись")
        print(" 2. Все записи")
        print(" 3. Поиск по ID")
        print(" 4. Расширенный поиск")
        print(" 5. Обновить запись")
        print(" 6. Удалить запись")
        print(" 0. Назад")
        print("-" * 60)
    
    def _read_int(self, prompt: str, allow_none: bool = False) -> int | None:
        """Чтение целого числа."""
        while True:
            try:
                value = input(prompt).strip()
                if allow_none and value == "":
                    return None
                return int(value)
            except ValueError:
                print("Ошибка: введите целое число")
    
    def _read_optional_int(self, prompt: str) -> Optional[int]:
        """Чтение опционального целого числа."""
        return self._read_int(prompt, allow_none=True)
    
    def _read_string(self, prompt: str, required: bool = True) -> Optional[str]:
        """Чтение строки."""
        while True:
            value = input(prompt).strip()
            if required and not value:
                print("Поле не может быть пустым!")
                continue
            return value if value else None
    
    def _read_choice(self, prompt: str, valid: list) -> str:
        """Чтение выбора из меню."""
        while True:
            choice = input(prompt).strip()
            if choice in valid:
                return choice
            print(f"Выберите: {', '.join(valid)}")
    
    def _print_records(self, records: list):
        """Вывод записей."""
        if not records:
            print("\nЗаписей не найдено")
            return
        
        print("\n" + "-" * 70)
        for r in records:
            print(f"ID: {r[0]}, Имя: {r[1]}, Фамилия: {r[2]}, Возраст: {r[3]}, Пол: {r[4]}")
        print("-" * 70)
        print(f"Всего: {len(records)}")
    
    def _handle_tables(self):
        """Обработка меню таблиц."""
        while True:
            try:
                self._print_header()
                self._print_table_menu()
                
                choice = self._read_choice("Выберите действие: ", ['1','2','3','4','5','6','0'])
                
                if choice == "1":
                    self._create_table()
                elif choice == "2":
                    self._select_table()
                elif choice == "3":
                    self._list_tables()
                elif choice == "4":
                    self._rename_table()
                elif choice == "5":
                    self._drop_table()
                elif choice == "6":
                    self._clear_table()
                elif choice == "0":
                    break
                    
            except DatabaseError as e:
                print(f"Ошибка: {e}")
                input("Enter...")
    
    def _handle_records(self):
        """Обработка меню записей."""
        if not self.current_table:
            print("Сначала выберите таблицу!")
            input("Enter...")
            return
        
        while True:
            try:
                self._print_header()
                print(f"\nТаблица: {self.current_table}")
                self._print_record_menu()
                
                choice = self._read_choice("Выберите действие: ", ['1','2','3','4','5','6','0'])
                
                table = self.db.get_table(self.current_table)
                
                if choice == "1":
                    self._create_record(table)
                elif choice == "2":
                    self._show_all_records(table)
                elif choice == "3":
                    self._find_by_id(table)
                elif choice == "4":
                    self._advanced_search(table)
                elif choice == "5":
                    self._update_record(table)
                elif choice == "6":
                    self._delete_record(table)
                elif choice == "0":
                    break
                    
            except DatabaseError as e:
                print(f"Ошибка: {e}")
                input("Enter...")
    
    def _create_table(self):
        """Создание таблицы."""
        print("\n--- СОЗДАНИЕ ТАБЛИЦЫ ---")
        name = self._read_string("Имя таблицы: ")
        
        if name:
            self.db.create_table(name)
            print(f"Таблица '{name}' создана")
            input("Enter...")
    
    def _select_table(self):
        """Выбор таблицы."""
        print("\n--- ВЫБОР ТАБЛИЦЫ ---")
        tables = self.db.list_tables()
        
        if not tables:
            print("Нет таблиц")
            input("Enter...")
            return
        
        for i, table in enumerate(tables, 1):
            count = len(self.db.get_table(table))
            print(f"{i}. {table} ({count} записей)")
        
        choice = input("Введите имя или номер: ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(tables):
                self.current_table = tables[idx]
                self.db.set_current(self.current_table)
                print(f"Текущая таблица: {self.current_table}")
            else:
                print("Неверный номер")
        else:
            if choice in tables:
                self.current_table = choice
                self.db.set_current(self.current_table)
                print(f"Текущая таблица: {self.current_table}")
            else:
                print(f"Таблица '{choice}' не найдена")
        
        input("Enter...")
    
    def _list_tables(self):
        """Список таблиц."""
        print("\n--- СПИСОК ТАБЛИЦ ---")
        tables = self.db.get_tables_with_counts()
        
        if not tables:
            print("Таблицы отсутствуют")
        else:
            for name, count in tables:
                marker = "→ " if name == self.current_table else "  "
                print(f"{marker}{name}: {count} записей")
        
        input("Enter...")
    
    def _rename_table(self):
        """Переименование таблицы."""
        print("\n--- ПЕРЕИМЕНОВАНИЕ ТАБЛИЦЫ ---")
        old_name = self._read_string("Текущее имя: ")
        new_name = self._read_string("Новое имя: ")
        
        if old_name and new_name:
            self.db.rename_table(old_name, new_name)
            print(f"Таблица переименована в '{new_name}'")
            input("Enter...")
    
    def _drop_table(self):
        """Удаление таблицы."""
        print("\n--- УДАЛЕНИЕ ТАБЛИЦЫ ---")
        name = self._read_string("Имя таблицы: ")
        
        if name:
            confirm = input(f"Удалить '{name}'? (y/n): ").strip().lower()
            if confirm == 'y':
                self.db.drop_table(name)
                print(f"Таблица '{name}' удалена")
            else:
                print("Удаление отменено")
        
        input("Enter...")
    
    def _clear_table(self):
        """Очистка таблицы."""
        print("\n--- ОЧИСТКА ТАБЛИЦЫ ---")
        name = self._read_string("Имя таблицы: ")
        
        try:
            table = self.db.get_table(name)
            count = table.count()
            
            if count == 0:
                print("Таблица уже пуста")
            else:
                confirm = input(f"Удалить все {count} записей? (y/n): ").strip().lower()
                if confirm == 'y':
                    table.clear()
                    print("Таблица очищена")
                else:
                    print("Очистка отменена")
        
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")
        
        input("Enter...")
    
    def _create_record(self, table):
        """Создание записи."""
        print("\n--- ДОБАВЛЕНИЕ ЗАПИСИ ---")
        print("(ID можно не указывать - сгенерируется автоматически)")
        
        try:
            student_id = self._read_optional_int("ID студента: ")
            first_name = self._read_string("Имя: ")
            second_name = self._read_string("Фамилия: ")
            age = self._read_int("Возраст: ")
            sex = self._read_string("Пол (м/ж): ")
            
            record = table.create_record(student_id, first_name, second_name, age, sex)
            print(f"Запись добавлена: ID={record[0]}, {record[1]} {record[2]}")
            
        except ValueError as e:
            print(f"Ошибка: {e}")
        
        input("Enter...")
    
    def _show_all_records(self, table):
        """Все записи."""
        print("\n--- ВСЕ ЗАПИСИ ---")
        records = table.select_record()
        self._print_records(records)
        input("Enter...")
    
    def _find_by_id(self, table):
        """Поиск по ID."""
        print("\n--- ПОИСК ПО ID ---")
        record_id = self._read_int("Введите ID: ")
        
        try:
            record = table.get_by_id(record_id)
            self._print_records([record])
        except RecordNotFoundError as e:
            print(f"Ошибка: {e}")
        
        input("Enter...")
    
    def _advanced_search(self, table):
        """Расширенный поиск."""
        print("\n--- РАСШИРЕННЫЙ ПОИСК ---")
        print("Оставьте поле пустым для пропуска")
        
        try:
            filters = {}
            
            student_id = self._read_optional_int("ID: ")
            if student_id is not None:
                filters['student_id'] = student_id
            
            first_name = input("Имя: ").strip()
            if first_name:
                filters['first_name'] = first_name
            
            second_name = input("Фамилия: ").strip()
            if second_name:
                filters['second_name'] = second_name
            
            age = self._read_optional_int("Возраст: ")
            if age is not None:
                filters['age'] = age
            
            sex = input("Пол (м/ж): ").strip()
            if sex:
                filters['sex'] = sex
            
            records = table.select_record(**filters)
            self._print_records(records)
            
        except ValueError as e:
            print(f"Ошибка: {e}")
        
        input("Enter...")
    
    def _update_record(self, table):
        """Обновление записи."""
        print("\n--- ОБНОВЛЕНИЕ ЗАПИСИ ---")
        
        record_id = self._read_int("ID записи: ")
        
        try:
            current = table.get_by_id(record_id)
            print(f"Текущие данные: {current}")
            print("\nНовые данные (Enter - без изменений):")
            
            updates = {}
            
            first_name = input("Имя: ").strip()
            if first_name:
                updates['first_name'] = first_name
            
            second_name = input("Фамилия: ").strip()
            if second_name:
                updates['second_name'] = second_name
            
            age = self._read_optional_int("Возраст: ")
            if age is not None:
                updates['age'] = age
            
            sex = input("Пол (м/ж): ").strip()
            if sex:
                updates['sex'] = sex
            
            if updates:
                record = table.update_record(record_id, **updates)
                print(f"Запись обновлена: {record}")
            else:
                print("Изменений нет")
            
        except (RecordNotFoundError, ValueError) as e:
            print(f"Ошибка: {e}")
        
        input("Enter...")
    
    def _delete_record(self, table):
        """Удаление записи."""
        print("\n--- УДАЛЕНИЕ ЗАПИСИ ---")
        
        record_id = self._read_int("ID записи: ")
        
        try:
            record = table.get_by_id(record_id)
            print(f"Запись: {record}")
            
            confirm = input("Удалить? (y/n): ").strip().lower()
            if confirm == 'y':
                table.delete_record(record_id)
                print("Запись удалена")
            else:
                print("Удаление отменено")
            
        except RecordNotFoundError as e:
            print(f"Ошибка: {e}")
        
        input("Enter...")
    
    def run(self):
        """Основной цикл."""
        try:
            while self.running:
                self._print_header()
                self._print_main_menu()
                
                choice = self._read_choice("Выберите действие: ", ['1','2','0'])
                
                if choice == "1":
                    self._handle_tables()
                elif choice == "2":
                    self._handle_records()
                elif choice == "0":
                    print("Выход")
                    self.running = False
                    sys.exit(0)
                    
        except KeyboardInterrupt:
            print("\nВыход")
            sys.exit(0)