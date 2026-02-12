"""
Terminal Access - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

terminal_access_bp = Blueprint('terminal_access', __name__, url_prefix='/it-environments/terminal-access')

@terminal_access_bp.route('/session', methods=['POST'])
@token_required
def create_session():
    return success_response(data={"status": "stub"}, status_code=501)
