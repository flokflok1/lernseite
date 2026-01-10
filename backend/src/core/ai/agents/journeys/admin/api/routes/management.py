"""
LernsystemX Agent API - Admin Endpoints

Admin-only endpoints for agent management and statistics:
- GET    /api/v1/admin/agents             - List all agents with statistics
- GET    /api/v1/admin/agents/:agent_id/stats - Get detailed agent statistics

ISO 9001:2015 compliant - Agent Admin Layer
Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

from flask import Blueprint, request, jsonify

from app.repositories.agent import AgentRepository
from app.middleware.auth import role_required

from app.api.system_features.agents._helpers import error_response

# Blueprint for admin agent endpoints
agents_admin_bp = Blueprint('agents_admin', __name__, url_prefix='/admin/agents')


@agents_admin_bp.route('', methods=['GET'])
@role_required('admin', 'superadmin')
def list_all_agents():
    """
    List all agents with statistics (admin only)

    Query Parameters:
        limit: int (optional) - Max results (default: 50)
        offset: int (optional) - Pagination offset
        status: str (optional) - Filter by knowledge status

    Response:
        200: List of agents with stats
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        status = request.args.get('status')

        agents = AgentRepository.get_all_agents_stats(
            limit=min(limit, 100),
            offset=offset,
            status=status
        )

        return jsonify({
            'success': True,
            'data': agents,
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        }), 200

    except Exception as e:
        return error_response('Failed to list agents', details=str(e))


@agents_admin_bp.route('/<agent_id>/stats', methods=['GET'])
@role_required('admin', 'superadmin')
def get_agent_stats(agent_id: str):
    """
    Get detailed agent statistics (admin only)

    Response:
        200: Agent statistics
        404: Agent not found
    """
    try:
        stats = AgentRepository.get_agent_stats(agent_id)

        if not stats:
            return error_response('Agent not found', code=404)

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        return error_response('Failed to get agent stats', details=str(e))
