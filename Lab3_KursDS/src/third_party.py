"""d. Класс сторонней зависимости.

Абстрактный базовый класс `ThirdPartyInterface` описывает передачу строки
результата стороннему процессу (например, email-серверу). Реализация
`SimulatedEmailSender` ничего не отправляет: она имитирует передачу,
складывая письма в историю и в лог-файл, поэтому тесты и учебный запуск
не требуют сети.
"""

import abc
import datetime
import os

LOG_DIR = "Logs"
LOG_FILE = os.path.join(LOG_DIR, "email_log.txt")

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

RECIPIENT_VALIDATION_ERROR = "получатель и текст письма не должны быть пустыми"


class ThirdPartyInterface(abc.ABC):
    """Интерфейс передачи данных стороннему процессу."""

    @abc.abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """Передаёт строку-результат и сообщает об успехе передачи."""


class SimulatedEmailSender(ThirdPartyInterface):
    """Имитация отправки письма: лог-файл плюс история отправлений."""

    def __init__(self, log_path=LOG_FILE):
        self.log_path = log_path
        self.history: list[tuple[str, str]] = []
        self.errors: list[str] = []

    def send(self, recipient: str, message: str) -> bool:
        if not recipient or not message:
            self.errors.append(RECIPIENT_VALIDATION_ERROR)
            return False
        self.history.append((recipient, message))
        self._write_log(recipient, message)
        return True

    def _write_log(self, recipient: str, message: str) -> None:
        folder = os.path.dirname(os.path.abspath(self.log_path))
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime(DATE_FORMAT)
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp} | Кому: {recipient} | {message}\n")