"""
Course Service (Application Layer)

Business logic for course operations.
ALL data loaded dynamically from database - NO hardcoded values.

Uses Repository Pattern for database access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.api.content.courses.core.domain.entities.course import Course
from src.api.content.courses.core.infrastructure.repositories.course_repository import CourseRepository
from src.core.events import EventBus, EventType, DomainEvent


class CourseService:
    """
    Course service for business logic.

    ALL configurations and values loaded from database dynamically.
    NO hardcoded course lists, status values, or visibility options.
    """

    @staticmethod
    def get_course_by_id(course_id: str, user_id: Optional[str] = None,
                         user_role: Optional[str] = None) -> Optional[Course]:
        """
        Get course by ID with access control.

        Args:
            course_id: Course UUID
            user_id: Optional user ID for access check
            user_role: Optional user role for access check

        Returns:
            Course entity or None if not found or no access

        Raises:
            PermissionError: If user has no access to course
        """
        course = CourseRepository.find_by_id(course_id)

        if not course:
            return None

        # Check access if user info provided
        if user_id and user_role:
            if not course.is_accessible_by(user_id, user_role):
                raise PermissionError(f"User has no access to course {course_id}")

        return course

    @staticmethod
    def list_courses(
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        user_org_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Course]:
        """
        List courses with dynamic filters from database.

        ALL filter options (status, visibility, categories) loaded from DB.
        NO hardcoded filter lists.

        Args:
            user_id: Optional user ID for filtering
            user_role: Optional user role for access control
            user_org_id: Optional organisation ID
            filters: Dynamic filters (status, visibility, category_id, creator_id)
            limit: Result limit
            offset: Result offset

        Returns:
            List of accessible courses
        """
        # Extract filters - all values from DB or parameters
        status = filters.get('status') if filters else None
        visibility = filters.get('visibility') if filters else None
        category_id = filters.get('category_id') if filters else None
        creator_id = filters.get('creator_id') if filters else None
        organisation_id = filters.get('organisation_id') if filters else None

        # Get courses from DB
        courses = CourseRepository.find_all(
            status=status,
            visibility=visibility,
            creator_id=creator_id,
            category_id=category_id,
            organisation_id=organisation_id,
            limit=limit,
            offset=offset
        )

        # Filter by access if user info provided
        if user_id and user_role:
            courses = [
                course for course in courses
                if course.is_accessible_by(user_id, user_role, user_org_id)
            ]

        return courses

    @staticmethod
    def list_published_courses(
        category_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Course]:
        """
        List published public courses.

        Args:
            category_id: Optional category filter (from DB)
            limit: Result limit
            offset: Result offset

        Returns:
            List of published courses
        """
        return CourseRepository.find_published(
            category_id=category_id,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def create_course(
        title: str,
        creator_id: str,
        category_id: str,
        description: Optional[str] = None,
        difficulty_level: int = 1,
        organisation_id: Optional[str] = None,
        price: Optional[float] = None
    ) -> Course:
        """
        Create new course.

        Args:
            title: Course title
            creator_id: Creator user ID
            category_id: Category ID (must exist in DB)
            description: Optional description
            difficulty_level: Difficulty (1-5)
            organisation_id: Optional organisation ID
            price: Optional price for marketplace

        Returns:
            Created course entity

        Raises:
            ValueError: If validation fails
        """
        # Validate difficulty level
        if difficulty_level < 1 or difficulty_level > 5:
            raise ValueError("Difficulty level must be between 1 and 5")

        # Create course entity (default status: 'draft', visibility: 'private')
        import uuid
        course = Course(
            course_id=str(uuid.uuid4()),
            title=title,
            description=description,
            creator_id=creator_id,
            category_id=category_id,
            difficulty_level=difficulty_level,
            status='draft',  # Default from DB enum
            visibility='private',  # Default from DB enum
            is_published=False,
            is_drm_protected=False,
            organisation_id=organisation_id,
            price=price,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to database
        created_course = CourseRepository.create(course)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.COURSE_CREATED,
            aggregate_id=created_course.course_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': created_course.title,
                'creator_id': created_course.creator_id,
                'category_id': created_course.category_id
            }
        )
        EventBus.publish(event)

        return created_course

    @staticmethod
    def update_course(
        course_id: str,
        user_id: str,
        user_role: str,
        updates: Dict[str, Any]
    ) -> Course:
        """
        Update course with access control.

        Args:
            course_id: Course UUID
            user_id: User ID making the update
            user_role: User role
            updates: Dictionary of fields to update

        Returns:
            Updated course entity

        Raises:
            PermissionError: If user cannot edit course
            ValueError: If course not found or validation fails
        """
        # Get existing course
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")

        # Check edit permission
        if not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to edit course {course_id}")

        # Update metadata
        course.update_metadata(**updates)

        # Save to database
        updated_course = CourseRepository.update(course)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.COURSE_UPDATED,
            aggregate_id=updated_course.course_id,
            occurred_at=datetime.utcnow(),
            data={
                'updated_fields': list(updates.keys()),
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return updated_course

    @staticmethod
    def publish_course(course_id: str, user_id: str, user_role: str) -> Course:
        """
        Publish course.

        Args:
            course_id: Course UUID
            user_id: User ID publishing the course
            user_role: User role

        Returns:
            Published course entity

        Raises:
            PermissionError: If user cannot edit course
            ValueError: If course not found or cannot be published
        """
        # Get existing course
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")

        # Check edit permission
        if not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to publish course {course_id}")

        # Publish (business rule in entity)
        course.publish()

        # Save to database
        published_course = CourseRepository.update(course)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.COURSE_PUBLISHED,
            aggregate_id=published_course.course_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': published_course.title,
                'creator_id': published_course.creator_id,
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return published_course

    @staticmethod
    def archive_course(course_id: str, user_id: str, user_role: str) -> Course:
        """
        Archive course (soft delete).

        Args:
            course_id: Course UUID
            user_id: User ID archiving the course
            user_role: User role

        Returns:
            Archived course entity

        Raises:
            PermissionError: If user cannot edit course
            ValueError: If course not found
        """
        # Get existing course
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")

        # Check edit permission
        if not course.can_be_edited_by(user_id, user_role):
            raise PermissionError(f"User has no permission to archive course {course_id}")

        # Archive
        course.archive()

        # Save to database
        archived_course = CourseRepository.update(course)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.COURSE_ARCHIVED,
            aggregate_id=archived_course.course_id,
            occurred_at=datetime.utcnow(),
            data={
                'title': archived_course.title,
                'user_id': user_id
            }
        )
        EventBus.publish(event)

        return archived_course

    @staticmethod
    def delete_course(course_id: str, user_id: str, user_role: str) -> bool:
        """
        Delete course (soft delete - archives instead).

        Args:
            course_id: Course UUID
            user_id: User ID deleting the course
            user_role: User role

        Returns:
            True if deleted

        Raises:
            PermissionError: If user cannot edit course
            ValueError: If course not found
        """
        # Archive instead of hard delete
        CourseService.archive_course(course_id, user_id, user_role)
        return True

    @staticmethod
    def count_courses(
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count courses with dynamic filters.

        Args:
            user_id: Optional user ID for creator filter
            filters: Dynamic filters (status, category_id)

        Returns:
            Course count
        """
        status = filters.get('status') if filters else None
        creator_id = filters.get('creator_id', user_id) if filters else user_id
        category_id = filters.get('category_id') if filters else None

        return CourseRepository.count(
            status=status,
            creator_id=creator_id,
            category_id=category_id
        )
