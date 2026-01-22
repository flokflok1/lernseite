"""
LernsystemX Admin System API - Audit Logs Module

Endpoints:
- GET /api/v1/admin/audit-logs - Paginated audit logs with filters

Phase 2.1 - Admin Dashboard Implementation
"""

from flask import request, jsonify, current_app, g
from datetime import datetime

from .system_operations import api_v1
from app.infrastructure.security.permissions import require_permission, Permissions
from app.application.services.audit_service import AuditService
from app.infrastructure.persistence.database.connection import fetch_all, fetch_one


@api_v1.route('/admin/audit-logs', methods=['GET'])
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_admin_audit_logs():
    """
    Get audit logs for admin dashboard.

    Query Parameters:
        page: Page number (default: 1)
        limit: Items per page (default: 20, max: 100)
        user_id: Filter by user ID (optional)
        action: Filter by action (optional)
        severity: Filter by severity (optional)

    Returns:
        Paginated list of audit logs

    **Endpoint:** GET /api/v1/admin/audit-logs

    **Authentication:** Required (Admin only)

    **Permissions:** ADMIN_SYSTEM_READ

    **Response:**
    ```json
    {
        "success": true,
        "logs": [...],
        "total": 1234,
        "page": 1,
        "limit": 20,
        "total_pages": 62
    }
    ```

    **Status Codes:**
    - 200: Success
    - 401: Unauthorized
    - 403: Forbidden (not admin)
    - 500: Server error
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        user_id = request.args.get('user_id')
        action = request.args.get('action')
        severity = request.args.get('severity')

        # Build WHERE clause
        where_conditions = []
        params = []

        if user_id:
            where_conditions.append("user_id = %s")
            params.append(user_id)

        if action:
            where_conditions.append("action ILIKE %s")
            params.append(f"%{action}%")

        if severity:
            where_conditions.append("severity = %s")
            params.append(severity)

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Count total
        count_query = f"SELECT COUNT(*) as total FROM audit_logs WHERE {where_clause}"
        total_result = fetch_one(count_query, tuple(params))
        total = total_result['total'] if total_result else 0

        # Calculate pagination
        total_pages = (total + limit - 1) // limit
        offset = (page - 1) * limit

        # Get logs
        logs_query = f"""
            SELECT
                log_id,
                user_id,
                action,
                resource_type,
                resource_id,
                description,
                metadata,
                severity,
                ip_address,
                user_agent,
                created_at
            FROM audit_logs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """

        logs = fetch_all(logs_query, tuple(params + [limit, offset]))

        # Convert UUIDs/timestamps/IPs to strings
        for log in logs:
            if 'log_id' in log and log['log_id']:
                log['log_id'] = str(log['log_id'])
            if 'user_id' in log and log['user_id']:
                log['user_id'] = str(log['user_id'])
            if 'resource_id' in log and log['resource_id']:
                log['resource_id'] = str(log['resource_id'])
            if 'ip_address' in log and log['ip_address']:
                log['ip_address'] = str(log['ip_address'])
            if 'created_at' in log:
                log['created_at'] = log['created_at'].isoformat() if log['created_at'] else None

        # Audit log (meta - logging that we viewed logs)
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_audit_logs',
            resource_type='audit_logs',
            severity='info',
            details={'filters': {'user_id': user_id, 'action': action, 'severity': severity}}
        )

        return jsonify({
            'success': True,
            'logs': logs,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': total_pages
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get audit logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve audit logs',
            'message': str(e)
        }), 500
