"""
Code Sandbox - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

code_sandbox_bp = Blueprint('code_sandbox', __name__, url_prefix='/it-environments/code-sandbox')

@code_sandbox_bp.route('/create', methods=['POST'])
@token_required
def create_sandbox():
    return success_response(data={"status": "stub"}, status_code=501)
