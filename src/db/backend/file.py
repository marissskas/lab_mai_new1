"""Реализация файловой базы данных с использованием JSON."""
import json
from pathlib import Path
from typing import Any, Optional

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError, TableAlreadyExistsError
from .table import Table


class FileDatabase(Database):
    """База данных, хранящая таблицы в JSON-файлах."""

    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._tables_cache: dict[str, Table] = {}

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        if table_name in self._tables_cache:
            return self._tables_cache[table_name]
        
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                "Файл таблицы содержит некорректный JSON."
            ) from error

        table = self._deserialize_table(table_name, data)
        self._tables_cache[table_name] = table
        return table

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        with table_path.open("w", encoding="utf-8") as file:
            json.dump(
                self._serialize_table(table),
                file,
                ensure_ascii=False,
                indent=2,
            )
        self._tables_cache[table_name] = table

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _serialize_table(self, table: Table) -> dict[str, Any]:
        """Преобразует таблицу в словарь для сериализации."""
        return table.to_dict()

    def _deserialize_table(self, table_name: str, data: dict[str, Any]) -> Table:
        """Восстанавливает таблицу из словаря."""
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError(
                "Файл таблицы имеет некорректную структуру."
            )
        return Table.from_dict(table_name, data)

    # ============================================================
    # Методы, реализующие интерфейс Database
    # ============================================================
    
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        """Создаёт новую таблицу."""
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует.")
        table = Table(table_name, columns)
        self._save_table(table_name, table)
    
    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        """Вставляет запись в таблицу."""
        table = self._load_table(table_name)
        table.insert(record)
        self._save_table(table_name, table)
    
    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        """Выполняет выборку записей."""
        table = self._load_table(table_name)
        return table.select(**filters)
    
    def update_records(self, table_name: str, updates: dict[str, Any], **filters: Any) -> int:
        """Обновляет записи."""
        table = self._load_table(table_name)
        updated = table.update(updates, **filters)
        self._save_table(table_name, table)
        return updated
    
    def delete_records(self, table_name: str, **filters: Any) -> int:
        """Удаляет записи."""
        table = self._load_table(table_name)
        deleted = table.delete(**filters)
        self._save_table(table_name, table)
        return deleted

    # ============================================================
    # Дополнительные методы для удобства (не в Database)
    # ============================================================

    def get_table_names(self) -> list[str]:
        """Возвращает список имён всех таблиц."""
        tables = []
        for file_path in self.directory.glob("*.json"):
            tables.append(file_path.stem)
        return tables

    def get_table_info(self, table_name: str) -> Optional[dict]:
        """Возвращает информацию о таблице."""
        try:
            table = self._load_table(table_name)
            return table.get_info()
        except TableNotFoundError:
            return None

    def insert(self, table_name: str, record: dict) -> dict:
        """Вставляет запись (альтернативный метод для совместимости с TUI)."""
        self.insert_record(table_name, record)
        return record

    def select(self, table_name: str, **filters) -> list[dict]:
        """Выбирает записи (альтернативный метод для совместимости с TUI)."""
        return self.select_records(table_name, **filters)

    def update(self, table_name: str, updates: dict, **filters) -> int:
        """Обновляет записи (альтернативный метод для совместимости с TUI)."""
        return self.update_records(table_name, updates, **filters)

    def delete(self, table_name: str, **filters) -> int:
        """Удаляет записи (альтернативный метод для совместимости с TUI)."""
        return self.delete_records(table_name, **filters)

    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> list[dict]:
        """Сортирует записи."""
        table = self._load_table(table_name)
        return table.sort_records(field, reverse)

    def clear_cache(self) -> None:
        """Очищает кэш таблиц."""
        self._tables_cache.clear()
