"""
Модуль реализации in-memory базы данных.

Поддерживает множество таблиц и полный набор CRUD операций.
"""

from typing import Optional


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

        # Проверка наличия всех обязательных полей
        for col in columns:
            if col not in record:
                raise ValueError(f"Отсутствует поле '{col}'")

        # Проверка отсутствия лишних полей
        for col in record:
            if col not in columns:
                raise ValueError(f"Поле '{col}' не определено в таблице")

        table["records"].append(record.copy())
        return record.copy()

    def select(self, table_name: str, **filters) -> list:
        """Выбирает записи с фильтрацией."""
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует")

        table = self._tables[table_name]
        records = table["records"]
        columns = table["columns"]

        # Проверка корректности фильтров
        for key in filters:
            if key not in columns:
                raise ValueError(f"Поле '{key}' не существует в таблице")

        # Если фильтров нет, возвращаем копию всех записей
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

        # Проверка корректности обновляемых полей
        for key in updates:
            if key not in columns:
                raise ValueError(f"Поле '{key}' не существует в таблице")

        # Проверка корректности фильтров
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
        """Удаляет записи по фильтру."""
        if table_name not in self._tables:
            raise ValueError(f"Таблица '{table_name}' не существует")

        table = self._tables[table_name]
        columns = table["columns"]

        # Проверка корректности фильтров
        for key in filters:
            if key not in columns:
                raise ValueError(f"Поле '{key}' не существует в таблице")

        # Если фильтров нет, удаляем все записи
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
    