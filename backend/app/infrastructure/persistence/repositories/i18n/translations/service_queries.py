"""
i18n Service Queries Repository - Part 1
==========================================
Language stats, suggestion, and key management queries.
Part 2 (service_queries_part2.py) contains AI, config, and translation queries.

Extracted from:
- application/services/i18n/languages.py
- application/services/i18n/suggestions.py
- application/services/i18n/keys.py
"""

from typing import Optional, Dict, Any, List, Tuple
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class I18nLanguageStatsRepository:
    """Language metadata, progress tracking, and primary language queries."""

    @staticmethod
    def get_primary_language_code() -> Optional[str]:
        """Get the primary language code."""
        result = fetch_one(
            "SELECT language_code FROM translations.supported_languages WHERE is_primary = TRUE LIMIT 1"
        )
        return result['language_code'] if result else None

    @staticmethod
    def get_total_key_count() -> int:
        """Get total active i18n key count."""
        result = fetch_one("SELECT COUNT(*) as cnt FROM translations.i18n_keys WHERE TRUE")
        return result['cnt'] if result else 0

    @staticmethod
    def get_languages_with_progress(active_only: bool = True) -> List[Dict[str, Any]]:
        """Get languages with translation progress stats."""
        total_keys = I18nLanguageStatsRepository.get_total_key_count()

        base_query = """
            SELECT
                sl.language_code,
                sl.language_name,
                sl.native_name,
                sl.flag AS flag_svg_code,
                sl.is_primary,
                COALESCE(sl.priority, 100) as priority,
                COALESCE(sl.is_rtl, FALSE) as rtl,
                sl.is_active as active,
                %s as total_keys,
                COALESCE(trans_count.cnt, 0) as translated_keys,
                CASE WHEN %s > 0 THEN ROUND(COALESCE(trans_count.cnt, 0) * 100.0 / %s)::int ELSE 0 END as completion_percent,
                0 as verified_keys,
                0 as pending_suggestions
            FROM translations.supported_languages sl
            LEFT JOIN (
                SELECT language_code, COUNT(*) as cnt
                FROM translations.i18n_translations
                GROUP BY language_code
            ) trans_count ON sl.language_code = trans_count.language_code
        """
        if active_only:
            base_query += " WHERE sl.is_active = TRUE"
        base_query += " ORDER BY sl.priority, sl.language_name"

        return fetch_all(base_query, (total_keys, total_keys, total_keys)) or []

    @staticmethod
    def set_primary_language(language_code: str) -> None:
        """Unset current primary, set new primary language."""
        execute_query(
            "UPDATE translations.supported_languages SET is_primary = FALSE WHERE is_primary = TRUE"
        )
        execute_query(
            "UPDATE translations.supported_languages SET is_primary = TRUE WHERE language_code = %s",
            (language_code,)
        )

    @staticmethod
    def get_language_progress(language_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed progress for a specific language."""
        total_keys = I18nLanguageStatsRepository.get_total_key_count()

        query = """
            SELECT
                sl.language_code,
                sl.language_name,
                sl.native_name,
                sl.flag AS flag_svg_code,
                sl.is_primary,
                COALESCE(sl.priority, 100) as priority,
                sl.is_active as active,
                %s as total_keys,
                COALESCE(trans_count.cnt, 0) as translated_keys,
                CASE WHEN %s > 0 THEN ROUND(COALESCE(trans_count.cnt, 0) * 100.0 / %s)::int ELSE 0 END as completion_percent
            FROM translations.supported_languages sl
            LEFT JOIN (
                SELECT language_code, COUNT(*) as cnt
                FROM translations.i18n_translations
                WHERE language_code = %s
                GROUP BY language_code
            ) trans_count ON sl.language_code = trans_count.language_code
            WHERE sl.language_code = %s
        """
        return fetch_one(query, (total_keys, total_keys, total_keys, language_code, language_code))


class I18nSuggestionQueriesRepository:
    """Translation suggestion and voting queries."""

    @staticmethod
    def submit_suggestion(
        translation_id: Optional[str],
        key_id: Optional[str],
        language_code: str,
        suggested_value: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Insert a translation suggestion, return suggestion_id."""
        return fetch_one(
            """
            INSERT INTO translations.i18n_suggestions
                (translation_id, key_id, language_code, suggested_value, reason, suggested_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING suggestion_id
            """,
            (translation_id, key_id, language_code, suggested_value, reason, user_id)
        )

    @staticmethod
    def vote_suggestion(suggestion_id: str, user_id: str, vote_type: str) -> None:
        """Upsert a vote on a suggestion."""
        execute_query(
            """
            INSERT INTO translations.i18n_suggestion_votes (suggestion_id, user_id, vote_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (suggestion_id, user_id)
            DO UPDATE SET vote_type = EXCLUDED.vote_type
            """,
            (suggestion_id, user_id, vote_type)
        )

    @staticmethod
    def get_suggestions(
        status: str = 'pending',
        language_code: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get suggestions with user and key info."""
        return fetch_all(
            """
            SELECT
                s.suggestion_id,
                s.translation_id,
                s.key_id,
                s.language_code,
                s.suggested_value,
                s.reason,
                s.suggested_by,
                u.username as suggested_by_username,
                s.suggested_at,
                s.votes_up,
                s.votes_down,
                s.vote_score,
                s.status,
                t.value as current_value,
                COALESCE(k.key_path, '') as key_path
            FROM translations.i18n_suggestions s
            LEFT JOIN core.users u ON s.suggested_by = u.user_id
            LEFT JOIN translations.i18n_translations t ON s.translation_id = t.translation_id
            LEFT JOIN translations.i18n_keys k ON COALESCE(s.key_id, t.key_id) = k.key_id
            WHERE s.status = %s
            AND (%s IS NULL OR s.language_code = %s)
            ORDER BY s.vote_score DESC, s.suggested_at DESC
            LIMIT %s
            """,
            (status, language_code, language_code, limit)
        ) or []

    @staticmethod
    def get_pending_request(target_language: str, scope: str) -> Optional[Dict[str, Any]]:
        """Check for existing pending/processing translation request."""
        return fetch_one(
            """
            SELECT request_id, request_count
            FROM translations.i18n_translation_requests
            WHERE target_language = %s AND scope = %s
            AND status IN ('pending', 'processing')
            """,
            (target_language, scope)
        )

    @staticmethod
    def increment_request_count(request_id: str) -> Optional[Dict[str, Any]]:
        """Increment request count and priority for existing request."""
        return fetch_one(
            """
            UPDATE translations.i18n_translation_requests
            SET request_count = request_count + 1, priority = priority + 1
            WHERE request_id = %s
            RETURNING request_id, request_count
            """,
            (request_id,)
        )

    @staticmethod
    def create_translation_request(
        target_language: str,
        scope: str,
        namespace_id: Optional[int],
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create a new translation request."""
        return fetch_one(
            """
            INSERT INTO translations.i18n_translation_requests
                (target_language, scope, namespace_id, requested_by)
            VALUES (%s, %s, %s, %s)
            RETURNING request_id, request_count
            """,
            (target_language, scope, namespace_id, user_id)
        )


class I18nKeyQueriesRepository:
    """Translation key and namespace management queries."""

    @staticmethod
    def get_namespaces_with_key_count() -> List[Dict[str, Any]]:
        """Get namespaces with active key counts."""
        return fetch_all(
            """
            SELECT
                n.namespace_code,
                n.name,
                n.description,
                n.icon,
                n.sort_order,
                (SELECT COUNT(*) FROM translations.i18n_keys k
                 WHERE k.namespace_code = n.namespace_code AND k.is_active = TRUE) as key_count
            FROM translations.i18n_namespaces n
            WHERE n.is_active = TRUE
            ORDER BY n.sort_order
            """
        ) or []

    @staticmethod
    def get_keys_paginated(
        primary_language: str,
        namespace_code: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get keys with pagination. Returns (keys, total_count)."""
        conditions = ["k.is_active = TRUE"]
        params: list = []

        if namespace_code:
            conditions.append("k.namespace_code = %s")
            params.append(namespace_code)

        if search:
            conditions.append("(k.key_path ILIKE %s OR k.context ILIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])

        where_clause = " AND ".join(conditions)

        count_result = fetch_one(
            f"SELECT COUNT(*) as total FROM translations.i18n_keys k WHERE {where_clause}",
            tuple(params)
        )
        total = count_result['total'] if count_result else 0

        query_params = [primary_language] + params + [limit, offset]
        keys = fetch_all(
            f"""
            SELECT
                k.key_id,
                k.namespace_code,
                k.key_path,
                k.default_value,
                k.description,
                k.context as context_hint,
                k.is_active,
                k.created_at,
                (SELECT translated_value FROM translations.i18n_translations
                 WHERE key_id = k.key_id AND language_code = %s LIMIT 1) as primary_value,
                (SELECT COUNT(*) FROM translations.i18n_translations
                 WHERE key_id = k.key_id) as translation_count,
                (SELECT COUNT(*) FROM translations.supported_languages
                 WHERE is_active = TRUE) as total_languages
            FROM translations.i18n_keys k
            WHERE {where_clause}
            ORDER BY k.namespace_code, k.key_path
            LIMIT %s OFFSET %s
            """,
            tuple(query_params)
        ) or []

        return keys, total

    @staticmethod
    def create_key(
        namespace_code: str,
        key_path: str,
        default_value: str = '',
        description: Optional[str] = None,
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new translation key."""
        return fetch_one(
            """
            INSERT INTO translations.i18n_keys
                (namespace_code, key_path, default_value, description, context)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (namespace_code, key_path) DO NOTHING
            RETURNING key_id
            """,
            (namespace_code, key_path, default_value, description, context)
        )


