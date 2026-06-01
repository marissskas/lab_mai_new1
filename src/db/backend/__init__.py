"""Пакет бэкенда базы данных."""

from .memory import MemoryDatabase, Student, create_record, select_record, init_student_table
from .errors import (
    DatabaseError,
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
    InvalidAgeError,
    DuplicateIDError,
)

__all__ = [
    "MemoryDatabase",
    "Student",
    "create_record",
    "select_record",
    "init_student_table",
    "DatabaseError",
    "TableAlreadyExistsError",
    "TableNotFoundError",
    "MissingColumnError",
    "UnknownColumnError",
    "InvalidStorageDataError",
    "InvalidAgeError",
    "DuplicateIDError",
]
