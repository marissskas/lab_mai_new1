"""In-memory реализация базы данных с поддержкой таблиц."""

from typing import Optional
from .errors import (
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidAgeError,
    DuplicateIDError,
)


class Table:
    """Класс таблицы базы данных."""
    
    def __init__(self, name: str, columns: tuple[str, ...]):
        self.name = name
        self.columns = columns
        self._records: list[dict] = []
    
    def _validate_record(self, record: dict) -> None:
        """Проверяет корректность записи."""
        for col in self.columns:
            if col not in record:
                raise MissingColumnError(f"Отсутствует поле: {col}")
        for key in record.keys():
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестное поле: {key}")
    
    def insert(self, record: dict) -> dict:
        """Добавляет запись."""
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
        """Обновляет записи."""
        # Проверяем, что все поля для обновления существуют
        for key in updates.keys():
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестное поле: {key}")
        
        # Находим индексы записей для обновления
        indices_to_update = []
        for idx, record in enumerate(self._records):
            match = True
            for key, value in filters.items():
                if key not in self.columns:
                    raise UnknownColumnError(f"Неизвестное поле фильтра: {key}")
                if str(record.get(key)) != str(value):
                    match = False
                    break
            if match:
                indices_to_update.append(idx)
        
        # Обновляем записи по индексам
        for idx in indices_to_update:
            for key, value in updates.items():
                self._records[idx][key] = value
        
        return len(indices_to_update)
    
    def delete(self, **filters) -> int:
        """Удаляет записи."""
        if not filters:
            count = len(self._records)
            self._records = []
            return count
        
        indices_to_keep = []
        for idx, record in enumerate(self._records):
            match = True
            for key, value in filters.items():
                if key not in self.columns:
                    raise UnknownColumnError(f"Неизвестное поле фильтра: {key}")
                if str(record.get(key)) != str(value):
                    match = False
                    break
            if not match:
                indices_to_keep.append(idx)
        
        count = len(self._records) - len(indices_to_keep)
        self._records = [self._records[i] for i in indices_to_keep]
        return count
    
    def sort_records(self, field: str, reverse: bool = False) -> list[dict]:
        """Сортирует записи."""
        if field not in self.columns:
            raise UnknownColumnError(f"Поле '{field}' не найдено в таблице")
        return sorted(self._records, key=lambda x: str(x.get(field, "")), reverse=reverse)
    
    def get_info(self) -> dict:
        """Возвращает информацию о таблице."""
        return {
            "name": self.name,
            "columns": self.columns,
            "records_count": len(self._records),
        }

class MemoryDatabase:
    """База данных в оперативной памяти."""
    
    def __init__(self):
        self._tables: dict[str, Table] = {}
    
    def _get_table(self, table_name: str) -> Table:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        return self._tables[table_name]
    
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        if table_name in self._tables:
            raise TableAlreadyExistsError(f"Таблица '{table_name}' уже существует.")
        self._tables[table_name] = Table(table_name, columns)
    
    def get_table_names(self) -> list[str]:
        return list(self._tables.keys())
    
    def get_table_info(self, table_name: str) -> Optional[dict]:
        if table_name not in self._tables:
            return None
        return self._tables[table_name].get_info()
    
    def insert(self, table_name: str, record: dict) -> dict:
        return self._get_table(table_name).insert(record)
    
    def select(self, table_name: str, **filters) -> list[dict]:
        return self._get_table(table_name).select(**filters)
    
    def update(self, table_name: str, updates: dict, **filters) -> int:
        return self._get_table(table_name).update(updates, **filters)
    
    def delete(self, table_name: str, **filters) -> int:
        return self._get_table(table_name).delete(**filters)
    
    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> list[dict]:
        return self._get_table(table_name).sort_records(field, reverse)


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
    
    # Проверка только на отрицательный возраст
    _validate_age(age)
    
    # Проверка уникальности ID
    existing = _db.select(_СТУДЕНТЫ_ТАБЛИЦА, id=str(student_id))
    if existing:
        raise DuplicateIDError(f"Запись с id={student_id} уже существует.")
    
    # Нормализация пола
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
