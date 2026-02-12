"""
Daily Recall - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

daily_recall_bp = Blueprint('daily_recall', __name__, url_prefix='/gamification/daily-recall')

@daily_recall_bp.route('/questions', methods=['GET'])
@token_required
def get_daily_questions():
    return success_response(data={"status": "stub"}, status_code=501)
