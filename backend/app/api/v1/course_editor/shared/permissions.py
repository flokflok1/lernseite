"""
Course Editor Permission System

Feature-based permissions for Course Editor.
Admins have full access, users only access their own courses.
"""

from functools import wraps
from flask import g, jsonify
from typing import Optional, Callable
from app.repositories.courses import CourseRepository
from app.database import get_connection


def check_course_permission(action: str = 'read'):
    """
    Permission decorator for course operations.

    Args:
        action: Permission action ('read', 'write', 'publish', 'delete')

    Returns:
        Decorator function

    Usage:
        @check_course_permission('write')
        def update_course(course_id):
            # Only course owner or admin can access
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = g.current_user
            user_id = user.get('user_id')
            is_admin = user.get('role') == 'admin'

            # Admin has full access
            if is_admin:
                return f(*args, **kwargs)

            # For non-admins, check course ownership
            course_id = kwargs.get('course_id')

            if course_id:
                with get_connection() as conn:
                    course_repo = CourseRepository(conn)
                    course = course_repo.find_by_id(course_id)

                    if not course:
                        return jsonify({
                            'error': {
                                'code': 'NOT_FOUND',
                                'message': f'Course {course_id} not found'
                            }
                        }), 404

                    # Check ownership
                    if course.created_by != user_id:
                        return jsonify({
                            'error': {
                                'code': 'FORBIDDEN',
                                'message': 'You do not have access to this course'
                            }
                        }), 403

            # Publish is admin-only
            if action == 'publish' and not is_admin:
                return jsonify({
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': 'Only admins can publish courses'
                    }
                }), 403

            # Delete is admin-only or course owner
            if action == 'delete' and not is_admin:
                if course_id:
                    with get_connection() as conn:
                        course_repo = CourseRepository(conn)
                        course = course_repo.find_by_id(course_id)

                        if course and course.created_by != user_id:
                            return jsonify({
                                'error': {
                                    'code': 'FORBIDDEN',
                                    'message': 'You can only delete your own courses'
                                }
                            }), 403

            return f(*args, **kwargs)

        return wrapper
    return decorator


def can_edit_course(user_id: str, course_id: str, is_admin: bool = False) -> bool:
    """
    Check if user can edit a course.

    Args:
        user_id: User ID
        course_id: Course ID
        is_admin: Whether user is admin

    Returns:
        True if user can edit, False otherwise
    """
    if is_admin:
        return True

    with get_db_connection() as conn:
        course_repo = CourseRepository(conn)
        course = course_repo.find_by_id(course_id)

        if not course:
            return False

        return course.created_by == user_id


def can_publish_course(is_admin: bool = False) -> bool:
    """
    Check if user can publish courses.

    Args:
        is_admin: Whether user is admin

    Returns:
        True if user can publish, False otherwise
    """
    return is_admin


def can_delete_course(user_id: str, course_id: str, is_admin: bool = False) -> bool:
    """
    Check if user can delete a course.

    Args:
        user_id: User ID
        course_id: Course ID
        is_admin: Whether user is admin

    Returns:
        True if user can delete, False otherwise
    """
    if is_admin:
        return True

    with get_db_connection() as conn:
        course_repo = CourseRepository(conn)
        course = course_repo.find_by_id(course_id)

        if not course:
            return False

        return course.created_by == user_id
