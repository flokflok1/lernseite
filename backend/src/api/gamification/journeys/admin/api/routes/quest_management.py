"""Gamification - Quest Management Routes (Admin Journey)

Endpoints:
  POST /admin/gamification/quests - Create quest
  GET  /admin/gamification/quests - List quests
  POST /admin/gamification/achievements - Create achievement

Phase: 5.3.3 - Gamification Domain
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, Field
from typing import Optional, Dict

from app.middleware.auth import admin_required
from src.api.gamification.core.domain.repositories import GamificationRepository
from src.api.gamification.core.domain.factories import QuestFactory, AchievementFactory


quest_management_bp = Blueprint('gamification_quest_management', __name__)


class QuestCreate(BaseModel):
    """Request model for creating quest"""
    quest_type: str = Field(..., description="daily, weekly, achievement, course, challenge")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    criteria: Dict = Field(...)
    reward_xp: int = Field(100, ge=0)
    reward_tokens: int = Field(0, ge=0)


class AchievementCreate(BaseModel):
    """Request model for creating achievement"""
    achievement_type: str = Field(..., description="bronze, silver, gold, platinum")
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(...)
    criteria: Dict = Field(...)
    reward_xp: int = Field(100, ge=0)
    icon: str = Field("trophy")


@quest_management_bp.route('/admin/gamification/quests', methods=['POST'])
@jwt_required()
@admin_required
def create_quest():
    """Create a new quest"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Request body required"}}), 400

        try:
            quest_request = QuestCreate(**data)
        except Exception as e:
            return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

        # Create quest using factory
        if quest_request.quest_type == 'daily':
            quest_data = QuestFactory.create_daily_quest(
                title=quest_request.title,
                description=quest_request.description or "",
                criteria=quest_request.criteria,
                reward_xp=quest_request.reward_xp
            )
        elif quest_request.quest_type == 'weekly':
            quest_data = QuestFactory.create_weekly_quest(
                title=quest_request.title,
                description=quest_request.description or "",
                criteria=quest_request.criteria,
                reward_xp=quest_request.reward_xp
            )
        else:
            quest_data = {
                'quest_type': quest_request.quest_type,
                'title': quest_request.title,
                'description': quest_request.description,
                'criteria': quest_request.criteria,
                'reward_xp': quest_request.reward_xp,
                'reward_tokens': quest_request.reward_tokens,
                'expires_at': None,
                'is_active': True
            }

        quest = GamificationRepository.create_quest(quest_data)
        return jsonify({"success": True, "data": quest}), 201

    except ValueError as e:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "CREATE_QUEST_ERROR", "message": str(e)}}), 500


@quest_management_bp.route('/admin/gamification/quests', methods=['GET'])
@jwt_required()
@admin_required
def list_quests():
    """List all quests"""
    try:
        quest_type = request.args.get('type')
        quests = GamificationRepository.get_active_quests(quest_type)
        return jsonify({"success": True, "data": {"quests": quests, "total": len(quests)}}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "LIST_QUESTS_ERROR", "message": str(e)}}), 500


@quest_management_bp.route('/admin/gamification/achievements', methods=['POST'])
@jwt_required()
@admin_required
def create_achievement():
    """Create a new achievement"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Request body required"}}), 400

        try:
            achievement_request = AchievementCreate(**data)
        except Exception as e:
            return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

        # Create achievement using factory
        achievement_data = AchievementFactory.create(
            achievement_type=achievement_request.achievement_type,
            name=achievement_request.name,
            description=achievement_request.description,
            criteria=achievement_request.criteria,
            reward_xp=achievement_request.reward_xp,
            icon=achievement_request.icon
        )

        achievement = GamificationRepository.create_achievement(achievement_data)
        return jsonify({"success": True, "data": achievement}), 201

    except ValueError as e:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "CREATE_ACHIEVEMENT_ERROR", "message": str(e)}}), 500


__all__ = ['quest_management_bp']
