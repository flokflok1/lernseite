"""
Content Translation Repository

Database operations for course content translations and translation jobs.
Distinct from i18n repositories which handle UI string translations.

Uses psycopg3 connection pooling - no ORM.
"""

from typing import Optional, Dict, Any, List
from uuid import uuid4
from psycopg.rows import dict_row

from app.infrastructure.persistence.database import get_connection
import logging

logger = logging.getLogger(__name__)


class ContentTranslationRepository:
    """Repository for content translation CRUD and job management."""

    # ================================================================
    # TRANSLATION CRUD
    # ================================================================

    @classmethod
    def create_job(
        cls,
        namespace: str,
        key_path: str,
        target_language: str,
        content_type: str,
        user_id: Optional[str],
        context: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a KI translation job record."""
        job_id = str(uuid4())
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "INSERT INTO translation_jobs "
                    "(job_id, namespace, key_path, target_language, content_type, "
                    "status, created_by, context, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW()) "
                    "RETURNING job_id, status, created_at",
                    (job_id, namespace, key_path, target_language,
                     content_type, 'pending', user_id, context)
                )
                result = cur.fetchone()
                conn.commit()
        return result

    @classmethod
    def find_translation(
        cls, namespace: str, key_path: str, language_code: str
    ) -> Optional[Dict[str, Any]]:
        """Get translation by namespace, key_path, and language."""
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT translation_id, namespace, key_path, language_code, "
                    "text, source, status, created_at, updated_at "
                    "FROM translations "
                    "WHERE namespace = %s AND key_path = %s AND language_code = %s",
                    (namespace, key_path, language_code)
                )
                return cur.fetchone()

    @classmethod
    def find_translation_by_id(cls, translation_id: str) -> Optional[Dict[str, Any]]:
        """Get translation by ID."""
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT translation_id, namespace, key_path, language_code, "
                    "text, source, status, created_at, updated_at "
                    "FROM translations WHERE translation_id = %s",
                    (translation_id,)
                )
                return cur.fetchone()

    @classmethod
    def upsert_translation(
        cls,
        namespace: str,
        key_path: str,
        language_code: str,
        text: str,
        source: str = 'manual',
        status: str = 'active',
        translated_by: Optional[str] = None
    ) -> Optional[str]:
        """Insert or update a translation, return translation_id."""
        translation_id = str(uuid4())
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "INSERT INTO translations "
                    "(translation_id, namespace, key_path, language_code, text, "
                    "source, status, translated_by, created_at, updated_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()) "
                    "ON CONFLICT (namespace, key_path, language_code) DO UPDATE SET "
                    "text = EXCLUDED.text, source = EXCLUDED.source, "
                    "status = EXCLUDED.status, translated_by = EXCLUDED.translated_by, "
                    "updated_at = NOW() "
                    "RETURNING translation_id",
                    (translation_id, namespace, key_path, language_code,
                     text, source, status, translated_by)
                )
                result = cur.fetchone()
                conn.commit()
        return result['translation_id'] if result else translation_id

    @classmethod
    def update_translation_text(
        cls, translation_id: str, text: str, status: str = 'active',
        updated_by: Optional[str] = None
    ) -> bool:
        """Update an existing translation's text and status."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE translations SET text = %s, status = %s, "
                    "source = 'manual', translated_by = COALESCE(%s, translated_by), "
                    "updated_at = NOW() WHERE translation_id = %s",
                    (text, status, updated_by, translation_id)
                )
                conn.commit()
        return True

    @classmethod
    def delete_translation(cls, translation_id: str) -> bool:
        """Delete a translation by ID."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM translations WHERE translation_id = %s",
                    (translation_id,)
                )
                conn.commit()
        return True

    # ================================================================
    # JOB MANAGEMENT
    # ================================================================

    @classmethod
    def get_job_status(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a translation job."""
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT job_id, namespace, key_path, target_language, "
                    "status, created_at, completed_at, result_translation_id "
                    "FROM translation_jobs WHERE job_id = %s",
                    (job_id,)
                )
                return cur.fetchone()

    @classmethod
    def get_pending_jobs(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """Get pending translation jobs ordered by creation time."""
        if limit > 1000:
            limit = 1000
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT job_id, namespace, key_path, target_language, "
                    "content_type, status, created_at, context "
                    "FROM translation_jobs WHERE status = 'pending' "
                    "ORDER BY created_at ASC LIMIT %s",
                    (limit,)
                )
                return cur.fetchall() or []

    @classmethod
    def mark_job_complete(cls, job_id: str, translation_id: str) -> bool:
        """Mark a translation job as completed."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE translation_jobs SET status = 'completed', "
                    "result_translation_id = %s, completed_at = NOW() "
                    "WHERE job_id = %s",
                    (translation_id, job_id)
                )
                conn.commit()
        return True
