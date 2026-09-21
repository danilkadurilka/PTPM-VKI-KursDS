import unittest

import triangle


class TriangleClassifyTestCase(unittest.TestCase):
    def test_equilateral(self):
        self.assertEqual(
            triangle.classify_triangle(5, 5, 5), triangle.TYPE_EQUILATERAL
        )

    def test_isosceles(self):
        self.assertEqual(
            triangle.classify_triangle(5, 5, 3), triangle.TYPE_ISOSCELES
        )

    def test_scalene(self):
        self.assertEqual(
            triangle.classify_triangle(3, 4, 5), triangle.TYPE_SCALENE
        )

    def test_degenerate_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(1, 2, 3), triangle.TYPE_NOT_TRIANGLE
        )

    def test_zero_side_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(0, 4, 5), triangle.TYPE_NOT_TRIANGLE
        )

    def test_negative_side_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(-3, 4, 5), triangle.TYPE_NOT_TRIANGLE
        )

    def test_nan_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(float("nan"), 4, 5),
            triangle.TYPE_NOT_TRIANGLE,
        )

    def test_infinity_not_triangle(self):
        self.assertEqual(
            triangle.classify_triangle(float("inf"), 4, 5),
            triangle.TYPE_NOT_TRIANGLE,
        )


class ParseSidesTestCase(unittest.TestCase):
    def test_valid_floats(self):
        self.assertEqual(
            triangle.parse_sides("3.0", "4.0", "5.0"), (3.0, 4.0, 5.0)
        )

    def test_integer_strings(self):
        self.assertEqual(triangle.parse_sides("3", "4", "5"), (3, 4, 5))

    def test_non_numeric(self):
        self.assertIsNone(triangle.parse_sides("abc", "4", "5"))

    def test_empty_string(self):
        self.assertIsNone(triangle.parse_sides("", "4", "5"))


class ComputeVerticesTestCase(unittest.TestCase):
    def _assert_in_field(self, vertices):
        for x, y in vertices:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x, triangle.FIELD_WIDTH)
            self.assertLessEqual(y, triangle.FIELD_HEIGHT)

    def test_valid_triangle_vertices_inside_field(self):
        vertices = triangle.compute_vertices(3, 4, 5)
        self.assertEqual(len(vertices), 3)
        self.assertTrue(all(isinstance(coord, int) for vertex in vertices for coord in vertex))
        self._assert_in_field(vertices)

    def test_vertices_unique(self):
        vertices = triangle.compute_vertices(3, 4, 5)
        self.assertEqual(len(set(vertices)), 3)

    def test_not_triangle_invalid_coords(self):
        self.assertEqual(
            triangle.compute_vertices(1, 2, 3),
            [(-1, -1), (-1, -1), (-1, -1)],
        )

    def test_non_finite_invalid_coords(self):
        self.assertEqual(
            triangle.compute_vertices(float("nan"), 4, 5),
            [(-1, -1), (-1, -1), (-1, -1)],
        )


class ErrorSignalCoordsTestCase(unittest.TestCase):
    def test_non_numeric_signal(self):
        self.assertEqual(
            triangle.NON_NUMERIC_COORDS, [(-2, -2), (-2, -2), (-2, -2)]
        )

    def test_invalid_numeric_signal(self):
        self.assertEqual(
            triangle.INVALID_NUMERIC_COORDS, [(-1, -1), (-1, -1), (-1, -1)]
        )


if __name__ == "__main__":
    unittest.main()