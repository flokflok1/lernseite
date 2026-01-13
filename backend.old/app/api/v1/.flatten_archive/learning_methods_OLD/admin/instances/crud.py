"""
Learning Method Instances CRUD Endpoints (DDD)

CRUD operations for learning method instances.
Uses LearningMethodInstanceFactory and MethodValidationService.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.learning_method.instances import LearningMethodInstanceRepository
from app.repositories.courses.chapters import ChapterRepository
from app.services.audit_service import AuditService

from app.api.system_features.learning_methods.core import (
    LearningMethodInstanceFactory,
    MethodValidationService,
    MethodEnrichmentService,
    MethodStatus
)

from . import lm_instances_bp

logger = logging.getLogger(__name__)


@lm_instances_bp.route('/chapters/<chapter_id>/learning-methods', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
@limiter.limit("60 per minute")
def get_chapter_learning_methods(chapter_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get all learning method instances for a chapter.

    Args:
        chapter_id: Chapter UUID

    Query Parameters:
        published_only (bool): Filter for published only (default: false)

    Returns:
        JSON response with learning methods list

    DDD: Uses MethodEnrichmentService for type info
    """
    try:
        published_only = request.args.get('published_only', 'false').lower() == 'true'

        # Fetch instances from repository
        methods = LearningMethodInstanceRepository.find_by_chapter(
            chapter_id,
            published_only=published_only
        )

        # DDD: Enrich with type information
        # TODO: Load method types mapping
        enriched_methods = methods  # Simplified for now

        # DDD: Calculate statistics using Service
        stats = MethodEnrichmentService.calculate_statistics(methods)

        return jsonify({
            'success': True,
            'learning_methods': enriched_methods,
            'total': len(enriched_methods),
            'chapter_id': chapter_id,
            'statistics': stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning methods for chapter {chapter_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning methods',
            'message': str(e)
        }), 500


@lm_instances_bp.route('/chapters/<chapter_id>/learning-methods', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def create_learning_method(chapter_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Create new learning method instance for a chapter.

    Args:
        chapter_id: Chapter UUID

    Request Body:
        method_type (int): Method type (0-11)
        title (str): Instance title
        content (dict): Optional method content
        order (int): Optional position order

    Returns:
        JSON response with created instance

    DDD: Uses LearningMethodInstanceFactory and MethodValidationService
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        method_type = data.get('method_type')
        title = data.get('title')

        if method_type is None or not title:
            return jsonify({
                'success': False,
                'error': 'method_type and title required'
            }), 400

        # DDD: Validate method_type using Service
        MethodValidationService.validate_method_type(method_type)

        # Verify chapter exists
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        user_id = g.current_user['user_id']

        # DDD: Use Factory to create instance
        instance_data = LearningMethodInstanceFactory.create_instance(
            chapter_id=chapter_id,
            method_type=method_type,
            title=title,
            created_by=user_id,
            content=data.get('content'),
            order=data.get('order')
        )

        # Save to repository
        created = LearningMethodInstanceRepository.create(instance_data)

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='learning_method.create',
            resource_type='learning_method',
            resource_id=created['method_id'],
            details={
                'chapter_id': chapter_id,
                'method_type': method_type,
                'title': title
            }
        )

        return jsonify({
            'success': True,
            'learning_method': created
        }), 201

    except ValueError as ve:
        logger.warning(f"Validation error creating learning method: {ve}")
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error creating learning method: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create learning method',
            'message': str(e)
        }), 500


@lm_instances_bp.route('/learning-methods/<method_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
@limiter.limit("60 per minute")
def get_learning_method(method_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get single learning method instance.

    Args:
        method_id: Method UUID

    Returns:
        JSON response with method instance

    DDD: Uses MethodEnrichmentService
    """
    try:
        method = LearningMethodInstanceRepository.find_by_id(method_id)

        if not method:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        # TODO: Enrich with type info
        enriched = method

        return jsonify({
            'success': True,
            'learning_method': enriched
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning method',
            'message': str(e)
        }), 500


@lm_instances_bp.route('/learning-methods/<method_id>', methods=['PATCH'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def update_learning_method(method_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Update learning method instance.

    Args:
        method_id: Method UUID

    Request Body:
        title (str): Optional new title
        content (dict): Optional new content
        status (str): Optional new status

    Returns:
        JSON response with updated instance

    DDD: Uses LearningMethodInstanceFactory and MethodValidationService
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        # Fetch existing instance
        existing = LearningMethodInstanceRepository.find_by_id(method_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        # Validate status transition if status changed
        new_status_str = data.get('status')
        if new_status_str:
            try:
                current_status = MethodStatus(existing['status'])
                new_status = MethodStatus(new_status_str)
                MethodValidationService.validate_status_transition(current_status, new_status)
            except ValueError as ve:
                return jsonify({
                    'success': False,
                    'error': 'Invalid status transition',
                    'message': str(ve)
                }), 400

        user_id = g.current_user['user_id']

        # DDD: Use Factory to create update data
        update_data = LearningMethodInstanceFactory.create_update_data(
            title=data.get('title'),
            content=data.get('content'),
            status=MethodStatus(new_status_str) if new_status_str else None,
            updated_by=user_id
        )

        # Update in repository
        updated = LearningMethodInstanceRepository.update(method_id, update_data)

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='learning_method.update',
            resource_type='learning_method',
            resource_id=method_id,
            details={'updates': list(update_data.keys())}
        )

        return jsonify({
            'success': True,
            'learning_method': updated
        }), 200

    except ValueError as ve:
        logger.warning(f"Validation error updating learning method: {ve}")
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error updating learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update learning method',
            'message': str(e)
        }), 500


@lm_instances_bp.route('/learning-methods/<method_id>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def delete_learning_method(method_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Delete learning method instance.

    Args:
        method_id: Method UUID

    Returns:
        JSON response with success status

    DDD: Business rule - can only delete DRAFT instances
    """
    try:
        # Fetch existing instance
        existing = LearningMethodInstanceRepository.find_by_id(method_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        # Business rule: Only delete draft instances
        if existing['status'] != MethodStatus.DRAFT.value:
            return jsonify({
                'success': False,
                'error': 'Can only delete draft instances',
                'message': 'Published or archived instances cannot be deleted'
            }), 400

        # Delete from repository
        LearningMethodInstanceRepository.delete(method_id)

        # Audit log
        user_id = g.current_user['user_id']
        AuditService.log_action(
            user_id=user_id,
            action='learning_method.delete',
            resource_type='learning_method',
            resource_id=method_id,
            details={
                'method_type': existing['method_type'],
                'title': existing['title']
            }
        )

        return jsonify({
            'success': True,
            'message': 'Learning method deleted'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete learning method',
            'message': str(e)
        }), 500
