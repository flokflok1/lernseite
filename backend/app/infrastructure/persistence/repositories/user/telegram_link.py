"""
Telegram-Verknüpfung im User-Modell.

Liest/schreibt die telegram_*-Felder in core.users.
DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, execute_query
)


# 6-stelliger Code aus Großbuchstaben + Ziffern (ohne ähnliche: 0/O, 1/I)
_CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
_CODE_LENGTH = 6
_CODE_TTL_HOURS = 24


def generate_link_code() -> str:
    """Generiert einen einmaligen Verknüpfungs-Code."""
    return ''.join(secrets.choice(_CODE_ALPHABET) for _ in range(_CODE_LENGTH))


class TelegramLinkRepository:
    """User ↔ Telegram-Chat-Verknüpfung."""

    @classmethod
    def create_link_code(cls, user_id: UUID) -> tuple[str, datetime]:
        """Erzeugt + persistiert neuen Verknüpfungs-Code für User.
        Bestehender Code wird überschrieben."""
        code = generate_link_code()
        expires = datetime.utcnow() + timedelta(hours=_CODE_TTL_HOURS)
        execute_query(
            """
            UPDATE core.users
            SET telegram_link_code = %s,
                telegram_link_expires_at = %s
            WHERE user_id = %s
            """,
            (code, expires, str(user_id)),
        )
        return code, expires

    @classmethod
    def find_user_by_link_code(cls, code: str) -> Optional[dict]:
        """Sucht User über noch nicht abgelaufenen Code."""
        row = fetch_one(
            """
            SELECT user_id, email, username, telegram_link_expires_at
            FROM core.users
            WHERE telegram_link_code = %s
              AND telegram_link_expires_at > NOW()
            """,
            (code.upper(),),
        )
        return dict(row) if row else None

    @classmethod
    def link_chat(cls, user_id: UUID, chat_id: int) -> None:
        """Bindet Telegram-Chat an User. Code wird invalidiert."""
        execute_query(
            """
            UPDATE core.users
            SET telegram_chat_id = %s,
                telegram_link_code = NULL,
                telegram_link_expires_at = NULL,
                telegram_linked_at = NOW()
            WHERE user_id = %s
            """,
            (chat_id, str(user_id)),
        )

    @classmethod
    def unlink_chat(cls, user_id: UUID) -> None:
        """Hebt Verknüpfung auf."""
        execute_query(
            """
            UPDATE core.users
            SET telegram_chat_id = NULL,
                telegram_linked_at = NULL
            WHERE user_id = %s
            """,
            (str(user_id),),
        )

    @classmethod
    def find_user_by_chat_id(cls, chat_id: int) -> Optional[dict]:
        """Sucht User über verknüpfte chat_id (für Webhook-Verarbeitung)."""
        row = fetch_one(
            """
            SELECT user_id, email, username, telegram_chat_id
            FROM core.users
            WHERE telegram_chat_id = %s
            """,
            (chat_id,),
        )
        return dict(row) if row else None

    @classmethod
    def get_chat_id(cls, user_id: UUID) -> Optional[int]:
        """Liefert chat_id wenn verknüpft, sonst None."""
        row = fetch_one(
            "SELECT telegram_chat_id FROM core.users WHERE user_id = %s",
            (str(user_id),),
        )
        if row and row.get('telegram_chat_id'):
            return int(row['telegram_chat_id'])
        return None

    @classmethod
    def list_all_linked_users(cls) -> list[dict]:
        """Alle User mit aktiver Telegram-Verknüpfung."""
        rows = fetch_one  # placeholder
        from app.infrastructure.persistence.database.connection import fetch_all
        rows = fetch_all(
            """
            SELECT user_id, username, email, telegram_chat_id
            FROM core.users
            WHERE telegram_chat_id IS NOT NULL
            """
        )
        return [dict(r) for r in (rows or [])]
