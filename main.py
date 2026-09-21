import logging
import os
import sys

import triangle

LOG_FORMAT = "%(asctime)s | [%(levelname)-7s] | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_DIR = "Logs"
LOG_FILE = os.path.join(LOG_DIR, "file_txt.log")

DEFAULT_INVALID_COORDS = "(-1, -1)"
DEFAULT_NON_NUMERIC_COORDS = "(-2, -2)"


def setup_logging():
    """Настраивает логирование параллельно в консоль и в файл."""
    os.makedirs(LOG_DIR, exist_ok=True)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")


def process_triangle(lines_a, lines_b, lines_c):
    """Обрабатывает запрос на определение вида треугольника.

    Возвращает кортеж (тип_треугольника, координаты_вершин).
    """
    logging.info("Запрос: сторона A = %r, сторона B = %r, сторона C = %r",
                 lines_a, lines_b, lines_c)

    parsed = triangle.parse_sides(lines_a, lines_b, lines_c)
    if parsed is None:
        logging.warning("Нечисловые входные данные: %r, %r, %r",
                        lines_a, lines_b, lines_c)
        return "", list(triangle.NON_NUMERIC_COORDS)

    side_a, side_b, side_c = parsed

    if not triangle.is_valid(side_a, side_b, side_c):
        logging.warning("Ошибочные числовые данные: %r, %r, %r",
                        side_a, side_b, side_c)
        return triangle.TYPE_NOT_TRIANGLE, list(triangle.INVALID_NUMERIC_COORDS)

    triangle_type = triangle.classify_triangle(side_a, side_b, side_c)
    if triangle_type == triangle.TYPE_NOT_TRIANGLE:
        logging.info("Стороны не образуют треугольник: %r, %r, %r",
                     side_a, side_b, side_c)
        return triangle_type, list(triangle.INVALID_NUMERIC_COORDS)

    vertices = triangle.compute_vertices(side_a, side_b, side_c)
    logging.info("Успешный запрос: стороны %r, %r, %r -> тип = %r, "
                 "координаты = %r", side_a, side_b, side_c, triangle_type, vertices)
    return triangle_type, vertices


def main():
    try:
        setup_logging()

        args = sys.argv[1:4]
        if len(args) == 3:
            lines = args
        else:
            lines = [
                input("Введите длину стороны A: "),
                input("Введите длину стороны B: "),
                input("Введите длину стороны C: "),
            ]

        triangle_type, vertices = process_triangle(*lines)
        print()
        print("Тип треугольника:", triangle_type if triangle_type else "<пусто>")
        print("Координаты вершин:", vertices)
        logging.info("Результат обработки запроса: тип = %r, координаты = %r",
                     triangle_type, vertices)
    except Exception as ex:
        logging.error("Неуспешный запрос: параметры недоступны, ошибка: %s", ex)
        logging.exception("Трассировка стека исключения:")
        print("Произошла ошибка:", ex)


if __name__ == "__main__":
    main()