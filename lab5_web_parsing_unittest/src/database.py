"""Модуль 1: работа с SQLite через DatabaseRepository."""

import sqlite3
from typing import Optional

from src.exceptions import (
    ValidationError,
    DuplicateIDError,
    RecordNotFoundError,
)

MAX_NAME_LEN = 256
MAX_MESSAGE_LEN = 8096


class DatabaseRepository:
    """Репозиторий для работы с таблицей comments."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._create_table()

    # ------------------------------------------------------------------ #
    # Служебные методы
    # ------------------------------------------------------------------ #
    def _create_table(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id      INTEGER PRIMARY KEY,
                name    TEXT NOT NULL,
                message TEXT NOT NULL
            );
            """
        )

    def close(self) -> None:
        if self._conn:
            self._conn.close()

    # ------------------------------------------------------------------ #
    # Валидация
    # ------------------------------------------------------------------ #
    @staticmethod
    def _validate_id(comment_id) -> None:
        if not isinstance(comment_id, int) or isinstance(comment_id, bool):
            raise ValidationError("comment_id должен быть целым числом.")
        if comment_id <= 0:
            raise ValidationError("comment_id должен быть положительным.")

    @staticmethod
    def _validate_name(username) -> None:
        if not isinstance(username, str):
            raise ValidationError("username должен быть строкой.")
        if not username.strip():
            raise ValidationError("username не может быть пустым.")
        if len(username) > MAX_NAME_LEN:
            raise ValidationError(
                f"username длиннее {MAX_NAME_LEN} символов."
            )

    @staticmethod
    def _validate_message(message) -> None:
        if not isinstance(message, str):
            raise ValidationError("message должен быть строкой.")
        if not message.strip():
            raise ValidationError("message не может быть пустым.")
        if len(message) > MAX_MESSAGE_LEN:
            raise ValidationError(
                f"message длиннее {MAX_MESSAGE_LEN} символов."
            )


    def add(self, comment_id: int, username: str, message: str) -> bool:
        self._validate_id(comment_id)
        self._validate_name(username)
        self._validate_message(message)

        try:
            self._conn.execute(
                "INSERT INTO comments (id, name, message) VALUES (?, ?, ?);",
                (comment_id, username, message),
            )
        except sqlite3.IntegrityError as exc:
            raise DuplicateIDError(
                f"Запись с id={comment_id} уже существует."
            ) from exc
        return True

    def get_by_id(self, comment_id: int) -> Optional[dict]:
        self._validate_id(comment_id)
        cursor = self._conn.execute(
            "SELECT id, name, message FROM comments WHERE id = ?;",
            (comment_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_name(self, username: str) -> list[dict]:
        self._validate_name(username)
        cursor = self._conn.execute(
            "SELECT id, name, message FROM comments WHERE name = ? ORDER BY id;",
            (username,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def update(self, comment_id: int, new_message: str) -> bool:
        self._validate_id(comment_id)
        self._validate_message(new_message)

        cursor = self._conn.execute(
            "UPDATE comments SET message = ? WHERE id = ?;",
            (new_message, comment_id),
        )
        if cursor.rowcount == 0:
            raise RecordNotFoundError(
                f"Запись с id={comment_id} не найдена."
            )
        return True

    def delete(self, comment_id: int) -> bool:
        self._validate_id(comment_id)
        cursor = self._conn.execute(
            "DELETE FROM comments WHERE id = ?;",
            (comment_id,),
        )
        if cursor.rowcount == 0:
            raise RecordNotFoundError(
                f"Запись с id={comment_id} не найдена."
            )
        return True