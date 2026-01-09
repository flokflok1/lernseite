"""
Repository for authoring_generations table (Long-Running Generation Jobs)
"""
from typing import Dict, List, Optional
import logging

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringGenerationsRepository(BaseRepository):
    """Repository for managing long-running course generation jobs"""

    @staticmethod
    def create_generation(
        session_id: str,
        generation_scope: str,
        scope_details: Dict,
        steps_total: int,
        ai_provider: str,
        ai_model: str
    ) -> Optional[str]:
        """
        Create a new generation job.

        Args:
            session_id: UUID of authoring session
            generation_scope: Scope of generation
            scope_details: Additional scope details
            steps_total: Total steps to complete
            ai_provider: AI provider
            ai_model: AI model

        Returns:
            generation_id if successful
        """
        query = """
            INSERT INTO ai_pipeline.authoring_generations (
                session_id, generation_scope, scope_details,
                steps_total, ai_provider, ai_model, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 'queued'
            ) RETURNING generation_id
        """
        try:
            result = AuthoringGenerationsRepository.fetch_one(query, (
                session_id, generation_scope, scope_details,
                steps_total, ai_provider, ai_model
            ))
            return result['generation_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating generation: {e}")
            return None

    @staticmethod
    def get_generation_by_id(generation_id: str) -> Optional[Dict]:
        """Get generation record by ID"""
        query = """
            SELECT
                generation_id, session_id, generation_scope, scope_details,
                status, progress_percentage, current_step, steps_total, steps_completed,
                generated_course_id, generated_chapter_ids, generated_lesson_ids,
                generated_chapters, generated_lessons, generated_methods,
                ai_provider, ai_model, total_tokens_used,
                estimated_tokens, estimated_cost_cents, actual_cost_cents,
                error_message, retry_count,
                user_cancelled, user_cancellation_reason,
                started_at, completed_at, estimated_completion_at,
                created_at, updated_at
            FROM ai_pipeline.authoring_generations
            WHERE generation_id = %s
        """
        try:
            return AuthoringGenerationsRepository.fetch_one(query, (generation_id,))
        except Exception as e:
            logger.error(f"Error fetching generation: {e}")
            return None

    @staticmethod
    def get_active_generations(session_id: str) -> List[Dict]:
        """Get active generation jobs for session"""
        query = """
            SELECT
                generation_id, generation_scope, status,
                progress_percentage, current_step,
                steps_completed, steps_total,
                estimated_completion_at, started_at
            FROM ai_pipeline.authoring_generations
            WHERE session_id = %s
            AND status IN ('queued', 'initializing', 'generating')
            ORDER BY created_at DESC
        """
        try:
            return AuthoringGenerationsRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching active generations: {e}")
            return []

    @staticmethod
    def update_progress(
        generation_id: str,
        progress_percentage: int,
        current_step: str,
        steps_completed: int,
        estimated_completion_at: Optional[str] = None
    ) -> bool:
        """
        Update generation progress.

        Args:
            generation_id: UUID of generation
            progress_percentage: Progress (0-100)
            current_step: Current step description
            steps_completed: Steps completed so far
            estimated_completion_at: ETA

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_generations
            SET progress_percentage = %s,
                current_step = %s,
                steps_completed = %s,
                estimated_completion_at = %s,
                updated_at = NOW()
            WHERE generation_id = %s
        """
        try:
            AuthoringGenerationsRepository.execute_update(query, (
                progress_percentage, current_step, steps_completed,
                estimated_completion_at, generation_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            return False

    @staticmethod
    def update_status(
        generation_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update generation status"""
        query = """
            UPDATE ai_pipeline.authoring_generations
            SET status = %s,
                error_message = %s,
                started_at = CASE
                    WHEN %s = 'generating' AND started_at IS NULL THEN NOW()
                    ELSE started_at
                END,
                completed_at = CASE
                    WHEN %s IN ('completed', 'failed', 'cancelled') THEN NOW()
                    ELSE completed_at
                END,
                updated_at = NOW()
            WHERE generation_id = %s
        """
        try:
            AuthoringGenerationsRepository.execute_update(
                query,
                (status, error_message, status, status, generation_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating generation status: {e}")
            return False

    @staticmethod
    def update_results(
        generation_id: str,
        generated_course_id: Optional[str],
        generated_chapter_ids: List[str],
        generated_lesson_ids: List[str],
        generated_chapters: int,
        generated_lessons: int,
        generated_methods: int
    ) -> bool:
        """Update generation results"""
        query = """
            UPDATE ai_pipeline.authoring_generations
            SET generated_course_id = %s,
                generated_chapter_ids = %s,
                generated_lesson_ids = %s,
                generated_chapters = %s,
                generated_lessons = %s,
                generated_methods = %s,
                updated_at = NOW()
            WHERE generation_id = %s
        """
        try:
            AuthoringGenerationsRepository.execute_update(query, (
                generated_course_id, generated_chapter_ids, generated_lesson_ids,
                generated_chapters, generated_lessons, generated_methods,
                generation_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error updating generation results: {e}")
            return False

    @staticmethod
    def update_token_usage(
        generation_id: str,
        tokens_used: int,
        cost_cents: Optional[int] = None
    ) -> bool:
        """Update token usage"""
        query = """
            UPDATE ai_pipeline.authoring_generations
            SET total_tokens_used = total_tokens_used + %s,
                actual_cost_cents = COALESCE(actual_cost_cents, 0) + COALESCE(%s, 0),
                updated_at = NOW()
            WHERE generation_id = %s
        """
        try:
            AuthoringGenerationsRepository.execute_update(
                query,
                (tokens_used, cost_cents, generation_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating token usage: {e}")
            return False

    @staticmethod
    def mark_cancelled(
        generation_id: str,
        cancellation_reason: str
    ) -> bool:
        """Mark generation as cancelled by user"""
        query = """
            UPDATE ai_pipeline.authoring_generations
            SET user_cancelled = TRUE,
                user_cancellation_reason = %s,
                status = 'cancelled',
                completed_at = NOW(),
                updated_at = NOW()
            WHERE generation_id = %s
        """
        try:
            AuthoringGenerationsRepository.execute_update(
                query,
                (cancellation_reason, generation_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error marking cancelled: {e}")
            return False

    @staticmethod
    def increment_retry_count(generation_id: str) -> bool:
        """Increment retry counter"""
        query = """
            UPDATE ai_pipeline.authoring_generations
            SET retry_count = retry_count + 1,
                updated_at = NOW()
            WHERE generation_id = %s
        """
        try:
            AuthoringGenerationsRepository.execute_update(query, (generation_id,))
            return True
        except Exception as e:
            logger.error(f"Error incrementing retry count: {e}")
            return False
