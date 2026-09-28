"""Юнит-тесты учебного модуля расчёта стоимости доставки (delivery.py).

Эталонное поведение восстановлено из контекста бизнес-требований
и зафиксировано в справочных функциях expected_cost / expected_date
в нижней части модуля. Тесты намеренно проверяют ИСПРАВЛЕННОЕ
поведение, поэтому на исходном коде delivery.py часть тестов падает.
"""

import datetime
import math
import unittest

from Lab2_KursDS.src import delivery

#: Фиксированная дата отправки, зашитая в модуль delivery.
SHIP_DATE = datetime.date(2026, 9, 3)

#: Документированный результат при критической ошибке.
ERROR_RESULT = (-1, "0000-00-00")

#: Допустимые типы посылки.
VALID_PACKAGE_TYPES = ("обычный", "хрупкий", "опасный")

#: Границы физических ограничений.
MIN_WEIGHT = 0.1
MAX_WEIGHT = 50.0
MIN_DISTANCE = 1
MAX_DISTANCE = 5000


def expected_cost(weight, distance, package_type, is_express=False):
    """Эталонный расчёт стоимости по восстановленным требованиям.

    Бизнес-правила:
      * базовый тариф 200 руб. + 5 руб. за каждый километр;
      * вес до 5 кг включительно — без коэффициента;
      * вес от 5 кг (не включая) до 20 кг включительно — коэффициент 1.2;
      * вес свыше 20 кг — коэффициент 1.5;
      * надбавка за «хрупкий» +300 руб., за «опасный» +1000 руб.;
      * экспресс — надбавка за скорость, коэффициент 1.5;
      * итог округляется до целого рубля (половина — вверх).
    """
    if not (MIN_WEIGHT <= weight <= MAX_WEIGHT):
        return -1
    if not (MIN_DISTANCE <= distance <= MAX_DISTANCE):
        return -1
    if package_type not in VALID_PACKAGE_TYPES:
        return -1

    total = 200 + distance * 5
    if weight > 20.0:
        total *= 1.5
    elif weight > 5.0:
        total *= 1.2

    if package_type == "хрупкий":
        total += 300
    elif package_type == "опасный":
        total += 1000

    if is_express:
        total *= 1.5

    return math.floor(total + 0.5)


def expected_date(distance, is_express=False):
    """Эталонный расчёт даты доставки по восстановленным требованиям.

    Бизнес-правила:
      * стандартная доставка — один день на каждые полные 500 км,
        но не менее одного дня;
      * экспресс сокращает срок вдвое с округлением вверх,
        но не менее одного дня.
    """
    days = math.ceil(distance / 500)
    if is_express:
        days = math.ceil(days / 2)
    delivery_day = SHIP_DATE + datetime.timedelta(days=max(1, days))
    return delivery_day.strftime("%Y-%m-%d")


def calculate(weight, distance, package_type="обычный", is_express=False):
    """Обёртка над тестируемой функцией модуля delivery."""
    return delivery.calculate_delivery_cost(weight, distance, package_type, is_express)


class DeliveryValidationTestCase(unittest.TestCase):
    """Проверка валидации входных параметров и граничных значений."""

    def test_returns_error_result_for_weight_below_minimum(self):
        self.assertEqual(calculate(0.09, 100), ERROR_RESULT)

    def test_accepts_weight_at_minimum_boundary(self):
        cost, date = calculate(MIN_WEIGHT, 100)
        self.assertEqual(cost, expected_cost(MIN_WEIGHT, 100, "обычный"))
        self.assertEqual(date, expected_date(100))

    def test_returns_error_result_for_weight_above_maximum(self):
        self.assertEqual(calculate(50.1, 100), ERROR_RESULT)

    def test_accepts_weight_at_maximum_boundary(self):
        cost, date = calculate(MAX_WEIGHT, 100)
        self.assertEqual(cost, expected_cost(MAX_WEIGHT, 100, "обычный"))
        self.assertEqual(date, expected_date(100))

    def test_returns_error_result_for_negative_weight(self):
        self.assertEqual(calculate(-5, 100), ERROR_RESULT)

    def test_returns_error_result_for_zero_distance(self):
        self.assertEqual(calculate(1, 0), ERROR_RESULT)

    def test_returns_error_result_for_distance_above_maximum(self):
        self.assertEqual(calculate(1, 5001), ERROR_RESULT)

    def test_accepts_distance_at_maximum_boundary(self):
        cost, date = calculate(1, MAX_DISTANCE)
        self.assertEqual(cost, expected_cost(1, MAX_DISTANCE, "обычный"))
        self.assertEqual(date, expected_date(MAX_DISTANCE))

    def test_returns_error_result_for_unknown_package_type(self):
        self.assertEqual(calculate(1, 100, "срочный"), ERROR_RESULT)

    def test_returns_error_result_for_empty_package_type(self):
        self.assertEqual(calculate(1, 100, ""), ERROR_RESULT)

    def test_returns_error_result_for_package_type_with_wrong_letter_case(self):
        self.assertEqual(calculate(1, 100, "Обычный"), ERROR_RESULT)


class DeliveryBaseCostTestCase(unittest.TestCase):
    """Проверка базового тарифа и весовых коэффициентов."""

    def test_computes_base_cost_as_200_plus_five_rubles_per_km(self):
        self.assertEqual(calculate(1, 100), (700, expected_date(100)))

    def test_applies_no_weight_coefficient_up_to_five_kg(self):
        self.assertEqual(calculate(3, 100)[0], 700)

    def test_applies_no_weight_coefficient_at_exactly_five_kg(self):
        self.assertEqual(calculate(5.0, 100)[0], 700)

    def test_applies_1_2_coefficient_between_five_and_twenty_kg(self):
        self.assertEqual(calculate(10, 100)[0], 840)

    def test_applies_1_5_coefficient_above_twenty_kg(self):
        self.assertEqual(calculate(25, 100)[0], 1050)

    def test_applies_1_2_coefficient_at_exactly_twenty_kg(self):
        self.assertEqual(calculate(20.0, 100)[0], 840)


class DeliveryPackageSurchargeTestCase(unittest.TestCase):
    """Проверка надбавок за тип посылки."""

    def test_adds_three_hundred_rubles_for_fragile_package(self):
        self.assertEqual(calculate(1, 100, "хрупкий")[0], 1000)

    def test_adds_one_thousand_rubles_for_hazardous_package(self):
        self.assertEqual(calculate(1, 100, "опасный")[0], 1700)

    def test_applies_fragile_surcharge_after_weight_coefficient(self):
        self.assertEqual(calculate(10, 100, "хрупкий")[0], 840 + 300)


class DeliveryExpressTestCase(unittest.TestCase):
    """Проверка логики экспресс-доставки."""

    def test_express_delivery_costs_more_than_standard_delivery(self):
        standard_cost = calculate(1, 100, "обычный", is_express=False)[0]
        express_cost = calculate(1, 100, "обычный", is_express=True)[0]
        self.assertGreater(express_cost, standard_cost)

    def test_express_delivery_applies_premium_coefficient_of_one_and_half(self):
        self.assertEqual(calculate(1, 100, "обычный", is_express=True)[0], 1050)

    def test_express_delivery_applies_premium_to_fragile_surcharge(self):
        self.assertEqual(calculate(1, 100, "хрупкий", is_express=True)[0], 1500)

    def test_express_delivery_never_arrives_on_the_day_of_dispatch(self):
        date = calculate(1, 600, "обычный", is_express=True)[1]
        self.assertGreater(date, SHIP_DATE.strftime("%Y-%m-%d"))

    def test_express_delivery_halves_travel_time_rounded_up(self):
        self.assertEqual(calculate(1, 1600, "обычный", is_express=True)[1], "2026-09-05")


class DeliveryDateTestCase(unittest.TestCase):
    """Проверка расчёта даты доставки."""

    def test_delivers_next_day_for_distance_below_500(self):
        self.assertEqual(calculate(1, 100)[1], "2026-09-04")

    def test_delivers_in_two_days_for_distance_above_500(self):
        self.assertEqual(calculate(1, 600)[1], "2026-09-05")

    def test_rounds_travel_days_up_when_distance_is_not_multiple_of_500(self):
        self.assertEqual(calculate(1, 750)[1], "2026-09-05")

    def test_adds_one_day_per_full_500_km(self):
        self.assertEqual(calculate(1, 1500)[1], "2026-09-06")

    def test_delivery_date_does_not_depend_on_package_type(self):
        dates = {calculate(1, 100, kind)[1] for kind in VALID_PACKAGE_TYPES}
        self.assertEqual(dates, {expected_date(100)})

    def test_delivery_date_does_not_depend_on_weight(self):
        dates = {calculate(weight, 100)[1] for weight in (0.5, 5, 10, 25, 50)}
        self.assertEqual(dates, {expected_date(100)})

    def test_delivery_date_does_not_depend_on_express_for_even_day_count(self):
        self.assertEqual(calculate(1, 2000, "обычный", is_express=True)[1], "2026-09-05")

    def test_returns_date_in_iso_format(self):
        date = calculate(1, 100)[1]
        self.assertRegex(date, r"^\d{4}-\d{2}-\d{2}$")
        datetime.date.fromisoformat(date)


class DeliveryResultContractTestCase(unittest.TestCase):
    """Проверка формы и типа возвращаемого результата."""

    def test_returns_tuple_of_two_elements(self):
        result = calculate(1, 100)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_returns_cost_as_integer_rubles(self):
        self.assertIsInstance(calculate(1, 100)[0], int)

    def test_rounds_total_cost_to_nearest_ruble(self):
        self.assertEqual(calculate(41, 41)[0], 608)

    def test_rounds_half_ruble_up_for_odd_distance_and_heavy_weight(self):
        self.assertEqual(calculate(21, 21)[0], 458)

    def test_matches_reference_implementation_for_valid_orders(self):
        cases = [
            (1, 100, "обычный", False),
            (0.1, 10, "обычный", False),
            (50, 5000, "опасный", False),
            (10, 2500, "хрупкий", False),
            (25, 750, "обычный", False),
        ]
        for weight, distance, kind, is_express in cases:
            with self.subTest(params=(weight, distance, kind, is_express)):
                self.assertEqual(
                    calculate(weight, distance, kind, is_express),
                    (
                        expected_cost(weight, distance, kind, is_express),
                        expected_date(distance, is_express),
                    ),
                )


if __name__ == "__main__":
    unittest.main()
