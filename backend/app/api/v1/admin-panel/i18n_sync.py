"""
i18n Sync API - REST endpoints for translation synchronization.

Endpoints:
- POST /api/admin/i18n-sync/scan - Initiate scan
- GET /api/admin/i18n-sync/results/{sync_id} - Get scan results
- POST /api/admin/i18n-sync/apply - Apply changes
- POST /api/admin/i18n-sync/rollback - Rollback sync
- GET /api/admin/i18n-sync/history - Get sync history
- GET /api/admin/i18n-sync/stats - Get dashboard statistics
- GET /api/admin/i18n-sync/{sync_id} - Get sync details
- POST /api/admin/i18n-sync/{sync_id}/resolve - Resolve conflict
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any
import logging
from datetime import datetime

from app.infrastructure.persistence.database import get_connection
from app.api.middleware.auth import token_required, admin_required
from app.services.i18n_sync_service import I18nSyncService
from app.services.i18n_sync_service_apply import I18nSyncServiceApply
from app.services.i18n_sync_service_analytics import I18nSyncServiceAnalytics
from app.infrastructure.utils.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.infrastructure.i18n.error_codes import ErrorCode, error_response

logger = logging.getLogger(__name__)

bp = Blueprint('i18n_sync', __name__, url_prefix='/api/admin-panel/i18n-sync')


# ============================================================================
# Dashboard & Statistics
# ============================================================================

@bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_dashboard_stats():
    """
    GET /api/admin/i18n-sync/stats
    
    Get system-wide i18n sync statistics.
    
    Returns:
        200: {
            total_syncs: int,
            syncs: {completed: int, failed: int, manual_mode: int, auto_mode: int},
            performance: {avg_scan_duration_ms: int},
            translations: {total_keys: int, by_language: {...}},
            success_rate: str
        }
    """
    with get_connection() as conn:
        service = I18nSyncServiceAnalytics(conn)
        stats = service.get_dashboard_stats()

    return jsonify({
        'success': True,
        'data': stats,
        'meta': {'timestamp': datetime.utcnow().isoformat()}
    }), 200


# ============================================================================
# Scan Operations
# ============================================================================

@bp.route('/scan', methods=['POST'])
@token_required
@admin_required
def initiate_scan():
    """
    POST /api/admin/i18n-sync/scan
    
    Initiate translation scan.
    
    Request Body:
        {
            "mode": "MANUAL" | "AUTO",
            "languages": ["de", "en", "pl"],
            "frontend_translations": {
                "de": {"key": "value", ...},
                "en": {"key": "value", ...},
                ...
            },
            "metadata": {...}  # optional
        }
    
    Returns:
        201: {
            sync_id: str,
            mode: str,
            status: str,
            languages_synced: str[],
            ...statistics...
        }
        
    Raises:
        400: Validation error
    """
    data = request.get_json()
    
    # Validate required fields
    if 'mode' not in data or 'languages' not in data:
        raise ValidationError("Missing required fields: mode, languages")
    
    if 'frontend_translations' not in data:
        raise ValidationError("Missing required field: frontend_translations")
    
    mode = data['mode'].upper()
    languages = data['languages']
    frontend_translations = data['frontend_translations']
    metadata = data.get('metadata', {})
    
    # Initiate sync
    with get_connection() as conn:
        service = I18nSyncService(conn)
        
        # Step 1: Create sync
        sync = service.initiate_sync(
            user_id=g.current_user.id,
            mode=mode,
            languages=languages,
            metadata=metadata
        )
        
        # Step 2: Run scan
        sync_completed, new_count, changed_count, deleted_count, conflict_count = service.scan_translations(
            sync.sync_id,
            frontend_translations
        )
    
    logger.info(
        f"Scan completed: {new_count} new, {changed_count} changed, "
        f"{deleted_count} deleted, {conflict_count} conflicts",
        extra={'sync_id': sync_completed.sync_id, 'user_id': g.current_user.id}
    )
    
    return jsonify({
        'success': True,
        'data': sync_completed.to_dict(),
        'meta': {'timestamp': datetime.utcnow().isoformat()}
    }), 201


@bp.route('/results/<sync_id>', methods=['GET'])
@token_required
@admin_required
def get_scan_results(sync_id: str):
    """
    GET /api/admin/i18n-sync/results/{sync_id}
    
    Get detailed scan results for a sync operation.
    
    Query Parameters:
        - limit: Max results (default 20, max 100)
        - offset: Skip N results (default 0)
        - type: Filter by change type (NEW, CHANGED, DELETED, CONFLICT)
        - language: Filter by language code
    
    Returns:
        200: {
            changes: [...],
            total: int,
            limit: int,
            offset: int
        }
    """
    limit = min(int(request.args.get('limit', 20)), 100)
    offset = int(request.args.get('offset', 0))
    change_type = request.args.get('type')
    language = request.args.get('language')
    
    with get_connection() as conn:
        service = I18nSyncService(conn)
        changes, total = service.get_scan_results(
            sync_id,
            limit=limit,
            offset=offset,
            change_type=change_type,
            language_code=language
        )
    
    return jsonify({
        'success': True,
        'data': [change.to_dict() for change in changes],
        'total': total,
        'limit': limit,
        'offset': offset,
        'meta': {'timestamp': datetime.utcnow().isoformat()}
    }), 200


# ============================================================================
# Conflict Resolution
# ============================================================================

@bp.route('/<sync_id>/resolve', methods=['POST'])
@token_required
@admin_required
def resolve_conflict(sync_id: str):
    """
    POST /api/admin/i18n-sync/{sync_id}/resolve
    
    Resolve a conflicted translation.
    
    Request Body:
        {
            "change_id": int,
            "action": "ADD" | "UPDATE" | "DELETE" | "SKIP",
            "notes": "..."  # optional
        }
    
    Returns:
        200: {resolution_id: int, ...resolution_data...}
        
    Raises:
        404: Sync or change not found
        422: Change is not a conflict
    """
    data = request.get_json()
    
    if 'change_id' not in data or 'action' not in data:
        raise ValidationError("Missing required fields: change_id, action")
    
    change_id = data['change_id']
    action = data['action'].upper()
    notes = data.get('notes')
    
    # Validate action
    valid_actions = ['ADD', 'UPDATE', 'DELETE', 'SKIP']
    if action not in valid_actions:
        raise ValidationError(f"Invalid action: {action}. Must be one of {valid_actions}")
    
    with get_connection() as conn:
        service = I18nSyncService(conn)
        resolution = service.resolve_conflict(
            sync_id,
            change_id,
            action,
            g.current_user.id,
            notes
        )
    
    return jsonify({
        'success': True,
        'data': resolution.to_dict(),
        'meta': {'timestamp': datetime.utcnow().isoformat()}
    }), 200


# ============================================================================
# Apply & Rollback
# ============================================================================

@bp.route('/apply', methods=['POST'])
@token_required
@admin_required
def apply_sync():
    """
    POST /api/admin/i18n-sync/apply
    
    Apply sync changes to database.
    
    Request Body:
        {
            "sync_id": str,
            "auto_resolve": bool  # optional, default false
        }
    
    Returns:
        200: {
            sync: {...sync_data...},
            stats: {applied: int, skipped: int, errors: int}
        }
        
    Raises:
        400: Validation error
        422: Sync has unresolved conflicts (MANUAL mode)
    """
    data = request.get_json()
    
    if 'sync_id' not in data:
        raise ValidationError("Missing required field: sync_id")
    
    sync_id = data['sync_id']
    auto_resolve = data.get('auto_resolve', False)
    
    with get_connection() as conn:
        service = I18nSyncServiceApply(conn)
        sync, stats = service.apply_sync(sync_id, auto_resolve=auto_resolve)
    
    logger.info(
        f"Applied sync {sync_id}",
        extra={'stats': stats, 'user_id': g.current_user.id}
    )
    
    return jsonify({
        'success': True,
        'data': {
            'sync': sync.to_dict(),
            'stats': stats
        },
        'meta': {'timestamp': datetime.utcnow().isoformat()}
    }), 200


@bp.route('/rollback', methods=['POST'])
@token_required
@admin_required
def rollback_sync():
    """
    POST /api/admin/i18n-sync/rollback
    
    Rollback a sync operation.
    
    Request Body:
        {
            "sync_id": str,
            "reason": str
        }
    
    Returns:
        200: {sync_id: str, status: "ROLLED_BACK", ...}
        
    Raises:
        404: Sync not found
    """
    data = request.get_json()
    
    if 'sync_id' not in data or 'reason' not in data:
        raise ValidationError("Missing required fields: sync_id, reason")
    
    sync_id = data['sync_id']
    reason = data['reason']

    with get_connection() as conn:
        service = I18nSyncServiceApply(conn)
        sync = service.rollback_sync(sync_id, g.current_user.id, reason)
    
    logger.warning(
        f"Rolled back sync {sync_id}: {reason}",
        extra={'user_id': g.current_user.id}
    )
    
    return jsonify({
        'success': True,
        'data': sync.to_dict(),
        'meta': {'timestamp': datetime.utcnow().isoformat()}
    }), 200


# ============================================================================
# History & Details
# ============================================================================

@bp.route('/history', methods=['GET'])
@token_required
@admin_required
def get_sync_history():
    """
    GET /api/admin/i18n-sync/history
    
    Get sync operation history.
    
    Query Parameters:
        - limit: Max results (default 20, max 100)
        - offset: Skip N results (default 0)
        - status: Filter by status (PENDING, SCANNING, COMPLETED, FAILED, ROLLED_BACK)
        - mode: Filter by mode (MANUAL, AUTO)
        - user_id: Filter by initiating user
    
    Returns:
        200: {
            syncs: [...],
            total: int,
            limit: int,
            offset: int
        }
    """
    limit = min(int(request.args.get('limit', 20)), 100)
    offset = int(request.args.get('offset', 0))
    status = request.args.get('status')
    mode = request.args.get('mode')
    user_id = request.args.get('user_id')
    
    with get_connection() as conn:
        # Get all syncs (limited)
        from app.infrastructure.persistence.repositories.i18n_sync import SyncRepository
        repo = SyncRepository(conn)
        syncs, total = repo.list_syncs(
            limit=limit,
            offset=offset,
            status=status,
            mode=mode,
            user_id=user_id
        )
    
    return jsonify({
        'success': True,
        'data': [sync.to_dict() for sync in syncs],
        'total': total,
        'limit': limit,
        'offset': offset,
        'meta': {'timestamp': datetime.utcnow().isoformat()}
    }), 200


@bp.route('/<sync_id>', methods=['GET'])
@token_required
@admin_required
def get_sync_details(sync_id: str):
    """
    GET /api/admin/i18n-sync/{sync_id}
    
    Get detailed sync operation information including all changes and resolutions.
    
    Returns:
        200: {
            sync: {...},
            changes: {
                by_type: {NEW: [...], CHANGED: [...], ...},
                total: int
            },
            resolutions: [...],
            stats: {...}
        }
    """
    with get_connection() as conn:
        service = I18nSyncServiceAnalytics(conn)
        details = service.get_sync_details(sync_id)
    
    return jsonify({
        'success': True,
        'data': details,
        'meta': {'timestamp': datetime.utcnow().isoformat()}
    }), 200


# ============================================================================
# Error Handler
# ============================================================================

@bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle validation errors."""
    return error_response(
        ErrorCode.VALIDATION_ERROR,
        status=error.status_code,
        details={'message': error.message}
    )


@bp.errorhandler(NotFoundError)
def handle_not_found(error):
    """Handle not found errors."""
    return error_response(
        ErrorCode.NOT_FOUND,
        status=error.status_code,
        details={'message': error.message}
    )


@bp.errorhandler(BusinessLogicError)
def handle_business_logic_error(error):
    """Handle business logic errors."""
    return error_response(
        ErrorCode.BUSINESS_LOGIC_ERROR,
        status=error.status_code,
        details={'message': error.message}
    )


# Import datetime for timestamp
from datetime import datetime
