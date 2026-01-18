"""
Content Translation Service - Part 2
=====================================
Background job processing for KI translation jobs.

This module handles batch operations and background task processing
for the translation pipeline (KI workers, async job completion).
Separate from Part 1 to maintain max 500 lines per file constraint.
"""

from typing import Optional, Dict, Any, List
from psycopg.rows import dict_row
from app.database import get_connection
import logging

logger = logging.getLogger(__name__)


class ContentTranslationJobProcessor:
    """
    Background job processor for translation jobs.

    Handles batch operations used by KI pipeline and async workers.
    Not directly called by API endpoints - used by background jobs.
    """

    @staticmethod
    def get_pending_jobs(limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all pending KI translation jobs.

        Used by background workers to fetch jobs for processing.

        Args:
            limit: Maximum number of jobs to return (default 100, max 1000)

        Returns:
            List of pending translation jobs with:
            - job_id: Unique job identifier
            - namespace: Content namespace
            - key_path: Content identifier
            - target_language: Target language code
            - content_type: Type of content (text, html, markdown)
            - status: Job status ('pending', 'processing', 'completed', 'failed')
            - created_at: When job was created
            - context: Additional context for translation
        """
        try:
            if limit > 1000:
                limit = 1000

            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    query = """
                        SELECT
                            job_id,
                            namespace,
                            key_path,
                            target_language,
                            content_type,
                            status,
                            created_at,
                            context
                        FROM translation_jobs
                        WHERE status = 'pending'
                        ORDER BY created_at ASC
                        LIMIT %s
                    """
                    cursor.execute(query, (limit,))
                    return cursor.fetchall() or []

        except Exception as e:
            logger.error(f"Failed to get pending jobs: {str(e)}")
            return []

    @staticmethod
    def mark_job_complete(job_id: str, translation_id: str) -> bool:
        """
        Mark a translation job as complete.

        Called by KI pipeline after successful translation to update job status.

        Args:
            job_id: ID of the translation job to mark complete
            translation_id: ID of the resulting translation record

        Returns:
            True if successful, False on error
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        UPDATE translation_jobs
                        SET status = 'completed',
                            result_translation_id = %s,
                            completed_at = NOW()
                        WHERE job_id = %s
                    """
                    cursor.execute(query, (translation_id, job_id))
                    conn.commit()

            logger.info(
                f"Translation job completed: {job_id}",
                extra={'translation_id': translation_id}
            )
            return True

        except Exception as e:
            logger.error(f"Failed to complete job: {str(e)}")
            return False


__all__ = ['ContentTranslationJobProcessor']
