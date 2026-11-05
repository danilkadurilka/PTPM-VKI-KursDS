"""Тесты для DatabaseRepository"""

import unittest

from src.database import DatabaseRepository, MAX_MESSAGE_LEN
from src.exceptions import (
    ValidationError,
    DuplicateIDError,
    RecordNotFoundError,
)


class TestDatabaseRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self) -> None:
        self.repo.close()


    def test_add_success(self):
        self.assertTrue(self.repo.add(1, "alice", "hello"))
        self.assertEqual(self.repo.get_by_id(1)["name"], "alice")

    def test_add_duplicate_id_raises(self):
        self.repo.add(1, "alice", "hello")
        with self.assertRaises(DuplicateIDError):
            self.repo.add(1, "bob", "other")

    def test_add_invalid_message_length_raises(self):
        with self.assertRaises(ValidationError):
            self.repo.add(2, "bob", "x" * (MAX_MESSAGE_LEN + 1))

    def test_get_by_id_success(self):
        self.repo.add(5, "carol", "msg")
        record = self.repo.get_by_id(5)
        self.assertIsNotNone(record)
        self.assertEqual(record["id"], 5)
        self.assertEqual(record["message"], "msg")

    def test_get_by_id_returns_none_for_missing(self):
        self.assertIsNone(self.repo.get_by_id(999))

    def test_get_by_id_invalid_type_raises(self):
        with self.assertRaises(ValidationError):
            self.repo.get_by_id("not-int")

    def test_get_by_name_success(self):
        self.repo.add(1, "alice", "m1")
        self.repo.add(2, "bob", "m2")
        self.repo.add(3, "alice", "m3")
        result = self.repo.get_by_name("alice")
        self.assertEqual(len(result), 2)
        self.assertEqual([r["id"] for r in result], [1, 3])

    def test_get_by_name_empty_result(self):
        self.assertEqual(self.repo.get_by_name("ghost"), [])

    def test_get_by_name_invalid_raises(self):
        with self.assertRaises(ValidationError):
            self.repo.get_by_name("")

    def test_update_success(self):
        self.repo.add(1, "alice", "old")
        self.assertTrue(self.repo.update(1, "new"))
        self.assertEqual(self.repo.get_by_id(1)["message"], "new")

    def test_update_missing_id_raises(self):
        with self.assertRaises(RecordNotFoundError):
            self.repo.update(42, "new")

    def test_update_invalid_message_raises(self):
        self.repo.add(1, "alice", "old")
        with self.assertRaises(ValidationError):
            self.repo.update(1, "x" * (MAX_MESSAGE_LEN + 1))

    def test_delete_success(self):
        self.repo.add(1, "alice", "m")
        self.assertTrue(self.repo.delete(1))
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_missing_id_raises(self):
        with self.assertRaises(RecordNotFoundError):
            self.repo.delete(777)

    def test_delete_then_delete_again_raises(self):
        self.repo.add(1, "alice", "m")
        self.repo.delete(1)
        with self.assertRaises(RecordNotFoundError):
            self.repo.delete(1)