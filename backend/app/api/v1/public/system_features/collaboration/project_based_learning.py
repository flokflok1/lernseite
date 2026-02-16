"""
Project-Based Learning - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

project_based_learning_bp = Blueprint('project_based_learning', __name__, url_prefix='/collaboration/project-based')

@project_based_learning_bp.route('/project', methods=['POST'])
@token_required
def create_project():
    return success_response(data={"status": "stub"}, status_code=501)
