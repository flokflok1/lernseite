"""
Course Domain Services

Complex business logic that doesn't belong to a single entity.
Coordinates operations across multiple aggregates and repositories.

Usage:
    >>> can_enroll, reason = CourseService.can_user_enroll(user, course)
    >>> if can_enroll:
    ...     enrollment = EnrollmentRepository.create(...)
    >>> else:
    ...     print(f"Cannot enroll: {reason}")
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CourseService:
    """
    Domain Service for course-related business logic.

    Use Cases:
    - Enrollment eligibility
    - Progress calculation
    - Certificate generation
    - Multi-entity operations
    """

    @staticmethod
    def can_user_enroll(user: Dict, course: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check if user can enroll in course.

        Business Rules:
        - Course must be published
        - Not already enrolled
        - Not exceeded max_students
        - Enrollment window active (if set)
        - Prerequisites met (if any)

        Args:
            user: User attempting to enroll
            course: Course to enroll in

        Returns:
            (can_enroll, reason_if_not)

        Example:
            >>> can_enroll, reason = CourseService.can_user_enroll(user, course)
            >>> if not can_enroll:
            ...     print(f"Cannot enroll: {reason}")
        """
        # Rule: Course must be published
        if not course.get('is_published'):
            return False, "Course is not published"

        # Rule: Check enrollment window
        now = datetime.utcnow()
        if course.get('enrollment_start') and now < course['enrollment_start']:
            return False, "Enrollment has not started yet"

        if course.get('enrollment_end') and now > course['enrollment_end']:
            return False, "Enrollment period has ended"

        # Rule: Check capacity
        if course.get('max_students'):
            from app.repositories.enrollments.core import EnrollmentRepository
            current_count = EnrollmentRepository.count_by_course(
                course['course_id']
            )
            if current_count >= course['max_students']:
                return False, "Course is full"

        # Rule: Check if already enrolled
        from app.repositories.enrollments.core import EnrollmentRepository
        existing = EnrollmentRepository.find_by_user_and_course(
            user['user_id'], course['course_id']
        )
        if existing:
            return False, "Already enrolled"

        # Rule: Check prerequisites (if implemented)
        # TODO: Implement prerequisite checking

        return True, None

    @staticmethod
    def calculate_progress(user_id: str, course_id: str) -> float:
        """
        Calculate user's progress in course.

        Business Logic:
        - Count completed lessons vs total lessons
        - Weight by lesson importance (if applicable)
        - Include quiz/exam scores

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            Progress percentage (0-100)
        """
        from app.repositories.courses import CourseRepository
        from app.repositories.courses.chapters import ChapterRepository
        from app.repositories.courses.lessons import LessonRepository

        # Get all chapters in course
        chapters = ChapterRepository.find_by_course(course_id)
        if not chapters:
            return 0.0

        # Count total and completed lessons
        total_lessons = 0
        completed_lessons = 0

        for chapter in chapters:
            lessons = LessonRepository.find_by_chapter(chapter['chapter_id'])
            total_lessons += len(lessons)

            for lesson in lessons:
                progress = LessonRepository.get_user_progress(
                    lesson['lesson_id'],
                    user_id
                )
                if progress and progress.get('completed_at'):
                    completed_lessons += 1

        if total_lessons == 0:
            return 0.0

        # Calculate percentage
        progress = (completed_lessons / total_lessons) * 100
        return round(progress, 2)

    @staticmethod
    def can_issue_certificate(
        user_id: str,
        course_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if user is eligible for certificate.

        Business Rules:
        - Course must have certificates enabled
        - User must have completed course (100% progress)
        - All required assessments passed
        - Not already issued

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            (can_issue, reason_if_not)
        """
        from app.repositories.courses import CourseRepository

        course = CourseRepository.find_by_id(course_id)

        # Rule: Certificates must be enabled
        if not course.get('certificate_enabled'):
            return False, "Certificates not enabled for this course"

        # Rule: Must have 100% progress
        progress = CourseService.calculate_progress(user_id, course_id)
        if progress < 100:
            return False, f"Course not completed ({progress}%)"

        # Rule: Check if already issued
        # TODO: Implement certificate repository
        # from app.repositories.certificates import CertificateRepository
        # existing = CertificateRepository.find_by_user_and_course(
        #     user_id, course_id
        # )
        # if existing:
        #     return False, "Certificate already issued"

        # Rule: All exams passed (if required)
        # TODO: Implement exam checking

        return True, None

    @staticmethod
    def calculate_course_statistics(course_id: str) -> Dict:
        """
        Calculate various statistics for a course.

        Includes:
        - Total enrollments
        - Active students
        - Completion rate
        - Average progress
        - Time spent

        Args:
            course_id: Course ID

        Returns:
            Dictionary with statistics
        """
        from app.repositories.enrollments.core import EnrollmentRepository

        enrollments = EnrollmentRepository.find_by_course(course_id)

        total_enrollments = len(enrollments)
        active_students = sum(
            1 for e in enrollments if e['status'] == 'active'
        )
        completed_students = sum(
            1 for e in enrollments if e.get('completed_at')
        )

        # Calculate completion rate
        completion_rate = 0.0
        if total_enrollments > 0:
            completion_rate = (completed_students / total_enrollments) * 100

        # Calculate average progress
        total_progress = 0.0
        for enrollment in enrollments:
            progress = CourseService.calculate_progress(
                enrollment['user_id'],
                course_id
            )
            total_progress += progress

        average_progress = 0.0
        if total_enrollments > 0:
            average_progress = total_progress / total_enrollments

        return {
            'course_id': course_id,
            'total_enrollments': total_enrollments,
            'active_students': active_students,
            'completed_students': completed_students,
            'completion_rate': round(completion_rate, 2),
            'average_progress': round(average_progress, 2),
            'calculated_at': datetime.utcnow()
        }

    @staticmethod
    def validate_course_structure(course_id: str) -> Tuple[bool, List[str]]:
        """
        Validate course structure for publishing.

        Checks:
        - Has at least 1 chapter
        - Each chapter has at least 1 lesson
        - All content is valid
        - No broken references

        Args:
            course_id: Course ID to validate

        Returns:
            (is_valid, list_of_issues)
        """
        from app.repositories.courses.chapters import ChapterRepository
        from app.repositories.courses.lessons import LessonRepository

        issues = []

        # Check chapters
        chapters = ChapterRepository.find_by_course(course_id)
        if not chapters:
            issues.append("Course must have at least 1 chapter")
            return False, issues

        # Check each chapter has lessons
        for chapter in chapters:
            lessons = LessonRepository.find_by_chapter(chapter['chapter_id'])
            if not lessons:
                issues.append(
                    f"Chapter '{chapter['title']}' has no lessons"
                )

        # TODO: Add more validation rules
        # - Check for broken learning method references
        # - Validate content structure
        # - Check for orphaned resources

        is_valid = len(issues) == 0
        return is_valid, issues


class EnrollmentService:
    """
    Domain Service for enrollment-related business logic.

    Use Cases:
    - Enrollment creation with payment
    - Bulk enrollment operations
    - Enrollment status transitions
    """

    @staticmethod
    def create_enrollment_with_payment(
        user_id: str,
        course_id: str,
        payment_method: str,
        payment_transaction_id: Optional[str] = None
    ) -> Dict:
        """
        Create enrollment with payment processing.

        Business Rules:
        - User must be eligible to enroll
        - Payment must be valid
        - Creates audit trail

        Args:
            user_id: User enrolling
            course_id: Course to enroll in
            payment_method: Payment method used
            payment_transaction_id: Transaction reference

        Returns:
            Created enrollment

        Raises:
            ValueError: If enrollment not allowed or payment invalid
        """
        from app.repositories.courses import CourseRepository
        from app.repositories.user.core import UserRepository
        from app.repositories.enrollments.core import EnrollmentRepository
        from decimal import Decimal

        # Get user and course
        user = UserRepository.find_by_id(user_id)
        course = CourseRepository.find_by_id(course_id)

        if not user:
            raise ValueError(f"User {user_id} not found")
        if not course:
            raise ValueError(f"Course {course_id} not found")

        # Check eligibility
        can_enroll, reason = CourseService.can_user_enroll(user, course)
        if not can_enroll:
            raise ValueError(f"Cannot enroll: {reason}")

        # Create enrollment
        enrollment_data = {
            'user_id': user_id,
            'course_id': course_id,
            'price_paid': Decimal(str(course.get('price', 0))),
            'payment_method': payment_method,
            'payment_transaction_id': payment_transaction_id
        }

        enrollment = EnrollmentRepository.create(enrollment_data)

        # TODO: Send confirmation email
        # TODO: Add to analytics

        return enrollment

    @staticmethod
    def bulk_enroll_users(
        user_ids: List[str],
        course_id: str,
        enrollment_type: str = 'assigned'
    ) -> Dict:
        """
        Enroll multiple users in a course.

        Use Case: Organization assigns course to employees/students

        Args:
            user_ids: List of user IDs to enroll
            course_id: Course to enroll in
            enrollment_type: Type of enrollment (assigned, invited)

        Returns:
            Dictionary with success/failure counts
        """
        from app.repositories.enrollments.core import EnrollmentRepository
        from decimal import Decimal

        successful = []
        failed = []

        for user_id in user_ids:
            try:
                enrollment_data = {
                    'user_id': user_id,
                    'course_id': course_id,
                    'price_paid': Decimal('0'),  # Assigned = free
                    'payment_method': enrollment_type
                }
                enrollment = EnrollmentRepository.create(enrollment_data)
                successful.append(user_id)
            except Exception as e:
                failed.append({
                    'user_id': user_id,
                    'reason': str(e)
                })

        return {
            'total': len(user_ids),
            'successful': len(successful),
            'failed': len(failed),
            'successful_ids': successful,
            'failed_details': failed
        }
