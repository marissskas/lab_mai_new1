"""Класс таблицы базы данных."""

from .errors import MissingColumnError, UnknownColumnError


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
        # Проверяем, что все поля фильтров существуют
        for key in filters.keys():
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестное поле фильтра: {key}")
        
        if not filters:
            return self._records.copy()
        
        result = []
        for record in self._records:
            match = True
            for key, value in filters.items():
                # Сравниваем значения без приведения к строке
                if record.get(key) != value:
                    match = False
                    break
            if match:
                result.append(record.copy())
        return result
    
    def update(self, updates: dict, **filters) -> int:
        """Обновляет записи."""
        # Проверяем поля для обновления
        for key in updates.keys():
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестное поле: {key}")
        
        # Проверяем поля фильтров
        for key in filters.keys():
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестное поле фильтра: {key}")
        
        indices_to_update = []
        for idx, record in enumerate(self._records):
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                indices_to_update.append(idx)
        
        for idx in indices_to_update:
            for key, value in updates.items():
                self._records[idx][key] = value
        
        return len(indices_to_update)
    
    def delete(self, **filters) -> int:
        """Удаляет записи."""
        # Проверяем поля фильтров
        for key in filters.keys():
            if key not in self.columns:
                raise UnknownColumnError(f"Неизвестное поле фильтра: {key}")
        
        if not filters:
            count = len(self._records)
            self._records = []
            return count
        
        indices_to_keep = []
        for idx, record in enumerate(self._records):
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if not match:
                indices_to_keep.append(idx)
        
        count = len(self._records) - len(indices_to_keep)
        self._records = [self._records[i] for i in indices_to_keep]
        return count
    
    def sort_records(self, field: str, reverse: bool = False) -> list[dict]:
        """
        Сортирует записи с сохранением исходных типов данных.
        
        Числовые поля сортируются как числа, строковые - как строки.
        """
        if field not in self.columns:
            raise UnknownColumnError(f"Поле '{field}' не найдено в таблице")
        
        # Функция для получения ключа сортировки с сохранением типа
        def get_sort_key(record: dict):
            value = record.get(field)
            # None значения отправляем в конец
            if value is None:
                return (1,)
            # Пробуем преобразовать в число для числовой сортировки
            if isinstance(value, str):
                # Если строка выглядит как число, сортируем как число
                try:
                    if '.' in value:
                        return (0, float(value))
                    else:
                        return (0, int(value))
                except (ValueError, TypeError):
                    return (0, value)
            # Для нестроковых значений (int, float, bool) сортируем как есть
            return (0, value)
        
        return sorted(self._records, key=get_sort_key, reverse=reverse)
    
    def get_records(self) -> list[dict]:
        """Возвращает копию всех записей."""
        return [record.copy() for record in self._records]
    
    def to_dict(self) -> dict:
        """Преобразует таблицу в словарь для сериализации."""
        return {
            "name": self.name,
            "columns": list(self.columns),
            "records": self.get_records(),
        }
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> "Table":
        """Создаёт таблицу из словаря (для десериализации)."""
        columns = tuple(data.get("columns", []))
        table = cls(name, columns)
        for record in data.get("records", []):
            table.insert(record)
        return table
    
    def get_info(self) -> dict:
        """Возвращает информацию о таблице."""
        return {
            "name": self.name,
            "columns": self.columns,
            "records_count": len(self._records),
        }
