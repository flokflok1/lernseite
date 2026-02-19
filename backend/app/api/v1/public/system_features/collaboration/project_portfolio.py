"""
Project Portfolio - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.responses.responses import success_response

project_portfolio_bp = Blueprint('project_portfolio', __name__, url_prefix='/collaboration/project-portfolio')

@project_portfolio_bp.route('/create', methods=['POST'])
@token_required
def create_portfolio():
    return success_response(data={"status": "stub"}, status_code=501)
