"""Gamification - Adaptive Difficulty Routes (User Journey)

ELO-based difficulty rating system.

Endpoints:
  GET  /gamification/difficulty - Get current difficulty rating
  POST /gamification/difficulty/update - Update after task completion

Phase: 5.3.3 - Gamification Domain
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field
from decimal import Decimal

from src.api.gamification.core.domain.repositories import GamificationRepository
from src.api.gamification.core.domain.value_objects import DifficultyRating


adaptive_difficulty_user_bp = Blueprint('gamification_adaptive_difficulty_user', __name__)


class DifficultyUpdate(BaseModel):
    """Request model for difficulty update"""
    task_difficulty: int = Field(..., ge=1000, le=3000, description="Task difficulty rating (1000-3000)")
    score: float = Field(..., ge=0.0, le=1.0, description="User score (0=fail, 0.5=partial, 1=success)")
    domain: str = Field("general", description="Domain (general, math, programming, etc.)")


@adaptive_difficulty_user_bp.route('/gamification/difficulty', methods=['GET'])
@jwt_required()
def get_difficulty_rating():
    """Get user's current difficulty rating"""
    try:
        user_id = get_jwt_identity()
        domain = request.args.get('domain', 'general')

        difficulty_data = GamificationRepository.get_user_difficulty(user_id, domain)

        if not difficulty_data:
            # Initialize with default rating
            rating = DifficultyRating.initial()
            difficulty_data = {
                'rating': rating.rating,
                'k_factor': rating.k_factor,
                'domain': domain
            }

        difficulty = DifficultyRating(rating=difficulty_data['rating'], k_factor=difficulty_data.get('k_factor', 32))

        return jsonify({
            "success": True,
            "data": {
                "rating": difficulty.rating,
                "difficulty_level": difficulty.get_difficulty_level(),
                "k_factor": difficulty.k_factor,
                "domain": domain
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_DIFFICULTY_ERROR", "message": str(e)}}), 500


@adaptive_difficulty_user_bp.route('/gamification/difficulty/update', methods=['POST'])
@jwt_required()
def update_difficulty_rating():
    """Update difficulty rating after task completion (ELO algorithm)"""
    try:
        user_id = get_jwt_identity()

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Request body required"}}), 400

        try:
            update_request = DifficultyUpdate(**data)
        except Exception as e:
            return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

        # Get current rating
        difficulty_data = GamificationRepository.get_user_difficulty(user_id, update_request.domain)

        if difficulty_data:
            current_rating = DifficultyRating(rating=difficulty_data['rating'], k_factor=difficulty_data.get('k_factor', 32))
        else:
            current_rating = DifficultyRating.initial()

        # Calculate new rating using ELO
        new_rating = current_rating.calculate_new_rating(
            opponent_rating=update_request.task_difficulty,
            actual_score=Decimal(str(update_request.score))
        )

        # Save to database
        GamificationRepository.update_difficulty_rating(user_id, update_request.domain, new_rating.rating)

        return jsonify({
            "success": True,
            "data": {
                "old_rating": current_rating.rating,
                "new_rating": new_rating.rating,
                "rating_change": new_rating.rating - current_rating.rating,
                "difficulty_level": new_rating.get_difficulty_level()
            }
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "UPDATE_DIFFICULTY_ERROR", "message": str(e)}}), 500


__all__ = ['adaptive_difficulty_user_bp']
