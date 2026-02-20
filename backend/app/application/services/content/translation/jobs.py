"""
Content Translation Service - Part 2
=====================================
Background job processing for KI translation jobs.

This module handles batch operations and background task processing
for the translation pipeline (KI workers, async job completion).
Separate from Part 1 to maintain max 500 lines per file constraint.
"""

from typing import Dict, Any, List
from app.infrastructure.persistence.repositories.content_translation.core import ContentTranslationRepository
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

        Args:
            limit: Maximum number of jobs to return (default 100, max 1000)

        Returns:
            List of pending translation jobs
        """
        try:
            return ContentTranslationRepository.get_pending_jobs(limit)
        except Exception as e:
            logger.error(f"Failed to get pending jobs: {str(e)}")
            return []

    @staticmethod
    def mark_job_complete(job_id: str, translation_id: str) -> bool:
        """
        Mark a translation job as complete.

        Args:
            job_id: ID of the translation job
            translation_id: ID of the resulting translation record

        Returns:
            True if successful, False on error
        """
        try:
            ContentTranslationRepository.mark_job_complete(job_id, translation_id)
            logger.info(
                f"Translation job completed: {job_id}",
                extra={'translation_id': translation_id}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to complete job: {str(e)}")
            return False


__all__ = ['ContentTranslationJobProcessor']
