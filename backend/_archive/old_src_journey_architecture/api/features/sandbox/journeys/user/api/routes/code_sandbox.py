"""IT Environments - Code Sandbox Routes (User Journey)

Endpoints:
  POST /it-environments/sandbox/execute - Execute code
  GET  /it-environments/sandbox/:session_id - Get execution result
  GET  /it-environments/sandbox/languages - Get supported languages

Phase: 5.3.4 - IT Environments Domain
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field

from src.api.it_environments.core.domain.repositories import ITEnvironmentsRepository
from src.api.it_environments.core.domain.value_objects import SandboxLanguage, SandboxStatusEnum


code_sandbox_user_bp = Blueprint('it_environments_code_sandbox_user', __name__)


class CodeExecute(BaseModel):
    """Request model for code execution"""
    language: str = Field(..., description="python, javascript, java, go, cpp, csharp")
    code: str = Field(..., min_length=1, description="Code to execute")


@code_sandbox_user_bp.route('/it-environments/sandbox/execute', methods=['POST'])
@jwt_required()
def execute_code():
    """Execute code in sandbox"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": {"code": "INVALID_REQUEST", "message": "Request body required"}}), 400

        try:
            exec_request = CodeExecute(**data)
        except Exception as e:
            return jsonify({"success": False, "error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 400

        # Create sandbox session
        session = ITEnvironmentsRepository.create_sandbox_session(user_id, exec_request.language, exec_request.code)

        # Here we would actually execute code in isolated environment
        # For now, simulate execution result
        import time
        time.sleep(0.1)  # Simulate execution

        output = f"Code executed successfully in {exec_request.language} sandbox"
        result = ITEnvironmentsRepository.update_sandbox_result(
            session_id=session['session_id'],
            status='completed',
            output=output,
            error=None,
            execution_time_ms=100
        )

        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        return jsonify({"success": False, "error": {"code": "EXECUTE_ERROR", "message": str(e)}}), 500


@code_sandbox_user_bp.route('/it-environments/sandbox/<session_id>', methods=['GET'])
@jwt_required()
def get_sandbox_result(session_id: str):
    """Get sandbox execution result"""
    try:
        session = ITEnvironmentsRepository.get_sandbox_session(session_id)
        if not session:
            return jsonify({"success": False, "error": {"code": "SESSION_NOT_FOUND", "message": "Session not found"}}), 404

        return jsonify({"success": True, "data": session}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"code": "GET_RESULT_ERROR", "message": str(e)}}), 500


@code_sandbox_user_bp.route('/it-environments/sandbox/languages', methods=['GET'])
@jwt_required()
def get_supported_languages():
    """Get supported programming languages"""
    languages = [
        {"language": "python", "version": "3.12", "max_execution_time": 30},
        {"language": "javascript", "version": "20", "max_execution_time": 30},
        {"language": "java", "version": "17", "max_execution_time": 45},
        {"language": "go", "version": "1.21", "max_execution_time": 30},
    ]
    return jsonify({"success": True, "data": {"languages": languages}}), 200


__all__ = ['code_sandbox_user_bp']
