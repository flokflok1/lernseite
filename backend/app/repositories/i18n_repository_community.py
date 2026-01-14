"""
i18n Repository - Community Suggestions, AI Reviews & Cache Management Data Access Layer

Implements database operations for:
- Community translation suggestions and voting
- AI moderation and quality reviews
- Translation cache management
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import psycopg
from psycopg.rows import dict_row
from app.repositories.base_repository import BaseRepository


class I18nCommunityRepository(BaseRepository):
    """
    i18n Community, Moderation & Cache Repository.

    Manages:
    - Community translation suggestions and voting system
    - AI moderation reviews for quality control
    - Translation cache invalidation
    """

    def __init__(self, connection: psycopg.Connection):
        self.table_name = "translations.i18n_suggestions"
        self.conn = connection

    # =========================================================================
    # COMMUNITY SUGGESTIONS & VOTING
    # =========================================================================

    def create_suggestion(
        self,
        namespace_code: str,
        key_path: str,
        language_code: str,
        suggested_text: str,
        user_id: str,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Create community translation suggestion.

        Args:
            namespace_code: Namespace code
            key_path: Key path
            language_code: Language code
            suggested_text: Suggested translation
            user_id: User who suggested
            reason: Reason for suggestion

        Returns:
            Created suggestion
        """
        # Get or create key
        from app.repositories.i18n_repository_languages import I18nLanguagesRepository
        lang_repo = I18nLanguagesRepository(self.conn)
        key = lang_repo.get_or_create_key(namespace_code, key_path)
        key_id = key['key_id']

        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                INSERT INTO translations.i18n_suggestions
                (key_id, language_code, suggested_text, suggested_by, reason, status)
                VALUES (%s, %s, %s, %s, %s, 'pending')
                RETURNING suggestion_id, suggested_text, status, created_at
            """, (key_id, language_code, suggested_text, user_id, reason))
            result = cursor.fetchone()
            self.conn.commit()
            return result

    def get_pending_suggestions(
        self,
        language_code: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get pending community suggestions.

        Args:
            language_code: Optional language filter
            limit: Max results

        Returns:
            List of pending suggestions
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            if language_code:
                cursor.execute("""
                    SELECT
                        s.suggestion_id,
                        k.key_path,
                        s.language_code,
                        s.suggested_text,
                        s.reason,
                        s.vote_score,
                        s.suggested_by,
                        s.created_at
                    FROM translations.i18n_suggestions s
                    JOIN translations.i18n_keys k ON s.key_id = k.key_id
                    WHERE s.status = 'pending' AND s.language_code = %s
                    ORDER BY s.vote_score DESC
                    LIMIT %s
                """, (language_code, limit))
            else:
                cursor.execute("""
                    SELECT
                        s.suggestion_id,
                        k.key_path,
                        s.language_code,
                        s.suggested_text,
                        s.reason,
                        s.vote_score,
                        s.suggested_by,
                        s.created_at
                    FROM translations.i18n_suggestions s
                    JOIN translations.i18n_keys k ON s.key_id = k.key_id
                    WHERE s.status = 'pending'
                    ORDER BY s.vote_score DESC, s.language_code
                    LIMIT %s
                """, (limit,))

            return cursor.fetchall()

    def vote_on_suggestion(
        self,
        suggestion_id: str,
        user_id: str,
        vote_value: int
    ) -> Dict[str, Any]:
        """
        Vote on suggestion (upvote/downvote).

        Args:
            suggestion_id: Suggestion ID
            user_id: User voting
            vote_value: +1 (upvote) or -1 (downvote)

        Returns:
            Updated suggestion
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Insert vote (ignore duplicates)
            cursor.execute("""
                INSERT INTO translations.i18n_suggestion_votes
                (suggestion_id, user_id, vote_value)
                VALUES (%s, %s, %s)
                ON CONFLICT (suggestion_id, user_id) DO UPDATE
                SET vote_value = %s
            """, (suggestion_id, user_id, vote_value, vote_value))

            # Update suggestion vote score
            cursor.execute("""
                UPDATE translations.i18n_suggestions s
                SET vote_score = (
                    SELECT COALESCE(SUM(vote_value), 0)
                    FROM translations.i18n_suggestion_votes
                    WHERE suggestion_id = %s
                )
                WHERE suggestion_id = %s
                RETURNING suggestion_id, vote_score, status
            """, (suggestion_id, suggestion_id))

            result = cursor.fetchone()
            self.conn.commit()
            return result

    # =========================================================================
    # AI MODERATION & REVIEWS
    # =========================================================================

    def create_ai_review(
        self,
        translation_id: str,
        quality_score: float,
        issues: List[str],
        suggestions: str = ""
    ) -> Dict[str, Any]:
        """
        Create AI moderation review for translation.

        Args:
            translation_id: Translation ID
            quality_score: Quality score (0.0-1.0)
            issues: List of identified issues
            suggestions: Suggestions for improvement

        Returns:
            Created review
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                INSERT INTO translations.i18n_ai_reviews
                (translation_id, quality_score, issues, suggestions, status)
                VALUES (%s, %s, %s, %s, 'completed')
                RETURNING review_id, quality_score, status, created_at
            """, (translation_id, quality_score, json.dumps(issues), suggestions))

            result = cursor.fetchone()
            self.conn.commit()
            return result

    def get_low_quality_translations(
        self,
        quality_threshold: float = 0.7,
        language_code: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get translations flagged by AI as low quality.

        Args:
            quality_threshold: Quality score threshold
            language_code: Optional language filter
            limit: Max results

        Returns:
            List of low-quality translations with issues
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            if language_code:
                cursor.execute("""
                    SELECT
                        t.translation_id,
                        k.key_path,
                        t.language_code,
                        t.value,
                        r.quality_score,
                        r.issues,
                        r.suggestions
                    FROM translations.i18n_translations t
                    JOIN translations.i18n_keys k ON t.key_id = k.key_id
                    JOIN translations.i18n_ai_reviews r ON t.translation_id = r.translation_id
                    WHERE r.quality_score < %s AND t.language_code = %s
                    ORDER BY r.quality_score ASC
                    LIMIT %s
                """, (quality_threshold, language_code, limit))
            else:
                cursor.execute("""
                    SELECT
                        t.translation_id,
                        k.key_path,
                        t.language_code,
                        t.value,
                        r.quality_score,
                        r.issues,
                        r.suggestions
                    FROM translations.i18n_translations t
                    JOIN translations.i18n_keys k ON t.key_id = k.key_id
                    JOIN translations.i18n_ai_reviews r ON t.translation_id = r.translation_id
                    WHERE r.quality_score < %s
                    ORDER BY r.quality_score ASC
                    LIMIT %s
                """, (quality_threshold, limit))

            return cursor.fetchall()

    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================

    def invalidate_language_cache(self, language_code: str) -> None:
        """
        Invalidate translation cache for a language.

        Args:
            language_code: Language code
        """
        with self.conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM translations.translation_cache
                WHERE language_code = %s
            """, (language_code,))
            self.conn.commit()

    def invalidate_all_caches(self) -> None:
        """Invalidate all translation caches."""
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM translations.translation_cache")
            self.conn.commit()
