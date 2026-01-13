"""
Exam Context API Endpoint (Admin).

Endpoint:
- GET /api/v1/courses/:id/exam-context - Get detected exam context
"""

from flask import Blueprint, jsonify
from uuid import UUID

from app.middleware.auth import token_required, get_current_user
from app.services.exam_context_detector import get_exam_context_sync
from app.database.connection import fetch_one


exam_context_bp = Blueprint(
    'exam_context',
    __name__,
    url_prefix='/courses'
)


@exam_context_bp.route('/<course_id>/exam-context', methods=['GET'])
@token_required
def get_course_exam_context(course_id: str):
    """
    Get detected exam context for a course.

    Uses ExamContextDetector to analyze:
    - User profile (profession, region, target exam)
    - Course metadata (profession_tag, exam_level)
    - Course files (PDFs, exam-relevant documents)
    - Learning analytics (weak/strong topics)

    Response:
        200: Exam context data
        404: Course not found
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Verify course exists
        course = fetch_one(
            "SELECT course_id, title FROM courses WHERE course_id = %s",
            (course_id,)
        )

        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get exam context using detector
        context = get_exam_context_sync(UUID(user_id), UUID(course_id))

        return jsonify({
            'success': True,
            'context': context
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get exam context',
            'details': str(e)
        }), 500
