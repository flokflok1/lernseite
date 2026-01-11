"""Gamification - XP & Quests Routes (User Journey)

Endpoints:
  GET    /gamification/profile - Get XP/Level
  GET    /gamification/quests - Get available quests
  POST   /gamification/quests/:id/start - Start quest
  POST   /gamification/quests/:id/complete - Complete quest
  GET    /gamification/achievements - Get user achievements

Phase: 5.3.3 - Gamification Domain
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal

from src.api.gamification.core.domain.repositories import GamificationRepository
from src.api.gamification.core.domain.value_objects import XPLevel


xp_quests_user_bp = Blueprint('gamification_xp_quests_user', __name__)


@xp_quests_user_bp.route('/gamification/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get user XP/Level profile"""
    try:
        user_id = get_jwt_identity()
        user_xp = GamificationRepository.get_user_xp(user_id)

        if not user_xp:
            # Initialize user XP
            user_xp = {'user_id': user_id, 'xp_total': 0, 'level': 1}

        xp_level = XPLevel.calculate_level(user_xp['xp_total'])

        return jsonify({
            "success": True,
            "data": {
                "xp_total": xp_level.xp_total,
                "level": xp_level.level,
                "xp_current_level": xp_level.xp_current_level,
                "xp_next_level": xp_level.xp_next_level,
                "progress_percentage": float(xp_level.progress_percentage())
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_PROFILE_ERROR", "message": str(e)}}), 500


@xp_quests_user_bp.route('/gamification/quests', methods=['GET'])
@jwt_required()
def get_available_quests():
    """Get available quests"""
    try:
        quest_type = request.args.get('type')
        quests = GamificationRepository.get_active_quests(quest_type)
        return jsonify({"success": True, "data": {"quests": quests, "total": len(quests)}}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_QUESTS_ERROR", "message": str(e)}}), 500


@xp_quests_user_bp.route('/gamification/quests/<quest_id>/start', methods=['POST'])
@jwt_required()
def start_quest(quest_id: str):
    """Start a quest"""
    try:
        user_id = get_jwt_identity()
        result = GamificationRepository.start_quest(user_id, quest_id)
        return jsonify({"success": True, "data": result}), 201
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "START_QUEST_ERROR", "message": str(e)}}), 500


@xp_quests_user_bp.route('/gamification/quests/<quest_id>/complete', methods=['POST'])
@jwt_required()
def complete_quest(quest_id: str):
    """Complete a quest and award XP"""
    try:
        user_id = get_jwt_identity()

        # Get quest to check reward
        progress = GamificationRepository.get_user_quest_progress(user_id, quest_id)
        if not progress or progress['status'] != 'in_progress':
            return jsonify({"success": False, "error": {"code": "QUEST_NOT_IN_PROGRESS", "message": "Quest not in progress"}}), 400

        # Complete quest
        GamificationRepository.complete_quest(user_id, quest_id)

        # Award XP
        reward_xp = progress['reward_xp']
        xp_result = GamificationRepository.add_xp(user_id, reward_xp, f"quest_{quest_id}")

        # Calculate new level
        xp_level = XPLevel.calculate_level(xp_result['xp_total'])

        # Update level if changed
        if xp_level.level != xp_result['level']:
            GamificationRepository.update_level(user_id, xp_level.level)

        return jsonify({
            "success": True,
            "data": {
                "quest_completed": True,
                "reward_xp": reward_xp,
                "new_xp_total": xp_level.xp_total,
                "new_level": xp_level.level,
                "leveled_up": xp_level.level > xp_result['level']
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "COMPLETE_QUEST_ERROR", "message": str(e)}}), 500


@xp_quests_user_bp.route('/gamification/achievements', methods=['GET'])
@jwt_required()
def get_user_achievements():
    """Get user's unlocked achievements"""
    try:
        user_id = get_jwt_identity()
        achievements = GamificationRepository.get_user_achievements(user_id)
        all_achievements = GamificationRepository.get_all_achievements()

        return jsonify({
            "success": True,
            "data": {
                "unlocked": achievements,
                "total_unlocked": len(achievements),
                "total_available": len(all_achievements)
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_ACHIEVEMENTS_ERROR", "message": str(e)}}), 500


__all__ = ['xp_quests_user_bp']
