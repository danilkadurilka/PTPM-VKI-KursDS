"""Юнит-тесты класса вычислений и валидации (src/calculator.py).

Лабораторная работа №2 проверяла чистые функции модуля ЛР1, поэтому здесь
тестируется новое поведение класса: объект `TriangleResult` и осмысленный
текст ошибки для каждой причины отказа.
"""

import unittest

from Lab3_KursDS.src import triangle
from Lab3_KursDS.src.calculator import TriangleCalculator


class CalculateSuccessTestCase(unittest.TestCase):
    """Проверка результата для корректных сторон."""

    def setUp(self):
        self.calculator = TriangleCalculator()

    def test_returns_triangle_result_instance(self):
        self.assertIsInstance(
            self.calculator.calculate("3", "4", "5"), triangle.TriangleResult
        )

    def test_error_message_is_empty_for_valid_triangle(self):
        self.assertEqual(self.calculator.calculate("3", "4", "5").error_message, "")

    def test_accepts_integer_and_decimal_sides_in_same_request(self):
        self.assertEqual(
            self.calculator.calculate("2.5", "3.5", "4.5").triangle_type,
            triangle.TYPE_SCALENE,
        )

    def test_determines_type_of_equilateral_triangle(self):
        self.assertEqual(
            self.calculator.calculate("5", "5", "5").triangle_type,
            triangle.TYPE_EQUILATERAL,
        )

    def test_determines_type_of_scalene_triangle(self):
        self.assertEqual(
            self.calculator.calculate("3", "4", "5").triangle_type,
            triangle.TYPE_SCALENE,
        )

    def test_determines_type_regardless_of_which_sides_are_equal(self):
        cases = {
            (5.0, 5.0, 3.0): triangle.TYPE_ISOSCELES,
            (3.0, 5.0, 5.0): triangle.TYPE_ISOSCELES,
            (3.0, 5.0, 3.0): triangle.TYPE_ISOSCELES,
        }
        for sides, expected in cases.items():
            with self.subTest(sides=sides):
                result = self.calculator.calculate(*(str(side) for side in sides))
                self.assertEqual(result.triangle_type, expected)


class CalculateErrorTestCase(unittest.TestCase):
    """Проверка текста ошибки для каждой причины отказа."""

    def setUp(self):
        self.calculator = TriangleCalculator()

    def assert_refused(self, sides, expected_error):
        result = self.calculator.calculate(*sides)
        self.assertEqual(result.triangle_type, triangle.TYPE_NOT_TRIANGLE)
        self.assertEqual(result.error_message, expected_error)

    def test_reports_non_numeric_error_for_alphabetic_input(self):
        self.assert_refused(
            ("a", "b", "c"), triangle.ERROR_NON_NUMERIC
        )

    def test_reports_non_numeric_error_for_empty_input(self):
        self.assert_refused(
            ("", "4", "5"), triangle.ERROR_NON_NUMERIC
        )

    def test_reports_non_numeric_error_when_side_is_not_a_string(self):
        self.assert_refused(
            (None, "4", "5"), triangle.ERROR_NON_NUMERIC
        )

    def test_reports_invalid_side_error_for_zero_side(self):
        self.assert_refused(
            ("0", "4", "5"), triangle.ERROR_INVALID_SIDE
        )

    def test_reports_invalid_side_error_for_negative_side(self):
        self.assert_refused(
            ("-3", "4", "5"), triangle.ERROR_INVALID_SIDE
        )

    def test_reports_invalid_side_error_for_nan_side(self):
        self.assert_refused(
            ("nan", "4", "5"), triangle.ERROR_INVALID_SIDE
        )

    def test_reports_invalid_side_error_for_infinite_side(self):
        self.assert_refused(
            ("inf", "4", "5"), triangle.ERROR_INVALID_SIDE
        )

    def test_reports_degenerate_error_when_longest_side_equals_sum(self):
        self.assert_refused(
            ("1", "2", "3"), triangle.ERROR_DEGENERATE
        )

    def test_reports_degenerate_error_when_longest_side_exceeds_sum(self):
        self.assert_refused(
            ("1", "2", "9"), triangle.ERROR_DEGENERATE
        )

    def test_every_error_message_is_described_in_russian(self):
        errors = {
            self.calculator.calculate("a", "b", "c").error_message,
            self.calculator.calculate("0", "4", "5").error_message,
            self.calculator.calculate("1", "2", "3").error_message,
        }
        self.assertEqual(len(errors), 3)
        for error in errors:
            self.assertTrue(error.islower())


if __name__ == "__main__":
    unittest.main()