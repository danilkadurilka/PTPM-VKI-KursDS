"""Юнит-тесты класса сторонней зависимости (src/third_party.py).

Реализация лишь имитирует отправку, поэтому проверяются история отправлений
и содержимое лог-файла, а не реальная передача данных.
"""

import os
import tempfile
import unittest

from Lab3_KursDS.src.third_party import (
    SimulatedEmailSender,
    ThirdPartyInterface,
)

RECIPIENT = "otdel@example.com"


class InterfaceTestCase(unittest.TestCase):
    """Проверка того, что абстрактный класс действительно является интерфейсом."""

    def test_interface_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            ThirdPartyInterface()

    def test_interface_exposes_abstract_send_method(self):
        self.assertEqual(
            list(ThirdPartyInterface.__abstractmethods__), ["send"]
        )


class SimulatedEmailSenderTestCase(unittest.TestCase):
    """Проверка имитации отправки письма в лог-файл."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(self.folder.name, "nested", "email.txt")
        self.sender = SimulatedEmailSender(self.log_path)

    def tearDown(self):
        self.folder.cleanup()

    def read_log(self):
        with open(self.log_path, encoding="utf-8") as log_file:
            return log_file.read()

    def test_send_returns_true_for_recipient_and_message(self):
        self.assertTrue(self.sender.send(RECIPIENT, "Треугольник найден"))

    def test_send_keeps_message_in_history(self):
        self.sender.send(RECIPIENT, "Треугольник найден")
        self.assertEqual(
            self.sender.history, [(RECIPIENT, "Треугольник найден")]
        )

    def test_send_appends_every_message_to_history(self):
        self.sender.send(RECIPIENT, "первое")
        self.sender.send(RECIPIENT, "второе")
        self.assertEqual(len(self.sender.history), 2)

    def test_send_writes_recipient_and_message_to_log(self):
        self.sender.send(RECIPIENT, "Треугольник найден")
        log = self.read_log()
        self.assertIn(RECIPIENT, log)
        self.assertIn("Треугольник найден", log)

    def test_send_creates_log_file_and_its_folder(self):
        self.sender.send(RECIPIENT, "Треугольник найден")
        self.assertTrue(os.path.isfile(self.log_path))

    def test_keeps_previous_log_lines_when_log_is_reused(self):
        self.sender.send(RECIPIENT, "первое")
        self.sender.send(RECIPIENT, "второе")
        self.assertEqual(len(self.read_log().splitlines()), 2)

    def test_send_returns_false_and_skips_history_for_empty_recipient(self):
        self.assertFalse(self.sender.send("", "Треугольник найден"))
        self.assertEqual(self.sender.history, [])

    def test_send_returns_false_and_skips_history_for_empty_message(self):
        self.assertFalse(self.sender.send(RECIPIENT, ""))
        self.assertEqual(self.sender.history, [])

    def test_failed_send_does_not_create_log_file(self):
        self.sender.send("", "Треугольник найден")
        self.assertFalse(os.path.exists(self.log_path))

    def test_failed_send_is_reported_in_errors_list(self):
        self.sender.send("", "")
        self.assertEqual(len(self.sender.errors), 1)


if __name__ == "__main__":
    unittest.main()