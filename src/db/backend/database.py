"""Абстрактный интерфейс базы данных."""
from abc import ABC, abstractmethod
from typing import Any

from .errors import TableAlreadyExistsError
from .table import Table


class Database(ABC):
    """Общий интерфейс базы данных."""

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        """Создаёт новую таблицу."""
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(
                f"Таблица '{table_name}' уже существует."
            )
        self._save_table(table_name, Table(table_name, columns))

    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        """Вставляет запись в таблицу."""
        table = self._load_table(table_name)
        table.insert(record)
        self._save_table(table_name, table)

    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        """Выполняет выборку записей."""
        table = self._load_table(table_name)
        # Проверка фильтров происходит внутри table.select()
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

    @abstractmethod
    def _table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы."""
        pass

    @abstractmethod
    def _load_table(self, table_name: str) -> Table:
        """Загружает таблицу из хранилища."""
        pass

    @abstractmethod
    def _save_table(self, table_name: str, table: Table) -> None:
        """Сохраняет таблицу в хранилище."""
        pass
