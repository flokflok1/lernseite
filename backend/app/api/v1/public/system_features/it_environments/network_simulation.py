"""
Network Simulation - System Feature

⚠️ STUB ONLY - TODO: Implementation
"""
from flask import Blueprint
from app.api.middleware.auth import token_required
from app.api.responses.responses import success_response

network_simulation_bp = Blueprint('network_simulation', __name__, url_prefix='/it-environments/network-simulation')

@network_simulation_bp.route('/simulate', methods=['POST'])
@token_required
def start_simulation():
    return success_response(data={"status": "stub"}, status_code=501)
