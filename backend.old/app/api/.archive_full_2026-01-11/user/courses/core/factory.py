"""
Course Factory - DDD Factory Pattern

Handles complex course, chapter, and lesson creation with business rules.
Implements Domain-Driven Design (DDD) Factory Pattern.

Usage:
    >>> course = CourseFactory.create_draft(
    ...     creator_id="user123",
    ...     title="Python Basics",
    ...     category_id="cat456"
    ... )
    >>> chapter = ChapterFactory.create(course_id, "Introduction", 1)
    >>> lesson = LessonFactory.create(chapter_id, "First Lesson", "text", 1)
"""
from typing import Dict, Optional
from datetime import datetime
import uuid


class CourseFactory:
    """
    Factory for creating Course instances.
    Implements Domain-Driven Design (DDD) Factory Pattern.

    Responsibilities:
    - Create courses with valid initial state
    - Apply business rules during creation
    - Handle complex construction logic
    - State transitions (draft → published → archived)
    """

    @staticmethod
    def create_draft(
        creator_id: str,
        title: str,
        category_id: str,
        description: Optional[str] = None
    ) -> Dict:
        """
        Create a new course in draft state.

        Business Rules:
        - Draft courses are always private
        - Creator automatically gets admin access
        - Requires enrollment by default
        - Not published initially

        Args:
            creator_id: User ID of course creator
            title: Course title
            category_id: Category assignment
            description: Optional course description

        Returns:
            Course dict with valid initial state

        Example:
            >>> course = CourseFactory.create_draft(
            ...     creator_id="user123",
            ...     title="Python Basics",
            ...     category_id="cat456"
            ... )
            >>> course['status']
            'draft'
            >>> course['is_published']
            False
        """
        course_id = str(uuid.uuid4())
        now = datetime.utcnow()

        return {
            # Identity
            'course_id': course_id,
            'creator_id': creator_id,

            # Content
            'title': title,
            'description': description or '',
            'category_id': category_id,

            # State (Business Rules!)
            'status': 'draft',                    # Always draft initially
            'visibility': 'private',              # Private until published
            'is_published': False,                # Not published
            'requires_enrollment': True,          # Default: enrollment required

            # Limits
            'max_students': None,                 # Unlimited by default
            'enrollment_start': None,
            'enrollment_end': None,

            # Settings
            'allow_reviews': True,
            'auto_enroll': False,
            'certificate_enabled': False,

            # Metadata
            'created_at': now,
            'updated_at': now,
            'published_at': None,
            'published_by': None
        }

    @staticmethod
    def create_from_template(
        template_id: str,
        creator_id: str,
        title_override: Optional[str] = None
    ) -> Dict:
        """
        Create course from existing template.

        Business Rules:
        - Copies template structure and settings
        - Creator becomes owner of new course
        - Title gets "(Copy)" suffix if not overridden
        - New course starts as draft

        Args:
            template_id: ID of template course
            creator_id: User creating from template
            title_override: Optional new title

        Returns:
            New course based on template

        Raises:
            ValueError: If template not found
        """
        from app.repositories.courses import CourseRepository

        # Load template
        template = CourseRepository.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Create base course
        title = title_override or f"{template['title']} (Copy)"
        course = CourseFactory.create_draft(
            creator_id=creator_id,
            title=title,
            category_id=template['category_id'],
            description=template['description']
        )

        # Apply template settings
        course['max_students'] = template['max_students']
        course['requires_enrollment'] = template['requires_enrollment']
        course['allow_reviews'] = template['allow_reviews']
        course['certificate_enabled'] = template['certificate_enabled']

        # Copy AI settings if present
        if 'ai_settings' in template:
            course['ai_settings'] = template['ai_settings'].copy()

        return course

    @staticmethod
    def publish(course: Dict, publisher_id: str) -> Dict:
        """
        Publish a course (state transition: draft → published).

        Business Rules:
        - Only draft/unpublished courses can be published
        - Must have at least 1 chapter with content
        - Becomes public upon publishing
        - Records who published and when

        Args:
            course: Course to publish
            publisher_id: User performing publish action

        Returns:
            Updated course in published state

        Raises:
            ValueError: If business rules violated

        Example:
            >>> course = CourseFactory.create_draft(...)
            >>> published = CourseFactory.publish(course, "admin123")
            >>> published['is_published']
            True
            >>> published['visibility']
            'public'
        """
        # Business Rule: Only unpublished can be published
        if course.get('is_published'):
            raise ValueError(
                f"Course {course['course_id']} is already published"
            )

        # Business Rule: Must have content
        if not CourseFactory._has_required_content(course):
            raise ValueError(
                f"Course {course['course_id']} must have at least 1 chapter "
                "with content before publishing"
            )

        # State Transition
        course['is_published'] = True
        course['status'] = 'published'
        course['visibility'] = 'public'         # Auto-public on publish
        course['published_at'] = datetime.utcnow()
        course['published_by'] = publisher_id
        course['updated_at'] = datetime.utcnow()

        return course

    @staticmethod
    def unpublish(course: Dict, reason: Optional[str] = None) -> Dict:
        """
        Unpublish a course (state transition: published → draft).

        Business Rules:
        - Only published courses can be unpublished
        - Becomes private again
        - Existing enrollments preserved

        Args:
            course: Course to unpublish
            reason: Optional reason for unpublishing

        Returns:
            Updated course in draft state

        Raises:
            ValueError: If course not published
        """
        if not course.get('is_published'):
            raise ValueError(
                f"Course {course['course_id']} is not published"
            )

        course['is_published'] = False
        course['status'] = 'draft'
        course['visibility'] = 'private'
        course['updated_at'] = datetime.utcnow()

        if reason:
            course['unpublish_reason'] = reason

        return course

    @staticmethod
    def archive(course: Dict) -> Dict:
        """
        Archive a course (final state transition).

        Business Rules:
        - Course becomes read-only
        - No new enrollments allowed
        - Existing students retain access

        Args:
            course: Course to archive

        Returns:
            Archived course
        """
        course['status'] = 'archived'
        course['is_published'] = False
        course['visibility'] = 'private'
        course['requires_enrollment'] = False  # Read-only
        course['archived_at'] = datetime.utcnow()
        course['updated_at'] = datetime.utcnow()

        return course

    @staticmethod
    def _has_required_content(course: Dict) -> bool:
        """
        Check if course meets minimum content requirements.

        Business Rule: Course must have at least 1 chapter

        Args:
            course: Course to check

        Returns:
            True if meets requirements
        """
        from app.repositories.courses.chapters import ChapterRepository

        chapters = ChapterRepository.find_by_course(course['course_id'])
        return len(chapters) > 0


class ChapterFactory:
    """
    Factory for creating Chapter instances.

    Responsibilities:
    - Create chapters with valid initial state
    - Apply ordering rules
    - Handle chapter structure
    """

    @staticmethod
    def create(
        course_id: str,
        title: str,
        order_index: int,
        description: Optional[str] = None
    ) -> Dict:
        """
        Create new chapter with valid initial state.

        Business Rules:
        - Chapters start unpublished
        - Order index determines chapter sequence
        - Belongs to exactly one course

        Args:
            course_id: Parent course ID
            title: Chapter title
            order_index: Position in course (0-based)
            description: Optional chapter description

        Returns:
            Chapter dict with valid initial state
        """
        return {
            'chapter_id': str(uuid.uuid4()),
            'course_id': course_id,
            'title': title,
            'description': description or '',
            'order_index': order_index,
            'is_published': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }


class LessonFactory:
    """
    Factory for creating Lesson instances.

    Responsibilities:
    - Create lessons with valid initial state
    - Validate lesson types
    - Handle lesson content structure
    """

    # Valid lesson types
    VALID_LESSON_TYPES = [
        'text', 'video', 'quiz', 'ai', 'whiteboard',
        'exercise', 'practical', 'assessment'
    ]

    @staticmethod
    def create(
        chapter_id: str,
        title: str,
        lesson_type: str,
        order_index: int,
        content: Optional[Dict] = None
    ) -> Dict:
        """
        Create new lesson with valid initial state.

        Business Rules:
        - Lessons start unpublished
        - Must have valid lesson type
        - Order index determines lesson sequence
        - Belongs to exactly one chapter

        Args:
            chapter_id: Parent chapter ID
            title: Lesson title
            lesson_type: Type of lesson (text, video, quiz, etc.)
            order_index: Position in chapter (0-based)
            content: Optional lesson content (JSON)

        Returns:
            Lesson dict with valid initial state

        Raises:
            ValueError: If lesson_type invalid
        """
        # Validate lesson type
        if lesson_type not in LessonFactory.VALID_LESSON_TYPES:
            raise ValueError(
                f"Invalid lesson type: {lesson_type}. "
                f"Valid types: {', '.join(LessonFactory.VALID_LESSON_TYPES)}"
            )

        return {
            'lesson_id': str(uuid.uuid4()),
            'chapter_id': chapter_id,
            'title': title,
            'lesson_type': lesson_type,
            'content': content or {},
            'order_index': order_index,
            'is_published': False,
            'duration_minutes': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
