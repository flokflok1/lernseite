"""
LernsystemX Agent API - Core Endpoints

Core agent endpoints for asking questions and managing configuration:
- POST   /api/v1/agents/:course_id/ask     - Ask the agent a question (text)
- GET    /api/v1/agents/:course_id/status  - Get agent status
- GET    /api/v1/agents/:course_id/config  - Get agent configuration
- PUT    /api/v1/agents/:course_id/config  - Update agent configuration (admin)

ISO 9001:2015 compliant - Agent Core Layer
Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.agent import (
    AgentAskRequest,
    AgentAskResponse,
    AgentConfigUpdate,
    AgentStatusResponse
)
from app.services.agent_service import AgentService
from app.repositories.agent import AgentRepository
from app.middleware.auth import token_required, role_required, get_current_user

from app.api.system_features.agents._helpers import validate_course_exists, check_course_authorization, error_response

# Blueprint for core agent endpoints
agents_core_bp = Blueprint('agents_core', __name__, url_prefix='/agents')


@agents_core_bp.route('/<course_id>/ask', methods=['POST'])
@token_required
def agent_ask(course_id: str):
    """
    Ask the course agent a question

    Request Body:
        question: str (required) - The question to ask
        context: dict (optional) - Context information (lesson_id, etc.)
        language: str (optional) - Response language (default: de)

    Response:
        200: Agent response with answer and metadata
        400: Invalid request
        404: Course not found
        500: Server error
    """
    try:
        # Get current user
        user = get_current_user()
        if not user:
            return error_response('Authentication required', code=401)

        # Validate course exists
        course, err = validate_course_exists(course_id)
        if err:
            return err

        # Parse and validate request
        try:
            data = AgentAskRequest(**request.get_json())
        except ValidationError as e:
            return error_response('Invalid request', details=e.errors(), code=400)

        # Get organization_id from user if available
        # Note: Database uses American spelling 'organization_id'
        organization_id = user.get('organization_id')

        # Ask the agent
        result = AgentService.ask(
            course_id=course_id,
            user_id=str(user['user_id']),
            question=data.question,
            context=data.context,
            language=data.language,
            organization_id=organization_id
        )

        # Build response
        response = AgentAskResponse(
            answer=result.get('answer', ''),
            source=result.get('source', 'error'),
            tokens_used=result.get('tokens_used', 0),
            tokens_saved=result.get('tokens_saved', 0),
            was_offline_mode=result.get('was_offline_mode', False),
            agent_id=result.get('agent_id', ''),
            knowledge_id=result.get('knowledge_id'),
            query_id=result.get('query_id'),
            offline_message=result.get('offline_message'),
            model=result.get('model'),
            provider=result.get('provider'),
            used_fallback=result.get('used_fallback', False),
            error=result.get('error')
        )

        return jsonify({
            'success': True,
            'data': response.model_dump()
        }), 200

    except Exception as e:
        return error_response('Failed to process agent request', details=str(e))


@agents_core_bp.route('/<course_id>/status', methods=['GET'])
@token_required
def agent_status(course_id: str):
    """
    Get agent status for a course

    Response:
        200: Agent status with statistics
        404: Course not found
    """
    try:
        # Validate course exists
        course, err = validate_course_exists(course_id)
        if err:
            return err

        # Get status
        status = AgentService.get_status(course_id)

        response = AgentStatusResponse(**status)

        return jsonify({
            'success': True,
            'data': response.model_dump()
        }), 200

    except Exception as e:
        return error_response('Failed to get agent status', details=str(e))


@agents_core_bp.route('/<course_id>/config', methods=['GET'])
@token_required
def get_agent_config(course_id: str):
    """
    Get agent configuration for a course

    Response:
        200: Agent configuration
        404: Course or agent not found
    """
    try:
        # Validate course exists
        course, err = validate_course_exists(course_id)
        if err:
            return err

        # Get agent
        agent = AgentRepository.get_agent_by_course(course_id)
        if not agent:
            return error_response('Agent not found for this course', code=404)

        return jsonify({
            'success': True,
            'data': agent
        }), 200

    except Exception as e:
        return error_response('Failed to get agent config', details=str(e))


@agents_core_bp.route('/<course_id>/config', methods=['PUT'])
@role_required('creator', 'teacher', 'school_admin', 'company_admin', 'admin', 'superadmin')
def update_agent_config(course_id: str):
    """
    Update agent configuration

    Request Body:
        name: str (optional) - Agent name
        persona: str (optional) - Agent persona
        language: str (optional) - Response language
        primary_provider: str (optional) - Primary AI provider
        primary_model: str (optional) - Primary AI model
        temperature: float (optional) - AI temperature (0-2)
        max_tokens: int (optional) - Max response tokens

    Response:
        200: Updated agent configuration
        400: Invalid request
        403: Not authorized
        404: Course not found
    """
    try:
        user = get_current_user()

        # Validate course exists and user has access
        course, err = validate_course_exists(course_id)
        if err:
            return err

        # Check authorization
        authorized, err = check_course_authorization(course, user)
        if not authorized:
            return err

        # Parse and validate request
        try:
            data = AgentConfigUpdate(**request.get_json())
        except ValidationError as e:
            return error_response('Invalid request', details=e.errors(), code=400)

        # Update config
        updated = AgentService.update_config(
            course_id=course_id,
            **data.model_dump(exclude_none=True)
        )

        return jsonify({
            'success': True,
            'data': updated
        }), 200

    except Exception as e:
        return error_response('Failed to update agent config', details=str(e))
