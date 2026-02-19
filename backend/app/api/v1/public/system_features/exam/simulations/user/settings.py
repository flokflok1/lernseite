"""
LernsystemX Exam Simulations - User Settings API

User exam profile and settings management.

Endpoints (2 total):
- GET /user-profile/exam-settings - Get user's exam profile
- PUT /user-profile/exam-settings - Update user's exam profile

ISO 9001:2015 compliant - Assessment & Evaluation Layer
Split from: exam_simulations.py (Part 3/3 - User Exam Profile)
"""

from flask import Blueprint, request, jsonify

from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.persistence.repositories.exams.simulations import ExamSimulationRepository

settings_bp = Blueprint('exam_user_profile', __name__, url_prefix='/user-profile')


# =============================================================================
# USER EXAM PROFILE ENDPOINTS
# =============================================================================

@settings_bp.route('/exam-settings', methods=['GET'])
@token_required
def get_user_exam_settings():
    """
    Get user's exam-related profile settings.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: User exam profile
             {
                 "profile": {
                     "profession": "FISI",
                     "profession_detail": "Windows Systems",
                     "training_year": 2,
                     "target_exam": "AP1",
                     "exam_date": "2026-06-15",
                     "region": "Baden-Württemberg",
                     "ihk": "IHK Stuttgart",
                     "detected_profession": "FISI",
                     "detected_level": "intermediate",
                     "detection_confidence": 0.92,
                     "preferred_difficulty": "realistic",
                     "preferred_question_types": ["multiple-choice", "single-choice"]
                 }
             }
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        profile = ExamSimulationRepository.get_user_exam_profile(user_id)

        if not profile:
            return jsonify({
                'success': True,
                'profile': {}
            }), 200

        return jsonify({
            'success': True,
            'profile': dict(profile)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get profile',
            'details': str(e)
        }), 500


@settings_bp.route('/exam-settings', methods=['PUT'])
@token_required
def update_user_exam_settings():
    """
    Update user's exam-related profile settings.

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "profession": "FISI",
            "profession_detail": "Windows Systems",
            "training_year": 2,
            "training_start_date": "2024-09-01",
            "training_end_date": "2027-09-01",
            "target_exam": "AP1",
            "exam_date": "2026-06-15",
            "region": "Baden-Württemberg",
            "ihk": "IHK Stuttgart",
            "ihk_code": "BW01",
            "preferred_difficulty": "realistic",
            "preferred_question_types": ["multiple-choice", "single-choice"],
            "daily_learning_goal_minutes": 60
        }

    Response:
        200: Profile updated
             {
                 "success": true,
                 "message": "Profile updated",
                 "profile": {...}
             }
    """
    try:
        user = get_current_user()
        user_id = user['user_id']
        data = request.get_json()

        # Check if profile exists
        existing = ExamSimulationRepository.get_user_profile_id(user_id)

        allowed_fields = [
            'profession', 'profession_detail', 'training_year',
            'training_start_date', 'training_end_date',
            'target_exam', 'exam_date', 'region', 'ihk', 'ihk_code',
            'preferred_difficulty', 'preferred_question_types',
            'daily_learning_goal_minutes'
        ]

        if existing:
            # Update existing profile
            set_parts = []
            values = []
            for field in allowed_fields:
                if field in data:
                    set_parts.append(f"{field} = %s")
                    value = data[field]
                    if isinstance(value, list):
                        value = value  # PostgreSQL arrays
                    values.append(value)

            if set_parts:
                result = ExamSimulationRepository.update_user_profile(
                    user_id, set_parts, values
                )
            else:
                result = existing
        else:
            # Insert new profile
            fields = ['user_id']
            placeholders = ['%s']
            values = [user_id]

            for field in allowed_fields:
                if field in data:
                    fields.append(field)
                    placeholders.append('%s')
                    values.append(data[field])

            result = ExamSimulationRepository.insert_user_profile(
                fields, placeholders, values
            )

        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'profile': dict(result) if result else {}
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update profile',
            'details': str(e)
        }), 500


__all__ = ['exam_user_profile_bp']
