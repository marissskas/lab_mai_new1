"""In-memory реализация базы данных."""

from typing import Optional
from .database import Database
from .table import Table
from .errors import TableAlreadyExistsError, TableNotFoundError


class MemoryDatabase(Database):
    """База данных, хранящая таблицы в оперативной памяти."""

    def __init__(self):
        self._tables: dict[str, Table] = {}

    def _get_table(self, table_name: str) -> Table:
        """Возвращает таблицу или вызывает ошибку."""
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        return self._tables[table_name]

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        """Создаёт новую таблицу."""
        if table_name in self._tables:
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует.")
        self._tables[table_name] = Table(table_name, columns)

    def get_table_names(self) -> list[str]:
        """Возвращает список имён всех таблиц."""
        return list(self._tables.keys())

    def get_table_info(self, table_name: str) -> Optional[dict]:
        """Возвращает информацию о таблице."""
        if table_name not in self._tables:
            return None
        return self._tables[table_name].get_info()

    def insert(self, table_name: str, record: dict) -> dict:
        """Вставляет запись в таблицу."""
        table = self._get_table(table_name)
        return table.insert(record)

    def select(self, table_name: str, **filters) -> list[dict]:
        """Выбирает записи из таблицы по фильтрам."""
        table = self._get_table(table_name)
        return table.select(**filters)

    def update(self, table_name: str, updates: dict, **filters) -> int:
        """Обновляет записи, соответствующие фильтрам."""
        table = self._get_table(table_name)
        return table.update(updates, **filters)

    def delete(self, table_name: str, **filters) -> int:
        """Удаляет записи, соответствующие фильтрам."""
        table = self._get_table(table_name)
        return table.delete(**filters)

    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> list[dict]:
        """Возвращает отсортированные записи."""
        table = self._get_table(table_name)
        return table.sort_records(field, reverse)
