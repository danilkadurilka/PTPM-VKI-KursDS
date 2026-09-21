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
    """Проверяет, что стороны являются положительными конечными числами."""
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

    Вершина A помещается в начало координат, B — на ось X (0, c),
    C вычисляется по теореме косинусов. Треугольник масштабируется
    и центрируется в поле размером 100x100.
    """
    if classify_triangle(a, b, c) == TYPE_NOT_TRIANGLE:
        return list(INVALID_NUMERIC_COORDS)

    x_c = (a * a + c * c - b * b) / (2.0 * c)
    y_c = math.sqrt(a * a - x_c * x_c)

    points = [(0.0, 0.0), (c, 0.0), (x_c, y_c)]

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    height = max_y - min_y

    scale = min(FIELD_WIDTH / width, FIELD_HEIGHT / height)
    offset_x = (FIELD_WIDTH - width * scale) / 2.0
    offset_y = (FIELD_HEIGHT - height * scale) / 2.0

    vertices = []
    for point_x, point_y in points:
        scaled_x = (point_x - min_x) * scale + offset_x
        scaled_y = (point_y - min_y) * scale + offset_y
        vertices.append((round(scaled_x), round(scaled_y)))
    return vertices