"""b. Класс работы с базой данных (SQLite).

Одна запись таблицы соответствует одной задаче пользователя: три длины
сторон, тип треугольника и текст ошибки. Запись идентифицируется тройкой
длин сторон, поэтому повторный запрос с теми же сторонами не пересчитывается,
а читается из базы как из кэша.
"""

import os
import sqlite3
from dataclasses import dataclass

#: Путь к файлу базы данных по умолчанию (создаётся при первом запуске).
DATABASE_PATH = os.path.join("data", "triangles.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS triangle_results (
    side1 REAL NOT NULL,
    side2 REAL NOT NULL,
    side3 REAL NOT NULL,
    triangle_type TEXT NOT NULL,
    error_message TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (side1, side2, side3)
)
"""

INSERT_SQL = """
INSERT OR IGNORE INTO triangle_results
    (side1, side2, side3, triangle_type, error_message)
VALUES (?, ?, ?, ?, ?)
"""

SELECT_SQL = """
SELECT side1, side2, side3, triangle_type, error_message
FROM triangle_results
WHERE side1 = ? AND side2 = ? AND side3 = ?
"""

DELETE_SQL = """
DELETE FROM triangle_results
WHERE side1 = ? AND side2 = ? AND side3 = ?
"""

MEMORY_DATABASE = ":memory:"


@dataclass(frozen=True)
class TriangleRecord:
    """Строка таблицы `triangle_results`."""

    side1: float
    side2: float
    side3: float
    triangle_type: str
    error_message: str = ""


class TriangleRepository:
    """Хранилище результатов вычислений на основе SQLite.

    Путь `:memory:` создаёт временную базу в оперативной памяти — такой
    режим используется в тестах, не затрагивая файловую систему.
    """

    def __init__(self, database=DATABASE_PATH):
        self.database = database
        if database != MEMORY_DATABASE:
            folder = os.path.dirname(os.path.abspath(database))
            os.makedirs(folder, exist_ok=True)
        self._connection = sqlite3.connect(database)
        self._connection.execute(CREATE_TABLE_SQL)
        self._connection.commit()

    def add(self, record):
        """Добавляет запись и сообщает, была ли она действительно сохранена.

        Возвращает `False`, если запись с такими же сторонами уже существует:
        повторная запись не перезаписывает результат первой проверки.
        """
        cursor = self._connection.execute(
            INSERT_SQL,
            (
                record.side1,
                record.side2,
                record.side3,
                record.triangle_type,
                record.error_message,
            ),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def get(self, side1, side2, side3):
        """Возвращает запись по трём длинам сторон либо `None`, если её нет."""
        row = self._connection.execute(
            SELECT_SQL, (side1, side2, side3)
        ).fetchone()
        if row is None:
            return None
        return TriangleRecord(*row)

    def delete(self, side1, side2, side3):
        """Удаляет запись по трём длинам сторон.

        Возвращает `True`, если запись была удалена, и `False`, если её
        в базе не было.
        """
        cursor = self._connection.execute(
            DELETE_SQL, (side1, side2, side3)
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def close(self):
        """Закрывает соединение с базой данных."""
        self._connection.close()