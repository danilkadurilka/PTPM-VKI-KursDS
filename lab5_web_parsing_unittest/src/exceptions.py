class ValidationError(ValueError):
    """Ошибка валидации входных данных."""


class DuplicateIDError(ValueError):
    """Попытка вставить запись с уже существующим ID."""


class RecordNotFoundError(LookupError):
    """Запись с указанным ID не найдена."""