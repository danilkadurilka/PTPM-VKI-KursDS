"""c. Класс взаимодействия с пользователем.

Абстрактный базовый класс `UserInteractionInterface` играет роль интерфейса:
контроллер зависит только от него и не знает, как именно получен ввод.
Реализация читает данные из консоли, поэтому её легко подменить заглушкой
в тестах.
"""

import abc

#: Приглашения, по одному на каждую сторону.
PROMPTS = (
    "Введите длину стороны A: ",
    "Введите длину стороны B: ",
    "Введите длину стороны C: ",
)

EMPTY_ANSWER_MESSAGE = "Пустой ответ не принимается, попробуйте ещё раз."

#: Сколько раз подряд переспрашивается пользователь, пока не введёт число.
MAX_ATTEMPTS = 3


class UserInteractionInterface(abc.ABC):
    """Интерфейс получения данных от пользователя и вывода результата."""

    @abc.abstractmethod
    def get_sides(self) -> tuple:
        """Возвращает три строки, введённые пользователем."""

    @abc.abstractmethod
    def show_result(self, message: str) -> None:
        """Показывает пользователю итоговую строку-результат."""


class ConsoleUserInteraction(UserInteractionInterface):
    """Взаимодействие через консоль: `input()` и `print()`."""

    def get_sides(self) -> tuple:
        return tuple(self._ask(prompt) for prompt in PROMPTS)

    def show_result(self, message: str) -> None:
        print(message)

    def _ask(self, prompt):
        """Читает непустой ответ, переспрашивая до MAX_ATTEMPTS попыток."""
        for _ in range(MAX_ATTEMPTS):
            answer = input(prompt).strip()
            if answer:
                return answer
            print(EMPTY_ANSWER_MESSAGE)
        return ""