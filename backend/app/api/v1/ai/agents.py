"""
LernsystemX Agents API - Consolidated

Core Agent Endpoints:
- POST /agents/<course_id>/ask - Ask the agent a question
- GET /agents/<course_id>/status - Get agent status
- GET /agents/<course_id>/config - Get agent configuration
- PUT /agents/<course_id>/config - Update agent configuration (admin)

Admin Agent Management:
- GET /agents/admin/all - List all agents with statistics
- GET /agents/admin/<agent_id>/stats - Get detailed agent statistics

All routes: /api/v1/agents/*
ISO 9001:2015 compliant - Agent Core Layer
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.domain.models.agent import (
    AgentAskRequest,
    AgentAskResponse,
    AgentConfigUpdate,
    AgentStatusResponse
)
from app.application.services.agent import AgentService
from app.infrastructure.persistence.repositories.agent import AgentRepository
from app.infrastructure.persistence.repositories.courses.crud import CourseRepositoryCRUD as CourseRepository
from app.api.middleware.auth import token_required, permission_required, get_current_user

agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

__all__ = ['agents_bp']


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def error_response(message: str, details: str = None, code: int = 500):
    """
    Create standard error response
    """
    response = {
        'success': False,
        'error': message
    }
    if details:
        response['details'] = details
    return jsonify(response), code


def validate_course_exists(course_id: str):
    """
    Validate that a course exists
    Returns (course, error_response) tuple
    """
    course = CourseRepository.find_by_id(course_id)
    if not course:
        return None, error_response('Course not found', code=404)
    return course, None


def check_course_authorization(course: dict, user: dict):
    """
    Check if user is authorized to modify course
    Returns (authorized, error_response) tuple
    """
    # User must be course creator or admin/org_admin (RBAC 2.0: dynamic from DB)
    if course.get('creator_id') != user.get('user_id'):
        from app.application.services.permission_service import PermissionService
        # Check if user can manage any course OR is org admin for same org
        can_manage_any = PermissionService.check_threshold(user, 'courses.edit_any')
        is_org_admin = (
            user.get('hierarchy_level', 0) == 5 and  # school_admin, company_admin
            user.get('organisation_id') == course.get('organisation_id')
        )
        if not (can_manage_any or is_org_admin):
            return False, error_response(
                'Not authorized to modify this course',
                code=403
            )
    return True, None


# =============================================================================
# CORE AGENT ENDPOINTS
# =============================================================================

@agents_bp.route('/<course_id>/ask', methods=['POST'])
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

        # Get organisation_id from user if available
        # Note: Database uses American spelling 'organisation_id'
        organisation_id = user.get('organisation_id')

        # Ask the agent
        result = AgentService.ask(
            course_id=course_id,
            user_id=str(user['user_id']),
            question=data.question,
            context=data.context,
            language=data.language,
            organisation_id=organisation_id
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


@agents_bp.route('/<course_id>/status', methods=['GET'])
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


@agents_bp.route('/<course_id>/config', methods=['GET'])
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


@agents_bp.route('/<course_id>/config', methods=['PUT'])
@permission_required('content.courses:write')
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


# =============================================================================
# ADMIN - AGENT MANAGEMENT
# =============================================================================

@agents_bp.route('/admin/all', methods=['GET'])
@permission_required('admin.system:read')
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


@agents_bp.route('/admin/<agent_id>/stats', methods=['GET'])
@permission_required('admin.system:read')
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
