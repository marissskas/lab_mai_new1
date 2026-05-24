"""Пользовательские исключения для базы данных."""


class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных."""
    pass


class TableAlreadyExistsError(DatabaseError):
    """Ошибка при создании уже существующей таблицы."""
    pass


class TableNotFoundError(DatabaseError):
    """Ошибка при обращении к несуществующей таблице."""
    pass


class MissingColumnError(DatabaseError):
    """Ошибка при вставке записи с отсутствующим полем."""
    pass


class UnknownColumnError(DatabaseError):
    """Ошибка при использовании несуществующего поля."""
    pass
