"""
Feedback Repository - Database operations for user feedback system.

Handles:
- Feedback submission (including anonymous)
- Feedback retrieval and filtering
- Admin operations (status updates, responses)
- AI processing results storage
- Summary batch management
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.infrastructure.persistence.repositories.core.base import BaseRepository


class FeedbackRepository(BaseRepository):
    """Repository for user feedback operations."""

    # =========================================================================
    # CREATE
    # =========================================================================

    @staticmethod
    def create_feedback(
        feedback_type: str,
        message: str,
        title: Optional[str] = None,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        is_anonymous: bool = False,
        context_course_id: Optional[str] = None,
        context_lesson_id: Optional[str] = None,
        context_page: Optional[str] = None,
        context_url: Optional[str] = None,
        context_user_agent: Optional[str] = None,
        context_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Create a new feedback entry."""
        query = """
            INSERT INTO user_feedback (
                feedback_type, message, title, user_id, email, is_anonymous,
                context_course_id, context_lesson_id, context_page,
                context_url, context_user_agent, context_data
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """
        import json
        return FeedbackRepository.fetch_one(query, (
            feedback_type,
            message,
            title,
            user_id,
            email,
            is_anonymous,
            context_course_id,
            context_lesson_id,
            context_page,
            context_url,
            context_user_agent,
            json.dumps(context_data or {})
        ))

    @staticmethod
    def create_attachment(
        feedback_id: str,
        file_name: str,
        file_path: str,
        file_type: Optional[str] = None,
        file_size: Optional[int] = None,
        is_screenshot: bool = False
    ) -> Optional[Dict]:
        """Add an attachment to feedback."""
        query = """
            INSERT INTO feedback_attachments (
                feedback_id, file_name, file_path, file_type, file_size, is_screenshot
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """
        return FeedbackRepository.fetch_one(query, (
            feedback_id, file_name, file_path, file_type, file_size, is_screenshot
        ))

    @staticmethod
    def create_note(
        feedback_id: str,
        author_id: str,
        note_text: str,
        is_internal: bool = True
    ) -> Optional[Dict]:
        """Add an internal note to feedback."""
        query = """
            INSERT INTO feedback_notes (feedback_id, author_id, note_text, is_internal)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return FeedbackRepository.fetch_one(query, (
            feedback_id, author_id, note_text, is_internal
        ))

    # =========================================================================
    # READ - Single
    # =========================================================================

    @staticmethod
    def get_by_id(feedback_id: str) -> Optional[Dict]:
        """Get feedback by ID with user and course info."""
        query = """
            SELECT
                f.*,
                u.username,
                u.email AS user_email,
                c.title AS course_title
            FROM user_feedback f
            LEFT JOIN core.users u ON f.user_id = u.user_id
            LEFT JOIN courses.courses c ON f.context_course_id = c.course_id
            WHERE f.feedback_id = %s
        """
        return FeedbackRepository.fetch_one(query, (feedback_id,))

    @staticmethod
    def get_attachments(feedback_id: str) -> List[Dict]:
        """Get all attachments for a feedback."""
        query = """
            SELECT * FROM feedback_attachments
            WHERE feedback_id = %s
            ORDER BY created_at
        """
        return FeedbackRepository.fetch_all(query, (feedback_id,))

    @staticmethod
    def get_notes(feedback_id: str) -> List[Dict]:
        """Get all notes for a feedback."""
        query = """
            SELECT
                n.*,
                u.username AS author_name
            FROM feedback_notes n
            JOIN core.users u ON n.author_id = u.user_id
            WHERE n.feedback_id = %s
            ORDER BY n.created_at
        """
        return FeedbackRepository.fetch_all(query, (feedback_id,))

    # =========================================================================
    # READ - Lists
    # =========================================================================

    @staticmethod
    def get_all(
        feedback_type: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        course_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get feedback list with filters."""
        conditions = []
        params = []

        if feedback_type:
            conditions.append("f.feedback_type = %s")
            params.append(feedback_type)

        if status:
            conditions.append("f.status = %s")
            params.append(status)

        if priority:
            conditions.append("f.priority = %s")
            params.append(priority)

        if course_id:
            conditions.append("f.context_course_id = %s")
            params.append(course_id)

        if search:
            conditions.append(
                "to_tsvector('german', coalesce(f.title, '') || ' ' || f.message) @@ plainto_tsquery('german', %s)"
            )
            params.append(search)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT
                f.*,
                u.username,
                c.title AS course_title,
                (SELECT COUNT(*) FROM feedback_attachments WHERE feedback_id = f.feedback_id) AS attachment_count,
                (SELECT COUNT(*) FROM feedback_notes WHERE feedback_id = f.feedback_id) AS note_count
            FROM user_feedback f
            LEFT JOIN core.users u ON f.user_id = u.user_id
            LEFT JOIN courses.courses c ON f.context_course_id = c.course_id
            {where_clause}
            ORDER BY
                CASE f.priority
                    WHEN 'urgent' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'normal' THEN 3
                    WHEN 'low' THEN 4
                END,
                f.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return FeedbackRepository.fetch_all(query, tuple(params))

    @staticmethod
    def get_new_count() -> int:
        """Get count of new/unread feedback."""
        query = "SELECT COUNT(*) AS count FROM user_feedback WHERE status = 'new'"
        result = FeedbackRepository.fetch_one(query)
        return result['count'] if result else 0

    @staticmethod
    def get_recent_by_user(user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent feedback from a specific user."""
        query = """
            SELECT * FROM user_feedback
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return FeedbackRepository.fetch_all(query, (user_id, limit))

    @staticmethod
    def get_unprocessed_for_ai(limit: int = 50) -> List[Dict]:
        """Get feedback that hasn't been AI processed yet."""
        query = """
            SELECT * FROM user_feedback
            WHERE ai_processed_at IS NULL
            ORDER BY created_at
            LIMIT %s
        """
        return FeedbackRepository.fetch_all(query, (limit,))

    @staticmethod
    def get_for_summary_batch(
        period_start: datetime,
        period_end: datetime
    ) -> List[Dict]:
        """Get feedback within a time period for batch summarization."""
        query = """
            SELECT * FROM user_feedback
            WHERE created_at >= %s AND created_at < %s
            ORDER BY created_at
        """
        return FeedbackRepository.fetch_all(query, (period_start, period_end))

    # =========================================================================
    # READ - Dashboard
    # =========================================================================

    @staticmethod
    def get_dashboard_stats() -> Optional[Dict]:
        """Get dashboard statistics."""
        query = "SELECT * FROM v_feedback_dashboard"
        return FeedbackRepository.fetch_one(query)

    @staticmethod
    def get_trending_topics(days: int = 30, limit: int = 10) -> List[Dict]:
        """Get trending topics/themes from AI analysis."""
        query = """
            SELECT
                unnest(ai_tags) AS tag,
                COUNT(*) AS count
            FROM user_feedback
            WHERE ai_tags IS NOT NULL
              AND created_at > NOW() - INTERVAL '%s days'
            GROUP BY tag
            ORDER BY count DESC
            LIMIT %s
        """
        return FeedbackRepository.fetch_all(query, (days, limit))

    @staticmethod
    def get_by_course_stats(limit: int = 10) -> List[Dict]:
        """Get feedback stats grouped by course."""
        query = """
            SELECT
                c.course_id,
                c.title AS course_title,
                COUNT(*) AS feedback_count,
                COUNT(*) FILTER (WHERE f.feedback_type = 'bug') AS bugs,
                COUNT(*) FILTER (WHERE f.feedback_type = 'question') AS questions,
                AVG(CASE f.ai_sentiment
                    WHEN 'positive' THEN 1
                    WHEN 'neutral' THEN 0
                    WHEN 'negative' THEN -1
                    ELSE 0
                END) AS avg_sentiment
            FROM user_feedback f
            JOIN courses.courses c ON f.context_course_id = c.course_id
            WHERE f.context_course_id IS NOT NULL
            GROUP BY c.course_id, c.title
            ORDER BY feedback_count DESC
            LIMIT %s
        """
        return FeedbackRepository.fetch_all(query, (limit,))

    # =========================================================================
    # UPDATE
    # =========================================================================

    @staticmethod
    def update_status(
        feedback_id: str,
        status: str,
        assigned_to: Optional[str] = None
    ) -> Optional[Dict]:
        """Update feedback status."""
        query = """
            UPDATE user_feedback
            SET status = %s, assigned_to = %s
            WHERE feedback_id = %s
            RETURNING *
        """
        return FeedbackRepository.fetch_one(query, (status, assigned_to, feedback_id))

    @staticmethod
    def update_priority(feedback_id: str, priority: str) -> Optional[Dict]:
        """Update feedback priority."""
        query = """
            UPDATE user_feedback
            SET priority = %s
            WHERE feedback_id = %s
            RETURNING *
        """
        return FeedbackRepository.fetch_one(query, (priority, feedback_id))

    @staticmethod
    def add_admin_response(
        feedback_id: str,
        response: str,
        admin_id: str
    ) -> Optional[Dict]:
        """Add admin response to feedback."""
        query = """
            UPDATE user_feedback
            SET
                admin_response = %s,
                admin_responded_by = %s,
                admin_responded_at = NOW(),
                status = CASE WHEN status = 'new' THEN 'in_progress' ELSE status END
            WHERE feedback_id = %s
            RETURNING *
        """
        return FeedbackRepository.fetch_one(query, (response, admin_id, feedback_id))

    @staticmethod
    def update_ai_analysis(
        feedback_id: str,
        summary: Optional[str] = None,
        category: Optional[str] = None,
        sentiment: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Update AI analysis results."""
        query = """
            UPDATE user_feedback
            SET
                ai_summary = COALESCE(%s, ai_summary),
                ai_category = COALESCE(%s, ai_category),
                ai_sentiment = COALESCE(%s, ai_sentiment),
                ai_tags = COALESCE(%s, ai_tags),
                ai_processed_at = NOW()
            WHERE feedback_id = %s
            RETURNING *
        """
        return FeedbackRepository.fetch_one(query, (
            summary, category, sentiment, tags, feedback_id
        ))

    # =========================================================================
    # SUMMARY BATCHES
    # =========================================================================

    @staticmethod
    def create_summary_batch(
        period_start: datetime,
        period_end: datetime,
        stats: Dict,
        ai_summary: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Create a summary batch."""
        import json
        query = """
            INSERT INTO feedback_summary_batches (
                period_start, period_end,
                total_feedbacks, questions_count, bugs_count,
                suggestions_count, praise_count, other_count,
                ai_executive_summary, ai_key_themes, ai_action_items,
                ai_sentiment_breakdown, ai_top_courses,
                processed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING *
        """
        return FeedbackRepository.fetch_one(query, (
            period_start,
            period_end,
            stats.get('total', 0),
            stats.get('questions', 0),
            stats.get('bugs', 0),
            stats.get('suggestions', 0),
            stats.get('praise', 0),
            stats.get('other', 0),
            ai_summary.get('executive_summary') if ai_summary else None,
            json.dumps(ai_summary.get('key_themes', [])) if ai_summary else '[]',
            json.dumps(ai_summary.get('action_items', [])) if ai_summary else '[]',
            json.dumps(ai_summary.get('sentiment_breakdown', {})) if ai_summary else '{}',
            json.dumps(ai_summary.get('top_courses', [])) if ai_summary else '[]'
        ))

    @staticmethod
    def get_latest_summary_batches(limit: int = 10) -> List[Dict]:
        """Get recent summary batches."""
        query = """
            SELECT * FROM feedback_summary_batches
            ORDER BY period_end DESC
            LIMIT %s
        """
        return FeedbackRepository.fetch_all(query, (limit,))

    @staticmethod
    def get_summary_batch_by_id(batch_id: str) -> Optional[Dict]:
        """Get a specific summary batch."""
        query = "SELECT * FROM feedback_summary_batches WHERE batch_id = %s"
        return FeedbackRepository.fetch_one(query, (batch_id,))

    # =========================================================================
    # DELETE
    # =========================================================================

    @staticmethod
    def delete_feedback(feedback_id: str) -> bool:
        """Delete feedback (cascades to attachments and notes)."""
        query = "DELETE FROM user_feedback WHERE feedback_id = %s RETURNING feedback_id"
        result = FeedbackRepository.fetch_one(query, (feedback_id,))
        return result is not None

    @staticmethod
    def delete_attachment(attachment_id: str) -> bool:
        """Delete an attachment."""
        query = "DELETE FROM feedback_attachments WHERE attachment_id = %s RETURNING attachment_id"
        result = FeedbackRepository.fetch_one(query, (attachment_id,))
        return result is not None
