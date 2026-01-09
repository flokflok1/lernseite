"""
User Profile Exam Settings Endpoints (User).

Endpoints:
- GET  /api/v1/user-profile/exam-settings - Get user's exam profile
- PUT  /api/v1/user-profile/exam-settings - Update user's exam profile
"""

from flask import Blueprint, request, jsonify

from app.middleware.auth import token_required, get_current_user
from app.database.connection import fetch_one


exam_user_profile_bp = Blueprint(
    'exam_user_profile',
    __name__,
    url_prefix='/user-profile'
)


@exam_user_profile_bp.route('/exam-settings', methods=['GET'])
@token_required
def get_user_exam_settings():
    """
    Get user's exam-related profile settings.

    Response:
        200: User exam profile
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        profile = fetch_one(
            """
            SELECT
                profession, profession_detail, training_year,
                target_exam, exam_date, region, ihk,
                detected_profession, detected_level, detection_confidence,
                preferred_difficulty, preferred_question_types
            FROM user_profiles
            WHERE user_id = %s
            """,
            (user_id,)
        )

        if not profile:
            # Return empty profile
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


@exam_user_profile_bp.route('/exam-settings', methods=['PUT'])
@token_required
def update_user_exam_settings():
    """
    Update user's exam-related profile settings.

    Request Body:
        {
            "profession": "FISI",
            "target_exam": "AP1",
            "region": "Baden-Württemberg",
            "preferred_difficulty": "realistic",
            ...
        }

    Response:
        200: Profile updated
    """
    try:
        user = get_current_user()
        user_id = user['user_id']
        data = request.get_json()

        # Check if profile exists
        existing = fetch_one(
            "SELECT profile_id FROM user_profiles WHERE user_id = %s",
            (user_id,)
        )

        allowed_fields = [
            'profession', 'profession_detail', 'training_year',
            'training_start_date', 'training_end_date',
            'target_exam', 'exam_date', 'region', 'ihk', 'ihk_code',
            'preferred_difficulty', 'preferred_question_types',
            'daily_learning_goal_minutes'
        ]

        if existing:
            # Update existing
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
                query = f"""
                    UPDATE user_profiles
                    SET {', '.join(set_parts)}
                    WHERE user_id = %s
                    RETURNING *
                """
                values.append(user_id)
                result = fetch_one(query, tuple(values))
            else:
                result = existing
        else:
            # Insert new
            fields = ['user_id']
            placeholders = ['%s']
            values = [user_id]

            for field in allowed_fields:
                if field in data:
                    fields.append(field)
                    placeholders.append('%s')
                    values.append(data[field])

            query = f"""
                INSERT INTO user_profiles ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """
            result = fetch_one(query, tuple(values))

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
