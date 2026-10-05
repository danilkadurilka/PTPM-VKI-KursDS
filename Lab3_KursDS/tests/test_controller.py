"""Интеграционные тесты класса-контроллера (src/controller.py).

Проверяется совместная работа реальных модулей проекта: вычислений,
базы данных и контроллера. Границы системы изолированы заглушками:
пользовательский ввод подменяется классом `StubUserInteraction`, а
передача данных стороннему серверу — объектом `unittest.mock`.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from Lab3_KursDS.src import triangle
from Lab3_KursDS.src.calculator import TriangleCalculator
from Lab3_KursDS.src.controller import Controller
from Lab3_KursDS.src.repository import TriangleRecord, TriangleRepository
from Lab3_KursDS.src.third_party import SimulatedEmailSender, ThirdPartyInterface
from Lab3_KursDS.src.user_interaction import ConsoleUserInteraction

from .doubles import StubUserInteraction

RECIPIENT = "otdel@example.com"

SCALENE_MESSAGE = "Треугольник по сторонам (3, 4, 5) — разносторонний."
CACHED_MESSAGE = (
    "Треугольник по сторонам (3, 4, 5) — разносторонний. "
    "Результат взят из базы данных."
)
NON_NUMERIC_MESSAGE = (
    "Определить тип треугольника не удалось: "
    "введены пустые или нечисловые значения."
)


class ControllerIntegrationTestCase(unittest.TestCase):
    """Общая сборка контроллера из настоящих модулей и заглушек по краям."""

    def setUp(self):
        self.repository = TriangleRepository(":memory:")
        self.addCleanup(self.repository.close)
        self.service = Mock()

    def build(self, *answer_sets, calculator=None, repository=None, service=None,
              recipient=RECIPIENT):
        return Controller(
            calculator=calculator if calculator else TriangleCalculator(),
            repository=repository if repository else self.repository,
            user_interaction=StubUserInteraction(*answer_sets),
            third_party=service if service else self.service,
            recipient=recipient,
        )


class FreshRequestTestCase(ControllerIntegrationTestCase):
    """Проверка ветки «записи в базе нет → вычисляем и сохраняем»."""

    def setUp(self):
        super().setUp()
        self.controller = self.build(("3", "4", "5"))

    def test_returns_message_with_calculated_type(self):
        self.assertEqual(self.controller.run(), SCALENE_MESSAGE)

    def test_saves_calculation_result_to_database(self):
        self.controller.run()
        self.assertEqual(
            self.repository.get(3.0, 4.0, 5.0),
            TriangleRecord(
                side1=3.0, side2=4.0, side3=5.0,
                triangle_type=triangle.TYPE_SCALENE, error_message="",
            ),
        )

    def test_sends_result_to_third_party_service_once(self):
        self.controller.run()
        self.service.send.assert_called_once_with(RECIPIENT, SCALENE_MESSAGE)

    def test_shows_same_message_to_user_and_to_service(self):
        message = self.controller.run()
        self.assertEqual(self.controller.user_interaction.shown, [message])
        self.assertEqual(self.service.send.call_args[0][1], message)

    def test_fresh_result_is_not_marked_as_taken_from_database(self):
        self.assertNotIn("базе данных", self.controller.run())

    def test_stores_requests_with_different_sides_independently(self):
        self.controller.run()
        self.repository.add(
            TriangleRecord(2.0, 2.0, 3.0, triangle.TYPE_ISOSCELES)
        )
        self.assertIsNotNone(self.repository.get(3.0, 4.0, 5.0))
        self.assertIsNotNone(self.repository.get(2.0, 2.0, 3.0))

    def test_refusal_for_impossible_triangle_is_cached_with_error_text(self):
        controller = self.build(("1", "2", "9"))
        controller.run()
        stored = self.repository.get(1.0, 2.0, 9.0)
        self.assertEqual(stored.triangle_type, triangle.TYPE_NOT_TRIANGLE)
        self.assertEqual(stored.error_message, triangle.ERROR_DEGENERATE)


class CachedRequestTestCase(ControllerIntegrationTestCase):
    """Проверка ветки «запись в базе есть → берём результат из БД»."""

    def setUp(self):
        super().setUp()
        self.calculator = Mock(spec=TriangleCalculator)
        self.repository.add(
            TriangleRecord(
                side1=3.0, side2=4.0, side3=5.0,
                triangle_type=triangle.TYPE_SCALENE, error_message="",
            )
        )
        self.controller = self.build(
            ("3.0", "4.0", "5.0"), calculator=self.calculator
        )

    def test_does_not_call_calculations_for_data_already_in_database(self):
        self.controller.run()
        self.calculator.calculate.assert_not_called()

    def test_returns_stored_result_marked_as_taken_from_database(self):
        self.assertEqual(self.controller.run(), CACHED_MESSAGE)

    def test_matches_record_written_with_equal_but_other_representation(self):
        self.controller.run()
        self.assertEqual(self.service.send.call_args[0][1], CACHED_MESSAGE)

    def test_sends_cached_result_to_third_party_service(self):
        self.controller.run()
        self.assertEqual(self.service.send.call_count, 1)

    def test_does_not_add_duplicate_record_to_database(self):
        controller = self.build(("3", "4", "5"), calculator=self.calculator)
        repository = Mock(wraps=self.repository)
        controller.repository = repository
        controller.run()
        repository.add.assert_not_called()

    def test_shows_cached_message_to_user(self):
        self.controller.run()
        self.assertEqual(
            self.controller.user_interaction.shown, [CACHED_MESSAGE]
        )


class RepeatedRequestTestCase(ControllerIntegrationTestCase):
    """Проверка сквозного сценария из двух одинаковых запросов подряд."""

    def setUp(self):
        super().setUp()
        self.controller = self.build(("3", "4", "5"), ("3", "4", "5"))

    def test_first_request_calculates_and_second_reads_from_database(self):
        calculate = self.controller.calculator.calculate
        with patch.object(
            self.controller.calculator, "calculate", wraps=calculate
        ) as calculate_mock:
            self.controller.run()
            self.controller.run()
        self.assertEqual(calculate_mock.call_count, 1)

    def test_both_requests_reach_third_party_service(self):
        self.controller.run()
        self.controller.run()
        self.assertEqual(self.service.send.call_count, 2)

    def test_service_receives_fresh_and_cached_versions_of_same_result(self):
        self.controller.run()
        self.controller.run()
        sent = [args[0][1] for args in self.service.send.call_args_list]
        self.assertEqual(sent, [SCALENE_MESSAGE, CACHED_MESSAGE])

    def test_database_contains_single_record_after_two_requests(self):
        self.controller.run()
        self.controller.run()
        self.assertIsNotNone(self.repository.get(3.0, 4.0, 5.0))
        self.assertIsNone(self.repository.get(5.0, 5.0, 5.0))


class InvalidInputTestCase(ControllerIntegrationTestCase):
    """Проверка ветки «ввод нечисловой → результат не кэшируется»."""

    def setUp(self):
        super().setUp()
        self.repository_spy = Mock(wraps=self.repository)
        self.controller = self.build(
            ("3", "четыре", "5"), repository=self.repository_spy
        )

    def test_returns_message_with_reason_of_refusal(self):
        self.assertEqual(self.controller.run(), NON_NUMERIC_MESSAGE)

    def test_does_not_add_unusable_request_to_database(self):
        self.controller.run()
        self.repository_spy.add.assert_not_called()

    def test_does_not_look_up_database_for_unparsable_sides(self):
        self.controller.run()
        self.repository_spy.get.assert_not_called()

    def test_still_sends_refusal_to_third_party_service(self):
        self.controller.run()
        self.assertEqual(self.service.send.call_count, 1)

    def test_returns_refusal_for_empty_side(self):
        controller = self.build(("", "", ""))
        self.assertEqual(controller.run(), NON_NUMERIC_MESSAGE)

    def test_returns_refusal_for_negative_side(self):
        controller = self.build(("-3", "4", "5"))
        message = controller.run()
        self.assertIn("не существует", message)
        self.assertIn(triangle.ERROR_INVALID_SIDE, message)


class IsolationTestCase(ControllerIntegrationTestCase):
    """Проверка изоляции модулей заглушками вместо реального сервиса."""

    def setUp(self):
        super().setUp()
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.log_path = os.path.join(self.folder.name, "email.txt")

    def test_service_mock_implements_whole_external_interface(self):
        service = Mock(spec=ThirdPartyInterface)
        controller = self.build(("3", "4", "5"), service=service)
        controller.run()
        service.send.assert_called_once_with(RECIPIENT, SCALENE_MESSAGE)

    def test_patched_send_keeps_real_service_from_writing_log(self):
        service = SimulatedEmailSender(self.log_path)
        controller = self.build(("3", "4", "5"), service=service)
        with patch.object(
            SimulatedEmailSender, "send", return_value=True
        ) as send_mock:
            controller.run()
        send_mock.assert_called_once_with(RECIPIENT, SCALENE_MESSAGE)
        self.assertEqual(service.history, [])
        self.assertFalse(os.path.exists(self.log_path))

    def test_console_input_is_replaced_by_patched_builtin(self):
        service = SimulatedEmailSender(self.log_path)
        controller = Controller(
            calculator=TriangleCalculator(),
            repository=self.repository,
            user_interaction=ConsoleUserInteraction(),
            third_party=service,
            recipient=RECIPIENT,
        )
        with patch("builtins.input", side_effect=["3", "4", "5"]):
            message = controller.run()
        self.assertEqual(message, SCALENE_MESSAGE)
        self.assertEqual(service.history, [(RECIPIENT, SCALENE_MESSAGE)])

    def test_console_input_stub_can_be_exhausted(self):
        controller = self.build(("3", "4", "5"))
        controller.run()
        with self.assertRaises(AssertionError):
            controller.run()

    def test_reports_unsent_result_if_service_refuses(self):
        service = Mock()
        service.send.return_value = False
        controller = self.build(("3", "4", "5"), service=service)
        self.assertEqual(
            controller.run(),
            f"{SCALENE_MESSAGE} Не удалось отправить результат "
            "стороннему сервису.",
        )

    def test_result_is_saved_to_database_even_if_service_refuses(self):
        service = Mock()
        service.send.return_value = False
        controller = self.build(("3", "4", "5"), service=service)
        controller.run()
        self.assertIsNotNone(self.repository.get(3.0, 4.0, 5.0))

    def test_custom_recipient_is_passed_to_service(self):
        controller = self.build(("3", "4", "5"), recipient="student@example.com")
        controller.run()
        self.assertEqual(self.service.send.call_args[0][0], "student@example.com")


if __name__ == "__main__":
    unittest.main()