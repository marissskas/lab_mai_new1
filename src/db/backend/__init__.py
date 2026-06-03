"""Пакет бэкенда базы данных."""

from .memory import MemoryDatabase, Student, create_record, select_record, init_student_table
from .file import FileDatabase
from .database import Database
from .table import Table
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
    "FileDatabase",
    "Database",
    "Table",
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
