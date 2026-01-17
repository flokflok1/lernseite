"""
LernsystemX Course Publishing Service

Business logic for course publishing workflow:
- State transitions (draft → submitted → approved/rejected → published)
- Validation of valid transitions
- Moderation feedback management
- Audit trail creation

Publishing Workflow:
- draft: Initial state
- submitted: Submitted for review
- approved: Approved by moderator
- rejected: Rejected, needs revision
- published: Published and visible to community

ISO 27001 compliant - Audit Trail & Compliance
GDPR compliant - State Transition Transparency
"""

from typing import Dict, Optional, Any, Literal
from datetime import datetime
from decimal import Decimal
from flask import current_app

from app.repositories.course_publishing import CoursePublishingRepository
from app.repositories.moderation_audit import ModerationAuditRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ValidationError, NotFoundError, ConflictError

# NOTE: CourseRepository imported lazily (inside methods) to avoid circular imports
# Import chain: repositories.courses -> cache_service -> services -> course_publishing_service -> repositories.courses

PublishingStatus = Literal["draft", "submitted", "approved", "published", "rejected"]
PublishingVisibility = Literal["private", "community", "public"]


class CoursePublishingService:
    """
    Service layer for course publishing workflow.

    Handles state machine transitions with validation and audit logging.
    Ensures compliance with publishing rules and transitions.
    """

    # Valid state transitions
    VALID_TRANSITIONS = {
        "draft": ["submitted"],  # Draft can only be submitted
        "submitted": ["approved", "rejected"],  # Submitted can be approved or rejected
        "approved": ["published", "rejected"],  # Approved can be published or rejected back
        "published": ["draft"],  # Published can go back to draft
        "rejected": ["submitted", "draft"],  # Rejected can be resubmitted or back to draft
    }

    @classmethod
    def submit_for_review(
        cls,
        course_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Submit course for review.

        Transitions: draft → submitted

        Args:
            course_id: Course UUID
            user_id: User ID submitting the course

        Returns:
            Updated publishing record

        Raises:
            NotFoundError: If course or publishing record not found
            ValidationError: If invalid state transition
        """
        # Lazy import to avoid circular dependency
        from app.repositories.courses import CourseRepository

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")

        # Get publishing record
        pub_record = CoursePublishingRepository.get_by_course(course_id)
        if not pub_record:
            raise NotFoundError(f"Publishing record not found for course: {course_id}")

        # Validate state transition
        current_status = pub_record["status"]
        if current_status not in cls.VALID_TRANSITIONS:
            raise ValidationError(
                f"Invalid current status: {current_status}",
                {"current_status": current_status},
            )

        if "submitted" not in cls.VALID_TRANSITIONS.get(current_status, []):
            raise ConflictError(
                f"Cannot submit from {current_status} status. "
                f"Valid transitions: {cls.VALID_TRANSITIONS.get(current_status, [])}",
                {"current_status": current_status},
            )

        # Update status to submitted
        updated = CoursePublishingRepository.update_status(
            course_id=course_id,
            new_status="submitted",
        )

        if not updated:
            raise NotFoundError(f"Failed to update publishing record for course: {course_id}")

        # Create audit trail
        ModerationAuditRepository.create(
            course_id=course_id,
            action="submitted",
            moderator_id=None,  # User submitting is not a moderator
            notes=f"Course submitted by user {user_id}",
            ai_analysis=None,
        )

        # Log action
        AuditService.log_action(
            user_id=user_id,
            action="admin.publishing.submit",
            resource_type="course_publishing",
            resource_id=course_id,
            details={"course_title": course.get("title"), "from_status": current_status},
            severity="info",
        )

        return updated

    @classmethod
    def approve(
        cls,
        course_id: str,
        moderator_id: str,
        moderation_notes: Optional[str] = None,
        moderation_ai_score: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """
        Approve course for publishing.

        Transitions: submitted → approved or approved → approved (update notes)

        Args:
            course_id: Course UUID
            moderator_id: Moderator approving the course
            moderation_notes: Optional moderator feedback
            moderation_ai_score: Optional AI moderation score (0.00-1.00)

        Returns:
            Updated publishing record

        Raises:
            NotFoundError: If course or publishing record not found
            ValidationError: If invalid state transition or AI score
        """
        # Lazy import to avoid circular dependency
        from app.repositories.courses import CourseRepository

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")

        # Get publishing record
        pub_record = CoursePublishingRepository.get_by_course(course_id)
        if not pub_record:
            raise NotFoundError(f"Publishing record not found for course: {course_id}")

        # Validate AI score if provided
        if moderation_ai_score is not None:
            if not (Decimal("0.00") <= moderation_ai_score <= Decimal("1.00")):
                raise ValidationError(
                    "AI moderation score must be between 0.00 and 1.00",
                    {"moderation_ai_score": str(moderation_ai_score)},
                )

        # Validate state transition
        current_status = pub_record["status"]
        if current_status not in ["submitted", "approved"]:
            raise ConflictError(
                f"Cannot approve from {current_status} status. "
                f"Must be submitted or approved.",
                {"current_status": current_status},
            )

        # Update status to approved with moderator feedback
        updated = CoursePublishingRepository.update_status(
            course_id=course_id,
            new_status="approved",
            moderator_id=moderator_id,
            moderation_notes=moderation_notes,
            moderation_ai_score=moderation_ai_score,
        )

        if not updated:
            raise NotFoundError(f"Failed to update publishing record for course: {course_id}")

        # Create audit trail
        ModerationAuditRepository.create(
            course_id=course_id,
            action="approved",
            moderator_id=moderator_id,
            notes=moderation_notes or f"Course approved by moderator {moderator_id}",
            ai_analysis={"ai_score": float(moderation_ai_score)} if moderation_ai_score else None,
        )

        # Log action
        AuditService.log_action(
            user_id=moderator_id,
            action="admin.publishing.approve",
            resource_type="course_publishing",
            resource_id=course_id,
            details={
                "course_title": course.get("title"),
                "from_status": current_status,
                "moderator_id": moderator_id,
                "ai_score": str(moderation_ai_score) if moderation_ai_score else None,
            },
            severity="info",
        )

        return updated

    @classmethod
    def reject(
        cls,
        course_id: str,
        moderator_id: str,
        moderation_notes: str,
    ) -> Dict[str, Any]:
        """
        Reject course.

        Transitions: submitted → rejected or approved → rejected

        Args:
            course_id: Course UUID
            moderator_id: Moderator rejecting the course
            moderation_notes: Required rejection reason/feedback

        Returns:
            Updated publishing record

        Raises:
            NotFoundError: If course or publishing record not found
            ValidationError: If invalid state transition or missing notes
        """
        # Lazy import to avoid circular dependency
        from app.repositories.courses import CourseRepository

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")

        # Validate moderation notes
        if not moderation_notes or not moderation_notes.strip():
            raise ValidationError(
                "Moderation notes are required for rejection",
                {"moderation_notes": "required"},
            )

        # Get publishing record
        pub_record = CoursePublishingRepository.get_by_course(course_id)
        if not pub_record:
            raise NotFoundError(f"Publishing record not found for course: {course_id}")

        # Validate state transition
        current_status = pub_record["status"]
        if current_status not in ["submitted", "approved"]:
            raise ConflictError(
                f"Cannot reject from {current_status} status. "
                f"Must be submitted or approved.",
                {"current_status": current_status},
            )

        # Update status to rejected
        updated = CoursePublishingRepository.update_status(
            course_id=course_id,
            new_status="rejected",
            moderator_id=moderator_id,
            moderation_notes=moderation_notes,
        )

        if not updated:
            raise NotFoundError(f"Failed to update publishing record for course: {course_id}")

        # Create audit trail
        ModerationAuditRepository.create(
            course_id=course_id,
            action="rejected",
            moderator_id=moderator_id,
            notes=moderation_notes,
            ai_analysis=None,
        )

        # Log action
        AuditService.log_action(
            user_id=moderator_id,
            action="admin.publishing.reject",
            resource_type="course_publishing",
            resource_id=course_id,
            details={
                "course_title": course.get("title"),
                "from_status": current_status,
                "moderator_id": moderator_id,
                "rejection_reason": moderation_notes[:100],  # First 100 chars for log
            },
            severity="warning",
        )

        return updated

    @classmethod
    def publish(
        cls,
        course_id: str,
        moderator_id: str,
        visibility: PublishingVisibility = "community",
    ) -> Dict[str, Any]:
        """
        Publish course.

        Transitions: approved → published

        Args:
            course_id: Course UUID
            moderator_id: Moderator publishing the course
            visibility: Initial visibility level (default: community)

        Returns:
            Updated publishing record

        Raises:
            NotFoundError: If course or publishing record not found
            ValidationError: If invalid state transition or visibility
        """
        # Lazy import to avoid circular dependency
        from app.repositories.courses import CourseRepository

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")

        # Get publishing record
        pub_record = CoursePublishingRepository.get_by_course(course_id)
        if not pub_record:
            raise NotFoundError(f"Publishing record not found for course: {course_id}")

        # Validate state transition
        current_status = pub_record["status"]
        if current_status != "approved":
            raise ConflictError(
                f"Cannot publish from {current_status} status. "
                f"Course must be approved first.",
                {"current_status": current_status},
            )

        # Update status to published with visibility
        updated = CoursePublishingRepository.update_status(
            course_id=course_id,
            new_status="published",
            moderator_id=moderator_id,
        )

        if not updated:
            raise NotFoundError(f"Failed to update publishing record for course: {course_id}")

        # Update visibility if not already set
        if pub_record.get("visibility") != visibility:
            updated = CoursePublishingRepository.update_visibility(course_id, visibility)

        # Create audit trail
        ModerationAuditRepository.create(
            course_id=course_id,
            action="approved",
            moderator_id=moderator_id,
            notes=f"Course published with {visibility} visibility",
            ai_analysis=None,
        )

        # Log action
        AuditService.log_action(
            user_id=moderator_id,
            action="admin.publishing.publish",
            resource_type="course_publishing",
            resource_id=course_id,
            details={
                "course_title": course.get("title"),
                "from_status": current_status,
                "visibility": visibility,
                "moderator_id": moderator_id,
            },
            severity="info",
        )

        return updated

    @classmethod
    def update_visibility(
        cls,
        course_id: str,
        new_visibility: PublishingVisibility,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Update course visibility.

        Args:
            course_id: Course UUID
            new_visibility: New visibility level (private, community, public)
            user_id: User making the change

        Returns:
            Updated publishing record

        Raises:
            NotFoundError: If course or publishing record not found
            ValidationError: If invalid visibility value
        """
        # Lazy import to avoid circular dependency
        from app.repositories.courses import CourseRepository

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")

        # Get publishing record
        pub_record = CoursePublishingRepository.get_by_course(course_id)
        if not pub_record:
            raise NotFoundError(f"Publishing record not found for course: {course_id}")

        # Validate visibility value
        valid_visibilities = ["private", "community", "public"]
        if new_visibility not in valid_visibilities:
            raise ValidationError(
                f"Invalid visibility: {new_visibility}. "
                f"Must be one of: {', '.join(valid_visibilities)}",
                {"new_visibility": new_visibility},
            )

        # Update visibility
        updated = CoursePublishingRepository.update_visibility(course_id, new_visibility)

        if not updated:
            raise NotFoundError(f"Failed to update visibility for course: {course_id}")

        # Create audit trail
        old_visibility = pub_record.get("visibility")
        ModerationAuditRepository.create(
            course_id=course_id,
            action="visibility_changed",
            moderator_id=user_id,
            notes=f"Visibility changed from {old_visibility} to {new_visibility}",
            ai_analysis=None,
        )

        # Log action
        AuditService.log_action(
            user_id=user_id,
            action="admin.publishing.update_visibility",
            resource_type="course_publishing",
            resource_id=course_id,
            details={
                "course_title": course.get("title"),
                "old_visibility": old_visibility,
                "new_visibility": new_visibility,
            },
            severity="info",
        )

        return updated

    @classmethod
    def get_submission_queue(
        cls,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Dict[str, Any]], int]:
        """
        Get courses waiting for review.

        Args:
            limit: Max results
            offset: Pagination offset

        Returns:
            Tuple of (publishing records, total count)
        """
        records = CoursePublishingRepository.list_submitted(limit=limit, offset=offset)
        total = CoursePublishingRepository.count_by_status("submitted")
        return records, total

    @classmethod
    def get_published_courses(
        cls,
        visibility: PublishingVisibility = "community",
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Dict[str, Any]], int]:
        """
        Get published courses by visibility.

        Args:
            visibility: Filter by visibility level
            limit: Max results
            offset: Pagination offset

        Returns:
            Tuple of (publishing records, total count)
        """
        records = CoursePublishingRepository.list_published(
            visibility=visibility, limit=limit, offset=offset
        )
        total = CoursePublishingRepository.count_by_status("published")
        return records, total

    @classmethod
    def validate_transition(
        cls,
        from_status: PublishingStatus,
        to_status: PublishingStatus,
    ) -> bool:
        """
        Check if a state transition is valid.

        Args:
            from_status: Current status
            to_status: Desired status

        Returns:
            True if transition is valid, False otherwise
        """
        valid_targets = cls.VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_targets
