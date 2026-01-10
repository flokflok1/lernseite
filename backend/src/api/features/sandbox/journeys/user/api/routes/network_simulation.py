"""IT Environments - Network Simulation Routes (User Journey)

Endpoints:
  POST /it-environments/network/create - Create network topology
  GET  /it-environments/network/:topology_id - Get topology
  GET  /it-environments/network/my-topologies - List user's topologies

Phase: 5.3.4 - IT Environments Domain
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field
from typing import List, Dict

from src.api.it_environments.core.domain.repositories import ITEnvironmentsRepository


network_simulation_user_bp = Blueprint('it_environments_network_simulation_user', __name__)


class NetworkCreate(BaseModel):
    """Request model for creating network"""
    nodes: List[Dict] = Field(..., min_items=1, max_items=20)
    connections: List[Dict] = Field(...)


@network_simulation_user_bp.route('/it-environments/network/create', methods=['POST'])
@jwt_required()
def create_network():
    """Create network topology"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Request body required"}}), 400

        try:
            network_request = NetworkCreate(**data)
        except Exception as e:
            return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

        topology_data = {"nodes": network_request.nodes, "connections": network_request.connections}
        topology = ITEnvironmentsRepository.create_network_topology(user_id, topology_data)

        return jsonify({"success": True, "data": topology}), 201
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "CREATE_NETWORK_ERROR", "message": str(e)}}), 500


@network_simulation_user_bp.route('/it-environments/network/<topology_id>', methods=['GET'])
@jwt_required()
def get_network(topology_id: str):
    """Get network topology"""
    try:
        topology = ITEnvironmentsRepository.get_network_topology(topology_id)
        if not topology:
            return jsonify({"success": False, "error": {"code": "TOPOLOGY_NOT_FOUND", "message": "Topology not found"}}), 404

        return jsonify({"success": True, "data": topology}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_NETWORK_ERROR", "message": str(e)}}), 500


@network_simulation_user_bp.route('/it-environments/network/my-topologies', methods=['GET'])
@jwt_required()
def list_my_topologies():
    """List user's network topologies"""
    try:
        user_id = get_jwt_identity()
        topologies = ITEnvironmentsRepository.get_user_topologies(user_id)
        return jsonify({"success": True, "data": {"topologies": topologies, "total": len(topologies)}}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "LIST_TOPOLOGIES_ERROR", "message": str(e)}}), 500


__all__ = ['network_simulation_user_bp']
