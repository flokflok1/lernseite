"""
LernsystemX Agent API - Shared Helpers

Common utilities and response builders for agent endpoints.

Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

import os
from flask import jsonify
from typing import Dict, Any, Tuple

from app.repositories.courses import CourseRepository

# Temporary upload path for voice recordings
UPLOAD_TEMP_PATH = os.getenv('UPLOAD_TEMP_PATH', 'storage/temp')

# Allowed audio file extensions
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'webm', 'm4a', 'ogg', 'flac'}


def validate_course_exists(course_id: str) -> Tuple[Dict[str, Any] | None, Tuple[Dict, int] | None]:
    """
    Validate that a course exists.

    Args:
        course_id: The course ID to validate

    Returns:
        Tuple of (course_dict, None) if found, or (None, error_response) if not found
    """
    course = CourseRepository.get_by_id(course_id)
    if not course:
        return None, (jsonify({
            'success': False,
            'error': 'Course not found'
        }), 404)
    return course, None


def check_course_authorization(course: Dict, user: Dict) -> Tuple[bool, Tuple[Dict, int] | None]:
    """
    Check if user is authorized to modify a course's agent.

    Args:
        course: Course dictionary
        user: User dictionary

    Returns:
        Tuple of (is_authorized, error_response_or_none)
    """
    is_owner = str(course.get('creator_id')) == str(user.get('user_id'))
    is_admin = user.get('role') in ['admin', 'superadmin']

    if not is_owner and not is_admin:
        return False, (jsonify({
            'success': False,
            'error': 'Not authorized to modify this agent'
        }), 403)

    return True, None


def error_response(message: str, details: Any = None, code: int = 500) -> Tuple[Dict, int]:
    """
    Build a standardized error response.

    Args:
        message: Error message
        details: Optional error details
        code: HTTP status code

    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        'success': False,
        'error': message
    }
    if details:
        response['details'] = str(details) if not isinstance(details, (list, dict)) else details
    return jsonify(response), code


def success_response(data: Any = None, message: str = None, code: int = 200) -> Tuple[Dict, int]:
    """
    Build a standardized success response.

    Args:
        data: Response data
        message: Optional success message
        code: HTTP status code

    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), code
