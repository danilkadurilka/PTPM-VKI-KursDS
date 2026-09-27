"""Юнит-тесты кода Лабораторной работы №1 (определение типа треугольника).

Покрываются модули: triangle.parse_sides, triangle.is_valid,
triangle.classify_triangle, triangle.compute_vertices.
"""

import math
import unittest

import triangle


class ParseSidesTestCase(unittest.TestCase):
    """Проверка преобразования строковых аргументов в числа."""

    def test_parses_positive_integer_strings(self):
        self.assertEqual(triangle.parse_sides("3", "4", "5"), (3.0, 4.0, 5.0))

    def test_parses_decimal_strings_with_dot(self):
        self.assertEqual(triangle.parse_sides("2.5", "3.5", "4.5"), (2.5, 3.5, 4.5))

    def test_parses_negative_decimal_strings(self):
        self.assertEqual(triangle.parse_sides("-2.5", "3.5", "-4.5"), (-2.5, 3.5, -4.5))

    def test_parses_strings_surrounded_by_whitespace(self):
        self.assertEqual(triangle.parse_sides("  3  ", " 4 ", "\t5\n"), (3.0, 4.0, 5.0))

    def test_parses_scientific_notation_string(self):
        self.assertEqual(triangle.parse_sides("1e2", "2E2", "3e2"), (100.0, 200.0, 300.0))

    def test_parses_nan_string_into_nan_value(self):
        parsed = triangle.parse_sides("nan", "4", "5")
        self.assertIsNotNone(parsed)
        self.assertTrue(math.isnan(parsed[0]))

    def test_parses_infinity_string_into_infinite_value(self):
        parsed = triangle.parse_sides("inf", "4", "5")
        self.assertIsNotNone(parsed)
        self.assertTrue(math.isinf(parsed[0]))

    def test_returns_none_for_alphabetic_string(self):
        self.assertIsNone(triangle.parse_sides("abc", "4", "5"))

    def test_returns_none_for_empty_string(self):
        self.assertIsNone(triangle.parse_sides("", "4", "5"))

    def test_returns_none_for_whitespace_only_string(self):
        self.assertIsNone(triangle.parse_sides("   ", "4", "5"))

    def test_returns_none_when_argument_is_none(self):
        self.assertIsNone(triangle.parse_sides(None, "4", "5"))

    def test_returns_none_when_only_one_argument_is_not_numeric(self):
        self.assertIsNone(triangle.parse_sides("3", "4", "пять"))


class IsValidTestCase(unittest.TestCase):
    """Проверка предиката корректности сторон."""

    def test_accepts_positive_finite_sides(self):
        self.assertTrue(triangle.is_valid(3, 4, 5))

    def test_accepts_fractional_positive_sides(self):
        self.assertTrue(triangle.is_valid(0.1, 0.2, 0.25))

    def test_accepts_very_small_positive_sides(self):
        self.assertTrue(triangle.is_valid(1e-300, 1e-300, 1e-300))

    def test_rejects_zero_side(self):
        self.assertFalse(triangle.is_valid(0, 4, 5))

    def test_rejects_negative_side(self):
        self.assertFalse(triangle.is_valid(-3, 4, 5))

    def test_rejects_nan_side(self):
        self.assertFalse(triangle.is_valid(float("nan"), 4, 5))

    def test_rejects_positive_infinite_side(self):
        self.assertFalse(triangle.is_valid(float("inf"), 4, 5))

    def test_rejects_negative_infinite_side(self):
        self.assertFalse(triangle.is_valid(4, 5, float("-inf")))

    def test_rejects_string_side_without_raising_exception(self):
        self.assertFalse(triangle.is_valid("3", 4, 5))

    def test_rejects_none_side_without_raising_exception(self):
        self.assertFalse(triangle.is_valid(3, None, 5))

    def test_rejects_list_side_without_raising_exception(self):
        self.assertFalse(triangle.is_valid(3, [4], 5))


class ClassifyTriangleTestCase(unittest.TestCase):
    """Проверка определения типа треугольника по трём сторонам."""

    def test_classifies_equilateral_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(5, 5, 5), triangle.TYPE_EQUILATERAL
        )

    def test_classifies_isosceles_with_equal_first_two_sides(self):
        self.assertEqual(
            triangle.classify_triangle(5, 5, 3), triangle.TYPE_ISOSCELES
        )

    def test_classifies_isosceles_with_equal_last_two_sides(self):
        self.assertEqual(
            triangle.classify_triangle(3, 5, 5), triangle.TYPE_ISOSCELES
        )

    def test_classifies_isosceles_with_equal_first_and_last_sides(self):
        self.assertEqual(
            triangle.classify_triangle(3, 5, 3), triangle.TYPE_ISOSCELES
        )

    def test_classifies_scalene_right_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(3, 4, 5), triangle.TYPE_SCALENE
        )

    def test_classifies_scalene_acute_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(4, 4.5, 5), triangle.TYPE_SCALENE
        )

    def test_classifies_degenerate_triangle_as_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(1, 2, 3), triangle.TYPE_NOT_TRIANGLE
        )

    def test_classifies_triangle_where_longest_equals_sum_of_others_as_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(1, 1, 2), triangle.TYPE_NOT_TRIANGLE
        )

    def test_classifies_triangle_with_zero_side_as_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(0, 4, 5), triangle.TYPE_NOT_TRIANGLE
        )

    def test_classifies_triangle_with_negative_side_as_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(-3, 4, 5), triangle.TYPE_NOT_TRIANGLE
        )

    def test_classifies_triangle_with_nan_side_as_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(float("nan"), 4, 5),
            triangle.TYPE_NOT_TRIANGLE,
        )

    def test_classifies_triangle_with_infinite_side_as_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(float("inf"), 4, 5),
            triangle.TYPE_NOT_TRIANGLE,
        )

    def test_classifies_triangle_with_string_side_as_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle("3", "4", "5"), triangle.TYPE_NOT_TRIANGLE
        )

    def test_classifies_triangle_with_none_side_as_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(3, None, 5), triangle.TYPE_NOT_TRIANGLE
        )

    def test_classification_does_not_depend_on_side_order(self):
        expected = triangle.TYPE_SCALENE
        for sides in ((3, 4, 5), (5, 3, 4), (4, 5, 3), (5, 4, 3), (3, 5, 4), (4, 3, 5)):
            with self.subTest(sides=sides):
                self.assertEqual(triangle.classify_triangle(*sides), expected)


class ComputeVerticesTestCase(unittest.TestCase):
    """Проверка расчёта координат вершин в поле 100x100 px."""

    #: Допустимое отклонение длины стороны, вызванное округлением
    #: координат до целых пикселей.
    PIXEL_TOLERANCE = 1.0

    def _assert_inside_field(self, vertices):
        for x, y in vertices:
            with self.subTest(vertex=(x, y)):
                self.assertGreaterEqual(x, 0)
                self.assertGreaterEqual(y, 0)
                self.assertLessEqual(x, triangle.FIELD_WIDTH)
                self.assertLessEqual(y, triangle.FIELD_HEIGHT)

    @staticmethod
    def _distance(first, second):
        return math.hypot(first[0] - second[0], first[1] - second[1])

    def _assert_side_proportions(self, a, b, c):
        vertex_a, vertex_b, vertex_c = triangle.compute_vertices(a, b, c)
        scale = self._distance(vertex_a, vertex_b) / c
        self.assertAlmostEqual(
            self._distance(vertex_a, vertex_c),
            a * scale,
            delta=self.PIXEL_TOLERANCE,
        )
        self.assertAlmostEqual(
            self._distance(vertex_b, vertex_c),
            b * scale,
            delta=self.PIXEL_TOLERANCE,
        )

    def test_returns_three_vertices_inside_field(self):
        vertices = triangle.compute_vertices(3, 4, 5)
        self.assertEqual(len(vertices), 3)
        self._assert_inside_field(vertices)

    def test_returns_integer_coordinates(self):
        vertices = triangle.compute_vertices(3, 4, 5)
        for vertex in vertices:
            self.assertTrue(all(isinstance(coord, int) for coord in vertex))

    def test_returns_three_distinct_vertices(self):
        vertices = triangle.compute_vertices(3, 4, 5)
        self.assertEqual(len(set(vertices)), 3)

    def test_computes_exact_vertices_for_scalene_triangle(self):
        self.assertEqual(
            triangle.compute_vertices(3, 4, 5), [(0, 26), (100, 26), (36, 74)]
        )

    def test_computes_exact_vertices_for_equilateral_triangle(self):
        self.assertEqual(
            triangle.compute_vertices(1, 1, 1), [(0, 7), (100, 7), (50, 93)]
        )

    def test_computes_exact_vertices_for_isosceles_triangle(self):
        self.assertEqual(
            triangle.compute_vertices(2, 2, 3), [(0, 28), (100, 28), (50, 72)]
        )

    def test_preserves_side_length_proportions(self):
        for a, b, c in [(3, 4, 5), (5, 12, 13), (2, 2, 3), (2.5, 3.5, 4.5), (6, 8, 10)]:
            with self.subTest(sides=(a, b, c)):
                self._assert_side_proportions(a, b, c)

    def test_returns_error_coords_for_degenerate_triangle(self):
        self.assertEqual(
            triangle.compute_vertices(1, 2, 3),
            [(-1, -1), (-1, -1), (-1, -1)],
        )

    def test_returns_error_coords_for_nan_side(self):
        self.assertEqual(
            triangle.compute_vertices(float("nan"), 4, 5),
            [(-1, -1), (-1, -1), (-1, -1)],
        )

    def test_returns_error_coords_for_string_side(self):
        self.assertEqual(
            triangle.compute_vertices("3", 4, 5),
            [(-1, -1), (-1, -1), (-1, -1)],
        )

    def test_computes_vertices_for_tiny_sides_without_crashing(self):
        vertices = triangle.compute_vertices(1e-300, 1e-300, 1e-300)
        self.assertEqual(len(vertices), 3)
        self._assert_inside_field(vertices)

    def test_computes_vertices_for_huge_sides_without_crashing(self):
        vertices = triangle.compute_vertices(1e300, 1e300, 1e300)
        self.assertEqual(len(vertices), 3)
        self._assert_inside_field(vertices)

    def test_computes_vertices_for_nearly_degenerate_triangle_without_crashing(self):
        vertices = triangle.compute_vertices(1, 1, 1.9999999999999)
        self.assertEqual(len(vertices), 3)
        self._assert_inside_field(vertices)

    def test_does_not_leak_mutable_error_coords_constant(self):
        vertices = triangle.compute_vertices(1, 2, 3)
        vertices.append((999, 999))
        self.assertEqual(
            triangle.INVALID_NUMERIC_COORDS, [(-1, -1), (-1, -1), (-1, -1)]
        )


class ErrorSignalCoordsTestCase(unittest.TestCase):
    """Проверка констант-сигналов ошибок ввода."""

    def test_non_numeric_signal_equals_minus_two_triple(self):
        self.assertEqual(
            triangle.NON_NUMERIC_COORDS, [(-2, -2), (-2, -2), (-2, -2)]
        )

    def test_invalid_numeric_signal_equals_minus_one_triple(self):
        self.assertEqual(
            triangle.INVALID_NUMERIC_COORDS, [(-1, -1), (-1, -1), (-1, -1)]
        )

    def test_error_signals_are_distinct(self):
        self.assertNotEqual(triangle.NON_NUMERIC_COORDS, triangle.INVALID_NUMERIC_COORDS)


if __name__ == "__main__":
    unittest.main()
