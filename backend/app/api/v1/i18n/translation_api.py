"""
Content Translation API - Content Translation Endpoints

Provides REST API for managing translations of course content:
- Initiating KI translation jobs
- Retrieving translations
- Manual corrections and updates
- Deleting translations

Distinct from /api/v1/i18n/ which handles UI string translations.
This API manages translations of actual course materials.
"""

from flask import Blueprint, jsonify, request, g
import logging
from typing import Dict, Any

from app.application.services.content_translation_service import ContentTranslationService
from app.api.middleware.auth import token_required, role_required
from app.infrastructure.utils.exceptions import NotFoundError, ValidationError, UnauthorizedError

logger = logging.getLogger(__name__)

bp = Blueprint('translation', __name__, url_prefix='/translation')


# ============================================================================
# PUBLIC ENDPOINTS - Basic translation retrieval
# ============================================================================

@bp.route('/<namespace>/<key_path>/<language_code>', methods=['GET'])
def get_translation(namespace: str, key_path: str, language_code: str):
    """
    GET /api/v1/translation/{namespace}/{key_path}/{language_code}

    Retrieve a translation for specific content and language.

    Path Parameters:
        - namespace: Content namespace (e.g., 'courses', 'chapters')
        - key_path: Content identifier (e.g., 'course_123.intro')
        - language_code: Target language (de, en, pl)

    Returns:
        200: Translation data
        404: Translation not found

    Example:
        GET /api/v1/translation/courses/course_123.chapter_5.title/de
        {
            "translation_id": "uuid",
            "namespace": "courses",
            "key_path": "course_123.chapter_5.title",
            "language_code": "de",
            "text": "Kapitel 5: Grundlagen",
            "source": "ki",
            "status": "active",
            "created_at": "2026-01-15T10:30:00Z"
        }
    """
    try:
        translation = ContentTranslationService.get_translation(
            namespace, key_path, language_code
        )

        if not translation:
            raise NotFoundError(
                f"Translation not found: {namespace}/{key_path}/{language_code}"
            )

        return jsonify({
            'data': translation,
            'success': True
        }), 200

    except NotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            },
            'success': False
        }), 404

    except Exception as e:
        logger.error(
            f"Error retrieving translation: {e}",
            extra={'namespace': namespace, 'key_path': key_path}
        )
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve translation'
            },
            'success': False
        }), 500


# ============================================================================
# KI TRANSLATION - Initiate AI translation jobs
# ============================================================================

@bp.route('/ki/translate', methods=['POST'])
@token_required
def initiate_ki_translation():
    """
    POST /api/v1/translation/ki/translate

    Initiate a KI (AI) translation job for content.

    This endpoint creates a translation job that will be processed by the
    AI/KI pipeline to translate course content into the specified language.

    Request Body:
        - namespace: Content namespace (required)
        - key_path: Content identifier (required)
        - target_language: Target language code (required)
        - content_type: Type of content, 'text'|'html'|'markdown' (default: 'text')
        - context: Optional context for better translation (dict)

    Returns:
        201: Translation job created
        400: Validation error
        401: Unauthorized

    Example:
        POST /api/v1/translation/ki/translate
        {
            "namespace": "courses",
            "key_path": "course_456.chapter_2.description",
            "target_language": "pl",
            "content_type": "html",
            "context": {
                "domain": "education",
                "tone": "academic"
            }
        }

        Response:
        {
            "data": {
                "job_id": "uuid",
                "status": "pending",
                "namespace": "courses",
                "key_path": "course_456.chapter_2.description",
                "target_language": "pl",
                "created_at": "2026-01-15T10:30:00Z",
                "estimated_completion": null
            },
            "success": true
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['namespace', 'key_path', 'target_language']
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing)}"
            )

        # Create translation job
        job = ContentTranslationService.initiate_ki_translation(
            namespace=data['namespace'],
            key_path=data['key_path'],
            target_language=data['target_language'],
            content_type=data.get('content_type', 'text'),
            context=data.get('context'),
            user_id=g.current_user.id
        )

        logger.info(
            f"KI translation job created: {job['job_id']}",
            extra={'user_id': g.current_user.id}
        )

        return jsonify({
            'data': job,
            'success': True,
            'message': 'Translation job initiated'
        }), 201

    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            },
            'success': False
        }), 400

    except Exception as e:
        logger.error(f"Error initiating KI translation: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to initiate translation'
            },
            'success': False
        }), 500


# ============================================================================
# MANUAL CORRECTION - Update translations
# ============================================================================

@bp.route('/<translation_id>', methods=['PATCH'])
@token_required
def update_translation(translation_id: str):
    """
    PATCH /api/v1/translation/{translation_id}

    Update a translation (manual correction).

    Allows users to manually correct or improve existing translations.
    Updates the translation text and marks the source as 'manual'.

    Path Parameters:
        - translation_id: ID of the translation to update

    Request Body:
        - text: Corrected translation text (required)
        - status: Translation status, 'draft'|'active'|'needs_review' (default: 'active')

    Returns:
        200: Translation updated
        400: Validation error
        401: Unauthorized
        404: Translation not found

    Example:
        PATCH /api/v1/translation/translation-uuid-123
        {
            "text": "Kapitel 5: Grundlagen und Konzepte",
            "status": "active"
        }

        Response:
        {
            "data": {
                "translation_id": "translation-uuid-123",
                "text": "Kapitel 5: Grundlagen und Konzepte",
                "status": "active",
                "source": "manual",
                "updated_at": "2026-01-15T10:30:00Z"
            },
            "success": true,
            "message": "Translation updated"
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if 'text' not in data:
            raise ValidationError("Missing required field: text")

        if not data['text'] or not data['text'].strip():
            raise ValidationError("Translation text cannot be empty")

        # Update translation
        success = ContentTranslationService.update_translation(
            translation_id=translation_id,
            text=data['text'].strip(),
            status=data.get('status', 'active'),
            updated_by=g.current_user.id
        )

        if not success:
            raise NotFoundError(f"Translation {translation_id} not found")

        # Retrieve updated translation
        translation = ContentTranslationService.get_translation_by_id(translation_id)

        logger.info(
            f"Translation updated: {translation_id}",
            extra={'user_id': g.current_user.id}
        )

        if translation:
            return jsonify({
                'data': translation,
                'success': True,
                'message': 'Translation updated'
            }), 200
        else:
            # Unlikely to happen, but handle gracefully
            return jsonify({
                'success': True,
                'message': 'Translation updated'
            }), 200

    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            },
            'success': False
        }), 400

    except NotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            },
            'success': False
        }), 404

    except Exception as e:
        logger.error(f"Error updating translation: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to update translation'
            },
            'success': False
        }), 500


# ============================================================================
# DELETION - Delete translations
# ============================================================================

@bp.route('/<translation_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'moderator')
def delete_translation(translation_id: str):
    """
    DELETE /api/v1/translation/{translation_id}

    Delete a translation.

    Only admins and moderators can delete translations.

    Path Parameters:
        - translation_id: ID of the translation to delete

    Returns:
        204: Translation deleted
        401: Unauthorized
        403: Forbidden (insufficient permissions)
        404: Translation not found

    Example:
        DELETE /api/v1/translation/translation-uuid-123

        Response: 204 No Content
    """
    try:
        # Delete translation
        success = ContentTranslationService.delete_translation(translation_id)

        if not success:
            raise NotFoundError(f"Translation {translation_id} not found")

        logger.info(
            f"Translation deleted: {translation_id}",
            extra={'user_id': g.current_user.id}
        )

        return '', 204

    except NotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            },
            'success': False
        }), 404

    except Exception as e:
        logger.error(f"Error deleting translation: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to delete translation'
            },
            'success': False
        }), 500


# ============================================================================
# JOB MANAGEMENT - Track translation jobs
# ============================================================================

@bp.route('/job/<job_id>', methods=['GET'])
@token_required
def get_job_status(job_id: str):
    """
    GET /api/v1/translation/job/{job_id}

    Get the status of a KI translation job.

    Path Parameters:
        - job_id: ID of the translation job

    Returns:
        200: Job status
        404: Job not found

    Example:
        GET /api/v1/translation/job/job-uuid-123

        Response:
        {
            "data": {
                "job_id": "job-uuid-123",
                "namespace": "courses",
                "key_path": "course_456.chapter_2.description",
                "target_language": "pl",
                "status": "pending",
                "created_at": "2026-01-15T10:30:00Z",
                "completed_at": null,
                "result_translation_id": null
            },
            "success": true
        }
    """
    try:
        job = ContentTranslationService.get_job_status(job_id)

        if not job:
            raise NotFoundError(f"Translation job {job_id} not found")

        return jsonify({
            'data': job,
            'success': True
        }), 200

    except NotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            },
            'success': False
        }), 404

    except Exception as e:
        logger.error(f"Error retrieving job status: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve job status'
            },
            'success': False
        }), 500


__all__ = ['bp']
