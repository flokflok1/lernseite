"""
Chapter Service (Application Layer)

Business logic for chapter operations.
ALL data loaded dynamically from database - NO hardcoded values.

Uses Repository Pattern for database access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.api.content.courses.chapters.domain.entities.chapter import Chapter
from src.api.content.courses.chapters.infrastructure.repositories.chapter_repository import ChapterRepository
from src.api.content.courses.core.infrastructure.repositories.course_repository import CourseRepository
from src.core.events import EventBus, EventType, DomainEvent


class ChapterService:
    """
    Chapter service for business logic.

    ALL configurations and values loaded from database dynamically.
    NO hardcoded chapter lists or configurations.
    """

    @staticmethod
    def get_chapter_by_id(chapter_id: str) -> Optional[Chapter]:
        """
        Get chapter by ID.

        Args:
            chapter_id: Chapter UUID

        Returns:
            Chapter entity or None
        """
        return ChapterRepository.find_by_id(chapter_id)

    @staticmethod
    def list_chapters(
        course_id: Optional[str] = None,
        published_only: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Chapter]:
        """
        List chapters with dynamic filters.

        Args:
            course_id: Optional course filter
            published_only: Only published chapters
            filters: Dynamic filters (has_video, has_quiz, has_exam)
            limit: Result limit
            offset: Result offset

        Returns:
            List of chapters
        """
        if course_id:
            # Optimized query for single course
            return ChapterRepository.find_by_course_id(
                course_id=course_id,
                published_only=published_only
            )

        # General listing with filters
        published = True if published_only else filters.get('published') if filters else None
        has_video = filters.get('has_video') if filters else None
        has_quiz = filters.get('has_quiz') if filters else None
        has_exam = filters.get('has_exam') if filters else None

        return ChapterRepository.find_all(
            course_id=course_id,
            published=published,
            has_video=has_video,
            has_quiz=has_quiz,
            has_exam=has_exam,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def list_course_chapters(course_id: str, published_only: bool = False) -> List[Chapter]:
        """
        List chapters for a specific course.

        Args:
            course_id: Course UUID
            published_only: Only published chapters

        Returns:
            List of chapters ordered by order_index
        """
        return ChapterRepository.find_by_course_id(
            course_id=course_id,
            published_only=published_only
        )

    @staticmethod
    def create_chapter(
        course_id: str,
        title: str,
        user_id: str,
        user_role: str,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        order_index: Optional[int] = None,
        prerequisite_chapter_id: Optional[str] = None
    ) -> Chapter:
        """
        Create new chapter.

        Args:
            course_id: Parent course UUID
            title: Chapter title
            user_id: User creating the chapter
            user_role: User role
            slug: Optional URL slug
            description: Optional description
            duration_minutes: Optional duration
            order_index: Optional order (auto-calculated if None)
            prerequisite_chapter_id: Optional prerequisite

        Returns:
            Created chapter entity

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

        # Get next order index if not provided
        if order_index is None:
            order_index = ChapterRepository.get_next_order_index(course_id)

        # Create chapter entity
        import uuid
        chapter = Chapter(
            chapter_id=str(uuid.uuid4()),
            course_id=course_id,
            title=title,
            slug=slug,
            description=description,
            order_index=order_index,
            duration_minutes=duration_minutes,
            estimated_duration=duration_minutes,
            prerequisite_chapter_id=prerequisite_chapter_id,
            published=False,
            has_video=False,
            has_quiz=False,
            has_exam=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to database
        created_chapter = ChapterRepository.create(chapter)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.CHAPTER_CREATED,
            aggregate_id=created_chapter.chapter_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': created_chapter.title,
                'course_id': created_chapter.course_id,
                'order_index': created_chapter.order_index
            }
        )
        EventBus.publish(event)

        return created_chapter

    @staticmethod
    def update_chapter(
        chapter_id: str,
        user_id: str,
        user_role: str,
        updates: Dict[str, Any]
    ) -> Chapter:
        """
        Update chapter with access control.

        Args:
            chapter_id: Chapter UUID
            user_id: User ID making the update
            user_role: User role
            updates: Dictionary of fields to update

        Returns:
            Updated chapter entity

        Raises:
            PermissionError: If user cannot edit chapter
            ValueError: If chapter not found or validation fails
        """
        # Get existing chapter
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        # Check edit permission on parent course
        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit chapter {chapter_id}")

        # Update metadata
        chapter.update_metadata(**updates)

        # Save to database
        updated_chapter = ChapterRepository.update(chapter)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.CHAPTER_UPDATED,
            aggregate_id=updated_chapter.chapter_id,
            occurred_at=datetime.utcnow(),
            data={
                'updated_fields': list(updates.keys()),
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return updated_chapter

    @staticmethod
    def publish_chapter(chapter_id: str, user_id: str, user_role: str) -> Chapter:
        """
        Publish chapter.

        Args:
            chapter_id: Chapter UUID
            user_id: User ID publishing the chapter
            user_role: User role

        Returns:
            Published chapter entity

        Raises:
            PermissionError: If user cannot edit chapter
            ValueError: If chapter not found
        """
        # Get existing chapter
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        # Check edit permission
        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to publish chapter {chapter_id}")

        # Publish
        chapter.publish()

        # Save to database
        published_chapter = ChapterRepository.update(chapter)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.CHAPTER_PUBLISHED,
            aggregate_id=published_chapter.chapter_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': published_chapter.title,
                'course_id': published_chapter.course_id,
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return published_chapter

    @staticmethod
    def unpublish_chapter(chapter_id: str, user_id: str, user_role: str) -> Chapter:
        """
        Unpublish chapter.

        Args:
            chapter_id: Chapter UUID
            user_id: User ID unpublishing the chapter
            user_role: User role

        Returns:
            Unpublished chapter entity
        """
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to unpublish chapter {chapter_id}")

        chapter.unpublish()
        return ChapterRepository.update(chapter)

    @staticmethod
    def delete_chapter(chapter_id: str, user_id: str, user_role: str) -> bool:
        """
        Delete chapter (hard delete - cascade to lessons).

        Args:
            chapter_id: Chapter UUID
            user_id: User ID deleting the chapter
            user_role: User role

        Returns:
            True if deleted

        Raises:
            PermissionError: If user cannot edit chapter
            ValueError: If chapter not found
        """
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to delete chapter {chapter_id}")

        # Delete from database
        deleted = ChapterRepository.delete(chapter_id)

        if deleted:
            # Publish domain event
            event = DomainEvent(
                event_type=EventType.CHAPTER_DELETED,
                aggregate_id=chapter_id,
                occurred_at=datetime.utcnow(),
                data={
                    'title': chapter.title,
                    'course_id': chapter.course_id,
                    'user_id': user_id
                }
            )
            EventBus.publish(event)

        return deleted

    @staticmethod
    def reorder_chapters(
        course_id: str,
        chapter_order: List[Dict[str, Any]],
        user_id: str,
        user_role: str
    ) -> bool:
        """
        Reorder chapters within a course.

        Args:
            course_id: Course UUID
            chapter_order: List of dicts with chapter_id and order_index
            user_id: User ID reordering chapters
            user_role: User role

        Returns:
            True if successful

        Raises:
            PermissionError: If user cannot edit course
        """
        # Check edit permission
        course = CourseRepository.find_by_id(course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to reorder chapters in course {course_id}")

        # Convert to tuple list
        order_tuples = [
            (item['chapter_id'], item['order_index'])
            for item in chapter_order
        ]

        # Reorder in database
        return ChapterRepository.reorder_chapters(course_id, order_tuples)

    @staticmethod
    def update_content_flags(
        chapter_id: str,
        user_id: str,
        user_role: str,
        has_video: Optional[bool] = None,
        has_quiz: Optional[bool] = None,
        has_exam: Optional[bool] = None
    ) -> Chapter:
        """
        Update chapter content type flags.

        Args:
            chapter_id: Chapter UUID
            user_id: User ID updating flags
            user_role: User role
            has_video: Has video content
            has_quiz: Has quiz content
            has_exam: Has exam content

        Returns:
            Updated chapter entity
        """
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to update chapter {chapter_id}")

        chapter.update_content_flags(
            has_video=has_video,
            has_quiz=has_quiz,
            has_exam=has_exam
        )

        return ChapterRepository.update(chapter)

    @staticmethod
    def count_chapters(course_id: Optional[str] = None, published: Optional[bool] = None) -> int:
        """
        Count chapters with filters.

        Args:
            course_id: Optional course filter
            published: Optional published filter

        Returns:
            Chapter count
        """
        return ChapterRepository.count(course_id=course_id, published=published)
