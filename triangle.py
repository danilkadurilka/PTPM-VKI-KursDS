import math

FIELD_WIDTH = 100
FIELD_HEIGHT = 100

TYPE_EQUILATERAL = "равносторонний"
TYPE_ISOSCELES = "равнобедренный"
TYPE_SCALENE = "разносторонний"
TYPE_NOT_TRIANGLE = "не треугольник"

EPSILON = 1e-9

INVALID_NUMERIC_COORDS = [(-1, -1), (-1, -1), (-1, -1)]
NON_NUMERIC_COORDS = [(-2, -2), (-2, -2), (-2, -2)]


def parse_sides(line_a, line_b, line_c):
    """Преобразует три строки в вещественные числа.

    Возвращает кортеж (a, b, c) либо None, если данные нечисловые.
    """
    try:
        a = float(line_a)
        b = float(line_b)
        c = float(line_c)
    except (TypeError, ValueError):
        return None
    return a, b, c


def is_valid(a, b, c):
    """Проверяет, что стороны являются положительными конечными числами.

    Нечисловые аргументы (строки, None и т.п.) считаются некорректными
    и приводят к возврату False вместо исключения TypeError.
    """
    if not all(isinstance(side, (int, float)) for side in (a, b, c)):
        return False
    return (
        math.isfinite(a)
        and math.isfinite(b)
        and math.isfinite(c)
        and a > 0
        and b > 0
        and c > 0
    )


def classify_triangle(a, b, c):
    """Определяет тип треугольника по трём сторонам."""
    if not is_valid(a, b, c):
        return TYPE_NOT_TRIANGLE
    if not (a + b > c and a + c > b and b + c > a):
        return TYPE_NOT_TRIANGLE
    if abs(a - b) < EPSILON and abs(b - c) < EPSILON:
        return TYPE_EQUILATERAL
    if (
        abs(a - b) < EPSILON
        or abs(b - c) < EPSILON
        or abs(a - c) < EPSILON
    ):
        return TYPE_ISOSCELES
    return TYPE_SCALENE


def compute_vertices(a, b, c):
    """Рассчитывает координаты трёх вершин для отрисовки в поле 100x100 px.

    Вершина A помещается в начало координат, B — на ось X, C вычисляется
    по теореме косинусов. Расчёт ведётся в нормализованных сторонах,
    поэтому устойчив к любому масштабу исходных чисел. Треугольник
    масштабируется и центрируется в поле размером 100x100.
    """
    if classify_triangle(a, b, c) == TYPE_NOT_TRIANGLE:
        return list(INVALID_NUMERIC_COORDS)

    # Стороны нормализуются делением на наибольшую из них: расчёт
    # пропорционален, поэтому результат не меняется, но перестаёт
    # зависеть от переполнения и исчезновения значащих разрядов
    # (a * a переполняется для a >~1e154 и обнуляется для a <~1e-162).
    longest = max(a, b, c)
    norm_a = a / longest
    norm_b = b / longest
    norm_c = c / longest

    x_c = (norm_a * norm_a + norm_c * norm_c - norm_b * norm_b) / (2.0 * norm_c)
    # max(0.0, ...) защищает sqrt от отрицательного нуля из-за
    # погрешности округления на почти вырожденных треугольниках.
    y_c = math.sqrt(max(0.0, norm_a * norm_a - x_c * x_c))

    points = [(0.0, 0.0), (norm_c, 0.0), (x_c, y_c)]

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    height = max_y - min_y
    # Почти вырожденный треугольник может дать высоту, равную нулю,
    # из-за чего масштабирование упало бы с ZeroDivisionError.
    width = width if width > 0.0 else norm_c
    height = height if height > 0.0 else norm_c

    scale = min(FIELD_WIDTH / width, FIELD_HEIGHT / height)
    offset_x = (FIELD_WIDTH - width * scale) / 2.0
    offset_y = (FIELD_HEIGHT - height * scale) / 2.0

    vertices = []
    for point_x, point_y in points:
        scaled_x = (point_x - min_x) * scale + offset_x
        scaled_y = (point_y - min_y) * scale + offset_y
        vertices.append((round(scaled_x), round(scaled_y)))
    return vertices