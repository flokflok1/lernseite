"""
LernsystemX Admin Course Analytics API

API endpoints for course-specific analytics in KI-Studio Pro.
Provides statistics about course content, AI usage, and learner engagement.

Endpoints:
  GET /admin/course-analytics/:course_id             - Course overview stats
  GET /admin/course-analytics/:course_id/ai-usage    - AI token/request stats
  GET /admin/course-analytics/:course_id/content     - Content statistics
  GET /admin/course-analytics/:course_id/engagement  - Learner engagement stats

ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta

from app.api.v1 import api_v1
from app.middleware.auth import admin_required
from app.database.connection import fetch_one, fetch_all


# ============================================================================
# Helper Functions
# ============================================================================

def _get_course_content_stats(course_id: str) -> dict:
    """Get content statistics for a course"""
    query = """
        WITH chapter_stats AS (
            SELECT
                COUNT(*) as chapter_count,
                SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published_chapters
            FROM chapters
            WHERE course_id = %s
        ),
        lesson_stats AS (
            SELECT
                COUNT(*) as lesson_count,
                SUM(CASE WHEN l.status = 'published' THEN 1 ELSE 0 END) as published_lessons
            FROM lessons l
            JOIN chapters ch ON ch.chapter_id = l.chapter_id
            WHERE ch.course_id = %s
        ),
        method_stats AS (
            SELECT
                COUNT(*) as method_count,
                COUNT(DISTINCT lmi.method_type) as unique_methods
            FROM learning_method_instances lmi
            JOIN lessons l ON l.lesson_id = lmi.lesson_id
            JOIN chapters ch ON ch.chapter_id = l.chapter_id
            WHERE ch.course_id = %s
        )
        SELECT
            cs.chapter_count,
            cs.published_chapters,
            ls.lesson_count,
            ls.published_lessons,
            ms.method_count,
            ms.unique_methods
        FROM chapter_stats cs, lesson_stats ls, method_stats ms
    """
    return fetch_one(query, (course_id, course_id, course_id)) or {
        'chapter_count': 0,
        'published_chapters': 0,
        'lesson_count': 0,
        'published_lessons': 0,
        'method_count': 0,
        'unique_methods': 0
    }


def _get_ai_usage_stats(course_id: str, days: int = 30) -> dict:
    """Get AI usage statistics for a course"""
    since = datetime.utcnow() - timedelta(days=days)

    query = """
        SELECT
            COUNT(*) as total_requests,
            COALESCE(SUM(tokens_used), 0) as total_tokens,
            COALESCE(SUM(cost_usd), 0) as total_cost_usd,
            COUNT(DISTINCT request_type) as request_types,
            COUNT(DISTINCT user_id) as unique_users
        FROM ki_requests
        WHERE course_id = %s AND created_at >= %s
    """
    stats = fetch_one(query, (course_id, since)) or {}

    # Get breakdown by request type
    type_query = """
        SELECT
            request_type,
            COUNT(*) as count,
            COALESCE(SUM(tokens_used), 0) as tokens
        FROM ki_requests
        WHERE course_id = %s AND created_at >= %s
        GROUP BY request_type
        ORDER BY count DESC
    """
    by_type = fetch_all(type_query, (course_id, since)) or []

    return {
        'total_requests': stats.get('total_requests', 0),
        'total_tokens': int(stats.get('total_tokens', 0)),
        'total_cost_usd': float(stats.get('total_cost_usd', 0)),
        'request_types': stats.get('request_types', 0),
        'unique_users': stats.get('unique_users', 0),
        'period_days': days,
        'by_type': [
            {'type': r['request_type'], 'count': r['count'], 'tokens': int(r['tokens'])}
            for r in by_type
        ]
    }


def _get_enrollment_stats(course_id: str) -> dict:
    """Get enrollment statistics for a course"""
    query = """
        SELECT
            COUNT(*) as total_enrollments,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_enrollments,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_enrollments,
            COALESCE(AVG(progress_percent), 0) as avg_progress
        FROM enrollments
        WHERE course_id = %s
    """
    return fetch_one(query, (course_id,)) or {
        'total_enrollments': 0,
        'active_enrollments': 0,
        'completed_enrollments': 0,
        'avg_progress': 0
    }


def _get_method_distribution(course_id: str) -> list:
    """Get learning method distribution for a course"""
    query = """
        SELECT
            lmi.method_type,
            lmt.name as method_name,
            COUNT(*) as count
        FROM learning_method_instances lmi
        JOIN lessons l ON l.lesson_id = lmi.lesson_id
        JOIN chapters ch ON ch.chapter_id = l.chapter_id
        LEFT JOIN learning_method_types lmt ON lmt.method_number = lmi.method_type
        WHERE ch.course_id = %s
        GROUP BY lmi.method_type, lmt.name
        ORDER BY count DESC
    """
    result = fetch_all(query, (course_id,)) or []
    return [
        {
            'method_type': r['method_type'],
            'method_name': r['method_name'] or f"LM{r['method_type']:02d}",
            'count': r['count']
        }
        for r in result
    ]


def _get_recent_sessions(course_id: str, limit: int = 10) -> list:
    """Get recent authoring sessions for a course"""
    query = """
        SELECT
            session_id,
            status,
            model_profile,
            total_tokens_used,
            total_operations,
            created_at,
            updated_at
        FROM course_authoring_sessions
        WHERE course_id = %s
        ORDER BY updated_at DESC
        LIMIT %s
    """
    result = fetch_all(query, (course_id, limit)) or []
    return [
        {
            'session_id': str(r['session_id']),
            'status': r['status'],
            'model_profile': r['model_profile'],
            'tokens_used': r['total_tokens_used'] or 0,
            'operations': r['total_operations'] or 0,
            'created_at': r['created_at'].isoformat() if r.get('created_at') else None,
            'updated_at': r['updated_at'].isoformat() if r.get('updated_at') else None
        }
        for r in result
    ]


# ============================================================================
# Endpoints
# ============================================================================

@api_v1.route('/admin/course-analytics/<course_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_course_analytics_overview(course_id: str):
    """
    Get analytics overview for a course

    Path Parameters:
        course_id: Course UUID

    Returns:
        Combined analytics overview

    Example Response:
        {
            "success": true,
            "data": {
                "course_id": "abc-123",
                "content": {...},
                "ai_usage": {...},
                "enrollments": {...},
                "method_distribution": [...],
                "recent_sessions": [...]
            }
        }
    """
    try:
        # Get all stats in parallel-ish (could be optimized with async)
        content = _get_course_content_stats(course_id)
        ai_usage = _get_ai_usage_stats(course_id, days=30)
        enrollments = _get_enrollment_stats(course_id)
        methods = _get_method_distribution(course_id)
        sessions = _get_recent_sessions(course_id, limit=5)

        return jsonify({
            "success": True,
            "data": {
                "course_id": course_id,
                "content": content,
                "ai_usage": ai_usage,
                "enrollments": enrollments,
                "method_distribution": methods,
                "recent_sessions": sessions,
                "generated_at": datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "ANALYTICS_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/course-analytics/<course_id>/ai-usage', methods=['GET'])
@jwt_required()
@admin_required
def get_course_ai_usage(course_id: str):
    """
    Get detailed AI usage statistics for a course

    Path Parameters:
        course_id: Course UUID

    Query Parameters:
        days: Number of days to look back (default 30)

    Returns:
        AI usage statistics

    Example Response:
        {
            "success": true,
            "data": {
                "total_requests": 150,
                "total_tokens": 45000,
                "total_cost_usd": 1.23,
                "by_type": [
                    {"type": "module_gen", "count": 50, "tokens": 20000},
                    ...
                ]
            }
        }
    """
    try:
        days = request.args.get('days', 30, type=int)
        days = min(max(days, 1), 365)  # Clamp to 1-365 days

        stats = _get_ai_usage_stats(course_id, days=days)

        return jsonify({
            "success": True,
            "data": stats
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "AI_USAGE_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/course-analytics/<course_id>/content', methods=['GET'])
@jwt_required()
@admin_required
def get_course_content_stats(course_id: str):
    """
    Get content statistics for a course

    Path Parameters:
        course_id: Course UUID

    Returns:
        Content statistics (chapters, lessons, methods)

    Example Response:
        {
            "success": true,
            "data": {
                "chapter_count": 5,
                "published_chapters": 3,
                "lesson_count": 25,
                "published_lessons": 15,
                "method_count": 50,
                "unique_methods": 8,
                "method_distribution": [...]
            }
        }
    """
    try:
        content = _get_course_content_stats(course_id)
        methods = _get_method_distribution(course_id)

        return jsonify({
            "success": True,
            "data": {
                **content,
                "method_distribution": methods
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "CONTENT_STATS_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/course-analytics/<course_id>/engagement', methods=['GET'])
@jwt_required()
@admin_required
def get_course_engagement_stats(course_id: str):
    """
    Get learner engagement statistics for a course

    Path Parameters:
        course_id: Course UUID

    Returns:
        Engagement statistics (enrollments, progress, completion)

    Example Response:
        {
            "success": true,
            "data": {
                "total_enrollments": 100,
                "active_enrollments": 75,
                "completed_enrollments": 20,
                "avg_progress": 45.5,
                "completion_rate": 20.0
            }
        }
    """
    try:
        stats = _get_enrollment_stats(course_id)

        # Calculate completion rate
        total = stats.get('total_enrollments', 0)
        completed = stats.get('completed_enrollments', 0)
        completion_rate = (completed / total * 100) if total > 0 else 0

        return jsonify({
            "success": True,
            "data": {
                **stats,
                'avg_progress': round(float(stats.get('avg_progress', 0)), 1),
                'completion_rate': round(completion_rate, 1)
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "ENGAGEMENT_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/course-analytics/<course_id>/sessions', methods=['GET'])
@jwt_required()
@admin_required
def get_course_authoring_sessions(course_id: str):
    """
    Get authoring session history for a course

    Path Parameters:
        course_id: Course UUID

    Query Parameters:
        limit: Maximum sessions to return (default 10)

    Returns:
        List of recent authoring sessions

    Example Response:
        {
            "success": true,
            "data": {
                "sessions": [
                    {
                        "session_id": "abc-123",
                        "status": "active",
                        "tokens_used": 5000,
                        ...
                    }
                ]
            }
        }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(max(limit, 1), 50)  # Clamp to 1-50

        sessions = _get_recent_sessions(course_id, limit=limit)

        return jsonify({
            "success": True,
            "data": {"sessions": sessions}
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "SESSIONS_ERROR", "message": str(e)}
        }), 500
