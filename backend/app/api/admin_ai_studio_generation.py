"""
LernsystemX Admin AI Studio - Content Generation API

Source data and content generation endpoints:
- POST   /api/v1/admin/ai-studio/sessions/{id}/source    - Set source data
- POST   /api/v1/admin/ai-studio/sessions/{id}/generate  - Generate content
- POST   /api/v1/admin/ai-studio/sessions/{id}/finalize  - Finalize and create chapter
- POST   /api/v1/admin/ai-studio/upload-pdf              - Upload and analyze PDF
- GET    /api/v1/admin/ai-studio/templates               - Get available templates
- GET    /api/v1/admin/ai-studio/stats                   - Get user stats

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
Module split according to 35_Developer-Guide-KI-Prompts.md guidelines
"""

from flask import request, jsonify, g
from pydantic import ValidationError
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.models.ai_studio import (
    AIStudioSourceDataRequest,
    AIStudioGenerateRequest,
    AIStudioFinalizeRequest
)
from app.repositories.ai_studio_repository import (
    AIStudioRepository,
    AIStudioAnalyticsRepository,
    AIGenerationVariantRepository,
    AIAuthoringTemplateRepository
)
from app.services.ai_studio_service import (
    AiStudioService,
    AiStudioServiceError
)
from app.services.audit_service import AuditService
from app.security.permissions import require_permission, Permissions


# ============================================================================
# Source Data & Content Generation
# ============================================================================

@api_v1.route('/admin/ai-studio/sessions/<session_id>/source', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def set_ai_studio_source(session_id: str):
    """
    Set source data for session

    Request Body:
        {
            "source_type": "pdf",
            "source_data": {
                "text": "Extracted PDF text...",
                "metadata": {...}
            }
        }
    """
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()
        req = AIStudioSourceDataRequest(**data)

        update_data = {
            'source_type': req.source_type.value,
            'source_data': req.source_data
        }

        updated = AIStudioRepository.update_session(session_id, update_data)

        # Mark step as completed
        steps_completed = session.get('steps_completed', [])
        if isinstance(steps_completed, str):
            steps_completed = json.loads(steps_completed)
        if 'source_selection' not in steps_completed:
            steps_completed.append('source_selection')

        AIStudioRepository.update_step(session_id, 'theory_generation', steps_completed)

        # Log analytics
        AIStudioAnalyticsRepository.log_event({
            'session_id': session_id,
            'user_id': user_id,
            'event_type': 'source_set',
            'event_data': {'source_type': req.source_type.value},
            'step_name': 'source_selection'
        })

        return jsonify({
            'success': True,
            'session': updated
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error setting source data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to set source data',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>/generate', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("5 per minute")
def generate_ai_studio_content(session_id: str):
    """
    Generate AI content

    Request Body:
        {
            "content_type": "theory",
            "prompt": "Custom prompt...",
            "generate_variants": 2
        }

    Response 202:
        {
            "success": true,
            "message": "Generation started",
            "job_id": "uuid"
        }

    Note: This starts an async job. Use WebSocket or polling to get results.
    """
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()
        req = AIStudioGenerateRequest(**data)

        # Update session status
        AIStudioRepository.update_status(session_id, 'in_progress')

        # Log analytics - generation started
        start_time = datetime.utcnow()
        AIStudioAnalyticsRepository.log_event({
            'session_id': session_id,
            'user_id': user_id,
            'event_type': 'generation_started',
            'event_data': {
                'content_type': req.content_type.value,
                'variants_requested': req.generate_variants
            },
            'step_name': f'{req.content_type.value}_generation'
        })

        # Use AI Studio Service for generation
        # Service uses prompt registry (NOT hardcoded prompts)
        service = AiStudioService()

        # Build context from session data
        source_data = session.get('source_data', {})
        generated_content = session.get('generated_content', {})

        context = {
            'target_audience': source_data.get('target_audience', 'Allgemein'),
            'difficulty': source_data.get('difficulty', 'mittel'),
            'target_language': source_data.get('target_language', 'de'),
            'learning_objectives': json.dumps(source_data.get('learning_objectives', [])),
        }

        # Add step-specific context
        step = req.content_type.value
        if step == 'theory':
            context['max_theory_variants'] = str(req.generate_variants or 4)
            context['pdf_analysis'] = json.dumps(generated_content.get('pdf_analysis', source_data.get('pdf_analysis', {})))
            context['selected_didactic_angle'] = generated_content.get('selected_didactic_angle', '')
        elif step == 'lesson':
            context['max_lessons'] = str(5)
            context['pdf_analysis'] = json.dumps(generated_content.get('pdf_analysis', {}))
            context['selected_theory_variant'] = json.dumps(generated_content.get('selected_theory_variant', {}))
        elif step == 'method':
            context['method_preferences'] = json.dumps(source_data.get('method_preferences', []))
            context['lessons'] = json.dumps(generated_content.get('lessons', []))

        # Generate content using the service
        result = service.generate_for_step(
            step=step,
            session_id=session_id,
            context=context,
            user_id=user_id
        )

        # Parse AI output and store variant
        try:
            output_data = json.loads(result.get('output_text', '{}'))
        except json.JSONDecodeError:
            output_data = {'raw_output': result.get('output_text')}

        # Store as variant
        variant_data = {
            'session_id': session_id,
            'variant_type': step,
            'variant_index': 0,
            'content': output_data,
            'metadata': {
                'prompt_code': result.get('prompt_code'),
                'model': result.get('model'),
                'provider': result.get('provider'),
                'tokens': result.get('total_tokens'),
                'cost_eur': result.get('cost_eur')
            }
        }
        variant_id = AIGenerationVariantRepository.create(variant_data)

        # Update session generated_content
        generated_content[step] = output_data
        AIStudioRepository.update(session_id, {'generated_content': generated_content})

        return jsonify({
            'success': True,
            'message': 'Generation complete',
            'step': step,
            'variant_id': variant_id,
            'prompt_code': result.get('prompt_code'),
            'tokens_used': result.get('total_tokens'),
            'cost_eur': result.get('cost_eur'),
            'data': output_data
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except AiStudioServiceError as e:
        logger.error(f"AI Studio service error: {str(e)}")
        AIStudioRepository.update_status(session_id, 'error')
        return jsonify({
            'success': False,
            'error': 'AI generation failed',
            'message': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        AIStudioRepository.update_status(session_id, 'error')
        return jsonify({
            'success': False,
            'error': 'Failed to generate content',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>/finalize', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("5 per minute")
def finalize_ai_studio_session(session_id: str):
    """
    Finalize session and create chapter with content

    Request Body:
        {
            "create_chapter": true,
            "create_lessons": true,
            "create_methods": true,
            "chapter_title": "Kapitel 1: Einfuehrung",
            "publish_immediately": false
        }
    """
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()
        req = AIStudioFinalizeRequest(**data)

        # TODO: Implement actual chapter creation from generated content
        # from app.services.ai_studio_service import AIStudioService
        # result = AIStudioService.finalize_session(session_id, req)

        # For now, mark as completed
        AIStudioRepository.update_status(session_id, 'completed')

        # Log analytics
        AIStudioAnalyticsRepository.log_event({
            'session_id': session_id,
            'user_id': user_id,
            'event_type': 'session_finalized',
            'event_data': {
                'create_chapter': req.create_chapter,
                'create_lessons': req.create_lessons,
                'create_methods': req.create_methods
            },
            'step_name': 'finalize'
        })

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='ai_studio_session_finalized',
            resource_type='ai_authoring_session',
            resource_id=session_id,
            details={'course_id': session['course_id']}
        )

        return jsonify({
            'success': True,
            'message': 'Session finalized',
            'chapter_id': None,  # Will be populated when implemented
            'note': 'Chapter creation will be implemented in Phase 4'
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error finalizing session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to finalize session',
            'message': str(e)
        }), 500


# ============================================================================
# PDF Upload & Templates
# ============================================================================

@api_v1.route('/admin/ai-studio/upload-pdf', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def upload_ai_studio_pdf():
    """
    Upload and analyze PDF file

    Form Data:
        file: PDF file

    Response 200:
        {
            "success": true,
            "file_hash": "sha256...",
            "extracted_text": "...",
            "page_count": 10,
            "structure_analysis": {...}
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        if not file.filename or not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': 'File must be a PDF'
            }), 400

        # Read file content
        file_content = file.read()

        # Validate PDF
        from app.services.pdf_service import PDFService, PDFExtractionError, PDFPasswordProtectedError

        is_valid, error_msg = PDFService.validate_pdf(file_content)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg or 'Invalid PDF file'
            }), 400

        # Extract text and analyze structure
        try:
            result = PDFService.extract_for_ai(file_content, file.filename)

            return jsonify({
                'success': True,
                'file_hash': result['file_hash'],
                'original_filename': result['filename'],
                'file_size_bytes': len(file_content),
                'page_count': result['page_count'],
                'extracted_text': result['main_text'],
                'structure_analysis': result['structure'],
                'metadata': result['metadata'],
                'summary': result['summary'],
                'recommendations': result['recommendations'],
                'word_count': result['word_count'],
                'estimated_reading_time': result['estimated_reading_time'],
                'from_cache': False
            }), 200

        except PDFPasswordProtectedError:
            return jsonify({
                'success': False,
                'error': 'PDF ist passwortgeschuetzt'
            }), 400

        except PDFExtractionError as e:
            return jsonify({
                'success': False,
                'error': f'PDF-Extraktion fehlgeschlagen: {str(e)}'
            }), 400

    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process PDF',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/templates', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_ai_studio_templates():
    """
    Get available authoring templates

    Query Parameters:
        category: Filter by category
    """
    try:
        category = request.args.get('category')

        if category:
            templates = AIAuthoringTemplateRepository.get_by_category(category)
        else:
            templates = AIAuthoringTemplateRepository.get_all_active()

        return jsonify({
            'success': True,
            'templates': templates
        }), 200

    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get templates',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/stats', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_ai_studio_stats():
    """Get user's AI Studio statistics"""
    try:
        user_id = g.current_user['user_id']

        # Get session counts
        all_sessions = AIStudioRepository.find_by_user(user_id, limit=1000)
        active_sessions = [s for s in all_sessions if s['status'] in ['draft', 'in_progress', 'review']]
        completed_sessions = [s for s in all_sessions if s['status'] == 'completed']

        # Get analytics stats
        analytics_stats = AIStudioAnalyticsRepository.get_user_stats(user_id)

        return jsonify({
            'success': True,
            'stats': {
                'total_sessions': len(all_sessions),
                'active_sessions': len(active_sessions),
                'completed_sessions': len(completed_sessions),
                'total_chapters_created': len(completed_sessions),  # Simplified for now
                'total_tokens_used': analytics_stats.get('total_tokens', 0),
                'avg_generation_time_ms': analytics_stats.get('avg_generation_time', 0)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get stats',
            'message': str(e)
        }), 500
