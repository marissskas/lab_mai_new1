# src/db/backend/file_db.py
"""File-based реализация базы данных (JSON)."""

import json
from pathlib import Path
from typing import Optional

from .database import Database
from .table import Table
from .errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)


class FileDatabase(Database):
    """База данных, хранящая таблицы в JSON-файлах."""

    def __init__(self, directory: str = "data"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Table] = {}  # Кэш для уменьшения чтений с диска

    def _get_table_path(self, table_name: str) -> Path:
        """Возвращает путь к файлу таблицы."""
        return self.directory / f"{table_name}.json"

    def _load_table_from_file(self, table_name: str) -> Table:
        """Загружает таблицу из JSON-файла."""
        table_path = self._get_table_path(table_name)
        
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        
        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}' содержит некорректный JSON."
            ) from e
        except OSError as e:
            raise InvalidStorageDataError(
                f"Ошибка при чтении файла таблицы '{table_name}': {e}"
            ) from e
        
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}' имеет некорректную структуру."
            )
        
        columns = tuple(data["columns"])
        records = data.get("records", [])
        
        # Создаём таблицу и заполняем записи
        table = Table(table_name, columns)
        for record in records:
            try:
                table.insert(record)
            except (MissingColumnError, UnknownColumnError) as e:
                raise InvalidStorageDataError(
                    f"Некорректная запись в файле '{table_name}': {e}"
                ) from e
        
        return table

    def _save_table_to_file(self, table_name: str, table: Table) -> None:
        """Сохраняет таблицу в JSON-файл."""
        table_path = self._get_table_path(table_name)
        
        data = {
            "columns": list(table.columns),
            "records": table._records.copy(),
        }
        
        try:
            with table_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except OSError as e:
            raise InvalidStorageDataError(
                f"Ошибка при сохранении таблицы '{table_name}': {e}"
            ) from e

    def _get_table(self, table_name: str) -> Table:
        """Возвращает таблицу из кэша или загружает из файла."""
        if table_name in self._cache:
            return self._cache[table_name]
        
        table = self._load_table_from_file(table_name)
        self._cache[table_name] = table
        return table

    def _invalidate_cache(self, table_name: str) -> None:
        """Удаляет таблицу из кэша."""
        self._cache.pop(table_name, None)

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        """Создаёт новую таблицу."""
        if self._get_table_path(table_name).exists():
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует.")
        
        table = Table(table_name, columns)
        self._save_table_to_file(table_name, table)
        self._cache[table_name] = table

    def get_table_names(self) -> list[str]:
        """Возвращает список имён всех таблиц."""
        table_names = []
        for file_path in self.directory.glob("*.json"):
            table_names.append(file_path.stem)
        return table_names

    def get_table_info(self, table_name: str) -> Optional[dict]:
        """Возвращает информацию о таблице."""
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            return None
        
        try:
            table = self._get_table(table_name)
            return table.get_info()
        except TableNotFoundError:
            return None

    def insert(self, table_name: str, record: dict) -> dict:
        """Вставляет запись в таблицу."""
        table = self._get_table(table_name)
        result = table.insert(record)
        self._save_table_to_file(table_name, table)
        self._invalidate_cache(table_name)
        return result

    def select(self, table_name: str, **filters) -> list[dict]:
        """Выбирает записи из таблицы по фильтрам."""
        table = self._get_table(table_name)
        return table.select(**filters)

    def update(self, table_name: str, updates: dict, **filters) -> int:
        """Обновляет записи, соответствующие фильтрам."""
        table = self._get_table(table_name)
        count = table.update(updates, **filters)
        if count > 0:
            self._save_table_to_file(table_name, table)
            self._invalidate_cache(table_name)
        return count

    def delete(self, table_name: str, **filters) -> int:
        """Удаляет записи, соответствующие фильтрам."""
        table = self._get_table(table_name)
        count = table.delete(**filters)
        self._save_table_to_file(table_name, table)
        self._invalidate_cache(table_name)
        return count

    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> list[dict]:
        """Возвращает отсортированные записи."""
        table = self._get_table(table_name)
        return table.sort_records(field, reverse)
