"""Юнит-тесты класса взаимодействия с пользователем (src/user_interaction.py).

Пользовательский ввод подменяется заглушкой `unittest.mock.patch` для
встроенной функции `input`, поэтому тесты не блокируют консоль.
"""

import unittest
from unittest.mock import call, patch

from Lab3_KursDS.src import user_interaction
from Lab3_KursDS.src.user_interaction import (
    ConsoleUserInteraction,
    UserInteractionInterface,
)


class InterfaceTestCase(unittest.TestCase):
    """Проверка того, что абстрактный класс действительно является интерфейсом."""

    def test_interface_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            UserInteractionInterface()

    def test_interface_exposes_both_abstract_methods(self):
        self.assertEqual(
            sorted(UserInteractionInterface.__abstractmethods__),
            ["get_sides", "show_result"],
        )

    def test_partial_implementation_cannot_be_instantiated(self):
        class OnlyGetsSides(UserInteractionInterface):
            def get_sides(self):
                return ("1", "1", "1")

        with self.assertRaises(TypeError):
            OnlyGetsSides()


class ConsoleGetSidesTestCase(unittest.TestCase):
    """Проверка чтения трёх сторон из консоли."""

    def setUp(self):
        self.interaction = ConsoleUserInteraction()

    def test_returns_three_answers_in_prompt_order(self):
        with patch("builtins.input", side_effect=["3", "4", "5"]) as input_mock:
            self.assertEqual(self.interaction.get_sides(), ("3", "4", "5"))
        self.assertEqual(
            input_mock.call_args_list,
            [call(prompt) for prompt in user_interaction.PROMPTS],
        )

    def test_trims_whitespace_around_answer(self):
        with patch("builtins.input", side_effect=["  3  ", "\t4\n", " 5"]):
            self.assertEqual(self.interaction.get_sides(), ("3", "4", "5"))

    def test_repeats_question_while_answer_is_empty(self):
        answers = ["", "   ", "7", "4", "5", "6"]
        with patch("builtins.input", side_effect=answers) as input_mock, \
                patch("builtins.print"):
            self.assertEqual(self.interaction.get_sides(), ("7", "4", "5"))
        self.assertEqual(input_mock.call_count, 5)

    def test_repeats_question_for_each_side_separately(self):
        answers = ["", "3", "", "4", "", "5"]
        with patch("builtins.input", side_effect=answers), \
                patch("builtins.print"):
            self.assertEqual(self.interaction.get_sides(), ("3", "4", "5"))

    def test_returns_empty_string_when_user_never_enters_value(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(self.interaction.get_sides(), ("", "", ""))

    def test_repeated_questions_use_exhausted_attempt_limit(self):
        limit = user_interaction.MAX_ATTEMPTS
        with patch("builtins.input", return_value="") as input_mock:
            self.interaction.get_sides()
        self.assertEqual(input_mock.call_count, 3 * limit)

    def test_accepts_non_numeric_text_without_validation(self):
        with patch("builtins.input", side_effect=["a", "b", "c"]):
            self.assertEqual(self.interaction.get_sides(), ("a", "b", "c"))


class ConsoleShowResultTestCase(unittest.TestCase):
    """Проверка вывода результата в консоль."""

    def test_prints_message_to_console(self):
        with patch("builtins.print") as print_mock:
            ConsoleUserInteraction().show_result("Треугольник равносторонний")
        print_mock.assert_called_once_with("Треугольник равносторонний")


if __name__ == "__main__":
    unittest.main()