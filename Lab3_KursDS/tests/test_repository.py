"""Юнит-тесты класса работы с базой данных (src/repository.py).

Покрываются методы `add`, `get`, `delete` и `close`, а также создание
файловой базы данных в отдельной временной папке.
"""

import os
import tempfile
import unittest

from Lab3_KursDS.src.repository import TriangleRecord, TriangleRepository


class InMemoryRepositoryTestCase(unittest.TestCase):
    """Проверка операций над базой, созданной в памяти процесса."""

    def setUp(self):
        self.repository = TriangleRepository(":memory:")
        self.record = TriangleRecord(
            side1=3.0, side2=4.0, side3=5.0,
            triangle_type="разносторонний", error_message="",
        )

    def tearDown(self):
        self.repository.close()

    def test_add_returns_true_for_new_record(self):
        self.assertTrue(self.repository.add(self.record))

    def test_add_returns_false_for_already_existing_record(self):
        self.repository.add(self.record)
        self.assertFalse(self.repository.add(self.record))

    def test_add_does_not_overwrite_existing_record(self):
        self.repository.add(self.record)
        changed = TriangleRecord(
            side1=3.0, side2=4.0, side3=5.0,
            triangle_type="не треугольник", error_message="подмена",
        )
        self.repository.add(changed)
        stored = self.repository.get(3.0, 4.0, 5.0)
        self.assertEqual(stored.triangle_type, "разносторонний")
        self.assertEqual(stored.error_message, "")

    def test_get_returns_record_saved_before(self):
        self.repository.add(self.record)
        self.assertEqual(self.repository.get(3.0, 4.0, 5.0), self.record)

    def test_get_returns_none_for_unknown_sides(self):
        self.assertIsNone(self.repository.get(1.0, 1.0, 1.0))

    def test_get_matches_sides_exactly_and_not_by_set(self):
        self.repository.add(self.record)
        self.assertIsNone(self.repository.get(4.0, 3.0, 5.0))

    def test_get_returns_record_with_error_message(self):
        self.repository.add(
            TriangleRecord(
                side1=1.0, side2=2.0, side3=3.0,
                triangle_type="не треугольник",
                error_message="самая длинная сторона не меньше суммы двух других",
            )
        )
        stored = self.repository.get(1.0, 2.0, 3.0)
        self.assertEqual(stored.triangle_type, "не треугольник")
        self.assertTrue(stored.error_message)

    def test_delete_returns_true_and_removes_existing_record(self):
        self.repository.add(self.record)
        self.assertTrue(self.repository.delete(3.0, 4.0, 5.0))
        self.assertIsNone(self.repository.get(3.0, 4.0, 5.0))

    def test_delete_returns_false_for_unknown_sides(self):
        self.assertFalse(self.repository.delete(3.0, 4.0, 5.0))

    def test_records_can_be_deleted_and_added_again(self):
        self.repository.add(self.record)
        self.repository.delete(3.0, 4.0, 5.0)
        self.assertTrue(self.repository.add(self.record))

    def test_records_with_different_sides_stored_independently(self):
        self.repository.add(self.record)
        self.repository.add(
            TriangleRecord(
                side1=5.0, side2=5.0, side3=5.0, triangle_type="равносторонний",
            )
        )
        self.assertIsNotNone(self.repository.get(3.0, 4.0, 5.0))
        self.assertIsNotNone(self.repository.get(5.0, 5.0, 5.0))


class FileRepositoryTestCase(unittest.TestCase):
    """Проверка создания файловой базы данных и её переиспользования."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "nested", "triangles.db")
        self.record = TriangleRecord(
            side1=2.0, side2=2.0, side3=3.0,
            triangle_type="равнобедренный", error_message="",
        )

    def tearDown(self):
        self.folder.cleanup()

    def test_creates_database_file_in_missing_folder(self):
        repository = TriangleRepository(self.path)
        repository.add(self.record)
        repository.close()
        self.assertTrue(os.path.isfile(self.path))

    def test_reads_record_written_by_previous_connection(self):
        first = TriangleRepository(self.path)
        first.add(self.record)
        first.close()

        second = TriangleRepository(self.path)
        self.assertEqual(second.get(2.0, 2.0, 3.0), self.record)
        second.close()


if __name__ == "__main__":
    unittest.main()