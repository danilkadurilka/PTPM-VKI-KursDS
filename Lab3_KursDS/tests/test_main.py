"""Интеграционные тесты точки входа (src/main.py).

Проверяется, что модули проекта соединяются в единый рабочий сценарий:
консольный ввод подменяется заглушкой `unittest.mock`, а база данных и
лог стороннего сервиса размещаются во временной папке, поэтому тест
не зависит от рабочих данных и не требует сети.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from Lab3_KursDS.src import main, repository, third_party, triangle
from Lab3_KursDS.src.calculator import TriangleCalculator
from Lab3_KursDS.src.controller import Controller
from Lab3_KursDS.src.repository import TriangleRepository
from Lab3_KursDS.src.third_party import SimulatedEmailSender
from Lab3_KursDS.src.user_interaction import ConsoleUserInteraction


class BuildControllerTestCase(unittest.TestCase):
    """Проверка фабрики зависимостей и полного прогона приложения."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.database = os.path.join(self.folder.name, "data", "triangles.db")
        self.log_path = os.path.join(self.folder.name, "Logs", "email_log.txt")
        self.controller = main.build_controller(
            database=self.database, log_path=self.log_path
        )
        self.addCleanup(self.controller.repository.close)

    def test_builds_controller_with_real_implementations_of_all_modules(self):
        self.assertIsInstance(self.controller, Controller)
        self.assertIsInstance(self.controller.calculator, TriangleCalculator)
        self.assertIsInstance(self.controller.repository, TriangleRepository)
        self.assertIsInstance(
            self.controller.user_interaction, ConsoleUserInteraction
        )
        self.assertIsInstance(
            self.controller.third_party, SimulatedEmailSender
        )

    def test_falls_back_to_default_database_and_log_paths(self):
        default_database = os.path.join(self.folder.name, "default", "triangles.db")
        default_log = os.path.join(self.folder.name, "default", "email_log.txt")
        with patch.object(repository, "DATABASE_PATH", default_database), \
                patch.object(third_party, "LOG_FILE", default_log):
            controller = main.build_controller()
        self.addCleanup(controller.repository.close)
        self.assertEqual(controller.repository.database, default_database)
        self.assertEqual(controller.third_party.log_path, default_log)

    def test_explicit_paths_override_defaults(self):
        self.assertEqual(self.controller.repository.database, self.database)
        self.assertEqual(self.controller.third_party.log_path, self.log_path)

    def test_full_run_creates_database_file_and_saves_result(self):
        with patch("builtins.input", side_effect=["3", "4", "5"]):
            message = self.controller.run()
        self.assertEqual(
            message, "Треугольник по сторонам (3, 4, 5) — разносторонний."
        )
        self.assertTrue(os.path.isfile(self.database))

    def test_full_run_writes_result_to_simulated_service_log(self):
        with patch("builtins.input", side_effect=["3", "4", "5"]):
            self.controller.run()
        with open(self.log_path, encoding="utf-8") as log_file:
            log = log_file.read()
        self.assertIn(triangle.TYPE_SCALENE, log)

    def test_second_run_in_new_application_uses_database_of_previous_run(self):
        with patch("builtins.input", side_effect=["3", "4", "5"]):
            self.controller.run()

        second = main.build_controller(
            database=self.database, log_path=self.log_path
        )
        self.addCleanup(second.repository.close)
        with patch("builtins.input", side_effect=["3", "4", "5"]):
            message = second.run()

        self.assertIn("Результат взят из базы данных", message)


if __name__ == "__main__":
    unittest.main()