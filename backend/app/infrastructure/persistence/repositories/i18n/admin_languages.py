"""
i18n Admin Language Management Repository

Database access for admin language operations:
- Check language existence
- Create/update/delete languages
- Delete translations for a language
- Get active language codes
- Export translations with keys
"""

from typing import Optional, List, Dict, Any, Tuple

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query
)


class I18nAdminLanguageRepository:
    """Repository for admin-level language management operations."""

    @staticmethod
    def language_exists(language_code: str) -> bool:
        """
        Check if a language exists.

        Args:
            language_code: ISO language code

        Returns:
            True if language exists
        """
        result = fetch_one(
            "SELECT 1 FROM translations.supported_languages WHERE language_code = %s",
            (language_code,)
        )
        return result is not None

    @staticmethod
    def create_language(
        language_code: str,
        language_name: str,
        native_name: str,
        flag_svg_code: str,
        active: bool = True,
        rtl: bool = False,
        is_primary: bool = False,
        priority: int = 100
    ) -> None:
        """
        Insert a new supported language.

        Args:
            language_code: ISO language code
            language_name: English name
            native_name: Native name
            flag_svg_code: SVG flag code
            active: Whether language is active
            rtl: Right-to-left language
            is_primary: Whether this is primary language
            priority: Sort priority
        """
        execute_query("""
            INSERT INTO translations.supported_languages (
                language_code, language_name, native_name, flag,
                is_active, is_rtl, is_primary, priority
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            language_code, language_name, native_name, flag_svg_code,
            active, rtl, is_primary, priority
        ))

    @staticmethod
    def update_language(
        language_code: str,
        updates: List[str],
        params: List[Any]
    ) -> None:
        """
        Update a language with dynamic SET clause.

        Args:
            language_code: Language code to update
            updates: List of 'column = %s' strings
            params: List of parameter values (language_code appended)
        """
        params_with_code = list(params) + [language_code]
        execute_query(f"""
            UPDATE translations.supported_languages
            SET {', '.join(updates)}
            WHERE language_code = %s
        """, tuple(params_with_code))

    @staticmethod
    def delete_translations_for_language(language_code: str) -> None:
        """
        Delete all translations for a language (cascade prep).

        Args:
            language_code: Language code
        """
        execute_query(
            "DELETE FROM translations.i18n_translations WHERE language_code = %s",
            (language_code,)
        )

    @staticmethod
    def delete_language(language_code: str) -> None:
        """
        Delete a supported language.

        Args:
            language_code: Language code to delete
        """
        execute_query(
            "DELETE FROM translations.supported_languages WHERE language_code = %s",
            (language_code,)
        )

    @staticmethod
    def get_active_language_codes() -> List[str]:
        """
        Get active language codes ordered by priority.

        Returns:
            List of language code strings
        """
        rows = fetch_all(
            "SELECT language_code FROM translations.supported_languages WHERE is_active = TRUE ORDER BY priority"
        ) or []
        return [r['language_code'] for r in rows]

    @staticmethod
    def export_translations(lang_codes: List[str]) -> List[Dict[str, Any]]:
        """
        Export all translations for given language codes.

        Args:
            lang_codes: List of language codes

        Returns:
            List of dicts with key_path, language_code, value
        """
        query = """
            SELECT
                k.key_path,
                t.language_code,
                t.value
            FROM translations.i18n_keys k
            LEFT JOIN translations.i18n_translations t ON k.key_id = t.key_id
            WHERE t.language_code = ANY(%s)
            ORDER BY k.key_path, t.language_code
        """
        return fetch_all(query, (lang_codes,)) or []
