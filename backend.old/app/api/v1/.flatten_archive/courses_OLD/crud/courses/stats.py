"""
Course Statistics and Analytics Endpoints

Endpoints:
- GET /courses/:id/stats - Get course statistics
"""

from flask import jsonify

from app.repositories.courses import CourseRepository
from app.repositories.enrollments.core import EnrollmentRepository
from app.middleware.auth import token_required, get_current_user

# Import blueprint from write.py and register stats endpoints
from .write import courses_bp


@courses_bp.route('/<course_id>/stats', methods=['GET'])
@token_required
def get_course_stats(course_id):
    """
    Get course statistics (creator or admin only)

    Response:
        200: Course statistics
        403: Access denied
    """
    try:
        user = get_current_user()
        course = CourseRepository.find_by_id(course_id)

        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Check permissions
        is_creator = user['user_id'] == course['creator_id']
        is_admin = user['role'] in ['admin', 'superadmin']

        if not (is_creator or is_admin):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Get statistics
        stats = CourseRepository.get_statistics(course_id)
        enrollment_stats = EnrollmentRepository.get_enrollment_stats(course_id)

        return jsonify({
            'success': True,
            'stats': {
                **stats,
                **enrollment_stats
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics',
            'details': str(e)
        }), 500
