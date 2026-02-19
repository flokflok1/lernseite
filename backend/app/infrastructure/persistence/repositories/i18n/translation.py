"""
i18n Translation Repository - Core CRUD operations for translations.

Implements the Repository Pattern for database operations related to
translation content, including:
- Loading translation files (frontend translations)
- Accessing database translations
- Creating, updating, and deleting translations (single and bulk)

Comparison and analytics methods are in translation_part2.py.

No ORM - Uses psycopg3 with direct SQL and parameterized queries.
"""

from typing import Optional, List, Dict, Any, Set, Tuple
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from dataclasses import dataclass


@dataclass
class Translation:
    """Represents a single translation entry."""

    translation_key: str
    language_code: str
    value: str
    source: str = 'database'  # 'database', 'frontend', 'cache'
    last_modified: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'translation_key': self.translation_key,
            'language_code': self.language_code,
            'value': self.value,
            'source': self.source,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TranslationRepository:
    """
    Repository for managing translations.

    Handles all database operations for translation content, including:
    - Loading translations by key and language
    - Comparing frontend vs database translations
    - Detecting translation changes (new, updated, deleted)
    - Calculating similarity scores for conflict detection
    - Applying translation updates
    """

    def __init__(self, connection: psycopg.Connection):
        """Initialize repository with database connection."""
        self.conn = connection

    def get_translation(
        self,
        translation_key: str,
        language_code: str
    ) -> Optional[Translation]:
        """
        Get single translation by key and language.

        Args:
            translation_key: Translation key (e.g., 'admin.users.title')
            language_code: Language code (de, en, pl)

        Returns:
            Translation or None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT translation_key, language_code, value, created_at, updated_at
                FROM support_systems.translations
                WHERE translation_key = %s AND language_code = %s
                """,
                (translation_key, language_code)
            )
            row = cursor.fetchone()

            if row:
                return Translation(
                    translation_key=row['translation_key'],
                    language_code=row['language_code'],
                    value=row['value'],
                    source='database',
                    last_modified=row['updated_at'],
                    created_at=row['created_at']
                )
            return None

    def get_translations_for_language(
        self,
        language_code: str,
        limit: int = 1000,
        offset: int = 0
    ) -> Tuple[List[Translation], int]:
        """
        Get all translations for a language.

        Args:
            language_code: Language code
            limit: Max results
            offset: Results to skip

        Returns:
            Tuple of (translations list, total count)
        """
        limit = min(limit, 1000)

        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Get count
            cursor.execute(
                "SELECT COUNT(*) as total FROM support_systems.translations WHERE language_code = %s",
                (language_code,)
            )
            total = cursor.fetchone()['total']

            # Get translations
            cursor.execute(
                """
                SELECT translation_key, language_code, value, created_at, updated_at
                FROM support_systems.translations
                WHERE language_code = %s
                ORDER BY translation_key ASC
                LIMIT %s OFFSET %s
                """,
                (language_code, limit, offset)
            )
            rows = cursor.fetchall()

            translations = [
                Translation(
                    translation_key=row['translation_key'],
                    language_code=row['language_code'],
                    value=row['value'],
                    source='database',
                    last_modified=row['updated_at'],
                    created_at=row['created_at']
                )
                for row in rows
            ]

            return translations, total

    def get_all_translation_keys(self) -> Set[str]:
        """
        Get set of all translation keys in database.

        Returns:
            Set of all translation keys
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT translation_key FROM support_systems.translations ORDER BY translation_key"
            )
            rows = cursor.fetchall()

            return {row[0] for row in rows}

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes.

        Returns:
            List of language codes (de, en, pl, etc.)
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT language_code FROM support_systems.translations ORDER BY language_code"
            )
            rows = cursor.fetchall()

            return [row[0] for row in rows]

    def create_translation(
        self,
        translation_key: str,
        language_code: str,
        value: str
    ) -> Translation:
        """
        Create new translation entry.

        Args:
            translation_key: Translation key
            language_code: Language code
            value: Translation value

        Returns:
            Created Translation instance
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO support_systems.translations
                (translation_key, language_code, value)
                VALUES (%s, %s, %s)
                RETURNING translation_key, language_code, value, created_at, updated_at
                """,
                (translation_key, language_code, value)
            )
            row = cursor.fetchone()
            self.conn.commit()

            return Translation(
                translation_key=row['translation_key'],
                language_code=row['language_code'],
                value=row['value'],
                source='database',
                last_modified=row['updated_at'],
                created_at=row['created_at']
            )

    def update_translation(
        self,
        translation_key: str,
        language_code: str,
        value: str
    ) -> Optional[Translation]:
        """
        Update existing translation.

        Args:
            translation_key: Translation key
            language_code: Language code
            value: New translation value

        Returns:
            Updated Translation or None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE support_systems.translations
                SET value = %s, updated_at = NOW()
                WHERE translation_key = %s AND language_code = %s
                RETURNING translation_key, language_code, value, created_at, updated_at
                """,
                (value, translation_key, language_code)
            )
            row = cursor.fetchone()
            self.conn.commit()

            if row:
                return Translation(
                    translation_key=row['translation_key'],
                    language_code=row['language_code'],
                    value=row['value'],
                    source='database',
                    last_modified=row['updated_at'],
                    created_at=row['created_at']
                )
            return None

    def delete_translation(
        self,
        translation_key: str,
        language_code: str
    ) -> bool:
        """
        Delete translation.

        Args:
            translation_key: Translation key
            language_code: Language code

        Returns:
            True if deleted, False if not found
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM support_systems.translations
                WHERE translation_key = %s AND language_code = %s
                """,
                (translation_key, language_code)
            )
            deleted = cursor.rowcount > 0
            self.conn.commit()

            return deleted

    def bulk_create_translations(
        self,
        translations: List[Dict[str, str]]
    ) -> int:
        """
        Create multiple translations in a single operation.

        Args:
            translations: List of dicts with keys: translation_key, language_code, value

        Returns:
            Number of translations created
        """
        if not translations:
            return 0

        with self.conn.cursor() as cursor:
            # Use executemany for bulk insert
            cursor.executemany(
                """
                INSERT INTO support_systems.translations
                (translation_key, language_code, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (translation_key, language_code) DO NOTHING
                """,
                [
                    (t['translation_key'], t['language_code'], t['value'])
                    for t in translations
                ]
            )
            created = cursor.rowcount
            self.conn.commit()

            return created

    def bulk_update_translations(
        self,
        updates: List[Dict[str, str]]
    ) -> int:
        """
        Update multiple translations.

        Args:
            updates: List of dicts with keys: translation_key, language_code, value

        Returns:
            Number of translations updated
        """
        if not updates:
            return 0

        total_updated = 0

        with self.conn.cursor() as cursor:
            for update in updates:
                cursor.execute(
                    """
                    UPDATE support_systems.translations
                    SET value = %s, updated_at = NOW()
                    WHERE translation_key = %s AND language_code = %s
                    """,
                    (update['value'], update['translation_key'], update['language_code'])
                )
                total_updated += cursor.rowcount

            self.conn.commit()

        return total_updated

    def bulk_delete_translations(
        self,
        deletes: List[Dict[str, str]]
    ) -> int:
        """
        Delete multiple translations.

        Args:
            deletes: List of dicts with keys: translation_key, language_code

        Returns:
            Number of translations deleted
        """
        if not deletes:
            return 0

        total_deleted = 0

        with self.conn.cursor() as cursor:
            for delete in deletes:
                cursor.execute(
                    """
                    DELETE FROM support_systems.translations
                    WHERE translation_key = %s AND language_code = %s
                    """,
                    (delete['translation_key'], delete['language_code'])
                )
                total_deleted += cursor.rowcount

            self.conn.commit()

        return total_deleted

    # Comparison and analytics methods are in translation_part2.py
