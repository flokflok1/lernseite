"""
XP & Quest System - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.responses.responses import success_response

xp_quest_bp = Blueprint('xp_quest', __name__, url_prefix='/gamification/xp-quest')

@xp_quest_bp.route('/status', methods=['GET'])
@token_required
def get_xp_status():
    return success_response(data={"status": "stub"}, status_code=501)
