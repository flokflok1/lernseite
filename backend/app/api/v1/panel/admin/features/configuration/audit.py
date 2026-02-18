"""
Feature Configuration Admin API - Audit Logging

Admin endpoints for viewing feature configuration changes:
- View audit logs
- Track feature changes over time
- Monitor admin actions

All endpoints require admin authentication.
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any, Tuple, Optional
import logging
from datetime import datetime, timedelta

from app.infrastructure.persistence.database import get_db_connection
from app.infrastructure.persistence.repositories.audit.log import AuditLogRepository
from app.infrastructure.error_handling.exceptions import ValidationError, NotFoundError
from app.api.middleware.auth import token_required, admin_required

logger = logging.getLogger(__name__)

bp = Blueprint(
    'admin_feature_audit',
    __name__,
    url_prefix='/admin/feature-configuration/audit'
)


# ============================================================================
# AUDIT LOG VIEWING
# ============================================================================

@bp.route('/logs', methods=['GET'])
@token_required
@admin_required
def list_audit_logs() -> Tuple[Dict[str, Any], int]:
    """
    List audit logs for feature configuration changes.

    Query Parameters:
        - feature_name: Filter by feature
        - action: Filter by action type
        - admin_id: Filter by admin who made change
        - days: Show last N days (default 7)
        - limit: Max results (default 100)
        - offset: Skip N results

    Returns:
        200: List of audit logs
        401: Unauthorized
        403: Forbidden

    Example:
        GET /api/v1/admin/feature-configuration/audit/logs?feature_name=ai_editor&days=7
    """
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        days = int(request.args.get('days', 7))

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        with get_db_connection() as conn:
            repo = AuditLogRepository(conn)

            filters = {
                'created_at_gte': start_date,
                'created_at_lte': end_date,
                'entity_type': 'feature_configuration'
            }

            # Apply optional filters
            if request.args.get('feature_name'):
                filters['entity_id'] = request.args.get('feature_name')

            if request.args.get('action'):
                filters['action'] = request.args.get('action')

            if request.args.get('admin_id'):
                filters['user_id'] = request.args.get('admin_id')

            logs = repo.find_all(filters=filters, limit=limit, offset=offset)
            total = repo.count(filters=filters)

        return jsonify({
            'success': True,
            'data': [l.to_dict() if hasattr(l, 'to_dict') else l for l in logs],
            'meta': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'days': days,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
        }), 200

    except ValueError as e:
        logger.warning(f"Invalid parameters: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_PARAMETERS', 'message': str(e)}
        }), 400

    except Exception as e:
        logger.error(f"Error listing audit logs: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'LIST_LOGS_FAILED', 'message': 'Failed to list audit logs'}
        }), 500


@bp.route('/logs/<log_id>', methods=['GET'])
@token_required
@admin_required
def get_audit_log(log_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get single audit log entry.

    Returns:
        200: Audit log entry
        404: Log not found

    Example:
        GET /api/v1/admin/feature-configuration/audit/logs/{log_id}
    """
    try:
        with get_db_connection() as conn:
            repo = AuditLogRepository(conn)
            log = repo.find_by_id(log_id)

        if not log:
            raise NotFoundError(f"Audit log {log_id} not found")

        return jsonify({
            'success': True,
            'data': log.to_dict() if hasattr(log, 'to_dict') else log
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'LOG_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error getting audit log {log_id}: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'GET_LOG_FAILED', 'message': 'Failed to get audit log'}
        }), 500


@bp.route('/logs/feature/<feature_name>', methods=['GET'])
@token_required
@admin_required
def get_feature_change_history(feature_name: str) -> Tuple[Dict[str, Any], int]:
    """
    Get complete change history for a specific feature.

    Query Parameters:
        - limit: Max results (default 50)
        - offset: Skip N results

    Returns:
        200: Feature change history
        404: No history found

    Example:
        GET /api/v1/admin/feature-configuration/audit/logs/feature/{feature_name}
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))

        with get_db_connection() as conn:
            repo = AuditLogRepository(conn)

            filters = {
                'entity_type': 'feature_configuration',
                'entity_id': feature_name
            }

            logs = repo.find_all(filters=filters, limit=limit, offset=offset)
            total = repo.count(filters=filters)

        if total == 0:
            raise NotFoundError(f"No change history found for feature {feature_name}")

        return jsonify({
            'success': True,
            'data': [l.to_dict() if hasattr(l, 'to_dict') else l for l in logs],
            'meta': {
                'feature_name': feature_name,
                'total_changes': total,
                'limit': limit,
                'offset': offset
            }
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'HISTORY_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error getting feature history: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'HISTORY_FAILED', 'message': 'Failed to get feature history'}
        }), 500


@bp.route('/logs/admin/<admin_id>', methods=['GET'])
@token_required
@admin_required
def get_admin_activity(admin_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get all activities performed by a specific admin.

    Query Parameters:
        - days: Show last N days (default 30)
        - limit: Max results (default 100)
        - offset: Skip N results

    Returns:
        200: Admin activity log

    Example:
        GET /api/v1/admin/feature-configuration/audit/logs/admin/{admin_id}?days=30
    """
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))
        days = int(request.args.get('days', 30))

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        with get_db_connection() as conn:
            repo = AuditLogRepository(conn)

            filters = {
                'user_id': admin_id,
                'entity_type': 'feature_configuration',
                'created_at_gte': start_date,
                'created_at_lte': end_date
            }

            logs = repo.find_all(filters=filters, limit=limit, offset=offset)
            total = repo.count(filters=filters)

        return jsonify({
            'success': True,
            'data': [l.to_dict() if hasattr(l, 'to_dict') else l for l in logs],
            'meta': {
                'admin_id': admin_id,
                'total_actions': total,
                'days': days,
                'limit': limit,
                'offset': offset
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting admin activity: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'ACTIVITY_FAILED', 'message': 'Failed to get admin activity'}
        }), 500


@bp.route('/logs/action-summary', methods=['GET'])
@token_required
@admin_required
def get_action_summary() -> Tuple[Dict[str, Any], int]:
    """
    Get summary of actions by type.

    Query Parameters:
        - days: Show last N days (default 7)

    Returns:
        200: Summary statistics

    Example:
        GET /api/v1/admin/feature-configuration/audit/logs/action-summary?days=7
    """
    try:
        days = int(request.args.get('days', 7))

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        with get_db_connection() as conn:
            repo = AuditLogRepository(conn)

            filters = {
                'entity_type': 'feature_configuration',
                'created_at_gte': start_date,
                'created_at_lte': end_date
            }

            logs = repo.find_all(filters=filters, limit=10000, offset=0)

        # Aggregate by action type
        action_summary: Dict[str, int] = {}
        admin_summary: Dict[str, int] = {}

        for log in logs:
            log_dict = log.to_dict() if hasattr(log, 'to_dict') else log

            action = log_dict.get('action', 'unknown')
            action_summary[action] = action_summary.get(action, 0) + 1

            user_id = log_dict.get('user_id', 'unknown')
            admin_summary[user_id] = admin_summary.get(user_id, 0) + 1

        return jsonify({
            'success': True,
            'data': {
                'actions': action_summary,
                'admins': admin_summary,
                'total_events': len(logs)
            },
            'meta': {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting action summary: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'SUMMARY_FAILED', 'message': 'Failed to get action summary'}
        }), 500


@bp.route('/logs/export', methods=['GET'])
@token_required
@admin_required
def export_audit_logs() -> Tuple[Dict[str, Any], int]:
    """
    Export audit logs in CSV format.

    Query Parameters:
        - feature_name: Filter by feature
        - days: Show last N days (default 7)
        - limit: Max results (default 1000)

    Returns:
        200: CSV data
        413: Too much data

    Example:
        GET /api/v1/admin/feature-configuration/audit/logs/export?days=7
    """
    try:
        days = int(request.args.get('days', 7))
        limit = min(int(request.args.get('limit', 1000)), 5000)

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        with get_db_connection() as conn:
            repo = AuditLogRepository(conn)

            filters = {
                'entity_type': 'feature_configuration',
                'created_at_gte': start_date,
                'created_at_lte': end_date
            }

            if request.args.get('feature_name'):
                filters['entity_id'] = request.args.get('feature_name')

            logs = repo.find_all(filters=filters, limit=limit, offset=0)

        # Build CSV data
        import io
        import csv

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'timestamp',
            'admin_id',
            'action',
            'feature_name',
            'details'
        ])

        # Write rows
        for log in logs:
            log_dict = log.to_dict() if hasattr(log, 'to_dict') else log

            writer.writerow([
                log_dict.get('created_at', ''),
                log_dict.get('user_id', ''),
                log_dict.get('action', ''),
                log_dict.get('entity_id', ''),
                log_dict.get('details', '')
            ])

        return jsonify({
            'success': True,
            'data': output.getvalue(),
            'meta': {
                'total_records': len(logs),
                'export_date': datetime.utcnow().isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Error exporting audit logs: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'EXPORT_FAILED', 'message': 'Failed to export audit logs'}
        }), 500
