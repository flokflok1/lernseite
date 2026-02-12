"""
Learning Journal - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

learning_journal_bp = Blueprint('learning_journal', __name__, url_prefix='/collaboration/learning-journal')

@learning_journal_bp.route('/entry', methods=['POST'])
@token_required
def create_entry():
    return success_response(data={"status": "stub"}, status_code=501)
