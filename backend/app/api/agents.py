"""
LernsystemX Smart Agent API

Course agent endpoints for intelligent Q&A:
- POST   /api/v1/agents/:course_id/ask         - Ask the agent a question (text)
- POST   /api/v1/agents/:course_id/ask/audio   - Ask with TTS audio response
- POST   /api/v1/agents/:course_id/ask/voice   - Ask via voice (transcribe + respond + TTS)
- GET    /api/v1/agents/:course_id/status      - Get agent status
- PUT    /api/v1/agents/:course_id/config      - Update agent config (admin)
- POST   /api/v1/agents/:course_id/warm        - Warm up agent cache (admin)
- POST   /api/v1/agents/:course_id/feedback    - Submit feedback
- POST   /api/v1/agents/:course_id/knowledge   - Add knowledge entry (admin)
- DELETE /api/v1/agents/:course_id/cache       - Invalidate cache (admin)
- GET    /api/v1/agents/:course_id/media/stats - Get media cache statistics

ISO 9001:2015 compliant - Agent API layer
"""

import os
from flask import request, jsonify, g, send_file
from pydantic import ValidationError
from werkzeug.utils import secure_filename

from app.api import api_v1
from app.models.agent import (
    AgentAskRequest,
    AgentAskResponse,
    AgentFeedbackRequest,
    AgentConfigUpdate,
    AgentStatusResponse,
    KnowledgeCreateRequest,
    AgentWarmRequest
)
from app.services.agent_service import AgentService
from app.services.media_cache_service import MediaCacheService
from app.repositories.agent_repository import AgentRepository
from app.repositories.course_repository import CourseRepository
from app.middleware.auth import token_required, role_required, get_current_user

# Temporary upload path for voice recordings
UPLOAD_TEMP_PATH = os.getenv('UPLOAD_TEMP_PATH', 'storage/temp')


# ============================================================================
# AGENT ENDPOINTS
# ============================================================================

@api_v1.route('/agents/<course_id>/ask', methods=['POST'])
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
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401

        # Validate course exists
        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Parse and validate request
        try:
            data = AgentAskRequest(**request.get_json())
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'details': e.errors()
            }), 400

        # Get organization_id from user if available
        # Note: Database uses American spelling 'organization_id'
        organisation_id = user.get('organization_id')

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
        return jsonify({
            'success': False,
            'error': 'Failed to process agent request',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/status', methods=['GET'])
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
        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get status
        status = AgentService.get_status(course_id)

        response = AgentStatusResponse(**status)

        return jsonify({
            'success': True,
            'data': response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get agent status',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/config', methods=['GET'])
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
        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get agent
        agent = AgentRepository.get_agent_by_course(course_id)
        if not agent:
            return jsonify({
                'success': False,
                'error': 'Agent not found for this course'
            }), 404

        return jsonify({
            'success': True,
            'data': agent
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get agent config',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/config', methods=['PUT'])
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
        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Check if user is course owner or admin
        is_owner = str(course.get('creator_id')) == str(user.get('user_id'))
        is_admin = user.get('role') in ['admin', 'superadmin']

        if not is_owner and not is_admin:
            return jsonify({
                'success': False,
                'error': 'Not authorized to modify this agent'
            }), 403

        # Parse and validate request
        try:
            data = AgentConfigUpdate(**request.get_json())
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'details': e.errors()
            }), 400

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
        return jsonify({
            'success': False,
            'error': 'Failed to update agent config',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/feedback', methods=['POST'])
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
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'details': e.errors()
            }), 400

        # Submit feedback
        success = AgentService.submit_feedback(
            query_id=data.query_id,
            rating=data.rating,
            helpful=data.helpful,
            feedback_text=data.feedback_text
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to submit feedback - query not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to submit feedback',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/knowledge', methods=['POST'])
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
        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Check authorization
        is_owner = str(course.get('creator_id')) == str(user.get('user_id'))
        is_admin = user.get('role') in ['admin', 'superadmin']

        if not is_owner and not is_admin:
            return jsonify({
                'success': False,
                'error': 'Not authorized to add knowledge to this agent'
            }), 403

        # Parse and validate request
        try:
            data = KnowledgeCreateRequest(**request.get_json())
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'details': e.errors()
            }), 400

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
        return jsonify({
            'success': False,
            'error': 'Failed to add knowledge',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/cache', methods=['DELETE'])
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
        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Check authorization
        is_owner = str(course.get('creator_id')) == str(user.get('user_id'))
        is_admin = user.get('role') in ['admin', 'superadmin']

        if not is_owner and not is_admin:
            return jsonify({
                'success': False,
                'error': 'Not authorized to invalidate cache'
            }), 403

        # Invalidate cache
        deleted = AgentService.invalidate_cache(course_id)

        return jsonify({
            'success': True,
            'message': f'Cache invalidated successfully',
            'keys_deleted': deleted
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to invalidate cache',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/warm', methods=['POST'])
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
        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Parse request
        try:
            data = AgentWarmRequest(**request.get_json()) if request.get_json() else AgentWarmRequest()
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'details': e.errors()
            }), 400

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
        return jsonify({
            'success': False,
            'error': 'Failed to start warm-up job',
            'details': str(e)
        }), 500


# ============================================================================
# AGENT STATS ENDPOINTS (Admin)
# ============================================================================

@api_v1.route('/admin/agents', methods=['GET'])
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
        return jsonify({
            'success': False,
            'error': 'Failed to list agents',
            'details': str(e)
        }), 500


@api_v1.route('/admin/agents/<agent_id>/stats', methods=['GET'])
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
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get agent stats',
            'details': str(e)
        }), 500


# ============================================================================
# AUDIO/VOICE ENDPOINTS
# ============================================================================

@api_v1.route('/agents/<course_id>/ask/audio', methods=['POST'])
@token_required
def agent_ask_with_audio(course_id: str):
    """
    Ask the agent with TTS audio response

    Request Body:
        question: str (required) - The question to ask
        context: dict (optional) - Context information
        language: str (optional) - Response language (default: de)
        voice: str (optional) - TTS voice (nova, alloy, echo, fable, onyx, shimmer)
        speed: float (optional) - Speech speed (0.25-4.0, default: 1.0)

    Response:
        200: Agent response with text and audio URL
        400: Invalid request
        404: Course not found
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401

        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        data = request.get_json()
        question = data.get('question', '').strip()

        if not question or len(question) < 3:
            return jsonify({
                'success': False,
                'error': 'Question must be at least 3 characters'
            }), 400

        result = AgentService.ask_with_audio(
            course_id=course_id,
            user_id=str(user['user_id']),
            question=question,
            context=data.get('context'),
            language=data.get('language', 'de'),
            organisation_id=user.get('organization_id'),
            voice=data.get('voice', 'nova'),
            speech_speed=float(data.get('speed', 1.0))
        )

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to process audio request',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/ask/voice', methods=['POST'])
@token_required
def agent_ask_voice(course_id: str):
    """
    Voice-to-Voice: Upload audio question, get audio response

    This endpoint:
    1. Transcribes the uploaded audio (with caching)
    2. Gets the agent's text response (with caching)
    3. Generates TTS audio response (with caching)

    Request:
        audio: file (required) - Audio file (mp3, wav, webm, m4a)
        voice: str (optional) - Response voice
        language: str (optional) - Language hint

    Response:
        200: {
            user_text: str,
            agent_text: str,
            audio_url: str,
            transcription_from_cache: bool,
            response_from_cache: bool,
            tts_from_cache: bool
        }
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401

        course = CourseRepository.get_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Check for audio file
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400

        # Validate file type
        allowed_extensions = {'mp3', 'wav', 'webm', 'm4a', 'ogg', 'flac'}
        ext = audio_file.filename.rsplit('.', 1)[-1].lower() if '.' in audio_file.filename else ''
        if ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'Invalid audio format. Allowed: {", ".join(allowed_extensions)}'
            }), 400

        # Save temporarily
        os.makedirs(UPLOAD_TEMP_PATH, exist_ok=True)
        filename = secure_filename(f"{user['user_id']}_{audio_file.filename}")
        temp_path = os.path.join(UPLOAD_TEMP_PATH, filename)
        audio_file.save(temp_path)

        try:
            # Start or get session
            session = MediaCacheService.start_realtime_session(
                agent_id=str(AgentRepository.get_or_create_agent(course_id)['agent_id']),
                user_id=str(user['user_id']),
                session_type='voice_chat'
            )

            # Process voice turn
            result = AgentService.voice_conversation_turn(
                course_id=course_id,
                user_id=str(user['user_id']),
                audio_path=temp_path,
                session=session,
                voice=request.form.get('voice', 'nova'),
                language=request.form.get('language', 'de')
            )

            return jsonify({
                'success': True,
                'data': result
            }), 200

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to process voice request',
            'details': str(e)
        }), 500


@api_v1.route('/agents/<course_id>/media/stats', methods=['GET'])
@token_required
def get_agent_media_stats(course_id: str):
    """
    Get media cache statistics for a course agent

    Response:
        200: {
            tts_cached: int,
            tts_accesses: int,
            videos_cached: int,
            transcripts_cached: int,
            total_storage_mb: float,
            estimated_savings_eur: float
        }
    """
    try:
        agent = AgentRepository.get_agent_by_course(course_id)
        if not agent:
            return jsonify({
                'success': True,
                'data': {
                    'tts_cached': 0,
                    'videos_cached': 0,
                    'transcripts_cached': 0,
                    'total_storage_mb': 0,
                    'estimated_savings_eur': 0
                }
            }), 200

        stats = MediaCacheService.get_cache_stats(agent['agent_id'])

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get media stats',
            'details': str(e)
        }), 500


@api_v1.route('/media/tts/<media_id>', methods=['GET'])
@token_required
def serve_tts_audio(media_id: str):
    """
    Serve cached TTS audio file

    Response:
        200: Audio file (audio/mpeg)
        404: Media not found
    """
    try:
        # Get media path from database
        from app.services.media_cache_service import MediaCacheRepository

        query = """
            SELECT storage_path, mime_type
            FROM agent_media_cache
            WHERE media_id = %s AND status = 'ready'
        """
        result = MediaCacheRepository.fetch_one(query, (media_id,))

        if not result or not os.path.exists(result['storage_path']):
            return jsonify({
                'success': False,
                'error': 'Media not found'
            }), 404

        return send_file(
            result['storage_path'],
            mimetype=result.get('mime_type', 'audio/mpeg'),
            as_attachment=False
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to serve media',
            'details': str(e)
        }), 500
