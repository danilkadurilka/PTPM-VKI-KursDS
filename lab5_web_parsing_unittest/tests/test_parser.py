"""Тесты для ForumParser"""

import os
import unittest
from unittest.mock import patch

from src.database import DatabaseRepository
from src.parser import ForumParser


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name: str) -> str:
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return f.read()


class TestForumParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = ForumParser()
        self.repo = DatabaseRepository(":memory:")
        self.html_page_1 = load_fixture("page1.html")
        self.html_page_2 = load_fixture("page2.html")

    def tearDown(self) -> None:
        self.repo.close()

    # 1. Корректный парсинг всех комментариев
    def test_parse_html_returns_all_comments(self):
        parsed = self.parser.parse_html(self.html_page_1)
        self.assertEqual(len(parsed), 3)
        self.assertEqual({item["id"] for item in parsed}, {101, 102, 103})

    # 2. Извлечение имени пользователя
    def test_parse_html_extracts_username(self):
        parsed = self.parser.parse_html(self.html_page_1)
        by_id = {item["id"]: item for item in parsed}
        self.assertEqual(by_id[101]["name"], "alice")
        self.assertEqual(by_id[102]["name"], "bob")

    # 3. Сохранение HTML-разметки в сообщении
    def test_parse_html_preserves_inner_html(self):
        parsed = self.parser.parse_html(self.html_page_1)
        by_id = {item["id"]: item for item in parsed}
        self.assertIn("<b>первое</b>", by_id[101]["message"])

    # 4. Пропуск некорректных блоков (нечисловой ID, нет автора)
    def test_parse_html_skips_invalid_nodes(self):
        parsed = self.parser.parse_html(self.html_page_2)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], 202)
        self.assertEqual(parsed[0]["name"], "dave")

    # 5. Интеграция: парсинг + сохранение в БД через save_to_db
    def test_save_to_db_persists_comments(self):
        parsed = self.parser.parse_html(self.html_page_1)
        saved = self.parser.save_to_db(parsed, self.repo)
        self.assertEqual(saved, 3)
        self.assertEqual(self.repo.get_by_id(101)["name"], "alice")
        self.assertEqual(len(self.repo.get_by_name("alice")), 2)

    # 6. save_to_db корректно игнорирует дубликаты
    def test_save_to_db_skips_duplicates(self):
        parsed = self.parser.parse_html(self.html_page_1)
        self.parser.save_to_db(parsed, self.repo)
        saved_again = self.parser.save_to_db(parsed, self.repo)
        self.assertEqual(saved_again, 0)
        self.assertEqual(len(self.repo.get_by_name("alice")), 2)

    # 7. parse_page использует requests (патчим, чтобы не ходить в сеть)
    def test_parse_page_uses_requests_mock(self):
        with patch.object(
            self.parser,
            "fetch_html",
            return_value=self.html_page_1,
        ) as mocked:
            parsed = self.parser.parse_page("http://example.com")
        mocked.assert_called_once_with("http://example.com")
        self.assertEqual(len(parsed), 3)


if __name__ == "__main__":
    unittest.main()