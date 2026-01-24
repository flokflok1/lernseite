"""
Admin Dashboard Statistics API

Provides dashboard statistics for admin panel:
- User statistics (total, active, by role)
- Course statistics (total, published, draft)
- System statistics (uptime, performance metrics)
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime, timedelta
from app.core.bootstrap import extensions

bp = Blueprint('admin_stats', __name__, url_prefix='/admin/stats')


@bp.route('/users', methods=['GET'])
def get_user_stats():
    """
    Get user statistics for dashboard.

    Returns:
        {
            "total_users": int,
            "active_users": int,
            "banned_users": int,
            "new_users_30d": int
        }
    """
    try:
        with extensions.db_pool.connection() as conn:
            with conn.cursor() as cur:
                # Get total users
                cur.execute("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL")
                total_users = cur.fetchone()[0]

                # Get active users (logged in last 7 days)
                cur.execute("""
                    SELECT COUNT(*) FROM users
                    WHERE last_login >= NOW() - INTERVAL '7 days'
                    AND deleted_at IS NULL
                """)
                active_users = cur.fetchone()[0]

                # Get banned users
                cur.execute("""
                    SELECT COUNT(*) FROM users
                    WHERE status = 'banned'
                    AND deleted_at IS NULL
                """)
                banned_users = cur.fetchone()[0]

                # Get new users in last 30 days
                cur.execute("""
                    SELECT COUNT(*) FROM users
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                    AND deleted_at IS NULL
                """)
                new_users_30d = cur.fetchone()[0]

        return jsonify({
            'success': True,
            'data': {
                'total_users': total_users,
                'active_users': active_users,
                'banned_users': banned_users,
                'new_users_30d': new_users_30d,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get user stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load user statistics'
        }), 500


@bp.route('/courses', methods=['GET'])
def get_course_stats():
    """
    Get course statistics for dashboard.

    Returns:
        {
            "total_courses": int,
            "published": int,
            "pending_review": int,
            "rejected": int
        }
    """
    try:
        with extensions.db_pool.connection() as conn:
            with conn.cursor() as cur:
                # Get total courses
                cur.execute("SELECT COUNT(*) FROM courses")
                total_courses = cur.fetchone()[0]

                # Get published courses
                cur.execute("""
                    SELECT COUNT(*) FROM courses
                    WHERE published = true
                """)
                published = cur.fetchone()[0]

                # Get pending review courses
                cur.execute("""
                    SELECT COUNT(*) FROM courses
                    WHERE status = 'pending_review'
                    OR published = false
                """)
                pending_review = cur.fetchone()[0]

                # Get rejected courses
                cur.execute("""
                    SELECT COUNT(*) FROM courses
                    WHERE status = 'rejected'
                """)
                rejected = cur.fetchone()[0]

        return jsonify({
            'success': True,
            'data': {
                'total_courses': total_courses,
                'published': published,
                'pending_review': pending_review,
                'rejected': rejected,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get course stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load course statistics'
        }), 500


@bp.route('/system', methods=['GET'])
def get_system_stats():
    """
    Get system statistics for dashboard.

    Returns:
        {
            "uptime": int (seconds since app start),
            "db_latency": float (milliseconds),
            "request_count_24h": int,
            "error_rate": float (0.0 to 1.0)
        }
    """
    try:
        # Calculate database latency
        import time
        db_start = time.time()

        with extensions.db_pool.connection() as conn:
            with conn.cursor() as cur:
                # Simple query to measure DB latency
                cur.execute("SELECT 1")
                cur.fetchone()

        db_latency = (time.time() - db_start) * 1000  # Convert to milliseconds

        # Get uptime (use app start time from config or default to 0)
        app_start = getattr(current_app, '_start_time', datetime.utcnow())
        uptime = int((datetime.utcnow() - app_start).total_seconds())

        # Request count in last 24 hours (placeholder - would need request logging)
        request_count_24h = 1000

        # Error rate (placeholder - would need error tracking)
        error_rate = 0.02

        return jsonify({
            'success': True,
            'data': {
                'uptime': uptime,
                'db_latency': round(db_latency, 2),
                'request_count_24h': request_count_24h,
                'error_rate': error_rate,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get system stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load system statistics'
        }), 500
