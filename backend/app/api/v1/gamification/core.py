"""
LernsystemX Gamification API

User gamification endpoints (XP, levels, badges, achievements).

Endpoints:
- GET /api/v1/gamification/me - Get current user's gamification data

ISO 27001:2013 compliant
"""

from flask import Blueprint, jsonify
from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.persistence.database import get_db_connection
from app.infrastructure.persistence.repositories.gamification_repository import GamificationRepository

gamification_bp = Blueprint('gamification', __name__, url_prefix='/gamification')


@gamification_bp.route('/me', methods=['GET'])
@token_required
def get_my_gamification():
    """
    Get current user's gamification data (XP, level, badges, achievements)

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: User gamification data
        {
            "xp": 0,
            "level": 1,
            "badges": [],
            "achievements": [],
            "quests": [],
            "stats": {}
        }
    """
    try:
        user = get_current_user()

        # Get gamification data from database
        with get_db_connection() as conn:
            repo = GamificationRepository(conn)
            gamification_data = repo.get_or_create_user_gamification(user['user_id'])

        # Add additional fields for frontend compatibility
        gamification_data.update({
            'total_courses_completed': 0,
            'total_lessons_completed': 0,
            'total_quizzes_completed': 0,
            'badges': [],
            'achievements': [],
            'active_quests': [],
            'completed_quests': [],
            'stats': {
                'login_streak': 0,
                'total_study_time_minutes': 0,
                'favorite_category': None
            }
        })

        return jsonify({
            'success': True,
            'data': gamification_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get gamification data',
            'details': str(e)
        }), 500


__all__ = ['gamification_bp']
