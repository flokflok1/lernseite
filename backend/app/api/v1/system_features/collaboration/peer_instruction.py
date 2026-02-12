"""
Peer Instruction - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

peer_instruction_bp = Blueprint('peer_instruction', __name__, url_prefix='/collaboration/peer-instruction')

@peer_instruction_bp.route('/session', methods=['POST'])
@token_required
def create_session():
    return success_response(data={"status": "stub"}, status_code=501)
