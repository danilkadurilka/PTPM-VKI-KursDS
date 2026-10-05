"""Тестовые заглушки (test doubles) для интеграционных тестов.

Заглушки реализуют те же абстрактные интерфейсы, что и рабочие модули,
поэтому контроллер принимает их без каких-либо изменений в коде.
"""

from ..src.user_interaction import UserInteractionInterface


class StubUserInteraction(UserInteractionInterface):
    """Заглушка пользовательского ввода вместо консоли.

    Каждый набор из трёх ответов используется один раз, поэтому тест может
    задать сценарий из нескольких последовательных запусков контроллера.
    Все показанные пользователю сообщения сохраняются в `shown`.
    """

    def __init__(self, *answer_sets):
        self.answer_sets = []
        for answer_set in answer_sets:
            answers = tuple(answer_set)
            if len(answers) != 3:
                raise ValueError(
                    f"Ожидалось три ответа, получено {len(answers)}"
                )
            self.answer_sets.append(answers)
        self.shown = []

    def get_sides(self):
        if not self.answer_sets:
            raise AssertionError(
                "Заглушка ввода исчерпала заготовленные ответы"
            )
        return self.answer_sets.pop(0)

    def show_result(self, message):
        self.shown.append(message)