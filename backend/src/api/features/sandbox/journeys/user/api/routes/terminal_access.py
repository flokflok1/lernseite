"""IT Environments - Terminal Access Routes (User Journey)

Endpoints:
  POST /it-environments/terminal/create - Create terminal session
  POST /it-environments/terminal/:session_id/execute - Execute command
  GET  /it-environments/terminal/:session_id - Get session status
  DELETE /it-environments/terminal/:session_id - Close session

Phase: 5.3.4 - IT Environments Domain
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field

from src.api.it_environments.core.domain.repositories import ITEnvironmentsRepository


terminal_access_user_bp = Blueprint('it_environments_terminal_access_user', __name__)


class TerminalCommand(BaseModel):
    """Request model for terminal command"""
    command: str = Field(..., min_length=1)


@terminal_access_user_bp.route('/it-environments/terminal/create', methods=['POST'])
@jwt_required()
def create_terminal():
    """Create terminal session"""
    try:
        user_id = get_jwt_identity()
        shell = request.json.get('shell', 'bash') if request.json else 'bash'

        session = ITEnvironmentsRepository.create_terminal_session(user_id, shell)
        return jsonify({"success": True, "data": session}), 201
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "CREATE_TERMINAL_ERROR", "message": str(e)}}), 500


@terminal_access_user_bp.route('/it-environments/terminal/<session_id>/execute', methods=['POST'])
@jwt_required()
def execute_command(session_id: str):
    """Execute terminal command"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Request body required"}}), 400

        try:
            cmd_request = TerminalCommand(**data)
        except Exception as e:
            return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

        # Here we would actually execute command in isolated environment
        # For now, simulate execution
        output = f"Command executed: {cmd_request.command}"

        # Log command
        log = ITEnvironmentsRepository.log_terminal_command(session_id, cmd_request.command, output)

        return jsonify({"success": True, "data": {"output": output, "log_id": log['log_id']}}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "EXECUTE_COMMAND_ERROR", "message": str(e)}}), 500


@terminal_access_user_bp.route('/it-environments/terminal/<session_id>', methods=['GET'])
@jwt_required()
def get_terminal_session(session_id: str):
    """Get terminal session status"""
    try:
        session = ITEnvironmentsRepository.get_terminal_session(session_id)
        if not session:
            return jsonify({"success": False, "error": {"code": "SESSION_NOT_FOUND", "message": "Session not found"}}), 404

        return jsonify({"success": True, "data": session}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_SESSION_ERROR", "message": str(e)}}), 500


@terminal_access_user_bp.route('/it-environments/terminal/<session_id>', methods=['DELETE'])
@jwt_required()
def close_terminal(session_id: str):
    """Close terminal session"""
    try:
        ITEnvironmentsRepository.close_terminal_session(session_id)
        return jsonify({"success": True, "data": {"session_id": session_id, "status": "closed"}}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "CLOSE_SESSION_ERROR", "message": str(e)}}), 500


__all__ = ['terminal_access_user_bp']
