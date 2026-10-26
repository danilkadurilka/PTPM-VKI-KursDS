import unittest
from Lab4_KursDS.converter import Converter

class TestConverter(unittest.TestCase):

    # ---------- Диапазон [100.7; +∞) -> 1000 ----------
    def test_upper_boundary_100_7(self):
        """Граничное значение: x = 100.7 -> 1000"""
        self.assertEqual(Converter.do(100.7), 1000)

    def test_above_upper_boundary(self):
        """Значение выше границы: x = 100.8 -> 1000"""
        self.assertEqual(Converter.do(100.8), 1000)

    def test_very_large_value(self):
        """Очень большое значение: x = 99999.9 -> 1000"""
        self.assertEqual(Converter.do(99999.9), 1000)

    # ---------- Диапазон (0; 100.7) -> int(x) ----------
    def test_just_above_zero(self):
        """Минимальное положительное: x = 0.1 -> 0"""
        self.assertEqual(Converter.do(0.1), 0)

    def test_positive_small(self):
        """x = 5.9 -> 5"""
        self.assertEqual(Converter.do(5.9), 5)

    def test_positive_medium(self):
        """x = 65.7 -> 65"""
        self.assertEqual(Converter.do(65.7), 65)

    def test_just_below_upper_boundary(self):
        """Граничное значение: x = 100.6 -> 100"""
        self.assertEqual(Converter.do(100.6), 100)

    # ---------- x == 0.0 -> ValueError ----------
    def test_zero_raises_value_error(self):
        """x = 0.0 должно вызывать ValueError"""
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    # ---------- Диапазон [-30.4; 0) -> int(x) - 5 ----------
    def test_negative_boundary_minus_30_4(self):
        """Граничное значение: x = -30.4 -> -35"""
        self.assertEqual(Converter.do(-30.4), -35)

    def test_negative_just_below_zero(self):
        """x = -0.1 -> -5"""
        self.assertEqual(Converter.do(-0.1), -5)

    def test_negative_minus_5(self):
        """x = -5.5 -> -10"""
        self.assertEqual(Converter.do(-5.5), -10)

    def test_negative_minus_20(self):
        """x = -20.3 -> -25"""
        self.assertEqual(Converter.do(-20.3), -25)

    # ---------- Диапазон (-∞; -30.5] -> -2000 ----------
    def test_lower_boundary_minus_30_5(self):
        """Граничное значение: x = -30.5 -> -2000"""
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_below_lower_boundary(self):
        """x = -30.6 -> -2000"""
        self.assertEqual(Converter.do(-30.6), -2000)

    def test_large_negative(self):
        """Очень маленькое значение: x = -94.5 -> -2000"""
        self.assertEqual(Converter.do(-94.5), -2000)

    def test_very_negative(self):
        """x = -99999.9 -> -2000"""
        self.assertEqual(Converter.do(-99999.9), -2000)

    # ---------- Проверка типа возвращаемого значения ----------
    def test_return_type_is_int(self):
        """Метод должен возвращать int"""
        self.assertIsInstance(Converter.do(50.5), int)
        self.assertIsInstance(Converter.do(150.5), int)
        self.assertIsInstance(Converter.do(-15.5), int)
        self.assertIsInstance(Converter.do(-40.5), int)