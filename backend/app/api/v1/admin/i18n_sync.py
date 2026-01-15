"""
i18n Sync API Endpoints - Translation Synchronization Routes

Provides REST API for:
- Initiating sync scans (MANUAL or AUTO mode)
- Viewing comparison panels (side-by-side diffs)
- Applying sync changes with resolutions
- Rolling back syncs to previous state
- Viewing sync history and statistics
- Managing snapshots

All endpoints require admin authentication.
"""

from flask import Blueprint, request, jsonify, g
from typing import Optional
from uuid import UUID

from app.models.i18n_sync import (
    SyncHistoryCreateRequest, SyncHistoryApplyRequest,
    SyncHistoryRollbackRequest, ScanResultsResponse
)
from app.services.i18n_sync_service import get_sync_service
from app.utils.exceptions import ValidationError, NotFoundError, UnauthorizedError
from app.middleware.auth import require_auth, require_role

# Create blueprint
bp = Blueprint('i18n_sync', __name__, url_prefix='/api/v1/admin/i18n-sync')


# ============================================================================
# SCAN INITIATION
# ============================================================================

@bp.route('/scan', methods=['POST'])
@require_auth
@require_role('admin')
def initiate_sync_scan():
    """
    POST /api/v1/admin/i18n-sync/scan

    Initiate a new translation synchronization scan.

    Compares frontend JSON against database translations, detects:
    - New keys (in JSON, not in DB)
    - Changed keys (different values)
    - Deleted keys (in DB, not in JSON)

    Request Body:
        {
            "sync_mode": "MANUAL" | "AUTO",    # Required
            "languages_affected": ["de", "en", "pl"]  # Required
        }

    Response (201 Created):
        {
            "success": true,
            "sync_id": "uuid",
            "sync_status": "PENDING",
            "sync_mode": "MANUAL",
            "languages_affected": ["de", "en"],
            "scan_results": {
                "keys_added": 45,
                "keys_updated": 23,
                "keys_deleted": 8,
                "keys_skipped": 0,
                "keys_conflicted": 12,
                "total_keys": 88
            }
        }

    Errors:
        - 400: Invalid sync_mode or languages_affected
        - 401: Unauthorized (not authenticated)
        - 403: Forbidden (not admin)
        - 500: Internal server error
    """
    try:
        data = request.get_json() or {}

        # Validate sync_mode
        sync_mode = data.get('sync_mode', '').upper()
        if sync_mode not in ['MANUAL', 'AUTO']:
            raise ValidationError(
                "Invalid sync_mode",
                details={'expected': ['MANUAL', 'AUTO'], 'got': sync_mode}
            )

        # Validate languages
        languages_affected = data.get('languages_affected', [])
        if not isinstance(languages_affected, list) or not languages_affected:
            raise ValidationError(
                "languages_affected must be a non-empty array",
                details={'expected': 'array', 'got': type(languages_affected).__name__}
            )

        # Initiate scan
        sync_service = get_sync_service()
        result = sync_service.start_sync_scan(
            sync_mode=sync_mode,
            languages_affected=languages_affected,
            initiated_by=g.current_user.id
        )

        return jsonify({
            'success': True,
            'data': result,
            'meta': {'timestamp': datetime.utcnow().isoformat()}
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e), 'details': e.details}
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


# ============================================================================
# COMPARISON PANEL
# ============================================================================

@bp.route('/<sync_id>/compare', methods=['GET'])
@require_auth
@require_role('admin')
def get_comparison_panel(sync_id: str):
    """
    GET /api/v1/admin/i18n-sync/{sync_id}/compare

    Get side-by-side comparison of frontend vs database translations.

    Results grouped by category:
    - NEW_KEYS: Only in frontend JSON
    - CHANGED_KEYS: In both, different values
    - DELETED_KEYS: Only in database
    - CONFLICTS: Changed keys with conflicts

    Query Parameters:
        - category: Filter by category (NEW_KEYS, CHANGED_KEYS, DELETED_KEYS, CONFLICTS)
        - limit: Max items per page (default 50, max 100)
        - offset: Pagination offset (default 0)

    Response (200 OK):
        {
            "success": true,
            "sync_id": "uuid",
            "categories": [
                {
                    "category": "NEW_KEYS",
                    "items": [
                        {
                            "namespace_code": "admin",
                            "key_path": "users.title",
                            "language": "de",
                            "action": "ADD",
                            "resolution_status": "PENDING",
                            "frontend_value": "Benutzer",
                            "database_value": null,
                            "similarity": 1.0,
                            "conflict_reason": null
                        }
                    ],
                    "count": 1
                }
            ],
            "total_items": 88,
            "sync_mode": "MANUAL",
            "pending_count": 12,
            "conflicts_count": 5,
            "can_apply": false
        }

    Errors:
        - 400: Invalid query parameters
        - 401: Unauthorized
        - 403: Forbidden
        - 404: Sync not found
    """
    try:
        # Validate sync_id UUID
        try:
            sync_uuid = UUID(sync_id)
        except ValueError:
            raise ValidationError("Invalid sync_id format", details={'expected': 'UUID', 'got': sync_id})

        # Get query parameters
        category = request.args.get('category')
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        # Get comparison panel
        sync_service = get_sync_service()
        result = sync_service.get_comparison_panel(
            sync_uuid,
            category=category,
            limit=limit,
            offset=offset
        )

        return jsonify({
            'success': True,
            'data': result,
            'meta': {'timestamp': datetime.utcnow().isoformat()}
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


# ============================================================================
# APPLY SYNC
# ============================================================================

@bp.route('/apply', methods=['POST'])
@require_auth
@require_role('admin')
def apply_sync():
    """
    POST /api/v1/admin/i18n-sync/apply

    Apply sync changes to database.

    In MANUAL mode: Only applies keys with provided resolutions
    In AUTO mode: Applies all keys with auto-generated actions

    Request Body:
        {
            "sync_id": "uuid",                      # Required
            "resolutions": {                        # Optional (MANUAL mode)
                "detail_id_1": {
                    "action": "SKIP" | "UPDATE" | "DELETE" | "ADD",
                    "manual_value": "Custom value"  # For MANUAL_OVERRIDE
                }
            },
            "force": false                          # Override conflict check
        }

    Response (200 OK):
        {
            "success": true,
            "status": "COMPLETED" | "FAILED",
            "applied_count": 76,
            "failed_count": 0,
            "errors": []
        }

    Errors:
        - 400: Validation error, unresolved conflicts
        - 401: Unauthorized
        - 403: Forbidden
        - 404: Sync not found
        - 409: Conflicts detected (use force=true to override)
    """
    try:
        data = request.get_json() or {}

        # Validate sync_id
        sync_id_str = data.get('sync_id')
        if not sync_id_str:
            raise ValidationError("sync_id is required")

        try:
            sync_uuid = UUID(sync_id_str)
        except ValueError:
            raise ValidationError("Invalid sync_id format")

        resolutions = data.get('resolutions')
        force = data.get('force', False)

        # Apply sync
        sync_service = get_sync_service()
        result = sync_service.apply_sync(
            sync_uuid,
            resolutions=resolutions,
            force=force
        )

        status_code = 200 if result['success'] else 409
        return jsonify({
            'success': result['success'],
            'data': result,
            'meta': {'timestamp': datetime.utcnow().isoformat()}
        }), status_code

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400

    except ValueError as e:
        if "conflicts" in str(e).lower():
            return jsonify({
                'success': False,
                'error': {'code': 'CONFLICT', 'message': str(e)}
            }), 409
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_REQUEST', 'message': str(e)}
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


# ============================================================================
# ROLLBACK
# ============================================================================

@bp.route('/<sync_id>/rollback', methods=['POST'])
@require_auth
@require_role('admin')
def rollback_sync(sync_id: str):
    """
    POST /api/v1/admin/i18n-sync/{sync_id}/rollback

    Rollback sync to PRE_SYNC snapshot state.

    Restores all translations to state before this sync was applied.
    Creates ROLLBACK type snapshot for audit trail.

    Request Body (optional):
        {
            "reason": "User requested rollback due to..." # Optional reason
        }

    Response (200 OK):
        {
            "success": true,
            "keys_restored": 156,
            "rollback_duration_ms": 1234,
            "message": "Successfully rolled back sync [sync_id]"
        }

    Errors:
        - 400: Invalid sync_id
        - 401: Unauthorized
        - 403: Forbidden
        - 404: Sync or snapshot not found
        - 409: Sync not in rolled-back state
    """
    try:
        # Validate sync_id
        try:
            sync_uuid = UUID(sync_id)
        except ValueError:
            raise ValidationError("Invalid sync_id format")

        data = request.get_json() or {}
        reason = data.get('reason', 'Admin requested rollback')

        # Perform rollback
        sync_service = get_sync_service()
        result = sync_service.rollback_sync(sync_uuid, reason=reason)

        return jsonify({
            'success': True,
            'data': {
                **result,
                'message': f"Successfully rolled back sync {sync_id}"
            },
            'meta': {'timestamp': datetime.utcnow().isoformat()}
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


# ============================================================================
# HISTORY & STATISTICS
# ============================================================================

@bp.route('/history', methods=['GET'])
@require_auth
@require_role('admin')
def get_sync_history():
    """
    GET /api/v1/admin/i18n-sync/history

    Get paginated list of past sync operations with statistics.

    Query Parameters:
        - limit: Max results (default 20, max 100)
        - offset: Pagination offset (default 0)
        - status: Filter by status (SCANNING, PENDING, APPLYING, COMPLETED, FAILED, ROLLED_BACK)
        - mode: Filter by mode (MANUAL, AUTO)

    Response (200 OK):
        {
            "success": true,
            "data": [
                {
                    "sync_id": "uuid",
                    "sync_mode": "MANUAL",
                    "sync_status": "COMPLETED",
                    "total_changes": 88,
                    "conflicts": 5,
                    "created_at": "2026-01-15T10:30:00Z",
                    "initiated_by": "user_id"
                }
            ],
            "total": 156,
            "limit": 20,
            "offset": 0
        }
    """
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        status = request.args.get('status')
        mode = request.args.get('mode')

        sync_service = get_sync_service()
        # TODO: Implement repository method for listing with filters
        result = {
            'data': [],
            'total': 0,
            'limit': limit,
            'offset': offset
        }

        return jsonify({
            'success': True,
            'data': result['data'],
            'meta': {
                'total': result['total'],
                'limit': result['limit'],
                'offset': result['offset'],
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@bp.route('/dashboard', methods=['GET'])
@require_auth
@require_role('admin')
def get_dashboard_stats():
    """
    GET /api/v1/admin/i18n-sync/dashboard

    Get dashboard statistics for i18n sync overview.

    Response (200 OK):
        {
            "success": true,
            "data": {
                "total_syncs": 42,
                "syncs_today": 3,
                "successful_syncs": 39,
                "failed_syncs": 3,
                "last_sync_timestamp": "2026-01-15T10:30:00Z",
                "last_sync_mode": "MANUAL",
                "avg_sync_duration_ms": 5432,
                "pending_resolutions": 12,
                "recent_syncs": [...]
            }
        }
    """
    try:
        sync_service = get_sync_service()
        # TODO: Implement repository method for dashboard statistics
        stats = {
            'total_syncs': 0,
            'syncs_today': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'pending_resolutions': 0,
            'recent_syncs': []
        }

        return jsonify({
            'success': True,
            'data': stats,
            'meta': {'timestamp': datetime.utcnow().isoformat()}
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


# Register blueprint
def register_i18n_sync_routes(app):
    """Register i18n sync blueprint with Flask app."""
    app.register_blueprint(bp)
