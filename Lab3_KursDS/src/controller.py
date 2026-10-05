"""e. Класс-контроллер: сквозной бизнес-сценарий.

Контроллер связывает все модули проекта: получает ввод, проверяет кэш в
базе данных, при необходимости запускает вычисления, записывает результат
и передаёт строку-результат стороннему сервису. Все зависимости передаются
в конструктор, поэтому в тестах подменяются заглушками.
"""

import logging

from . import triangle
from .repository import TriangleRecord

#: Адрес получателя письма со стороны стороннего сервиса.
DEFAULT_RECIPIENT = "otdel.obrazovaniya@example.com"


class Controller:
    """Оркестратор сценария «запрос → вычисление → кэш → отправка»."""

    def __init__(self, calculator, repository, user_interaction, third_party,
                 recipient=DEFAULT_RECIPIENT):
        self.calculator = calculator
        self.repository = repository
        self.user_interaction = user_interaction
        self.third_party = third_party
        self.recipient = recipient

    def run(self):
        """Выполняет один полный цикл и возвращает строку-результат."""
        raw_sides = self.user_interaction.get_sides()
        logging.info("Запрос: стороны = %r", raw_sides)

        parsed_sides = triangle.parse_sides(*raw_sides)
        record = (
            self.repository.get(*parsed_sides) if parsed_sides is not None else None
        )
        from_cache = record is not None

        if from_cache:
            logging.info("Найдена запись в базе данных: %r", record)
            result = triangle.TriangleResult(
                triangle_type=record.triangle_type,
                error_message=record.error_message,
            )
        else:
            result = self.calculator.calculate(*raw_sides)
            if parsed_sides is not None:
                added = self.repository.add(
                    TriangleRecord(
                        side1=parsed_sides[0],
                        side2=parsed_sides[1],
                        side3=parsed_sides[2],
                        triangle_type=result.triangle_type,
                        error_message=result.error_message,
                    )
                )
                logging.info("Запись добавлена в базу данных: %s", added)

        message = self._build_message(parsed_sides, result, from_cache)
        if not self.third_party.send(self.recipient, message):
            logging.warning("Сторонний сервис не принял результат")
            message += " Не удалось отправить результат стороннему сервису."
        self.user_interaction.show_result(message)
        return message

    def _build_message(self, sides, result, from_cache):
        """Собирает строку-результат для показа пользователю и отправки."""
        if sides is None:
            core = (
                "Определить тип треугольника не удалось: "
                f"{result.error_message}."
            )
        else:
            formatted = ", ".join(f"{side:g}" for side in sides)
            if result.triangle_type == triangle.TYPE_NOT_TRIANGLE:
                core = (
                    f"Треугольник по сторонам ({formatted}) не существует: "
                    f"{result.error_message}."
                )
            else:
                core = (
                    f"Треугольник по сторонам ({formatted}) — "
                    f"{result.triangle_type}."
                )
        source = " Результат взят из базы данных." if from_cache else ""
        return core + source