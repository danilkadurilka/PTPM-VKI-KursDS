import unittest
from src.password_validator import validate_password


class TestPasswordValidator(unittest.TestCase):
    """Тестовый класс для проверки функции validate_password."""

    # --- 1. Позитивное тестирование ---
    def test_valid_latin_password(self):
        self.assertTrue(validate_password("SecurePass1!"))

    def test_valid_cyrillic_password(self):
        self.assertTrue(validate_password("ПарольТест9#"))

    # --- 2. Анализ граничных значений длины (BVA) ---
    def test_length_7_too_short(self):
        self.assertFalse(validate_password("Aa1!bbb"))

    def test_length_8_boundary_min(self):
        self.assertTrue(validate_password("Aa1!bbbb"))

    def test_length_20_boundary_max(self):
        password = "Aa1!" + "b" * 16
        self.assertEqual(len(password), 20)
        self.assertTrue(validate_password(password))

    def test_length_21_too_long(self):
        password = "Aa1!" + "b" * 12 + "SHHHH"
        self.assertEqual(len(password), 21)
        self.assertFalse(validate_password(password))

    # --- 3. Классы эквивалентности (неполный состав символов) ---
    def test_missing_uppercase(self):
        """Пароль без заглавных букв -> False."""
        self.assertFalse(validate_password("securepass1!"))

    def test_missing_lowercase(self):
        """Пароль без строчных букв -> False."""
        self.assertFalse(validate_password("SECUREPASS1!"))

    def test_missing_digit(self):
        """Пароль без цифр -> False."""
        self.assertFalse(validate_password("SecurePassword!"))

    def test_missing_special_char(self):
        """Пароль без специальных символов -> False."""
        self.assertFalse(validate_password("SecurePassword1"))

    def test_invalid_special_char_underscore(self):
        """Пароль со спецсимволом, не входящим в перечень (_) -> False."""
        self.assertFalse(validate_password("SecurePass1_"))

    def test_invalid_special_char_question(self):
        """Пароль со спецсимволом, не входящим в перечень (?) -> False."""
        self.assertFalse(validate_password("SecurePass1?"))

    # --- 4. Тестирование исключительных ситуаций ---
    def test_type_error_none(self):
        """Проверка выброса TypeError при передаче None."""
        with self.assertRaises(TypeError):
            validate_password(None)

    def test_type_error_int(self):
        """Проверка выброса TypeError при передаче int."""
        with self.assertRaises(TypeError):
            validate_password(12345678)

    def test_type_error_list(self):
        """Проверка выброса TypeError при передаче list."""
        with self.assertRaises(TypeError):
            validate_password(["P", "a", "s", "s"])

    def test_value_error_space_inside(self):
        """Проверка выброса ValueError при наличии пробела внутри."""
        with self.assertRaises(ValueError):
            validate_password("Pass 1234!")

    def test_value_error_space_start(self):
        """Проверка выброса ValueError при наличии пробела в начале."""
        with self.assertRaises(ValueError):
            validate_password(" Pass1234!")

    def test_value_error_space_end(self):
        """Проверка выброса ValueError при наличии пробела в конце."""
        with self.assertRaises(ValueError):
            validate_password("Pass1234! ")

    def test_empty_string(self):
        """Пустая строка -> False (нарушает длину и состав)."""
        self.assertFalse(validate_password(""))

if __name__ == '__main__':
    unittest.main()