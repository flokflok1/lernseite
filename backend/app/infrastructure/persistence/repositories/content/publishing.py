"""
Course Publishing Repository

Repository for managing course publishing workflow and status.

Publishing Workflow:
- draft: Course created, not yet submitted
- submitted: User submitted for community review
- approved: Moderator approved for publishing
- rejected: Moderator rejected (needs revision)
- published: Course is published and available

Visibility Levels:
- private: Only owner can see
- community: Visible in community (requires published status)
- public: Public listing (future feature)

Phase: AI Editor Implementation - Publishing System
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from decimal import Decimal
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository

logger = logging.getLogger(__name__)

PublishingStatus = Literal["draft", "submitted", "approved", "published", "rejected"]
PublishingVisibility = Literal["private", "community", "public"]


class CoursePublishingRepository(BaseRepository):
    """Repository for course publishing operations."""

    @staticmethod
    def get_by_course(course_id: str) -> Optional[Dict[str, Any]]:
        """
        Get publishing record for a course.

        Args:
            course_id: UUID of the course

        Returns:
            Publishing record or None if not found
        """
        query = """
            SELECT
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
            FROM courses.course_publishing
            WHERE course_id = %s
        """
        return CoursePublishingRepository.fetch_one(query, (course_id,))

    @staticmethod
    def get_by_id(publish_id: str) -> Optional[Dict[str, Any]]:
        """
        Get publishing record by ID.

        Args:
            publish_id: UUID of the publishing record

        Returns:
            Publishing record or None if not found
        """
        query = """
            SELECT
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
            FROM courses.course_publishing
            WHERE publish_id = %s
        """
        return CoursePublishingRepository.fetch_one(query, (publish_id,))

    @staticmethod
    def create(
        course_id: str,
        status: PublishingStatus = "draft",
        visibility: PublishingVisibility = "private"
    ) -> Dict[str, Any]:
        """
        Create publishing record for course.

        Args:
            course_id: UUID of the course
            status: Initial status (default: draft)
            visibility: Initial visibility (default: private)

        Returns:
            Created publishing record

        Note:
            One record per course (enforced by UNIQUE constraint in DB)
        """
        query = """
            INSERT INTO courses.course_publishing
            (course_id, status, visibility, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            RETURNING
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
        """
        return CoursePublishingRepository.fetch_one(
            query,
            (course_id, status, visibility)
        )

    @staticmethod
    def update_status(
        course_id: str,
        new_status: PublishingStatus,
        moderator_id: Optional[str] = None,
        moderation_notes: Optional[str] = None,
        moderation_ai_score: Optional[Decimal] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update publishing status for course.

        Args:
            course_id: UUID of the course
            new_status: New status
            moderator_id: ID of moderator making change (optional)
            moderation_notes: Feedback/notes (optional)
            moderation_ai_score: AI score (0.00-1.00, optional)

        Returns:
            Updated publishing record or None if not found
        """
        updates = ["status = %s", "updated_at = NOW()"]
        params = [new_status]

        # Set submission_date on first submission
        if new_status == "submitted":
            updates.append("submission_date = NOW()")

        # Set published_date when published
        if new_status == "published":
            updates.append("published_date = NOW()")

        if moderator_id is not None:
            updates.append("moderator_id = %s")
            params.append(moderator_id)

        if moderation_notes is not None:
            updates.append("moderation_notes = %s")
            params.append(moderation_notes)

        if moderation_ai_score is not None:
            updates.append("moderation_ai_score = %s")
            params.append(moderation_ai_score)

        params.append(course_id)
        set_clause = ", ".join(updates)

        query = f"""
            UPDATE courses.course_publishing
            SET {set_clause}
            WHERE course_id = %s
            RETURNING
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
        """
        return CoursePublishingRepository.fetch_one(query, tuple(params))

    @staticmethod
    def update_visibility(
        course_id: str,
        new_visibility: PublishingVisibility
    ) -> Optional[Dict[str, Any]]:
        """
        Update visibility for course.

        Args:
            course_id: UUID of the course
            new_visibility: New visibility level

        Returns:
            Updated publishing record or None if not found
        """
        query = """
            UPDATE courses.course_publishing
            SET visibility = %s, updated_at = NOW()
            WHERE course_id = %s
            RETURNING
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
        """
        return CoursePublishingRepository.fetch_one(
            query,
            (new_visibility, course_id)
        )

    @staticmethod
    def list_submitted(
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List courses submitted for review.

        Args:
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of submitted publishing records
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
            FROM courses.course_publishing
            WHERE status = 'submitted'
            ORDER BY submission_date ASC
            LIMIT %s OFFSET %s
        """
        return CoursePublishingRepository.fetch_all(query, (limit, offset))

    @staticmethod
    def list_published(
        visibility: PublishingVisibility = "community",
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List published courses by visibility.

        Args:
            visibility: Filter by visibility (default: community)
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of published publishing records
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
            FROM courses.course_publishing
            WHERE status = 'published' AND visibility = %s
            ORDER BY published_date DESC
            LIMIT %s OFFSET %s
        """
        return CoursePublishingRepository.fetch_all(
            query,
            (visibility, limit, offset)
        )

    @staticmethod
    def list_by_status(
        status: PublishingStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List courses by publishing status.

        Args:
            status: Filter by status
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of publishing records with given status
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
            FROM courses.course_publishing
            WHERE status = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return CoursePublishingRepository.fetch_all(
            query,
            (status, limit, offset)
        )

    @staticmethod
    def list_by_moderator(
        moderator_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List courses moderated by a specific moderator.

        Args:
            moderator_id: UUID of moderator
            limit: Max results (max 1000)
            offset: Skip N records

        Returns:
            List of publishing records moderated by this moderator
        """
        limit = min(limit, 1000)
        query = """
            SELECT
                publish_id, course_id, status, visibility,
                submission_date, moderator_id, moderation_notes,
                moderation_ai_score, published_date,
                created_at, updated_at
            FROM courses.course_publishing
            WHERE moderator_id = %s
            ORDER BY updated_at DESC
            LIMIT %s OFFSET %s
        """
        return CoursePublishingRepository.fetch_all(
            query,
            (moderator_id, limit, offset)
        )

    @staticmethod
    def count_by_status(status: PublishingStatus) -> int:
        """
        Count courses with given status.

        Args:
            status: Publishing status to filter by

        Returns:
            Count of courses with this status
        """
        query = """
            SELECT COUNT(*) as count
            FROM courses.course_publishing
            WHERE status = %s
        """
        result = CoursePublishingRepository.fetch_one(query, (status,))
        return result['count'] if result else 0

    @staticmethod
    def exists_for_course(course_id: str) -> bool:
        """
        Check if publishing record exists for course.

        Args:
            course_id: UUID of the course

        Returns:
            True if exists, False otherwise
        """
        query = """
            SELECT 1 FROM courses.course_publishing
            WHERE course_id = %s
            LIMIT 1
        """
        return CoursePublishingRepository.fetch_one(query, (course_id,)) is not None
