"""a. Класс вычислений и валидации.

Класс инкапсулирует единственный метод из Лабораторной работы №1
(определение типа треугольника) и добавляет к результату текст ошибки,
который требуется для записи в базу данных.
"""

from . import triangle


class TriangleCalculator:
    """Вычисляет тип треугольника по трём строкам пользовательского ввода."""

    def calculate(self, line_a, line_b, line_c):
        """Возвращает `TriangleResult` для трёх строк со сторонами.

        Некорректный ввод не приводит к исключению: метод всегда возвращает
        результат, в котором `error_message` описывает причину отказа.
        """
        parsed = triangle.parse_sides(line_a, line_b, line_c)
        if parsed is None:
            return triangle.TriangleResult(
                triangle_type=triangle.TYPE_NOT_TRIANGLE,
                error_message=triangle.ERROR_NON_NUMERIC,
            )

        side_a, side_b, side_c = parsed
        triangle_type = triangle.classify_triangle(side_a, side_b, side_c)
        if triangle_type == triangle.TYPE_NOT_TRIANGLE:
            if triangle.is_valid(side_a, side_b, side_c):
                error_message = triangle.ERROR_DEGENERATE
            else:
                error_message = triangle.ERROR_INVALID_SIDE
            return triangle.TriangleResult(
                triangle_type=triangle_type, error_message=error_message
            )

        return triangle.TriangleResult(triangle_type=triangle_type)