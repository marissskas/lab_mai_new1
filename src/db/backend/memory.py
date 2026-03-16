from typing import Dict, List, Any, Optional, Tuple
from .exceptions import RecordNotFoundError, ValidationError, TableNotFoundError

# Тип для записи студента - кортеж (как в методичке)
type StudentRecord = Tuple[int, str, str, int, str]

class Table:
    def __init__(self, name: str):
        self.name = name
        self._records: Dict[int, StudentRecord] = {}
        self._counter = 0  # Счетчик для автоинкремента
    
    def _validate_age(self, age: int) -> None:
        """Внутренняя проверка возраста."""
        if age < 0:
            raise ValueError("Возраст не может быть отрицательным")
        if age > 120:
            raise ValueError("Возраст не может быть больше 120 лет")
    
    def _validate_name(self, name: str) -> str:
        """Очистка и проверка имени."""
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Имя не может быть пустым")
        if len(cleaned) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")
        return cleaned.capitalize()
    
    def _validate_sex(self, sex: str) -> str:
        """Проверка пола."""
        cleaned = sex.strip().upper()
        if cleaned not in ['М', 'Ж', 'M', 'F']:
            raise ValueError("Пол должен быть 'м' или 'ж'")
        return 'М' if cleaned in ['М', 'M'] else 'Ж'
    
    def _generate_id(self) -> int:
        """Генерация уникального ID."""
        self._counter += 1
        return self._counter
    
    def create_record(self, student_id: int | None = None, first_name: str = "", 
                     second_name: str = "", age: int = 0, sex: str = "") -> StudentRecord:
        """Создаёт новую запись и добавляет её в таблицу."""
        
        # Если ID не указан, генерируем автоматически
        if student_id is None:
            student_id = self._generate_id()
        
        # Проверка возраста
        self._validate_age(age)
        
        # Проверка имени
        first_name = self._validate_name(first_name)
        second_name = self._validate_name(second_name)
        
        # Проверка пола
        sex = self._validate_sex(sex)
        
        # Проверка уникальности ID
        if student_id in self._records:
            raise ValueError(f"Запись с id={student_id} уже существует.")
        
        # Создание записи
        new_record: StudentRecord = (
            student_id,
            first_name,
            second_name,
            age,
            sex,
        )
        
        self._records[student_id] = new_record
        return new_record
    
    def select_record(self, student_id: int | None = None, first_name: str | None = None, 
                      second_name: str | None = None, age: int | None = None, 
                      sex: str | None = None, **kwargs) -> list[StudentRecord]:
        """Возвращает записи, подходящие под запрос или фильтр."""
        
        # Поддержка дополнительных фильтров через kwargs
        all_filters = {
            'student_id': student_id,
            'first_name': first_name,
            'second_name': second_name,
            'age': age,
            'sex': sex,
            **kwargs
        }
        
        # Проверяем, есть ли хоть один фильтр
        has_filter = any(v is not None for v in all_filters.values())
        
        # Если фильтры не заданы - возвращаем всё
        if not has_filter:
            return list(self._records.values())
        
        result = []
        for record in self._records.values():
            match = True
            
            # Проверка по ID
            if all_filters.get('student_id') is not None and record[0] != all_filters['student_id']:
                match = False
            
            # Проверка по имени (регистронезависимо)
            if match and all_filters.get('first_name') is not None:
                if record[1].lower() != all_filters['first_name'].lower():
                    match = False
            
            # Проверка по фамилии
            if match and all_filters.get('second_name') is not None:
                if record[2].lower() != all_filters['second_name'].lower():
                    match = False
            
            # Проверка по возрасту
            if match and all_filters.get('age') is not None and record[3] != all_filters['age']:
                match = False
            
            # Проверка по полу
            if match and all_filters.get('sex') is not None:
                if record[4].upper() != all_filters['sex'].upper():
                    match = False
            
            if match:
                result.append(record)
        
        return result
    
    def get_by_id(self, record_id: int) -> StudentRecord:
        """Быстрый доступ к записи по ID."""
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с id={record_id} не найдена")
        return self._records[record_id]
    
    def update_record(self, record_id: int, first_name: str | None = None, 
                      second_name: str | None = None, age: int | None = None, 
                      sex: str | None = None) -> StudentRecord:
        """Обновляет поля существующей записи."""
        
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с id={record_id} не найдена")
        
        old = self._records[record_id]
        
        # Подготовка новых значений с валидацией
        new_first_name = old[1]
        if first_name is not None:
            new_first_name = self._validate_name(first_name)
        
        new_second_name = old[2]
        if second_name is not None:
            new_second_name = self._validate_name(second_name)
        
        new_age = old[3]
        if age is not None:
            self._validate_age(age)
            new_age = age
        
        new_sex = old[4]
        if sex is not None:
            new_sex = self._validate_sex(sex)
        
        # Обновляем только переданные поля
        new_record: StudentRecord = (
            record_id,
            new_first_name,
            new_second_name,
            new_age,
            new_sex,
        )
        
        self._records[record_id] = new_record
        return new_record
    
    def delete_record(self, record_id: int) -> bool:
        """Удаляет запись из таблицы."""
        
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с id={record_id} не найдена")
        
        del self._records[record_id]
        return True
    
    def count(self) -> int:
        """Возвращает количество записей."""
        return len(self._records)
    
    def clear(self) -> None:
        """Очищает таблицу."""
        self._records.clear()
        self._counter = 0
    
    def __len__(self) -> int:
        return len(self._records)
    
    def __contains__(self, record_id: int) -> bool:
        return record_id in self._records


class Database:
    def __init__(self):
        self._tables: Dict[str, Table] = {}
        self._current: Optional[str] = None
    
    def create_table(self, name: str) -> Table:
        """Создает новую таблицу."""
        if not name or not name.strip():
            raise ValidationError("Имя таблицы не может быть пустым")
        
        if name in self._tables:
            raise ValidationError(f"Таблица '{name}' уже существует")
        
        table = Table(name.strip())
        self._tables[name] = table
        return table
    
    def get_table(self, name: str) -> Table:
        """Возвращает таблицу по имени."""
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        
        return self._tables[name]
    
    def drop_table(self, name: str) -> bool:
        """Удаляет таблицу."""
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        
        del self._tables[name]
        if self._current == name:
            self._current = None
        return True
    
    def list_tables(self) -> List[str]:
        """Возвращает список всех таблиц."""
        return list(self._tables.keys())
    
    def get_tables_with_counts(self) -> List[Tuple[str, int]]:
        """Возвращает список таблиц с количеством записей."""
        return [(name, len(table)) for name, table in self._tables.items()]
    
    def set_current(self, name: str) -> None:
        """Устанавливает текущую таблицу."""
        if name not in self._tables:
            raise TableNotFoundError(f"Таблица '{name}' не найдена")
        self._current = name
    
    def get_current(self) -> Optional[str]:
        """Возвращает текущую таблицу."""
        return self._current
    
    def rename_table(self, old_name: str, new_name: str) -> bool:
        """Переименовывает таблицу."""
        if old_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{old_name}' не найдена")
        
        if new_name in self._tables:
            raise ValidationError(f"Таблица '{new_name}' уже существует")
        
        self._tables[new_name] = self._tables.pop(old_name)
        if self._current == old_name:
            self._current = new_name
        return True
    
    def exists(self, name: str) -> bool:
        """Проверяет существование таблицы."""
        return name in self._tables