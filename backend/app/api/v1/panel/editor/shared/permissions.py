"""
Course Editor Permission System

Feature-based permissions for Course Editor.
Admins have full access, users only access their own courses.

Uses token_required to ensure g.current_user is populated before
checking course-level permissions.
"""

from functools import wraps
from flask import g, jsonify
from typing import Callable
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.api.middleware.auth import token_required

# Roles with full course editor access (admin-equivalent)
ADMIN_ROLES = {'admin', 'owner', 'superadmin'}


def _is_admin_user(user: dict) -> bool:
    """Check if user has admin-level access based on role or permissions."""
    return user.get('role') in ADMIN_ROLES


def check_course_permission(action: str = 'read'):
    """
    Permission decorator for course operations.

    Chains token_required to ensure g.current_user is populated,
    then checks course-level permissions.

    Args:
        action: Permission action ('read', 'write', 'publish', 'delete')

    Usage:
        @check_course_permission('write')
        def update_course(course_id):
            # Only course owner or admin can access
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @token_required
        def wrapper(*args, **kwargs):
            user = g.current_user
            user_id = user.get('user_id')
            is_admin = _is_admin_user(user)

            # Admin has full access
            if is_admin:
                return f(*args, **kwargs)

            # For non-admins, check course ownership
            course_id = kwargs.get('course_id')

            if course_id:
                course = CourseRepository.find_by_id(course_id)

                if not course:
                    return jsonify({
                        'error': {
                            'code': 'NOT_FOUND',
                            'message': f'Course {course_id} not found'
                        }
                    }), 404

                # Check ownership
                if course.get('created_by') != user_id:
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
                    course = CourseRepository.find_by_id(course_id)

                    if course and course.get('created_by') != user_id:
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
    """Check if user can edit a course."""
    if is_admin:
        return True

    course = CourseRepository.find_by_id(course_id)
    if not course:
        return False

    return course.get('created_by') == user_id


def can_publish_course(is_admin: bool = False) -> bool:
    """Check if user can publish courses."""
    return is_admin


def can_delete_course(user_id: str, course_id: str, is_admin: bool = False) -> bool:
    """Check if user can delete a course."""
    if is_admin:
        return True

    course = CourseRepository.find_by_id(course_id)
    if not course:
        return False

    return course.get('created_by') == user_id
