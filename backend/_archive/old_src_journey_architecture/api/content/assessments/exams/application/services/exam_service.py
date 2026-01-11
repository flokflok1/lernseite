"""
Exam Service (Application Layer)

Business logic for exam operations.
ALL data loaded dynamically from database - NO hardcoded values.

Uses Repository Pattern for database access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from src.api.content.assessments.exams.domain.entities.exam import Exam
from src.api.content.assessments.exams.infrastructure.repositories.exam_repository import ExamRepository
from src.api.content.courses.core.infrastructure.repositories.course_repository import CourseRepository
from src.api.content.courses.chapters.infrastructure.repositories.chapter_repository import ChapterRepository
from src.core.events import EventBus, EventType, DomainEvent


class ExamService:
    """
    Exam service for business logic.

    ALL configurations and values loaded from database dynamically.
    NO hardcoded exam types or configurations.
    """

    @staticmethod
    def get_exam_by_id(exam_id: str) -> Optional[Exam]:
        """
        Get exam by ID.

        Args:
            exam_id: Exam UUID

        Returns:
            Exam entity or None
        """
        return ExamRepository.find_by_id(exam_id)

    @staticmethod
    def list_exams(
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        published_only: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Exam]:
        """
        List exams with dynamic filters.

        Args:
            course_id: Optional course filter
            chapter_id: Optional chapter filter
            published_only: Only published exams
            filters: Dynamic filters (exam_type, created_by)
            limit: Result limit
            offset: Result offset

        Returns:
            List of exams
        """
        if course_id:
            return ExamRepository.find_by_course_id(
                course_id=course_id,
                published_only=published_only
            )

        if chapter_id:
            return ExamRepository.find_by_chapter_id(
                chapter_id=chapter_id,
                published_only=published_only
            )

        # General listing with filters
        exam_type = filters.get('exam_type') if filters else None
        created_by = filters.get('created_by') if filters else None
        published = True if published_only else filters.get('published') if filters else None

        return ExamRepository.find_all(
            course_id=course_id,
            chapter_id=chapter_id,
            exam_type=exam_type,
            created_by=created_by,
            published=published,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def create_exam(
        course_id: str,
        exam_type: str,
        title: str,
        duration_minutes: int,
        passing_score: Decimal,
        user_id: str,
        user_role: str,
        chapter_id: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        total_points: Optional[Decimal] = None,
        randomize_questions: bool = False,
        show_results_immediately: bool = True,
        allow_review: bool = True,
        max_attempts: Optional[int] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Exam:
        """
        Create new exam.

        Args:
            course_id: Parent course UUID
            exam_type: Type of exam (from DB)
            title: Exam title
            duration_minutes: Time limit
            passing_score: Minimum score to pass (percentage)
            user_id: User creating the exam
            user_role: User role
            chapter_id: Optional chapter UUID
            description: Optional description
            instructions: Optional instructions
            total_points: Optional total points
            randomize_questions: Randomize question order
            show_results_immediately: Show results after submission
            allow_review: Allow reviewing answers
            max_attempts: Maximum attempts (None = unlimited)
            settings: Optional JSONB settings

        Returns:
            Created exam entity

        Raises:
            ValueError: If validation fails
            PermissionError: If user cannot edit course
        """
        # Verify course exists and user can edit
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")

        if not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit course {course_id}")

        # Verify chapter if provided
        if chapter_id:
            chapter = ChapterRepository.find_by_id(chapter_id)
            if not chapter or chapter.course_id != course_id:
                raise ValueError(f"Chapter {chapter_id} not found or not in course {course_id}")

        # Create exam entity
        import uuid
        exam = Exam(
            exam_id=str(uuid.uuid4()),
            course_id=course_id,
            chapter_id=chapter_id,
            created_by=user_id,
            exam_type=exam_type,
            title=title,
            description=description,
            instructions=instructions,
            duration_minutes=duration_minutes,
            passing_score=passing_score,
            total_points=total_points,
            randomize_questions=randomize_questions,
            show_results_immediately=show_results_immediately,
            allow_review=allow_review,
            max_attempts=max_attempts,
            settings=settings or {},
            published=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to database
        created_exam = ExamRepository.create(exam)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.EXAM_CREATED,
            aggregate_id=created_exam.exam_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': created_exam.title,
                'course_id': created_exam.course_id,
                'exam_type': created_exam.exam_type
            }
        )
        EventBus.publish(event)

        return created_exam

    @staticmethod
    def update_exam(
        exam_id: str,
        user_id: str,
        user_role: str,
        updates: Dict[str, Any]
    ) -> Exam:
        """
        Update exam with access control.

        Args:
            exam_id: Exam UUID
            user_id: User ID making the update
            user_role: User role
            updates: Dictionary of fields to update

        Returns:
            Updated exam entity

        Raises:
            PermissionError: If user cannot edit exam
            ValueError: If exam not found or validation fails
        """
        # Get existing exam
        exam = ExamRepository.find_by_id(exam_id)
        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        # Check edit permission on course
        course = CourseRepository.find_by_id(exam.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit exam {exam_id}")

        # Update metadata
        exam.update_metadata(**updates)

        # Save to database
        updated_exam = ExamRepository.update(exam)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.EXAM_UPDATED,
            aggregate_id=updated_exam.exam_id,
            occurred_at=datetime.utcnow(),
            data={
                'updated_fields': list(updates.keys()),
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return updated_exam

    @staticmethod
    def update_exam_settings(
        exam_id: str,
        settings: Dict[str, Any],
        user_id: str,
        user_role: str
    ) -> Exam:
        """Update exam settings (JSONB)."""
        exam = ExamRepository.find_by_id(exam_id)
        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        course = CourseRepository.find_by_id(exam.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit exam {exam_id}")

        exam.update_settings(settings)
        return ExamRepository.update(exam)

    @staticmethod
    def publish_exam(exam_id: str, user_id: str, user_role: str) -> Exam:
        """
        Publish exam.

        Args:
            exam_id: Exam UUID
            user_id: User ID publishing the exam
            user_role: User role

        Returns:
            Published exam entity
        """
        exam = ExamRepository.find_by_id(exam_id)
        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        course = CourseRepository.find_by_id(exam.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to publish exam {exam_id}")

        exam.publish()
        published_exam = ExamRepository.update(exam)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.EXAM_PUBLISHED,
            aggregate_id=published_exam.exam_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': published_exam.title,
                'course_id': published_exam.course_id,
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return published_exam

    @staticmethod
    def unpublish_exam(exam_id: str, user_id: str, user_role: str) -> Exam:
        """Unpublish exam."""
        exam = ExamRepository.find_by_id(exam_id)
        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        course = CourseRepository.find_by_id(exam.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to unpublish exam {exam_id}")

        exam.unpublish()
        return ExamRepository.update(exam)

    @staticmethod
    def delete_exam(exam_id: str, user_id: str, user_role: str) -> bool:
        """
        Delete exam (hard delete - cascade to questions and attempts).

        Args:
            exam_id: Exam UUID
            user_id: User ID deleting the exam
            user_role: User role

        Returns:
            True if deleted
        """
        exam = ExamRepository.find_by_id(exam_id)
        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        course = CourseRepository.find_by_id(exam.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to delete exam {exam_id}")

        deleted = ExamRepository.delete(exam_id)

        if deleted:
            event = DomainEvent(
                event_type=EventType.EXAM_DELETED,
                aggregate_id=exam_id,
                occurred_at=datetime.utcnow(),
                data={
                    'title': exam.title,
                    'course_id': exam.course_id,
                    'user_id': user_id
                }
            )
            EventBus.publish(event)

        return deleted

    @staticmethod
    def get_available_exam_types() -> List[str]:
        """
        Get available exam types from database.

        Returns:
            List of valid exam types (loaded from DB constraint)
        """
        return ExamRepository.get_available_exam_types()

    @staticmethod
    def count_exams(
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        exam_type: Optional[str] = None,
        published: Optional[bool] = None
    ) -> int:
        """
        Count exams with filters.

        Args:
            course_id: Optional course filter
            chapter_id: Optional chapter filter
            exam_type: Optional exam type filter
            published: Optional published filter

        Returns:
            Exam count
        """
        return ExamRepository.count(
            course_id=course_id,
            chapter_id=chapter_id,
            exam_type=exam_type,
            published=published
        )
