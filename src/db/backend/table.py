"""Класс Table для хранения данных одной таблицы."""

from typing import Optional
from .errors import MissingColumnError, UnknownColumnError


class Table:
    """Таблица базы данных."""

    def __init__(self, name: str, columns: tuple[str, ...]):
        self.name = name
        self.columns = columns
        self._records: list[dict] = []

    def _validate_record(self, record: dict) -> None:
        """Проверяет, что запись содержит все колонки и не содержит лишних."""
        for col in self.columns:
            if col not in record:
                raise MissingColumnError(f"Отсутствует поле: {col}")
        for key in record.keys():
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестное поле: {key}")

    def insert(self, record: dict) -> dict:
        """Добавляет запись в таблицу."""
        self._validate_record(record)
        self._records.append(record.copy())
        return record

    def select(self, **filters) -> list[dict]:
        """Выбирает записи по фильтрам."""
        if not filters:
            return self._records.copy()

        result = []
        for record in self._records:
            match = True
            for key, value in filters.items():
                if key not in self.columns:
                    raise UnknownColumnError(f"Неизвестное поле фильтра: {key}")
                if str(record.get(key)) != str(value):
                    match = False
                    break
            if match:
                result.append(record.copy())
        return result

    def update(self, updates: dict, **filters) -> int:
        """Обновляет записи по фильтрам."""
        # Проверяем, что все поля для обновления существуют в таблице
        for key in updates.keys():
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестное поле: {key}")

        records_to_update = self.select(**filters)
        count = 0
        for record in records_to_update:
            for key, value in updates.items():
                record[key] = value
            count += 1
        return count

    def delete(self, **filters) -> int:
        """Удаляет записи по фильтрам."""
        records_to_delete = self.select(**filters)
        count = len(records_to_delete)
        self._records = [r for r in self._records if r not in records_to_delete]
        return count

    def sort_records(self, field: str, reverse: bool = False) -> list[dict]:
        """Возвращает отсортированные записи."""
        if field not in self.columns:
            raise UnknownColumnError(f"Поле '{field}' не найдено в таблице")

        return sorted(self._records, key=lambda x: x.get(field, ""), reverse=reverse)

    def get_info(self) -> dict:
        """Возвращает информацию о таблице."""
        return {
            "name": self.name,
            "columns": self.columns,
            "records_count": len(self._records),
        }
