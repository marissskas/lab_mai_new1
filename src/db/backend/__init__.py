# src/db/backend/__init__.py
"""Пакет бэкенда базы данных."""

from .database import Database
from .memory_db import MemoryDatabase
from .file_db import FileDatabase
from .errors import (
    DatabaseError,
    TableAlreadyExistsError,
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)

__all__ = [
    "Database",
    "MemoryDatabase",
    "FileDatabase",
    "DatabaseError",
    "TableAlreadyExistsError",
    "TableNotFoundError",
    "MissingColumnError",
    "UnknownColumnError",
    "InvalidStorageDataError",
]
