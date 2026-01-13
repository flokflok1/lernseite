"""
Repository for authoring_finalization table (Merge & Conflict Resolution)
"""
from typing import Dict, List, Optional
import logging

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringFinalizationRepository(BaseRepository):
    """Repository for managing finalization of authoring sessions"""

    @staticmethod
    def create_finalization(
        session_id: str,
        merge_strategy: str = 'safe_merge'
    ) -> Optional[str]:
        """
        Create a new finalization record.

        Args:
            session_id: UUID of authoring session
            merge_strategy: Merge strategy to use

        Returns:
            finalization_id if successful
        """
        query = """
            INSERT INTO ai_pipeline.authoring_finalization (
                session_id, merge_strategy, status
            ) VALUES (
                %s, %s, 'pending'
            ) RETURNING finalization_id
        """
        try:
            result = AuthoringFinalizationRepository.fetch_one(query, (session_id, merge_strategy))
            return result['finalization_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating finalization: {e}")
            return None

    @staticmethod
    def get_finalization_by_id(finalization_id: str) -> Optional[Dict]:
        """Get finalization record by ID"""
        query = """
            SELECT
                finalization_id, session_id, merge_strategy,
                has_conflicts, conflicts, conflict_resolution,
                changes_applied, changes_skipped,
                created_course_id, created_chapter_ids, created_lesson_ids, created_method_ids,
                updated_chapter_ids, updated_lesson_ids, updated_method_ids,
                deleted_chapter_ids, deleted_lesson_ids, deleted_method_ids,
                total_changes, successful_changes, failed_changes,
                rollback_data, rollback_at,
                status, error_message, warnings,
                started_at, completed_at, created_at
            FROM ai_pipeline.authoring_finalization
            WHERE finalization_id = %s
        """
        try:
            return AuthoringFinalizationRepository.fetch_one(query, (finalization_id,))
        except Exception as e:
            logger.error(f"Error fetching finalization: {e}")
            return None

    @staticmethod
    def get_finalization_by_session(session_id: str) -> Optional[Dict]:
        """Get latest finalization for session"""
        query = """
            SELECT
                finalization_id, session_id, merge_strategy,
                has_conflicts, conflicts, conflict_resolution,
                changes_applied, changes_skipped,
                created_course_id, created_chapter_ids, created_lesson_ids,
                updated_chapter_ids, updated_lesson_ids,
                deleted_chapter_ids, deleted_lesson_ids,
                total_changes, successful_changes, failed_changes,
                status, error_message, warnings,
                started_at, completed_at, created_at
            FROM ai_pipeline.authoring_finalization
            WHERE session_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        try:
            return AuthoringFinalizationRepository.fetch_one(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching session finalization: {e}")
            return None

    @staticmethod
    def update_status(
        finalization_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update finalization status"""
        query = """
            UPDATE ai_pipeline.authoring_finalization
            SET status = %s,
                error_message = %s,
                completed_at = CASE
                    WHEN %s IN ('completed', 'failed', 'rolled_back') THEN NOW()
                    ELSE completed_at
                END
            WHERE finalization_id = %s
        """
        try:
            AuthoringFinalizationRepository.execute_update(
                query,
                (status, error_message, status, finalization_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating finalization status: {e}")
            return False

    @staticmethod
    def set_conflicts(
        finalization_id: str,
        conflicts: List[Dict],
        has_conflicts: bool = True
    ) -> bool:
        """
        Set detected conflicts.

        Args:
            finalization_id: UUID of finalization
            conflicts: List of conflict objects
            has_conflicts: Whether conflicts exist

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_finalization
            SET has_conflicts = %s,
                conflicts = %s,
                status = 'pre_check'
            WHERE finalization_id = %s
        """
        try:
            AuthoringFinalizationRepository.execute_update(
                query,
                (has_conflicts, conflicts, finalization_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting conflicts: {e}")
            return False

    @staticmethod
    def set_conflict_resolution(
        finalization_id: str,
        conflict_resolution: Dict
    ) -> bool:
        """
        Store user's conflict resolution decisions.

        Args:
            finalization_id: UUID of finalization
            conflict_resolution: Dict with user decisions

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_finalization
            SET conflict_resolution = %s,
                status = 'in_progress'
            WHERE finalization_id = %s
        """
        try:
            AuthoringFinalizationRepository.execute_update(
                query,
                (conflict_resolution, finalization_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting conflict resolution: {e}")
            return False

    @staticmethod
    def update_results(
        finalization_id: str,
        created_course_id: Optional[str] = None,
        created_chapter_ids: Optional[List[str]] = None,
        created_lesson_ids: Optional[List[str]] = None,
        created_method_ids: Optional[List[str]] = None,
        updated_chapter_ids: Optional[List[str]] = None,
        updated_lesson_ids: Optional[List[str]] = None,
        updated_method_ids: Optional[List[str]] = None,
        deleted_chapter_ids: Optional[List[str]] = None,
        deleted_lesson_ids: Optional[List[str]] = None,
        deleted_method_ids: Optional[List[str]] = None
    ) -> bool:
        """
        Update finalization results.

        Args:
            finalization_id: UUID of finalization
            created_*_ids: Lists of created entity IDs
            updated_*_ids: Lists of updated entity IDs
            deleted_*_ids: Lists of deleted entity IDs

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_finalization
            SET created_course_id = %s,
                created_chapter_ids = %s,
                created_lesson_ids = %s,
                created_method_ids = %s,
                updated_chapter_ids = %s,
                updated_lesson_ids = %s,
                updated_method_ids = %s,
                deleted_chapter_ids = %s,
                deleted_lesson_ids = %s,
                deleted_method_ids = %s
            WHERE finalization_id = %s
        """
        try:
            AuthoringFinalizationRepository.execute_update(query, (
                created_course_id,
                created_chapter_ids or [],
                created_lesson_ids or [],
                created_method_ids or [],
                updated_chapter_ids or [],
                updated_lesson_ids or [],
                updated_method_ids or [],
                deleted_chapter_ids or [],
                deleted_lesson_ids or [],
                deleted_method_ids or [],
                finalization_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error updating results: {e}")
            return False

    @staticmethod
    def update_statistics(
        finalization_id: str,
        total_changes: int,
        successful_changes: int,
        failed_changes: int,
        changes_applied: List[Dict],
        changes_skipped: Optional[List[Dict]] = None
    ) -> bool:
        """
        Update change statistics.

        Args:
            finalization_id: UUID of finalization
            total_changes: Total number of changes
            successful_changes: Successfully applied changes
            failed_changes: Failed changes
            changes_applied: List of applied change details
            changes_skipped: List of skipped change details

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_finalization
            SET total_changes = %s,
                successful_changes = %s,
                failed_changes = %s,
                changes_applied = %s,
                changes_skipped = %s
            WHERE finalization_id = %s
        """
        try:
            AuthoringFinalizationRepository.execute_update(query, (
                total_changes,
                successful_changes,
                failed_changes,
                changes_applied,
                changes_skipped or [],
                finalization_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            return False

    @staticmethod
    def store_rollback_data(
        finalization_id: str,
        rollback_data: Dict
    ) -> bool:
        """
        Store data for potential rollback.

        Args:
            finalization_id: UUID of finalization
            rollback_data: Snapshot of data before changes

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_finalization
            SET rollback_data = %s
            WHERE finalization_id = %s
        """
        try:
            AuthoringFinalizationRepository.execute_update(
                query,
                (rollback_data, finalization_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error storing rollback data: {e}")
            return False

    @staticmethod
    def mark_rolled_back(finalization_id: str) -> bool:
        """
        Mark finalization as rolled back.

        Args:
            finalization_id: UUID of finalization

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_finalization
            SET status = 'rolled_back',
                rollback_at = NOW()
            WHERE finalization_id = %s
        """
        try:
            AuthoringFinalizationRepository.execute_update(query, (finalization_id,))
            return True
        except Exception as e:
            logger.error(f"Error marking rollback: {e}")
            return False

    @staticmethod
    def add_warnings(
        finalization_id: str,
        warnings: List[str]
    ) -> bool:
        """
        Add warnings to finalization.

        Args:
            finalization_id: UUID of finalization
            warnings: List of warning messages

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_finalization
            SET warnings = COALESCE(warnings, '[]'::jsonb) || %s::jsonb
            WHERE finalization_id = %s
        """
        try:
            AuthoringFinalizationRepository.execute_update(
                query,
                (warnings, finalization_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error adding warnings: {e}")
            return False

    @staticmethod
    def get_success_rate(
        session_id: Optional[str] = None,
        merge_strategy: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get finalization success rate statistics.

        Args:
            session_id: Optional filter by session
            merge_strategy: Optional filter by strategy

        Returns:
            Statistics dict
        """
        where_clauses = []
        params = []

        if session_id:
            where_clauses.append("session_id = %s")
            params.append(session_id)

        if merge_strategy:
            where_clauses.append("merge_strategy = %s")
            params.append(merge_strategy)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN status = 'rolled_back' THEN 1 END) as rolled_back,
                COUNT(CASE WHEN has_conflicts = TRUE THEN 1 END) as with_conflicts,
                AVG(CASE
                    WHEN total_changes > 0
                    THEN (successful_changes::FLOAT / total_changes * 100)
                    ELSE 0
                END) as avg_success_rate
            FROM ai_pipeline.authoring_finalization
            {where_sql}
        """
        try:
            return AuthoringFinalizationRepository.fetch_one(query, tuple(params))
        except Exception as e:
            logger.error(f"Error fetching success rate: {e}")
            return None
