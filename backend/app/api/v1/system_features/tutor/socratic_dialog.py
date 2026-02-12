"""
Socratic Dialog - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

socratic_dialog_bp = Blueprint('socratic_dialog', __name__, url_prefix='/tutor/socratic')

@socratic_dialog_bp.route('/start', methods=['POST'])
@token_required
def start_dialog():
    return success_response(data={"status": "stub", "message": "Socratic Dialog - Coming Soon"}, status_code=501)
