"""
Moderation Audit Repository

Repository for managing moderation audit trail records.

Immutable audit trail:
- Create: Record audit events
- Read: Query audit history
- No Update/Delete: Audit records are permanent for compliance

Actions Tracked:
- submitted: Course submitted for review
- reviewed: Moderator reviewed the course
- approved: Approved for publishing
- rejected: Rejected (needs revision)
- revision_requested: Requested changes
- ai_analyzed: KI analysis completed

Phase: AI Editor Implementation - KI Moderation
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
import logging
import json

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

ModerationAction = Literal[
    "submitted",
    "reviewed",
    "approved",
    "rejected",
    "revision_requested",
    "ai_analyzed"
]


class ModerationAuditRepository(BaseRepository):
    """Repository for moderation audit trail operations (IMMUTABLE)."""

    @staticmethod
    def create(
        course_id: str,
        action: ModerationAction,
        moderator_id: Optional[str] = None,
        notes: Optional[str] = None,
        ai_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create audit trail entry (IMMUTABLE - log only).

        Args:
            course_id: UUID of the course being audited
            action: Action taken (submitted, reviewed, approved, rejected, etc.)
            moderator_id: ID of human moderator (optional, null for AI actions)
            notes: Notes/feedback (optional)
            ai_analysis: KI analysis results as dict (optional, for ai_analyzed action)

        Returns:
            Created audit record
        """
        query = """
            INSERT INTO courses.moderation_audit
            (course_id, moderator_id, action, notes, ai_analysis, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING
                audit_id, course_id, moderator_id, action, notes,
                ai_analysis, created_at
        """

        # Convert ai_analysis dict to JSON if provided
        ai_analysis_json = json.dumps(ai_analysis) if ai_analysis else None

        return ModerationAuditRepository.fetch_one(
            query,
            (course_id, moderator_id, action, notes, ai_analysis_json)
        )

    @staticmethod
    def get_by_id(audit_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audit record by ID.

        Args:
            audit_id: UUID of the audit record

        Returns:
            Audit record or None if not found
        """
        query = """
            SELECT
                audit_id, course_id, moderator_id, action, notes,
                ai_analysis, created_at
            FROM courses.moderation_audit
            WHERE audit_id = %s
        """
        return ModerationAuditRepository.fetch_one(query, (audit_id,))

    @staticmethod
    def list_by_course(
        course_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all audit entries for a course.

        Args:
            course_id: UUID of the course
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of audit records, ordered by created_at DESC
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                audit_id, course_id, moderator_id, action, notes,
                ai_analysis, created_at
            FROM courses.moderation_audit
            WHERE course_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return ModerationAuditRepository.fetch_all(
            query,
            (course_id, limit, offset)
        )

    @staticmethod
    def list_by_action(
        action: ModerationAction,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List audit entries by action type.

        Args:
            action: Action type to filter by
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of audit records with given action
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                audit_id, course_id, moderator_id, action, notes,
                ai_analysis, created_at
            FROM courses.moderation_audit
            WHERE action = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return ModerationAuditRepository.fetch_all(
            query,
            (action, limit, offset)
        )

    @staticmethod
    def list_by_moderator(
        moderator_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List audit entries created by a specific moderator.

        Args:
            moderator_id: UUID of the moderator
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of audit records created by this moderator
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                audit_id, course_id, moderator_id, action, notes,
                ai_analysis, created_at
            FROM courses.moderation_audit
            WHERE moderator_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return ModerationAuditRepository.fetch_all(
            query,
            (moderator_id, limit, offset)
        )

    @staticmethod
    def list_ai_analyses(
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all AI analysis audit entries (where ai_analysis is not null).

        Args:
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of audit records with AI analysis
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                audit_id, course_id, moderator_id, action, notes,
                ai_analysis, created_at
            FROM courses.moderation_audit
            WHERE ai_analysis IS NOT NULL AND action = 'ai_analyzed'
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return ModerationAuditRepository.fetch_all(query, (limit, offset))

    @staticmethod
    def list_by_date_range(
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List audit entries within date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of audit records in date range
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                audit_id, course_id, moderator_id, action, notes,
                ai_analysis, created_at
            FROM courses.moderation_audit
            WHERE created_at >= %s AND created_at <= %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return ModerationAuditRepository.fetch_all(
            query,
            (start_date, end_date, limit, offset)
        )

    @staticmethod
    def list_by_course_and_action(
        course_id: str,
        action: ModerationAction,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List audit entries for course filtered by action.

        Args:
            course_id: UUID of the course
            action: Action type to filter by
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of audit records matching both filters
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                audit_id, course_id, moderator_id, action, notes,
                ai_analysis, created_at
            FROM courses.moderation_audit
            WHERE course_id = %s AND action = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return ModerationAuditRepository.fetch_all(
            query,
            (course_id, action, limit, offset)
        )

    @staticmethod
    def count_by_course(course_id: str) -> int:
        """
        Count audit entries for a course.

        Args:
            course_id: UUID of the course

        Returns:
            Number of audit entries for this course
        """
        query = """
            SELECT COUNT(*) as count
            FROM courses.moderation_audit
            WHERE course_id = %s
        """
        result = ModerationAuditRepository.fetch_one(query, (course_id,))
        return result['count'] if result else 0

    @staticmethod
    def count_by_action(action: ModerationAction) -> int:
        """
        Count audit entries by action type.

        Args:
            action: Action type to count

        Returns:
            Number of entries with this action
        """
        query = """
            SELECT COUNT(*) as count
            FROM courses.moderation_audit
            WHERE action = %s
        """
        result = ModerationAuditRepository.fetch_one(query, (action,))
        return result['count'] if result else 0

    @staticmethod
    def count_by_moderator(moderator_id: str) -> int:
        """
        Count audit entries created by a moderator.

        Args:
            moderator_id: UUID of the moderator

        Returns:
            Number of entries created by this moderator
        """
        query = """
            SELECT COUNT(*) as count
            FROM courses.moderation_audit
            WHERE moderator_id = %s
        """
        result = ModerationAuditRepository.fetch_one(query, (moderator_id,))
        return result['count'] if result else 0

    @staticmethod
    def get_latest_action(
        course_id: str,
        action: Optional[ModerationAction] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get most recent audit entry for course (optionally filtered by action).

        Args:
            course_id: UUID of the course
            action: Optional action to filter by

        Returns:
            Latest audit record or None
        """
        if action:
            query = """
                SELECT
                    audit_id, course_id, moderator_id, action, notes,
                    ai_analysis, created_at
                FROM courses.moderation_audit
                WHERE course_id = %s AND action = %s
                ORDER BY created_at DESC
                LIMIT 1
            """
            return ModerationAuditRepository.fetch_one(query, (course_id, action))
        else:
            query = """
                SELECT
                    audit_id, course_id, moderator_id, action, notes,
                    ai_analysis, created_at
                FROM courses.moderation_audit
                WHERE course_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """
            return ModerationAuditRepository.fetch_one(query, (course_id,))
