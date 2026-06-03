"""In-memory реализация базы данных с поддержкой таблиц."""

from typing import Optional, Any
from .database import Database
from .errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidAgeError,
    DuplicateIDError,
)
from .table import Table


class MemoryDatabase(Database):
    """База данных в оперативной памяти."""
    
    def __init__(self):
        self._tables: dict[str, Table] = {}
    
    def _table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы."""
        return table_name in self._tables
    
    def _load_table(self, table_name: str) -> Table:
        """Загружает таблицу по имени."""
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        return self._tables[table_name]
    
    def _save_table(self, table_name: str, table: Table) -> None:
        """Сохраняет таблицу."""
        self._tables[table_name] = table
    
    # ============================================================
    # Публичные методы, соответствующие интерфейсу Database
    # ============================================================
    
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        """Создаёт новую таблицу."""
        if self._table_exists(table_name):
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует.")
        self._save_table(table_name, Table(table_name, columns))
    
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
        return list(self._tables.keys())
    
    def get_table_info(self, table_name: str) -> Optional[dict]:
        """Возвращает информацию о таблице."""
        if table_name not in self._tables:
            return None
        return self._tables[table_name].get_info()
    
    def insert(self, table_name: str, record: dict) -> dict:
        """
        Вставляет запись (альтернативный метод для совместимости с TUI).
        """
        self.insert_record(table_name, record)
        return record
    
    def select(self, table_name: str, **filters) -> list[dict]:
        """
        Выбирает записи (альтернативный метод для совместимости с TUI).
        """
        return self.select_records(table_name, **filters)
    
    def update(self, table_name: str, updates: dict, **filters) -> int:
        """
        Обновляет записи (альтернативный метод для совместимости с TUI).
        """
        return self.update_records(table_name, updates, **filters)
    
    def delete(self, table_name: str, **filters) -> int:
        """
        Удаляет записи (альтернативный метод для совместимости с TUI).
        """
        return self.delete_records(table_name, **filters)
    
    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> list[dict]:
        """Сортирует записи."""
        table = self._load_table(table_name)
        return table.sort_records(field, reverse)


# ============================================================
# Интерфейс для работы со студентами (русские названия полей)
# ============================================================

_db = MemoryDatabase()
_СТУДЕНТЫ_ТАБЛИЦА = "студенты"
_КОЛОНКИ_СТУДЕНТОВ = ("id", "имя", "фамилия", "возраст", "пол")


def init_student_table() -> None:
    """Инициализирует таблицу студентов с русскими колонками."""
    if _СТУДЕНТЫ_ТАБЛИЦА not in _db.get_table_names():
        _db.create_table(_СТУДЕНТЫ_ТАБЛИЦА, _КОЛОНКИ_СТУДЕНТОВ)


def _validate_age(age: int) -> None:
    """Проверяет, что возраст не отрицательный."""
    if age < 0:
        raise InvalidAgeError("Поле 'возраст' не может быть отрицательным.")


def create_record(
    student_id: int,
    first_name: str,
    second_name: str,
    age: int,
    sex: str,
) -> tuple:
    """Создаёт новую запись."""
    init_student_table()
    
    _validate_age(age)
    
    # Проверка уникальности ID
    existing = _db.select(_СТУДЕНТЫ_ТАБЛИЦА, id=str(student_id))
    if existing:
        raise DuplicateIDError(f"Запись с id={student_id} уже существует.")
    
    sex_normalized = sex.strip().upper()
    if sex_normalized not in ("М", "Ж"):
        sex_normalized = sex.strip()
    
    record = {
        "id": str(student_id),
        "имя": first_name.strip(),
        "фамилия": second_name.strip(),
        "возраст": str(age),
        "пол": sex_normalized,
    }
    
    _db.insert(_СТУДЕНТЫ_ТАБЛИЦА, record)
    
    return (student_id, first_name.strip(), second_name.strip(), age, sex_normalized)


def select_record(
    student_id: Optional[int] = None,
    first_name: Optional[str] = None,
    second_name: Optional[str] = None,
    age: Optional[int] = None,
    sex: Optional[str] = None,
) -> list[tuple]:
    """Выбирает записи."""
    init_student_table()
    
    filters = {}
    if student_id is not None:
        filters["id"] = str(student_id)
    if first_name is not None:
        filters["имя"] = first_name
    if second_name is not None:
        filters["фамилия"] = second_name
    if age is not None:
        filters["возраст"] = str(age)
    if sex is not None:
        filters["пол"] = sex
    
    records = _db.select(_СТУДЕНТЫ_ТАБЛИЦА, **filters)
    
    result = []
    for r in records:
        result.append((
            int(r["id"]),
            r["имя"],
            r["фамилия"],
            int(r["возраст"]),
            r["пол"],
        ))
    
    return result


class Student:
    """Класс для доступа к таблице студентов."""
    
    @classmethod
    def clear(cls):
        """Очищает таблицу студентов."""
        global _db
        _db = MemoryDatabase()
    
    def __len__(self):
        return len(select_record())
