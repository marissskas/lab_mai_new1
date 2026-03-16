from typing import Dict, Any, Optional, List, Tuple

def parse_filters(filter_str: str) -> Optional[Dict[str, Any]]:
    """Парсинг строки фильтров."""
    if not filter_str or filter_str.strip() == "":
        return None
    
    filters = {}
    pairs = filter_str.split(',')
    
    for pair in pairs:
        if '=' not in pair:
            continue
        
        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        try:
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit() and value.count('.') == 1:
                value = float(value)
        except ValueError:
            pass
        
        filters[key] = value
    
    return filters if filters else None

def print_records(records: List[Tuple], title: str = "Результаты") -> None:
    """Вывод записей."""
    if not records:
        print(f"\n{title}: записей не найдено")
        return
    
    print(f"\n{title}:")
    print("-" * 60)
    
    for record in records:
        if len(record) == 5:
            print(f"ID: {record[0]}, Имя: {record[1]}, Фамилия: {record[2]}, Возраст: {record[3]}, Пол: {record[4]}")
        else:
            print(record)
    
    print("-" * 60)
    print(f"Всего: {len(records)}")

def read_int(prompt: str) -> int:
    """Чтение целого числа."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Ошибка: введите целое число")

def read_optional_int(prompt: str) -> Optional[int]:
    """Чтение опционального целого числа."""
    value = input(prompt).strip()
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        print("Ошибка: введите целое число")
        return None

def read_optional_float(prompt: str) -> Optional[float]:
    """Чтение опционального числа с плавающей точкой."""
    value = input(prompt).strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        print("Ошибка: введите число")
        return None

def read_string(prompt: str, required: bool = True) -> Optional[str]:
    """Чтение строки."""
    while True:
        value = input(prompt).strip()
        if required and not value:
            print("Поле не может быть пустым")
            continue
        return value if value else None