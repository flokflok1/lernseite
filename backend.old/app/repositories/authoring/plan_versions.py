"""
Repository for authoring_plan_versions table (Versioned Curriculum Plans)
"""
from typing import Dict, List, Optional
import logging

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringPlanVersionsRepository(BaseRepository):
    """Repository for managing versioned curriculum plans with approval workflow"""

    @staticmethod
    def create_version(
        session_id: str,
        version_number: int,
        plan_structure: Dict,
        change_summary: Optional[str] = None,
        changes_detail: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """
        Create a new plan version.

        Args:
            session_id: UUID of authoring session
            version_number: Version number
            plan_structure: Complete plan structure
            change_summary: Summary of changes
            changes_detail: Detailed changelog

        Returns:
            version_id if successful
        """
        query = """
            INSERT INTO courses.authoring_plan_versions (
                session_id, version_number, plan_structure,
                change_summary, changes_detail
            ) VALUES (
                %s, %s, %s, %s, %s
            ) RETURNING version_id
        """
        try:
            result = AuthoringPlanVersionsRepository.fetch_one(query, (
                session_id, version_number, plan_structure,
                change_summary, changes_detail or []
            ))
            return result['version_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating plan version: {e}")
            return None

    @staticmethod
    def get_version_by_id(version_id: str) -> Optional[Dict]:
        """Get plan version by ID"""
        query = """
            SELECT
                version_id, session_id, version_number, is_current,
                plan_structure, change_summary, changes_detail,
                approval_status, submitted_for_approval_at,
                approved_by, approved_at, rejection_reason,
                estimated_total_lessons, estimated_total_hours, completeness_score,
                created_at
            FROM courses.authoring_plan_versions
            WHERE version_id = %s
        """
        try:
            return AuthoringPlanVersionsRepository.fetch_one(query, (version_id,))
        except Exception as e:
            logger.error(f"Error fetching plan version: {e}")
            return None

    @staticmethod
    def get_versions_by_session(session_id: str) -> List[Dict]:
        """Get all versions for session"""
        query = """
            SELECT
                version_id, version_number, is_current,
                change_summary, approval_status,
                estimated_total_lessons, estimated_total_hours,
                created_at
            FROM courses.authoring_plan_versions
            WHERE session_id = %s
            ORDER BY version_number DESC
        """
        try:
            return AuthoringPlanVersionsRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching session versions: {e}")
            return []

    @staticmethod
    def get_current_version(session_id: str) -> Optional[Dict]:
        """Get current version for session"""
        query = """
            SELECT
                version_id, version_number, plan_structure,
                approval_status, estimated_total_lessons,
                estimated_total_hours, completeness_score,
                created_at
            FROM courses.authoring_plan_versions
            WHERE session_id = %s AND is_current = TRUE
            LIMIT 1
        """
        try:
            return AuthoringPlanVersionsRepository.fetch_one(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching current version: {e}")
            return None

    @staticmethod
    def set_current_version(
        session_id: str,
        version_id: str
    ) -> bool:
        """
        Set a version as current.

        Args:
            session_id: UUID of authoring session
            version_id: UUID of version to make current

        Returns:
            True if successful
        """
        # First, unset all current versions for session
        query1 = """
            UPDATE courses.authoring_plan_versions
            SET is_current = FALSE
            WHERE session_id = %s
        """
        # Then set new current version
        query2 = """
            UPDATE courses.authoring_plan_versions
            SET is_current = TRUE
            WHERE version_id = %s
        """
        try:
            AuthoringPlanVersionsRepository.execute_update(query1, (session_id,))
            AuthoringPlanVersionsRepository.execute_update(query2, (version_id,))
            return True
        except Exception as e:
            logger.error(f"Error setting current version: {e}")
            return False

    @staticmethod
    def update_approval_status(
        version_id: str,
        approval_status: str,
        approved_by: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> bool:
        """
        Update approval status of version.

        Args:
            version_id: UUID of version
            approval_status: New status
            approved_by: Optional approver user ID
            rejection_reason: Optional rejection reason

        Returns:
            True if successful
        """
        query = """
            UPDATE courses.authoring_plan_versions
            SET approval_status = %s,
                approved_by = %s,
                approved_at = CASE
                    WHEN %s = 'approved' THEN NOW()
                    ELSE NULL
                END,
                rejection_reason = %s,
                submitted_for_approval_at = CASE
                    WHEN %s = 'pending_review' AND submitted_for_approval_at IS NULL THEN NOW()
                    ELSE submitted_for_approval_at
                END
            WHERE version_id = %s
        """
        try:
            AuthoringPlanVersionsRepository.execute_update(query, (
                approval_status, approved_by, approval_status,
                rejection_reason, approval_status, version_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error updating approval status: {e}")
            return False

    @staticmethod
    def update_quality_metrics(
        version_id: str,
        estimated_total_lessons: int,
        estimated_total_hours: float,
        completeness_score: float
    ) -> bool:
        """Update quality metrics for version"""
        query = """
            UPDATE courses.authoring_plan_versions
            SET estimated_total_lessons = %s,
                estimated_total_hours = %s,
                completeness_score = %s
            WHERE version_id = %s
        """
        try:
            AuthoringPlanVersionsRepository.execute_update(query, (
                estimated_total_lessons, estimated_total_hours,
                completeness_score, version_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error updating quality metrics: {e}")
            return False

    @staticmethod
    def get_next_version_number(session_id: str) -> int:
        """Get next version number for session"""
        query = """
            SELECT COALESCE(MAX(version_number), 0) + 1 as next_version
            FROM courses.authoring_plan_versions
            WHERE session_id = %s
        """
        try:
            result = AuthoringPlanVersionsRepository.fetch_one(query, (session_id,))
            return result['next_version'] if result else 1
        except Exception as e:
            logger.error(f"Error getting next version number: {e}")
            return 1
