"""
LernsystemX Agent API - Knowledge Management Endpoints

Endpoints for managing agent knowledge and feedback:
- POST   /api/v1/agents/:course_id/feedback    - Submit feedback for agent response
- POST   /api/v1/agents/:course_id/knowledge   - Add knowledge entry (admin)
- DELETE /api/v1/agents/:course_id/cache       - Invalidate cache (admin)
- POST   /api/v1/agents/:course_id/warm        - Warm up agent cache (admin)

ISO 9001:2015 compliant - Agent Knowledge Layer
Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.agent import (
    AgentFeedbackRequest,
    KnowledgeCreateRequest,
    AgentWarmRequest
)
from app.services.agent_service import AgentService
from app.repositories.agent import AgentRepository
from app.middleware.auth import token_required, role_required, get_current_user

from app.api.system_features.agents._helpers import validate_course_exists, check_course_authorization, error_response

# Blueprint for knowledge management endpoints
agents_knowledge_bp = Blueprint('agents_knowledge', __name__, url_prefix='/agents')


@agents_knowledge_bp.route('/<course_id>/feedback', methods=['POST'])
@token_required
def submit_agent_feedback(course_id: str):
    """
    Submit feedback for an agent response

    Request Body:
        query_id: str (required) - Query ID from agent response
        rating: int (required) - Rating (1-5)
        helpful: bool (optional) - Was the response helpful?
        feedback_text: str (optional) - Additional feedback

    Response:
        200: Feedback submitted
        400: Invalid request
    """
    try:
        # Parse and validate request
        try:
            data = AgentFeedbackRequest(**request.get_json())
        except ValidationError as e:
            return error_response('Invalid request', details=e.errors(), code=400)

        # Submit feedback
        success = AgentService.submit_feedback(
            query_id=data.query_id,
            rating=data.rating,
            helpful=data.helpful,
            feedback_text=data.feedback_text
        )

        if not success:
            return error_response('Failed to submit feedback - query not found', code=404)

        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        }), 200

    except Exception as e:
        return error_response('Failed to submit feedback', details=str(e))


@agents_knowledge_bp.route('/<course_id>/knowledge', methods=['POST'])
@role_required('creator', 'teacher', 'school_admin', 'company_admin', 'admin', 'superadmin')
def add_agent_knowledge(course_id: str):
    """
    Manually add knowledge to agent

    Request Body:
        question: str (required) - Question text
        answer: str (required) - Answer text
        scope_type: str (optional) - Scope type (course, chapter, lesson)
        scope_id: str (optional) - Scope ID
        knowledge_type: str (optional) - Knowledge type

    Response:
        201: Knowledge entry created
        400: Invalid request
        403: Not authorized
        404: Course not found
    """
    try:
        user = get_current_user()

        # Validate course exists
        course, err = validate_course_exists(course_id)
        if err:
            return err

        # Check authorization
        authorized, err = check_course_authorization(course, user)
        if not authorized:
            return err

        # Parse and validate request
        try:
            data = KnowledgeCreateRequest(**request.get_json())
        except ValidationError as e:
            return error_response('Invalid request', details=e.errors(), code=400)

        # Add knowledge
        knowledge = AgentService.add_knowledge(
            course_id=course_id,
            question=data.question,
            answer=data.answer,
            scope_type=data.scope_type.value,
            scope_id=data.scope_id or course_id,
            knowledge_type=data.knowledge_type.value
        )

        return jsonify({
            'success': True,
            'data': knowledge
        }), 201

    except Exception as e:
        return error_response('Failed to add knowledge', details=str(e))


@agents_knowledge_bp.route('/<course_id>/cache', methods=['DELETE'])
@role_required('creator', 'teacher', 'school_admin', 'company_admin', 'admin', 'superadmin')
def invalidate_agent_cache(course_id: str):
    """
    Invalidate agent cache for a course

    Response:
        200: Cache invalidated
        403: Not authorized
        404: Course not found
    """
    try:
        user = get_current_user()

        # Validate course exists
        course, err = validate_course_exists(course_id)
        if err:
            return err

        # Check authorization
        authorized, err = check_course_authorization(course, user)
        if not authorized:
            return err

        # Invalidate cache
        deleted = AgentService.invalidate_cache(course_id)

        return jsonify({
            'success': True,
            'message': 'Cache invalidated successfully',
            'keys_deleted': deleted
        }), 200

    except Exception as e:
        return error_response('Failed to invalidate cache', details=str(e))


@agents_knowledge_bp.route('/<course_id>/warm', methods=['POST'])
@role_required('admin', 'superadmin')
def warm_agent_cache(course_id: str):
    """
    Warm up agent cache (admin only)

    Request Body:
        tier: int (optional) - Cache tier to warm (1-3)
        force: bool (optional) - Force regeneration

    Response:
        200: Warm-up job started
        403: Not authorized
        404: Course not found
    """
    try:
        # Validate course exists
        course, err = validate_course_exists(course_id)
        if err:
            return err

        # Parse request
        try:
            data = AgentWarmRequest(**request.get_json()) if request.get_json() else AgentWarmRequest()
        except ValidationError as e:
            return error_response('Invalid request', details=e.errors(), code=400)

        # Get agent
        agent = AgentRepository.get_or_create_agent(course_id)

        # Create warm job
        job = AgentRepository.create_warm_job(
            agent_id=agent['agent_id'],
            job_type='full_warm' if not data.tier else f'tier_{data.tier}',
            target_tier=data.tier,
            total_items=0  # Will be updated by celery task
        )

        # TODO: Trigger Celery task for actual warming
        # from app.tasks.agent_tasks import warm_agent_knowledge
        # warm_agent_knowledge.delay(agent['agent_id'], job['job_id'], data.tier)

        return jsonify({
            'success': True,
            'message': 'Warm-up job started',
            'data': {
                'job_id': job['job_id'],
                'agent_id': agent['agent_id'],
                'status': job['status']
            }
        }), 200

    except Exception as e:
        return error_response('Failed to start warm-up job', details=str(e))
