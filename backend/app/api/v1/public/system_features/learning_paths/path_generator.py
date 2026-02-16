"""
Learning Path Generator - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

path_generator_bp = Blueprint('path_generator', __name__, url_prefix='/learning-paths/path-generator')

@path_generator_bp.route('/generate', methods=['POST'])
@token_required
def generate_path():
    return success_response(data={"status": "stub"}, status_code=501)
