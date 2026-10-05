"""Точка входа: собирает модули проекта и запускает контроллер.

Запуск выполняется из корня репозитория как модуль:

    python -m Lab3_KursDS.src.main
"""

import logging
import os
import sys

from . import repository, third_party
from .calculator import TriangleCalculator
from .controller import Controller
from .repository import TriangleRepository
from .third_party import SimulatedEmailSender
from .user_interaction import ConsoleUserInteraction

LOG_DIR = "Logs"
LOG_FILE = "app_log.txt"

LOG_FORMAT = "%(asctime)s | [%(levelname)-7s] | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging():
    """Настраивает логирование параллельно в консоль и в файл."""
    os.makedirs(LOG_DIR, exist_ok=True)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                os.path.join(LOG_DIR, LOG_FILE), encoding="utf-8"
            ),
        ],
    )
    logging.info("Логгер успешно сконфигурирован")


def build_controller(database=None, log_path=None):
    """Создаёт контроллер с реальными реализациями всех зависимостей.

    Пути передаются явно, чтобы тесты могли работать с временными файлами
    и базой в памяти, не затрагивая рабочие данные.
    """
    if database is None:
        database = repository.DATABASE_PATH
    if log_path is None:
        log_path = third_party.LOG_FILE

    return Controller(
        calculator=TriangleCalculator(),
        repository=TriangleRepository(database),
        user_interaction=ConsoleUserInteraction(),
        third_party=SimulatedEmailSender(log_path),
    )


def main():
    setup_logging()
    controller = build_controller()
    try:
        message = controller.run()
        logging.info("Результат операции: %s", message)
    except Exception as ex:
        logging.error("Сценарий прерван: %s", ex)
        logging.exception("Трассировка стека исключения:")
    finally:
        controller.repository.close()


if __name__ == "__main__":
    main()