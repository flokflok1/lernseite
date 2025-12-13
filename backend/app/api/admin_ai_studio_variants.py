"""
LernsystemX Admin AI Studio - Variants & Snapshots API

Variant selection and snapshot management endpoints:
- GET    /api/v1/admin/ai-studio/sessions/{id}/variants              - Get variants
- POST   /api/v1/admin/ai-studio/sessions/{id}/variants/select       - Select variant
- POST   /api/v1/admin/ai-studio/sessions/{id}/variants/rate         - Rate variant
- GET    /api/v1/admin/ai-studio/sessions/{id}/snapshots             - Get snapshots
- POST   /api/v1/admin/ai-studio/sessions/{id}/snapshots             - Create snapshot
- POST   /api/v1/admin/ai-studio/sessions/{id}/snapshots/{snap_id}/restore - Restore snapshot

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
Module split according to 35_Developer-Guide-KI-Prompts.md guidelines
"""

from flask import request, jsonify, g
from pydantic import ValidationError
import logging
import json

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.models.ai_studio import (
    AIStudioSelectVariantRequest,
    AIStudioRateVariantRequest,
    AIStudioSnapshotRequest
)
from app.repositories.ai_studio_repository import (
    AIStudioRepository,
    AISessionSnapshotRepository,
    AIGenerationVariantRepository
)
from app.security.permissions import require_permission, Permissions


# ============================================================================
# Variants Management
# ============================================================================

@api_v1.route('/admin/ai-studio/sessions/<session_id>/variants', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_ai_studio_variants(session_id: str):
    """
    Get generated variants for session

    Query Parameters:
        type: Filter by variant type (theory, lesson, method, quiz, summary)
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

        variant_type = request.args.get('type')
        variants = AIGenerationVariantRepository.get_variants(session_id, variant_type)

        return jsonify({
            'success': True,
            'variants': variants
        }), 200

    except Exception as e:
        logger.error(f"Error getting variants: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get variants',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>/variants/select', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def select_ai_studio_variant(session_id: str):
    """Select a variant"""
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
        req = AIStudioSelectVariantRequest(**data)

        variant = AIGenerationVariantRepository.select_variant(req.variant_id)

        if not variant:
            return jsonify({
                'success': False,
                'error': 'Variant not found'
            }), 404

        return jsonify({
            'success': True,
            'variant': variant
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error selecting variant: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to select variant',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>/variants/rate', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def rate_ai_studio_variant(session_id: str):
    """Rate a variant"""
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
        req = AIStudioRateVariantRequest(**data)

        variant = AIGenerationVariantRepository.rate_variant(req.variant_id, req.rating, req.feedback)

        if not variant:
            return jsonify({
                'success': False,
                'error': 'Variant not found'
            }), 404

        return jsonify({
            'success': True,
            'variant': variant
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error rating variant: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to rate variant',
            'message': str(e)
        }), 500


# ============================================================================
# Snapshots (Undo/Redo)
# ============================================================================

@api_v1.route('/admin/ai-studio/sessions/<session_id>/snapshots', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_ai_studio_snapshots(session_id: str):
    """Get all snapshots for session"""
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

        snapshots = AISessionSnapshotRepository.get_snapshots(session_id)

        return jsonify({
            'success': True,
            'snapshots': snapshots
        }), 200

    except Exception as e:
        logger.error(f"Error getting snapshots: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get snapshots',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>/snapshots', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def create_ai_studio_snapshot(session_id: str):
    """Create a snapshot of current session state"""
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

        data = request.get_json() or {}
        req = AIStudioSnapshotRequest(**data)

        # Create snapshot data
        snapshot_data = {
            'generated_theory': session.get('generated_theory'),
            'generated_lessons': session.get('generated_lessons'),
            'generated_methods': session.get('generated_methods'),
            'current_step': session.get('current_step'),
            'steps_completed': session.get('steps_completed')
        }

        snapshot = AISessionSnapshotRepository.create_snapshot(
            session_id,
            snapshot_data,
            req.description
        )

        return jsonify({
            'success': True,
            'snapshot': snapshot
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error creating snapshot: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create snapshot',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>/snapshots/<snapshot_id>/restore', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def restore_ai_studio_snapshot(session_id: str, snapshot_id: str):
    """Restore session to a snapshot"""
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

        snapshot = AISessionSnapshotRepository.restore_snapshot(snapshot_id)

        if not snapshot:
            return jsonify({
                'success': False,
                'error': 'Snapshot not found'
            }), 404

        # Restore session state from snapshot
        snapshot_data = snapshot.get('snapshot_data', {})
        if isinstance(snapshot_data, str):
            snapshot_data = json.loads(snapshot_data)

        AIStudioRepository.update_session(session_id, snapshot_data)

        # Get updated session
        updated_session = AIStudioRepository.find_by_id(session_id)

        return jsonify({
            'success': True,
            'session': updated_session,
            'restored_from': snapshot_id
        }), 200

    except Exception as e:
        logger.error(f"Error restoring snapshot: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to restore snapshot',
            'message': str(e)
        }), 500
