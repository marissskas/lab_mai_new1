"""Абстрактный класс Database."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class Database(ABC):
    """Абстрактный класс для всех реализаций базы данных."""

    @abstractmethod
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        """Создаёт новую таблицу."""
        pass

    @abstractmethod
    def get_table_names(self) -> list[str]:
        """Возвращает список имён всех таблиц."""
        pass

    @abstractmethod
    def get_table_info(self, table_name: str) -> Optional[dict]:
        """Возвращает информацию о таблице."""
        pass

    @abstractmethod
    def insert(self, table_name: str, record: dict) -> dict:
        """Вставляет запись в таблицу."""
        pass

    @abstractmethod
    def select(self, table_name: str, **filters) -> list[dict]:
        """Выбирает записи из таблицы по фильтрам."""
        pass

    @abstractmethod
    def update(self, table_name: str, updates: dict, **filters) -> int:
        """Обновляет записи, соответствующие фильтрам."""
        pass

    @abstractmethod
    def delete(self, table_name: str, **filters) -> int:
        """Удаляет записи, соответствующие фильтрам."""
        pass

    @abstractmethod
    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> list[dict]:
        """Возвращает отсортированные записи."""
        pass
