"""Gamification - Daily Recall Routes (User Journey)

Spaced Repetition System using SM2 algorithm.

Endpoints:
  GET  /gamification/recall/due - Get due recall cards
  POST /gamification/recall/:card_id/review - Submit review
  GET  /gamification/recall/stats - Get recall statistics

Phase: 5.3.3 - Gamification Domain
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field
from datetime import datetime

from src.api.gamification.core.domain.repositories import GamificationRepository
from src.api.gamification.core.domain.value_objects import RecallInterval


daily_recall_user_bp = Blueprint('gamification_daily_recall_user', __name__)


class RecallReview(BaseModel):
    """Request model for recall review"""
    quality: int = Field(..., ge=0, le=5, description="Recall quality (0-5)")


@daily_recall_user_bp.route('/gamification/recall/due', methods=['GET'])
@jwt_required()
def get_due_recalls():
    """Get due recall cards for review"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 20))

        due_cards = GamificationRepository.get_due_recalls(user_id, limit)

        return jsonify({
            "success": True,
            "data": {
                "cards": due_cards,
                "total_due": len(due_cards)
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_DUE_RECALLS_ERROR", "message": str(e)}}), 500


@daily_recall_user_bp.route('/gamification/recall/<card_id>/review', methods=['POST'])
@jwt_required()
def submit_recall_review(card_id: str):
    """Submit a recall review and update interval using SM2 algorithm"""
    try:
        user_id = get_jwt_identity()

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Request body required"}}), 400

        try:
            review = RecallReview(**data)
        except Exception as e:
            return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

        # Get current card state (would come from database)
        # For now, create a RecallInterval from defaults
        current_interval = RecallInterval(
            interval_days=1,
            repetition_count=0,
            easiness_factor=Decimal("2.5"),
            next_review_date=datetime.utcnow()
        )

        # Calculate next interval using SM2
        next_interval = current_interval.calculate_next(review.quality)

        # Update in database
        updated_card = GamificationRepository.update_recall_card(
            recall_card_id=card_id,
            interval_days=next_interval.interval_days,
            repetition_count=next_interval.repetition_count,
            easiness_factor=float(next_interval.easiness_factor),
            next_review_date=next_interval.next_review_date
        )

        return jsonify({
            "success": True,
            "data": {
                "card_id": card_id,
                "next_review_date": next_interval.next_review_date.isoformat(),
                "interval_days": next_interval.interval_days,
                "repetition_count": next_interval.repetition_count
            }
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "REVIEW_ERROR", "message": str(e)}}), 500


@daily_recall_user_bp.route('/gamification/recall/stats', methods=['GET'])
@jwt_required()
def get_recall_stats():
    """Get recall statistics for user"""
    try:
        user_id = get_jwt_identity()

        # Get due cards count
        due_cards = GamificationRepository.get_due_recalls(user_id, limit=1000)

        return jsonify({
            "success": True,
            "data": {
                "total_due": len(due_cards),
                "reviewed_today": 0,  # Would calculate from database
                "streak_days": 0  # Would calculate from database
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_STATS_ERROR", "message": str(e)}}), 500


__all__ = ['daily_recall_user_bp']
