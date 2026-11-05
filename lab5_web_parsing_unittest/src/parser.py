"""Модуль 2: парсер форума с использованием requests + BeautifulSoup."""

from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup, Tag

from src.database import DatabaseRepository

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class ForumParser:
    """Извлекает комментарии форума и сохраняет их в БД.

    Ожидаемая структура HTML:
        <div class="comment" data-comment-id="123">
            <span class="username">alice</span>
            <div class="message">Текст <b>сообщения</b></div>
        </div>
    """

    COMMENT_SELECTOR = "div.comment"
    ID_ATTR = "data-comment-id"
    USERNAME_SELECTOR = ".username"
    MESSAGE_SELECTOR = ".message"

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    # ------------------------------------------------------------------ #
    # Загрузка HTML
    # ------------------------------------------------------------------ #
    def fetch_html(self, url: str) -> str:
        """Скачивает HTML страницы и возвращает строку."""
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        # явно задаём кодировку, чтобы избежать проблем с windows-1251
        if not response.encoding or response.encoding.lower() == "iso-8859-1":
            response.encoding = response.apparent_encoding
        return response.text

    # ------------------------------------------------------------------ #
    # Парсинг
    # ------------------------------------------------------------------ #
    def parse_html(self, html: str) -> list[dict]:
        """Разбирает HTML-строку и возвращает список словарей."""
        soup = BeautifulSoup(html, "lxml")
        result: list[dict] = []

        for node in soup.select(self.COMMENT_SELECTOR):
            parsed = self._parse_comment_node(node)
            if parsed:
                result.append(parsed)

        return result

    def parse_page(self, url: str) -> list[dict]:
        """Скачивает страницу по URL и парсит её."""
        html = self.fetch_html(url)
        return self.parse_html(html)

    # ------------------------------------------------------------------ #
    # Внутренние помощники
    # ------------------------------------------------------------------ #
    def _parse_comment_node(self, node: Tag) -> Optional[dict]:
        raw_id = node.get(self.ID_ATTR)
        if raw_id is None:
            return None
        try:
            comment_id = int(str(raw_id).strip())
        except (ValueError, TypeError):
            return None

        username_tag = node.select_one(self.USERNAME_SELECTOR)
        if username_tag is None:
            return None
        username = username_tag.get_text(strip=True)
        if not username:
            return None

        message_tag = node.select_one(self.MESSAGE_SELECTOR)
        if message_tag is None:
            return None
        # сохраняем внутреннюю HTML-разметку
        message = message_tag.decode_contents().strip()
        if not message:
            return None

        return {
            "id": comment_id,
            "name": username,
            "message": message,
        }

    # ------------------------------------------------------------------ #
    # Сохранение
    # ------------------------------------------------------------------ #
    def save_to_db(
        self,
        parsed_data: Iterable[dict],
        repository: DatabaseRepository,
    ) -> int:
        """Сохраняет данные в БД. Возвращает число сохранённых записей."""
        from src.exceptions import DuplicateIDError, ValidationError

        saved = 0
        for item in parsed_data:
            try:
                repository.add(
                    comment_id=item["id"],
                    username=item["name"],
                    message=item["message"],
                )
                saved += 1
            except (DuplicateIDError, ValidationError):
                # дубликаты и невалидные записи пропускаем
                continue
        return saved