"""
Learning Method Service (Application Layer)

Business logic for learning method operations.
ALL data loaded dynamically from database - NO hardcoded values.

Uses Repository Pattern for database access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.api.content.learning_methods.domain.entities.learning_method_type import LearningMethodType
from src.api.content.learning_methods.domain.entities.learning_method_instance import LearningMethodInstance
from src.api.content.learning_methods.infrastructure.repositories.learning_method_repository import LearningMethodRepository
from src.api.content.courses.chapters.infrastructure.repositories.chapter_repository import ChapterRepository
from src.api.content.courses.core.infrastructure.repositories.course_repository import CourseRepository
from src.core.events import EventBus, EventType, DomainEvent


class LearningMethodService:
    """
    Learning method service for business logic.

    ALL configurations and values loaded from database dynamically.
    NO hardcoded method types or configurations.
    """

    # ============================================================================
    # LEARNING METHOD TYPES (The 12 Content-LMs)
    # ============================================================================

    @staticmethod
    def get_type_by_id(type_id: int) -> Optional[LearningMethodType]:
        """
        Get learning method type by ID.

        Args:
            type_id: Type ID

        Returns:
            LearningMethodType or None
        """
        return LearningMethodRepository.find_type_by_id(type_id)

    @staticmethod
    def get_type_by_method_type(method_type: int) -> Optional[LearningMethodType]:
        """
        Get learning method type by method_type (0-11).

        Args:
            method_type: Method type ID

        Returns:
            LearningMethodType or None
        """
        return LearningMethodRepository.find_type_by_method_type(method_type)

    @staticmethod
    def list_types(
        group_code: Optional[str] = None,
        tier: Optional[str] = None,
        active_only: bool = True
    ) -> List[LearningMethodType]:
        """
        List learning method types with filters.

        Args:
            group_code: Optional group filter (A, B, C)
            tier: Optional tier filter (basic, premium)
            active_only: Only active types

        Returns:
            List of LearningMethodType
        """
        return LearningMethodRepository.find_all_types(
            group_code=group_code,
            tier=tier,
            active_only=active_only
        )

    @staticmethod
    def get_available_method_types() -> List[int]:
        """
        Get available learning method types from database.

        Returns valid method_type values (0-11 for 12 Content-LMs) by querying
        the database CHECK constraint. NO hardcoded lists.

        Returns:
            List of valid method type IDs
        """
        return LearningMethodRepository.get_available_method_types()

    # ============================================================================
    # LEARNING METHOD INSTANCES (Concrete instances in chapters)
    # ============================================================================

    @staticmethod
    def get_instance_by_id(method_id: str) -> Optional[LearningMethodInstance]:
        """
        Get learning method instance by ID.

        Args:
            method_id: Method instance UUID

        Returns:
            LearningMethodInstance or None
        """
        return LearningMethodRepository.find_by_id(method_id)

    @staticmethod
    def list_instances(
        chapter_id: Optional[str] = None,
        method_type: Optional[int] = None,
        tier: Optional[str] = None,
        published_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[LearningMethodInstance]:
        """
        List learning method instances with filters.

        Args:
            chapter_id: Optional chapter filter
            method_type: Optional method type filter (0-11)
            tier: Optional tier filter (basic, premium)
            published_only: Only published instances
            limit: Result limit
            offset: Result offset

        Returns:
            List of LearningMethodInstance
        """
        if chapter_id:
            return LearningMethodRepository.find_by_chapter_id(
                chapter_id=chapter_id,
                published_only=published_only
            )

        return LearningMethodRepository.find_all(
            chapter_id=chapter_id,
            method_type=method_type,
            tier=tier,
            published=True if published_only else None,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def create_instance(
        chapter_id: str,
        method_type: int,
        title: str,
        data: Dict[str, Any],
        tier: str,
        user_id: str,
        user_role: str,
        instructions: Optional[str] = None,
        solution: Optional[Dict[str, Any]] = None,
        duration_minutes: Optional[int] = None,
        difficulty: Optional[str] = None,
        order_index: int = 0
    ) -> LearningMethodInstance:
        """
        Create new learning method instance.

        Args:
            chapter_id: Parent chapter UUID
            method_type: Type of learning method (0-11 for 12 Content-LMs)
            title: Instance title
            data: JSONB data (structure varies by method_type)
            tier: Access tier (basic, premium)
            user_id: User creating the instance
            user_role: User role
            instructions: Optional instructions
            solution: Optional solution data
            duration_minutes: Optional estimated duration
            difficulty: Optional difficulty level
            order_index: Order within chapter

        Returns:
            Created LearningMethodInstance

        Raises:
            ValueError: If validation fails
            PermissionError: If user cannot edit chapter
        """
        # Verify chapter exists and get course_id
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        # Verify user can edit course
        course = CourseRepository.find_by_id(chapter.course_id)
        if not course:
            raise ValueError(f"Course {chapter.course_id} not found")

        if not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit course {chapter.course_id}")

        # Verify method_type is valid (0-11)
        method_type_obj = LearningMethodRepository.find_type_by_method_type(method_type)
        if not method_type_obj:
            raise ValueError(f"Invalid method_type {method_type}. Must be between 0 and 11.")

        # Create instance entity
        import uuid
        instance = LearningMethodInstance(
            method_id=str(uuid.uuid4()),
            chapter_id=chapter_id,
            method_type=method_type,
            title=title,
            instructions=instructions,
            data=data,
            solution=solution,
            tier=tier,
            duration_minutes=duration_minutes,
            difficulty=difficulty,
            order_index=order_index,
            published=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to database
        created_instance = LearningMethodRepository.create(instance)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.LEARNING_METHOD_CREATED,
            aggregate_id=created_instance.method_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': created_instance.title,
                'chapter_id': created_instance.chapter_id,
                'method_type': created_instance.method_type
            }
        )
        EventBus.publish(event)

        return created_instance

    @staticmethod
    def update_instance(
        method_id: str,
        user_id: str,
        user_role: str,
        updates: Dict[str, Any]
    ) -> LearningMethodInstance:
        """
        Update learning method instance with access control.

        Args:
            method_id: Method instance UUID
            user_id: User ID making the update
            user_role: User role
            updates: Dictionary of fields to update

        Returns:
            Updated LearningMethodInstance

        Raises:
            PermissionError: If user cannot edit instance
            ValueError: If instance not found or validation fails
        """
        # Get existing instance
        instance = LearningMethodRepository.find_by_id(method_id)
        if not instance:
            raise ValueError(f"Learning method instance {method_id} not found")

        # Get chapter and course for permission check
        chapter = ChapterRepository.find_by_id(instance.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {instance.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit learning method {method_id}")

        # Update metadata
        instance.update_metadata(**updates)

        # Save to database
        updated_instance = LearningMethodRepository.update(instance)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.LEARNING_METHOD_UPDATED,
            aggregate_id=updated_instance.method_id,
            occurred_at=datetime.utcnow(),
            data={
                'updated_fields': list(updates.keys()),
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return updated_instance

    @staticmethod
    def update_instance_data(
        method_id: str,
        data: Dict[str, Any],
        user_id: str,
        user_role: str
    ) -> LearningMethodInstance:
        """
        Update learning method instance data (JSONB).

        Args:
            method_id: Method instance UUID
            data: New JSONB data
            user_id: User ID
            user_role: User role

        Returns:
            Updated LearningMethodInstance
        """
        instance = LearningMethodRepository.find_by_id(method_id)
        if not instance:
            raise ValueError(f"Learning method instance {method_id} not found")

        chapter = ChapterRepository.find_by_id(instance.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {instance.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit learning method {method_id}")

        instance.update_data(data)
        return LearningMethodRepository.update(instance)

    @staticmethod
    def update_instance_solution(
        method_id: str,
        solution: Dict[str, Any],
        user_id: str,
        user_role: str
    ) -> LearningMethodInstance:
        """
        Update learning method instance solution (JSONB).

        Args:
            method_id: Method instance UUID
            solution: New JSONB solution
            user_id: User ID
            user_role: User role

        Returns:
            Updated LearningMethodInstance
        """
        instance = LearningMethodRepository.find_by_id(method_id)
        if not instance:
            raise ValueError(f"Learning method instance {method_id} not found")

        chapter = ChapterRepository.find_by_id(instance.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {instance.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit learning method {method_id}")

        instance.update_solution(solution)
        return LearningMethodRepository.update(instance)

    @staticmethod
    def publish_instance(method_id: str, user_id: str, user_role: str) -> LearningMethodInstance:
        """
        Publish learning method instance.

        Args:
            method_id: Method instance UUID
            user_id: User ID publishing the instance
            user_role: User role

        Returns:
            Published LearningMethodInstance
        """
        instance = LearningMethodRepository.find_by_id(method_id)
        if not instance:
            raise ValueError(f"Learning method instance {method_id} not found")

        chapter = ChapterRepository.find_by_id(instance.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {instance.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to publish learning method {method_id}")

        instance.publish()
        published_instance = LearningMethodRepository.update(instance)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.LEARNING_METHOD_PUBLISHED,
            aggregate_id=published_instance.method_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': published_instance.title,
                'chapter_id': published_instance.chapter_id,
                'method_type': published_instance.method_type,
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return published_instance

    @staticmethod
    def unpublish_instance(method_id: str, user_id: str, user_role: str) -> LearningMethodInstance:
        """Unpublish learning method instance."""
        instance = LearningMethodRepository.find_by_id(method_id)
        if not instance:
            raise ValueError(f"Learning method instance {method_id} not found")

        chapter = ChapterRepository.find_by_id(instance.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {instance.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to unpublish learning method {method_id}")

        instance.unpublish()
        return LearningMethodRepository.update(instance)

    @staticmethod
    def delete_instance(method_id: str, user_id: str, user_role: str) -> bool:
        """
        Delete learning method instance (hard delete - cascade to progress).

        Args:
            method_id: Method instance UUID
            user_id: User ID deleting the instance
            user_role: User role

        Returns:
            True if deleted
        """
        instance = LearningMethodRepository.find_by_id(method_id)
        if not instance:
            raise ValueError(f"Learning method instance {method_id} not found")

        chapter = ChapterRepository.find_by_id(instance.chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {instance.chapter_id} not found")

        course = CourseRepository.find_by_id(chapter.course_id)
        if not course or not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to delete learning method {method_id}")

        deleted = LearningMethodRepository.delete(method_id)

        if deleted:
            event = DomainEvent(
                event_type=EventType.LEARNING_METHOD_DELETED,
                aggregate_id=method_id,
                occurred_at=datetime.utcnow(),
                data={
                    'title': instance.title,
                    'chapter_id': instance.chapter_id,
                    'method_type': instance.method_type,
                    'user_id': user_id
                }
            )
            EventBus.publish(event)

        return deleted

    @staticmethod
    def count_instances(
        chapter_id: Optional[str] = None,
        method_type: Optional[int] = None,
        tier: Optional[str] = None,
        published: Optional[bool] = None
    ) -> int:
        """
        Count learning method instances with filters.

        Args:
            chapter_id: Optional chapter filter
            method_type: Optional method type filter
            tier: Optional tier filter
            published: Optional published filter

        Returns:
            Instance count
        """
        return LearningMethodRepository.count(
            chapter_id=chapter_id,
            method_type=method_type,
            tier=tier,
            published=published
        )
