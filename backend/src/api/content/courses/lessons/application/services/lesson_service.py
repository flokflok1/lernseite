"""
Lesson Service (Application Layer)

Business logic for lesson operations.
ALL data loaded dynamically from database - NO hardcoded values.

Uses Repository Pattern for database access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.api.content.courses.lessons.domain.entities.lesson import Lesson
from src.api.content.courses.lessons.infrastructure.repositories.lesson_repository import LessonRepository
from src.api.content.courses.chapters.infrastructure.repositories.chapter_repository import ChapterRepository
from src.api.content.courses.core.infrastructure.repositories.course_repository import CourseRepository
from src.core.events import EventBus, EventType, DomainEvent


class LessonService:
    """
    Lesson service for business logic.

    ALL configurations and values loaded from database dynamically.
    NO hardcoded lesson lists or lesson types.
    """

    @staticmethod
    def get_lesson_by_id(lesson_id: str) -> Optional[Lesson]:
        """
        Get lesson by ID.

        Args:
            lesson_id: Lesson UUID

        Returns:
            Lesson entity or None
        """
        return LessonRepository.find_by_id(lesson_id)

    @staticmethod
    def list_lessons(
        chapter_id: Optional[str] = None,
        published_only: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Lesson]:
        """
        List lessons with dynamic filters.

        Args:
            chapter_id: Optional chapter filter
            published_only: Only published lessons
            filters: Dynamic filters (lesson_type, free_preview)
            limit: Result limit
            offset: Result offset

        Returns:
            List of lessons
        """
        if chapter_id:
            # Optimized query for single chapter
            return LessonRepository.find_by_chapter_id(
                chapter_id=chapter_id,
                published_only=published_only
            )

        # General listing with filters
        lesson_type = filters.get('lesson_type') if filters else None
        published = True if published_only else filters.get('published') if filters else None
        free_preview = filters.get('free_preview') if filters else None

        return LessonRepository.find_all(
            chapter_id=chapter_id,
            lesson_type=lesson_type,
            published=published,
            free_preview=free_preview,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def list_chapter_lessons(chapter_id: str, published_only: bool = False) -> List[Lesson]:
        """
        List lessons for a specific chapter.

        Args:
            chapter_id: Chapter UUID
            published_only: Only published lessons

        Returns:
            List of lessons ordered by order_index
        """
        return LessonRepository.find_by_chapter_id(
            chapter_id=chapter_id,
            published_only=published_only
        )

    @staticmethod
    def create_lesson(
        chapter_id: str,
        title: str,
        lesson_type: str,
        user_id: str,
        user_role: str,
        slug: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        duration_minutes: Optional[int] = None,
        order_index: Optional[int] = None,
        free_preview: bool = False
    ) -> Lesson:
        """
        Create new lesson.

        Args:
            chapter_id: Parent chapter UUID
            title: Lesson title
            lesson_type: Type of lesson (from DB)
            user_id: User creating the lesson
            user_role: User role
            slug: Optional URL slug
            content: Optional JSONB content
            duration_minutes: Optional duration
            order_index: Optional order (auto-calculated if None)
            free_preview: Free preview flag

        Returns:
            Created lesson entity

        Raises:
            ValueError: If validation fails
            PermissionError: If user cannot edit chapter
        """
        # Verify chapter exists and get parent course
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course:
            raise ValueError(f"Course {chapter.course_id} not found")

        # Check edit permission on course
        if not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit course {course.course_id}")

        # Get next order index if not provided
        if order_index is None:
            order_index = LessonRepository.get_next_order_index(chapter_id)

        # Create lesson entity
        import uuid
        lesson = Lesson(
            lesson_id=str(uuid.uuid4()),
            chapter_id=chapter_id,
            title=title,
            slug=slug,
            lesson_type=lesson_type,
            content=content or {},
            duration_minutes=duration_minutes,
            order_index=order_index,
            published=False,
            free_preview=free_preview,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to database
        created_lesson = LessonRepository.create(lesson)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.LESSON_CREATED,
            aggregate_id=created_lesson.lesson_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': created_lesson.title,
                'chapter_id': created_lesson.chapter_id,
                'lesson_type': created_lesson.lesson_type,
                'order_index': created_lesson.order_index
            }
        )
        EventBus.publish(event)

        return created_lesson

    @staticmethod
    def update_lesson(
        lesson_id: str,
        user_id: str,
        user_role: str,
        updates: Dict[str, Any]
    ) -> Lesson:
        """
        Update lesson with access control.

        Args:
            lesson_id: Lesson UUID
            user_id: User ID making the update
            user_role: User role
            updates: Dictionary of fields to update

        Returns:
            Updated lesson entity

        Raises:
            PermissionError: If user cannot edit lesson
            ValueError: If lesson not found or validation fails
        """
        # Get existing lesson
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        # Get chapter and course for permission check
        chapter = ChapterRepository.find_by_id(lesson.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {lesson.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit lesson {lesson_id}")

        # Update metadata
        lesson.update_metadata(**updates)

        # Save to database
        updated_lesson = LessonRepository.update(lesson)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.LESSON_UPDATED,
            aggregate_id=updated_lesson.lesson_id,
            occurred_at=datetime.utcnow(),
            data={
                'updated_fields': list(updates.keys()),
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return updated_lesson

    @staticmethod
    def update_lesson_content(
        lesson_id: str,
        content: Dict[str, Any],
        user_id: str,
        user_role: str
    ) -> Lesson:
        """
        Update lesson content.

        Args:
            lesson_id: Lesson UUID
            content: New JSONB content
            user_id: User ID making the update
            user_role: User role

        Returns:
            Updated lesson entity
        """
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        chapter = ChapterRepository.find_by_id(lesson.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {lesson.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit lesson {lesson_id}")

        lesson.update_content(content)
        return LessonRepository.update(lesson)

    @staticmethod
    def publish_lesson(lesson_id: str, user_id: str, user_role: str) -> Lesson:
        """
        Publish lesson.

        Args:
            lesson_id: Lesson UUID
            user_id: User ID publishing the lesson
            user_role: User role

        Returns:
            Published lesson entity

        Raises:
            PermissionError: If user cannot edit lesson
            ValueError: If lesson not found
        """
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        chapter = ChapterRepository.find_by_id(lesson.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {lesson.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to publish lesson {lesson_id}")

        lesson.publish()
        published_lesson = LessonRepository.update(lesson)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.LESSON_PUBLISHED,
            aggregate_id=published_lesson.lesson_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': published_lesson.title,
                'chapter_id': published_lesson.chapter_id,
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return published_lesson

    @staticmethod
    def unpublish_lesson(lesson_id: str, user_id: str, user_role: str) -> Lesson:
        """Unpublish lesson."""
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        chapter = ChapterRepository.find_by_id(lesson.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {lesson.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to unpublish lesson {lesson_id}")

        lesson.unpublish()
        return LessonRepository.update(lesson)

    @staticmethod
    def delete_lesson(lesson_id: str, user_id: str, user_role: str) -> bool:
        """
        Delete lesson (hard delete - cascade to completions).

        Args:
            lesson_id: Lesson UUID
            user_id: User ID deleting the lesson
            user_role: User role

        Returns:
            True if deleted
        """
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        chapter = ChapterRepository.find_by_id(lesson.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {lesson.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to delete lesson {lesson_id}")

        deleted = LessonRepository.delete(lesson_id)

        if deleted:
            event = DomainEvent(
                event_type=EventType.LESSON_DELETED,
                aggregate_id=lesson_id,
                occurred_at=datetime.utcnow(),
                data={
                    'title': lesson.title,
                    'chapter_id': lesson.chapter_id,
                    'user_id': user_id
                }
            )
            EventBus.publish(event)

        return deleted

    @staticmethod
    def reorder_lessons(
        chapter_id: str,
        lesson_order: List[Dict[str, Any]],
        user_id: str,
        user_role: str
    ) -> bool:
        """
        Reorder lessons within a chapter.

        Args:
            chapter_id: Chapter UUID
            lesson_order: List of dicts with lesson_id and order_index
            user_id: User ID reordering lessons
            user_role: User role

        Returns:
            True if successful
        """
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to reorder lessons in chapter {chapter_id}")

        order_tuples = [
            (item['lesson_id'], item['order_index'])
            for item in lesson_order
        ]

        return LessonRepository.reorder_lessons(chapter_id, order_tuples)

    @staticmethod
    def set_free_preview(
        lesson_id: str,
        is_free: bool,
        user_id: str,
        user_role: str
    ) -> Lesson:
        """Set lesson free preview status."""
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        chapter = ChapterRepository.find_by_id(lesson.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {lesson.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to modify lesson {lesson_id}")

        lesson.set_free_preview(is_free)
        return LessonRepository.update(lesson)

    @staticmethod
    def get_available_lesson_types() -> List[str]:
        """
        Get available lesson types from database.

        Returns:
            List of valid lesson types (loaded from DB constraint)
        """
        return LessonRepository.get_available_lesson_types()

    @staticmethod
    def count_lessons(
        chapter_id: Optional[str] = None,
        lesson_type: Optional[str] = None,
        published: Optional[bool] = None
    ) -> int:
        """
        Count lessons with filters.

        Args:
            chapter_id: Optional chapter filter
            lesson_type: Optional lesson type filter
            published: Optional published filter

        Returns:
            Lesson count
        """
        return LessonRepository.count(
            chapter_id=chapter_id,
            lesson_type=lesson_type,
            published=published
        )
