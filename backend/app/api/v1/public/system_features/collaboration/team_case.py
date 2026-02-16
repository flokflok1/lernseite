"""
Team Case - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

team_case_bp = Blueprint('team_case', __name__, url_prefix='/collaboration/team-case')

@team_case_bp.route('/create', methods=['POST'])
@token_required
def create_case():
    return success_response(data={"status": "stub"}, status_code=501)
