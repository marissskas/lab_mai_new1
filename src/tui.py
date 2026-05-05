"""
Модуль текстового пользовательского интерфейса.

Предоставляет консольный интерфейс для взаимодействия с базой данных.
"""

from typing import Optional
from .backend.memory import Database # type: ignore


def print_menu() -> None:
    """Выводит главное меню."""
    print("\n" + "=" * 50)
    print("      IN-MEMORY DATABASE")
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
    """Считывает строку (обязательное поле)."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print(" Ошибка. Поле не может быть пустым")


def read_optional(prompt: str) -> Optional[str]:
    """Читает необязательное значение."""
    value = input(prompt).strip()
    return value if value else None


def select_table(db: Database) -> Optional[str]:
    """Выбирает таблицу из списка."""
    tables = db.get_table_names()
    if not tables:
        print("\n Ошибка. Нет созданных таблиц. Сначала создайте таблицу.")
        return None

    print("\n📋 Доступные таблицы:")
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


def create_table_ui(db: Database) -> None:
    """Создание таблицы."""
    print("\n--- СОЗДАНИЕ ТАБЛИЦЫ ---")
    name = read_string("Имя таблицы: ")
    cols_input = input("Колонки (через пробел): ").strip()

    if not cols_input:
        print(" Ошибка. Необходимо указать хотя бы одну колонку")
        return

    columns = tuple(cols_input.split())

    try:
        db.create_table(name, columns)
        print(f" Таблица '{name}' создана. Колонки: {columns}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def show_tables_ui(db: Database) -> None:
    """Показывает все таблицы."""
    print("\n--- ВСЕ ТАБЛИЦЫ ---")
    tables = db.get_table_names()
    if not tables:
        print("Таблиц не создано")
        return

    for name in tables:
        info = db.get_table_info(name)
        print(f"\n {name}")
        print(f"   Колонки: {info['columns']}")
        print(f"   Записей: {info['records_count']}")


def insert_ui(db: Database) -> None:
    """Добавление записи."""
    table_name = select_table(db)
    if not table_name:
        return

    info = db.get_table_info(table_name)
    print(f"\n--- ДОБАВЛЕНИЕ В ТАБЛИЦУ '{table_name}' ---")
    print(f"Колонки: {info['columns']}")

    record = {}
    for col in info['columns']:
        value = read_string(f"   {col}: ")
        record[col] = value

    try:
        result = db.insert(table_name, record)
        print(f" Запись добавлена: {result}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def select_all_ui(db: Database) -> None:
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


def search_ui(db: Database) -> None:
    """Поиск по фильтру."""
    table_name = select_table(db)
    if not table_name:
        return

    info = db.get_table_info(table_name)
    print(f"\n--- ПОИСК В ТАБЛИЦЕ '{table_name}' ---")
    print("(Enter — пропустить поле)")

    filters = {}
    for col in info['columns']:
        value = read_optional(f"   {col}: ")
        if value is not None:
            filters[col] = value

    try:
        records = db.select(table_name, **filters)
        print(f"\n Найдено: {len(records)} записей")
        for i, rec in enumerate(records, 1):
            print(f"{i}. {rec}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def update_ui(db: Database) -> None:
    """Обновление записей."""
    table_name = select_table(db)
    if not table_name:
        return

    info = db.get_table_info(table_name)
    print(f"\n--- ОБНОВЛЕНИЕ В ТАБЛИЦЕ '{table_name}' ---")

    print("\n Фильтры (Enter — пропустить):")
    filters = {}
    for col in info['columns']:
        value = read_optional(f"   {col}: ")
        if value is not None:
            filters[col] = value

    # Предупреждение, если фильтры не заданы
    if not filters:
        print("\n ВНИМАНИЕ: Будут обновлены ВСЕ записи в таблице!")

    print("\n Новые значения (Enter — пропустить):")
    updates = {}
    for col in info['columns']:
        value = read_optional(f"   {col}: ")
        if value is not None:
            updates[col] = value

    if not updates:
        print(" Не указаны поля для обновления")
        return

    # Подтверждение, если обновляются все записи
    if not filters:
        confirm = input("\n Подтвердите обновление ВСЕХ записей (y/n): ").strip().lower()
        if confirm != 'y':
            print("Обновление отменено")
            return

    try:
        count = db.update(table_name, updates, **filters)
        print(f" Обновлено записей: {count}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def delete_ui(db: Database) -> None:
    """Удаление записей."""
    table_name = select_table(db)
    if not table_name:
        return

    info = db.get_table_info(table_name)
    print(f"\n--- УДАЛЕНИЕ ИЗ ТАБЛИЦЫ '{table_name}' ---")

    print("\n Фильтры (Enter — удалить ВСЕ записи):")
    filters = {}
    for col in info['columns']:
        value = read_optional(f"   {col}: ")
        if value is not None:
            filters[col] = value

    # Подтверждение
    if not filters:
        print("\n ВНИМАНИЕ: будут удалены ВСЕ записи в таблице!")

    confirm = input("\nПодтвердите удаление (y/n): ").strip().lower()
    if confirm != 'y':
        print("Удаление отменено")
        return

    try:
        count = db.delete(table_name, **filters)
        print(f" Удалено записей: {count}")
    except ValueError as e:
        print(f" Ошибка: {e}")


def table_info_ui(db: Database) -> None:
    """Информация о таблице."""
    table_name = select_table(db)
    if not table_name:
        return

    info = db.get_table_info(table_name)
    print(f"\n--- ИНФОРМАЦИЯ О ТАБЛИЦЕ '{table_name}' ---")
    print(f"Колонки: {info['columns']}")
    print(f"Количество записей: {info['records_count']}")


def run() -> None:
    """Запускает основной цикл текстового интерфейса."""
    db = Database()

    print("\n" + "=" * 50)
    print("   ДОБРО ПОЖАЛОВАТЬ В БАЗУ ДАННЫХ В ОПЕРАТИВНОЙ ПАМЯТИ")
    print("=" * 50)

    # Создаём демонстрационную таблицу
    try:
        db.create_table("students", ("id", "name", "age", "group"))
        db.insert("students", {"id": "1", "name": "Иванов Иван", "age": "18", "group": "113bv"})
        db.insert("students", {"id": "2", "name": "Петров Петр", "age": "19", "group": "113bv"})
        db.insert("students", {"id": "3", "name": "Сидоренков Дмитрий", "age": "18", "group": "113bv"})
        print("\n✓ Демонстрационная таблица 'students' создана с 3 записями!")
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