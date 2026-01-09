"""
Admin Learning Method Routes (Journey-Based API)

Admin journey for learning method management (12 Content-LMs).
ALL data loaded dynamically from database - NO hardcoded values.

Endpoints:
- GET /api/v1/admin/learning-methods/types - List all 12 Content-LM types
- GET /api/v1/admin/learning-methods/types/<type_id> - Get LM type details
- GET /api/v1/admin/learning-methods/available-types - Get valid method_type IDs (from DB)
- GET /api/v1/admin/chapters/<chapter_id>/learning-methods - List chapter LM instances
- GET /api/v1/admin/learning-methods/<id> - Get LM instance details
- POST /api/v1/admin/chapters/<chapter_id>/learning-methods - Create LM instance
- PUT /api/v1/admin/learning-methods/<id> - Update LM instance metadata
- PATCH /api/v1/admin/learning-methods/<id>/data - Update LM instance data (JSONB)
- PATCH /api/v1/admin/learning-methods/<id>/solution - Update LM instance solution (JSONB)
- POST /api/v1/admin/learning-methods/<id>/publish - Publish LM instance
- POST /api/v1/admin/learning-methods/<id>/unpublish - Unpublish LM instance
- DELETE /api/v1/admin/learning-methods/<id> - Delete LM instance
"""

from flask import Blueprint, request, jsonify
from src.core.auth.permissions import require_auth, require_role
from src.api.content.learning_methods.application.services.learning_method_service import LearningMethodService
from src.core.utils.validators import Validators, ValidationError


# Create blueprint
admin_learning_methods_bp = Blueprint('admin_learning_methods', __name__)


# ============================================================================
# LEARNING METHOD TYPES (The 12 Content-LMs)
# ============================================================================

@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/types', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_learning_method_types():
    """
    List all learning method types (the 12 Content-LMs).

    Query params:
    - group_code: Filter by group (A, B, C)
    - tier: Filter by tier (basic, premium)
    - active_only: Only active types (default: true)
    """
    try:
        group_code = request.args.get('group_code')
        tier = request.args.get('tier')
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        types = LearningMethodService.list_types(
            group_code=group_code,
            tier=tier,
            active_only=active_only
        )

        types_data = [
            {
                'type_id': t.type_id,
                'method_type': t.method_type,
                'name': t.name,
                'description': t.description,
                'group_code': t.group_code,
                'group_name': t.get_group_name(),
                'tier': t.tier,
                'ki_usage': t.ki_usage,
                'active': t.active,
                'config': t.config,
                'icon': t.icon,
                'created_at': t.created_at.isoformat() if t.created_at else None
            }
            for t in types
        ]

        return jsonify({
            'success': True,
            'data': types_data,
            'meta': {'count': len(types_data)}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_TYPES_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/types/<int:type_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_learning_method_type(type_id: int):
    """Get learning method type details by ID."""
    try:
        lm_type = LearningMethodService.get_type_by_id(type_id)

        if not lm_type:
            return jsonify({'success': False, 'error': {'code': 'TYPE_NOT_FOUND', 'message': f'Learning method type {type_id} not found'}}), 404

        type_data = {
            'type_id': lm_type.type_id,
            'method_type': lm_type.method_type,
            'name': lm_type.name,
            'description': lm_type.description,
            'group_code': lm_type.group_code,
            'group_name': lm_type.get_group_name(),
            'tier': lm_type.tier,
            'ki_usage': lm_type.ki_usage,
            'active': lm_type.active,
            'config': lm_type.config,
            'icon': lm_type.icon,
            'created_at': lm_type.created_at.isoformat() if lm_type.created_at else None,
            'updated_at': lm_type.updated_at.isoformat() if lm_type.updated_at else None
        }

        return jsonify({'success': True, 'data': type_data}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_TYPE_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/available-types', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_available_learning_method_types():
    """
    Get available learning method types from database.

    Returns valid method_type IDs loaded dynamically from DB constraint.
    NO hardcoded method type lists.

    Returns: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] for 12 Content-LMs
    """
    try:
        method_types = LearningMethodService.get_available_method_types()

        return jsonify({
            'success': True,
            'data': method_types,
            'meta': {'count': len(method_types)}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_AVAILABLE_TYPES_ERROR', 'message': str(e)}}), 500


# ============================================================================
# LEARNING METHOD INSTANCES (Concrete instances in chapters)
# ============================================================================

@admin_learning_methods_bp.route('/api/v1/admin/chapters/<chapter_id>/learning-methods', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_chapter_learning_methods(chapter_id: str):
    """List learning method instances for a chapter."""
    try:
        Validators.validate_uuid(chapter_id)
        published_only = request.args.get('published_only', 'false').lower() == 'true'

        instances = LearningMethodService.list_instances(
            chapter_id=chapter_id,
            published_only=published_only
        )

        instances_data = [
            {
                'method_id': i.method_id,
                'chapter_id': i.chapter_id,
                'method_type': i.method_type,
                'title': i.title,
                'tier': i.tier,
                'difficulty': i.difficulty,
                'duration_minutes': i.duration_minutes,
                'order_index': i.order_index,
                'published': i.published,
                'created_at': i.created_at.isoformat() if i.created_at else None
            }
            for i in instances
        ]

        return jsonify({
            'success': True,
            'data': instances_data,
            'meta': {'chapter_id': chapter_id, 'count': len(instances_data)}
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_INSTANCES_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/<method_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_learning_method_instance(method_id: str):
    """Get learning method instance by ID with full details."""
    try:
        Validators.validate_uuid(method_id)
        instance = LearningMethodService.get_instance_by_id(method_id)

        if not instance:
            return jsonify({'success': False, 'error': {'code': 'INSTANCE_NOT_FOUND', 'message': f'Learning method instance {method_id} not found'}}), 404

        instance_data = {
            'method_id': instance.method_id,
            'chapter_id': instance.chapter_id,
            'method_type': instance.method_type,
            'title': instance.title,
            'instructions': instance.instructions,
            'data': instance.data,
            'solution': instance.solution,
            'tier': instance.tier,
            'duration_minutes': instance.duration_minutes,
            'difficulty': instance.difficulty,
            'order_index': instance.order_index,
            'published': instance.published,
            'created_at': instance.created_at.isoformat() if instance.created_at else None,
            'updated_at': instance.updated_at.isoformat() if instance.updated_at else None
        }

        return jsonify({'success': True, 'data': instance_data}), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_INSTANCE_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/chapters/<chapter_id>/learning-methods', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def create_learning_method_instance(chapter_id: str):
    """Create new learning method instance in chapter."""
    try:
        Validators.validate_uuid(chapter_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['method_type', 'title', 'data', 'tier'])

        user_id = request.user_id
        user_role = request.user_role

        instance = LearningMethodService.create_instance(
            chapter_id=chapter_id,
            method_type=data['method_type'],
            title=data['title'],
            data=data['data'],
            tier=data['tier'],
            user_id=user_id,
            user_role=user_role,
            instructions=data.get('instructions'),
            solution=data.get('solution'),
            duration_minutes=data.get('duration_minutes'),
            difficulty=data.get('difficulty'),
            order_index=data.get('order_index', 0)
        )

        instance_data = {
            'method_id': instance.method_id,
            'chapter_id': instance.chapter_id,
            'method_type': instance.method_type,
            'title': instance.title,
            'tier': instance.tier,
            'published': instance.published,
            'created_at': instance.created_at.isoformat() if instance.created_at else None
        }

        return jsonify({'success': True, 'data': instance_data}), 201

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_DATA', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'CREATE_INSTANCE_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/<method_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'creator'])
def update_learning_method_instance(method_id: str):
    """Update learning method instance metadata."""
    try:
        Validators.validate_uuid(method_id)
        data = request.get_json()

        user_id = request.user_id
        user_role = request.user_role

        instance = LearningMethodService.update_instance(
            method_id=method_id,
            user_id=user_id,
            user_role=user_role,
            updates=data
        )

        instance_data = {
            'method_id': instance.method_id,
            'title': instance.title,
            'tier': instance.tier,
            'published': instance.published,
            'updated_at': instance.updated_at.isoformat() if instance.updated_at else None
        }

        return jsonify({'success': True, 'data': instance_data}), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INSTANCE_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_INSTANCE_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/<method_id>/data', methods=['PATCH'])
@require_auth
@require_role(['admin', 'creator'])
def update_learning_method_data(method_id: str):
    """Update learning method instance data (JSONB)."""
    try:
        Validators.validate_uuid(method_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['data'])

        user_id = request.user_id
        user_role = request.user_role

        instance = LearningMethodService.update_instance_data(
            method_id=method_id,
            data=data['data'],
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'method_id': instance.method_id, 'data': instance.data},
            'message': 'Learning method data updated successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INSTANCE_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_DATA_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/<method_id>/solution', methods=['PATCH'])
@require_auth
@require_role(['admin', 'creator'])
def update_learning_method_solution(method_id: str):
    """Update learning method instance solution (JSONB)."""
    try:
        Validators.validate_uuid(method_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['solution'])

        user_id = request.user_id
        user_role = request.user_role

        instance = LearningMethodService.update_instance_solution(
            method_id=method_id,
            solution=data['solution'],
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'method_id': instance.method_id, 'solution': instance.solution},
            'message': 'Learning method solution updated successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INSTANCE_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_SOLUTION_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/<method_id>/publish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def publish_learning_method_instance(method_id: str):
    """Publish learning method instance."""
    try:
        Validators.validate_uuid(method_id)
        user_id = request.user_id
        user_role = request.user_role

        instance = LearningMethodService.publish_instance(
            method_id=method_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'method_id': instance.method_id, 'title': instance.title, 'published': instance.published},
            'message': 'Learning method published successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INSTANCE_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'PUBLISH_INSTANCE_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/<method_id>/unpublish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def unpublish_learning_method_instance(method_id: str):
    """Unpublish learning method instance."""
    try:
        Validators.validate_uuid(method_id)
        user_id = request.user_id
        user_role = request.user_role

        instance = LearningMethodService.unpublish_instance(
            method_id=method_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'method_id': instance.method_id, 'title': instance.title, 'published': instance.published},
            'message': 'Learning method unpublished successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INSTANCE_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UNPUBLISH_INSTANCE_ERROR', 'message': str(e)}}), 500


@admin_learning_methods_bp.route('/api/v1/admin/learning-methods/<method_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_learning_method_instance(method_id: str):
    """Delete learning method instance (hard delete - cascade to progress)."""
    try:
        Validators.validate_uuid(method_id)
        user_id = request.user_id
        user_role = request.user_role

        LearningMethodService.delete_instance(
            method_id=method_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({'success': True, 'message': 'Learning method instance deleted successfully'}), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INSTANCE_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'DELETE_INSTANCE_ERROR', 'message': str(e)}}), 500
