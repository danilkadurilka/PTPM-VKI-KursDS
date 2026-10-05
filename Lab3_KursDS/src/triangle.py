"""Доменная логика определения типа треугольника (наследие Лабораторной работы №1).

Модуль не содержит классов и не знает ни о базе данных, ни о пользователе,
ни о сторонних сервисах: это переиспользованная и слегка упрощённая версия
кода ЛР1. Все функции принимают и возвращают только `float`, потому что
преобразование пользовательских строк в числа делает `parse_sides`.
"""

import math
from dataclasses import dataclass

TYPE_EQUILATERAL = "равносторонний"
TYPE_ISOSCELES = "равнобедренный"
TYPE_SCALENE = "разносторонний"
TYPE_NOT_TRIANGLE = "не треугольник"

EPSILON = 1e-9

#: Сообщения об ошибках, которые попадают в базу данных и в отчёт стороннему сервису.
ERROR_NON_NUMERIC = "введены пустые или нечисловые значения"
ERROR_INVALID_SIDE = "длины сторон должны быть конечными положительными числами"
ERROR_DEGENERATE = "самая длинная сторона не меньше суммы двух других"


@dataclass(frozen=True)
class TriangleResult:
    """Неизменяемый результат вычислений: тип треугольника и текст ошибки.

    Пустая `error_message` означает, что треугольник построен успешно.
    """

    triangle_type: str
    error_message: str = ""


def parse_sides(line_a, line_b, line_c):
    """Преобразует три строки в тройку `float`.

    Возвращает `None`, если хотя бы одно значение не является числом:
    такой ввод нельзя превратить в ключ записи базы данных.
    """
    try:
        return float(line_a), float(line_b), float(line_c)
    except (TypeError, ValueError):
        return None


def is_valid(a, b, c):
    """Проверяет, что стороны — конечные положительные числа."""
    return (
        math.isfinite(a)
        and math.isfinite(b)
        and math.isfinite(c)
        and a > 0
        and b > 0
        and c > 0
    )


def classify_triangle(a, b, c):
    """Определяет тип треугольника по трём длинам сторон."""
    if not is_valid(a, b, c):
        return TYPE_NOT_TRIANGLE
    if not (a + b > c and a + c > b and b + c > a):
        return TYPE_NOT_TRIANGLE
    if abs(a - b) < EPSILON and abs(b - c) < EPSILON:
        return TYPE_EQUILATERAL
    if abs(a - b) < EPSILON or abs(b - c) < EPSILON or abs(a - c) < EPSILON:
        return TYPE_ISOSCELES
    return TYPE_SCALENE