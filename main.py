"""
База данных
Лабораторная работа №2
Группа: 113bv-25
"""

from typing import Any, Optional

# ============================================================
# БАЗА ДАННЫХ (хранилище таблиц)
# ============================================================

class Database:
    """Класс для работы с базой данных в памяти."""
    
    def __init__(self):
        # Структура: {имя_таблицы: {"columns": (col1, col2,...), "records": [записи]}}
        self._tables = {}
    
    def create_table(self, table_name: str, columns: tuple) -> None:
        """Создать новую таблицу."""
        if not table_name or not table_name.strip():
            raise ValueError("Имя таблицы не может быть пустым")
        
        if not columns:
            raise ValueError("Таблица должна содержать хотя бы одну колонку")
        
        if table_name in self._tables:
            raise ValueError(f"Таблица '{table_name}' уже существует")
        
        self._tables[table_name] = {
            "columns": columns,
            "records": []
        }
        print(f" Таблица '{table_name}' создана. Колонки: {columns}")
    
    def get_table_names(self) -> list:
        """Возвращает список всех таблиц."""
        return list(self._tables.keys())
    
    def get_table_info(self, table_name: str) -> Optional[dict]:
        """Возвращает информацию о таблице."""
        if table_name not in self._tables:
            return None
        table = self._tables[table_name]
        return {
            "columns": table["columns"],
            "records_count": len(table["records"])
        }
    
    def insert(self, table_name: str, record: dict) -> dict:
        """Добавляет запись в таблицу."""
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует")
        
        table = self._tables[table_name]
        columns = table["columns"]
        
        
        for col in columns:
            if col not in record:
                raise ValueError(f"Отсутствует поле '{col}'")
        
        
        for col in record:
            if col not in columns:
                raise ValueError(f"Поле '{col}' не определено в таблице")
        
        table["records"].append(record.copy())
        return record.copy()
    
    def select(self, table_name: str, **filters) -> list:
        """Рассматривает записи с фильтрацией."""
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует")
        
        table = self._tables[table_name]
        records = table["records"]
        columns = table["columns"]
        
        
        for key in filters:
            if key not in columns:
                raise ValueError(f"Поле '{key}' не существует в таблице")
        
        if not filters:
            return [r.copy() for r in records]
        
        result = []
        for record in records:
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                result.append(record.copy())
        
        return result
    
    def update(self, table_name: str, updates: dict, **filters) -> int:
        """Обновление записей по фильтру."""
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует")
        
        table = self._tables[table_name]
        columns = table["columns"]
        
        
        for key in updates:
            if key not in columns:
                raise ValueError(f"Поле '{key}' не существует в таблице")
        
        
        for key in filters:
            if key not in columns:
                raise ValueError(f"Поле '{key}' не существует в таблице")
        
        updated = 0
        for record in table["records"]:
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                record.update(updates)
                updated += 1
        
        return updated
    
    def delete(self, table_name: str, **filters) -> int:
        """Удалить запись по фильтру."""
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует")
        
        table = self._tables[table_name]
        columns = table["columns"]
        
        
        for key in filters:
            if key not in columns:
                raise ValueError(f"Поле '{key}' не существует в таблице")
        
        if not filters:
            count = len(table["records"])
            table["records"] = []
            return count
        
        new_records = []
        deleted = 0
        for record in table["records"]:
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                deleted += 1
            else:
                new_records.append(record)
        
        table["records"] = new_records
        return deleted


# ============================================================
# ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС
# ============================================================

def print_menu():
    """Выводит главное меню."""
    print("\n" + "=" * 50)
    print("         IN-MEMORY DATABASE")
    print("=" * 50)
    print("1. Создать таблицу")
    print("2. Показать все таблицы")
    print("3. Добавить запись")
    print("4. Показать все записи")
    print("5. Найти записи по фильтру")
    print("6. Обновить записи")
    print("7. Удалить записи")
    print("8. Информация о таблице")
    print("0. Выход")
    print("-" * 50)


def read_string(prompt: str) -> str:
    """Читает строку (обязательное поле)."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Ошибка. Поле не может быть пустым")


def read_optional(prompt: str) -> Optional[str]:
    """Читает опциональное значение."""
    value = input(prompt).strip()
    return value if value else None


def select_table(db: Database) -> Optional[str]:
    """Выбирает таблицу из списка."""
    tables = db.get_table_names()
    if not tables:
        print("\nОшибка. Нет созданных таблиц. Сначала создайте таблицу.")
        return None
    
    print("\n Доступные таблицы:")
    for i, name in enumerate(tables, 1):
        info = db.get_table_info(name)
        print(f"   {i}. {name} ({info['records_count']} записей)")
    
    while True:
        try:
            choice = input("\nВыберите номер таблицы: ").strip()
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(tables):
                return tables[idx]
            print(" Неверный номер")
        except ValueError:
            print(" Введите число")


def create_table_ui(db: Database):
    """Создание таблицы."""
    print("\n--- СОЗДАНИЕ ТАБЛИЦЫ ---")
    name = read_string("Имя таблицы: ")
    cols_input = input("Колонки (через пробел): ").strip()
    
    if not cols_input:
        print("Ошибка. Нужно указать хотя бы одну колонку")
        return
    
    columns = tuple(cols_input.split())
    
    try:
        db.create_table(name, columns)
    except ValueError as e:
        print(f" Ошибка: {e}")


def show_tables_ui(db: Database):
    """Показывает все таблицы."""
    print("\n--- ВСЕ ТАБЛИЦЫ ---")
    tables = db.get_table_names()
    if not tables:
        print("Нет созданных таблиц")
        return
    
    for name in tables:
        info = db.get_table_info(name)
        print(f"\n {name}")
        print(f"   Колонки: {info['columns']}")
        print(f"   Записей: {info['records_count']}")


def insert_ui(db: Database):
    """Добавление записи."""
    table_name = select_table(db)
    if not table_name:
        return
    
    info = db.get_table_info(table_name)
    print(f"\n--- ДОБАВЛЕНИЕ В ТАБЛИЦУ '{table_name}' ---")
    print(f"Колонки: {info['columns']}")
    
    record = {}
    for col in info['columns']:
        value = read_string(f"  {col}: ")
        record[col] = value
    
    try:
        result = db.insert(table_name, record)
        print(f" Запись добавлена: {result}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def select_all_ui(db: Database):
    """Показывает все записи."""
    table_name = select_table(db)
    if not table_name:
        return
    
    print(f"\n--- ВСЕ ЗАПИСИ ТАБЛИЦЫ '{table_name}' ---")
    
    try:
        records = db.select(table_name)
        if not records:
            print("Записей нет")
            return
        
        for i, rec in enumerate(records, 1):
            print(f"{i}. {rec}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def search_ui(db: Database):
    """Поиск по фильтру."""
    table_name = select_table(db)
    if not table_name:
        return
    
    info = db.get_table_info(table_name)
    print(f"\n--- ПОИСК В ТАБЛИЦЕ '{table_name}' ---")
    print("(Enter - пропустить поле)")
    
    filters = {}
    for col in info['columns']:
        value = read_optional(f"  {col}: ")
        if value is not None:
            filters[col] = value
    
    try:
        records = db.select(table_name, **filters)
        print(f"\n Найдено: {len(records)} записей")
        for i, rec in enumerate(records, 1):
            print(f"{i}. {rec}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def update_ui(db: Database):
    """Обновление записей."""
    table_name = select_table(db)
    if not table_name:
        return
    
    info = db.get_table_info(table_name)
    print(f"\n--- ОБНОВЛЕНИЕ В ТАБЛИЦЕ '{table_name}' ---")
    
    print("\n Фильтры (Enter - пропустить):")
    filters = {}
    for col in info['columns']:
        value = read_optional(f"  {col}: ")
        if value is not None:
            filters[col] = value
    
    print("\n Новые значения (Enter - пропустить):")
    updates = {}
    for col in info['columns']:
        value = read_optional(f"  {col}: ")
        if value is not None:
            updates[col] = value
    
    if not updates:
        print(" Не указаны поля для обновления")
        return
    
    try:
        count = db.update(table_name, updates, **filters)
        print(f" Обновлено записей: {count}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def delete_ui(db: Database):
    """Удаление записей."""
    table_name = select_table(db)
    if not table_name:
        return
    
    info = db.get_table_info(table_name)
    print(f"\n--- УДАЛЕНИЕ ИЗ ТАБЛИЦЫ '{table_name}' ---")
    
    print("\n Фильтры (Enter - удалить ВСЕ записи):")
    filters = {}
    for col in info['columns']:
        value = read_optional(f"  {col}: ")
        if value is not None:
            filters[col] = value
    
    # Подтверждение
    if not filters:
        print("\n ВНИМАНИЕ: Будут удалены ВСЕ записи таблицы!")
    
    confirm = input("\nПодтвердите удаление (y/n): ").strip().lower()
    if confirm != 'y':
        print("Удаление отменено")
        return
    
    try:
        count = db.delete(table_name, **filters)
        print(f" Удалено записей: {count}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def table_info_ui(db: Database):
    """Информация о таблице."""
    table_name = select_table(db)
    if not table_name:
        return
    
    info = db.get_table_info(table_name)
    print(f"\n--- ИНФОРМАЦИЯ О ТАБЛИЦЕ '{table_name}' ---")
    print(f"Колонки: {info['columns']}")
    print(f"Количество записей: {info['records_count']}")


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция программы."""
    db = Database()
    
    print("\n" + "=" * 50)
    print("   ДОБРО ПОЖАЛОВАТЬ В IN-MEMORY DATABASE")
    print("=" * 50)
    
    # Создаём демонстрационную таблицу
    try:
        db.create_table("students", ("id", "name", "age", "group"))
        db.insert("students", {"id": "1", "name": "Иванов Иван", "age": "18", "group": "113bv"})
        db.insert("students", {"id": "2", "name": "Петров Петр", "age": "19", "group": "113bv"})
        db.insert("students", {"id": "3", "name": "Сидоренков Дмитрий", "age": "18", "group": "113bv"})
        print("\n Демонстрационная таблица 'students' создана с 3 записями!")
    except ValueError:
        pass
    
    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            create_table_ui(db)
        elif choice == "2":
            show_tables_ui(db)
        elif choice == "3":
            insert_ui(db)
        elif choice == "4":
            select_all_ui(db)
        elif choice == "5":
            search_ui(db)
        elif choice == "6":
            update_ui(db)
        elif choice == "7":
            delete_ui(db)
        elif choice == "8":
            table_info_ui(db)
        elif choice == "0":
            print("\n До свидания!")
            break
        else:
            print(" Неизвестная команда")


if __name__ == "__main__":
    main()