"""
Peer Review - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.utils.responses import success_response

peer_review_bp = Blueprint('peer_review', __name__, url_prefix='/collaboration/peer-review')

@peer_review_bp.route('/submit', methods=['POST'])
@token_required
def submit_review():
    return success_response(data={"status": "stub"}, status_code=501)
