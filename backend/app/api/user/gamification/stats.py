"""
LernsystemX Gamification API - User Stats

Endpoints:
- GET /api/v1/gamification/me - Get current user's gamification data

ISO 27001:2013 compliant - User gamification data
"""

from flask import Blueprint, jsonify

from app.middleware.auth import token_required, get_current_user
from app.repositories.gamification import UserGamificationRepository


gamification_stats_bp = Blueprint('gamification_stats', __name__, url_prefix='/gamification')


@gamification_stats_bp.route('/me', methods=['GET'])
@token_required
def get_my_gamification_data():
    """
    Get current user's gamification data (XP, Level, Skills, Achievements)

    Response:
        200: Gamification data
        500: Server error
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Get complete gamification data from DB
        gamification_data = UserGamificationRepository.get_user_gamification_data(user_id)

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


@gamification_stats_bp.route('/stats', methods=['GET'])
@token_required
def get_my_stats():
    """
    Get current user's basic stats (XP, Level only)

    Response:
        200: Stats data
        500: Server error
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Get stats from DB
        stats = UserGamificationRepository.get_user_stats(user_id)

        # If no stats, create default
        if not stats:
            stats = UserGamificationRepository.create_default_stats(user_id)

        return jsonify({
            'success': True,
            'stats': {
                'level': stats.get('current_level', 1),
                'xp': stats.get('total_xp', 0),
                'xpToNext': stats.get('xp_to_next_level', 100)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get stats',
            'details': str(e)
        }), 500


@gamification_stats_bp.route('/skills', methods=['GET'])
@token_required
def get_my_skills():
    """
    Get current user's skills (Strength, Intelligence, Stamina)

    Response:
        200: Skills data
        500: Server error
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Get skills from DB
        skills = UserGamificationRepository.get_user_skills(user_id)

        # Calculate base stats from skills
        base_stats = {
            'strength': 0,
            'intelligence': 0,
            'stamina': 0
        }

        for skill in skills:
            category = skill.get('skill_category', '').lower()
            if 'strength' in category or 'code' in category:
                base_stats['strength'] += 1
            elif 'intelligence' in category or 'logic' in category:
                base_stats['intelligence'] += 1
            elif 'stamina' in category or 'endurance' in category:
                base_stats['stamina'] += 1

        return jsonify({
            'success': True,
            'baseStats': base_stats,
            'skills': skills
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get skills',
            'details': str(e)
        }), 500


@gamification_stats_bp.route('/achievements', methods=['GET'])
@token_required
def get_my_achievements():
    """
    Get current user's achievements

    Response:
        200: Achievements data
        500: Server error
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Get achievements from DB
        achievements = UserGamificationRepository.get_user_achievements(user_id)

        return jsonify({
            'success': True,
            'achievements': achievements
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get achievements',
            'details': str(e)
        }), 500
