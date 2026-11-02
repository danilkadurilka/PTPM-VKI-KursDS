def validate_password(password: str) -> bool:
    """
    :param password: Проверяемый пароль
    :return: True, если пароль удовлетворяет всем условиям, иначе False
    :raises TypeError: Если входной параметр не является строкой
    :raises ValueError: Если входная строка содержит символы пробела
    """
    # Этап 1: Проверка входных данных

    # 1. Контроль типа аргумента
    if not isinstance(password, str):
        raise TypeError("Пароль должен быть строкой")

    # 2. Контроль пробельных символов (ASCII 32)
    if ' ' in password:
        raise ValueError("Пароль не должен содержать пробелы")

    # Этап 2: Проверка критериев валидности

    # 1. Длина строки: от 8 до 20 символов включительно
    if not (8 <= len(password) <= 20):
        return False

    # Флаги для проверки наличия символов
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    # Разрешенные специальные символы
    special_chars = {'!', '@', '#', '$', '%', '^', '&', '*'}

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_chars:
            has_special = True

    # Возвращаем True только если ВСЕ условия выполнены
    return has_upper and has_lower and has_digit and has_special