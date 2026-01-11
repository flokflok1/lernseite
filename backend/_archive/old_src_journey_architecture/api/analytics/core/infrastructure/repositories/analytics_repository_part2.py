"""
Analytics Repository Part 2 (Infrastructure Layer)

Database access for:
- user_feedback
- feedback_summary_batches
- feedback_attachments
- feedback_notes

ALL queries use parameterized statements for security.
NO hardcoded values - everything loaded from database.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from src.core.database import get_db_connection
from src.api.analytics.core.domain.entities.user_feedback import UserFeedback
from src.api.analytics.core.domain.entities.feedback_summary_batch import FeedbackSummaryBatch
from src.api.analytics.core.domain.entities.feedback_attachment import FeedbackAttachment
from src.api.analytics.core.domain.entities.feedback_note import FeedbackNote


class AnalyticsRepositoryPart2:
    """
    Analytics Repository Part 2 - Feedback System.
    """

    # ============================================================================
    # USER FEEDBACK
    # ============================================================================

    @staticmethod
    def find_feedback_by_id(feedback_id: str) -> Optional[UserFeedback]:
        """Find user feedback by ID."""
        query = """
            SELECT feedback_id, user_id, is_anonymous, email, feedback_type,
                   title, message, context_course_id, context_lesson_id,
                   context_page, context_url, context_user_agent, context_data,
                   status, priority, assigned_to, ai_summary, ai_category,
                   ai_sentiment, ai_tags, ai_processed_at, admin_response,
                   admin_responded_by, admin_responded_at, created_at,
                   updated_at, resolved_at
            FROM support_systems.user_feedback
            WHERE feedback_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (feedback_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return UserFeedback(
                    feedback_id=row[0],
                    user_id=row[1],
                    is_anonymous=row[2] or False,
                    email=row[3],
                    feedback_type=row[4],
                    title=row[5],
                    message=row[6],
                    context_course_id=row[7],
                    context_lesson_id=row[8],
                    context_page=row[9],
                    context_url=row[10],
                    context_user_agent=row[11],
                    context_data=row[12],
                    status=row[13] or 'new',
                    priority=row[14] or 'normal',
                    assigned_to=row[15],
                    ai_summary=row[16],
                    ai_category=row[17],
                    ai_sentiment=row[18],
                    ai_tags=row[19],
                    ai_processed_at=row[20],
                    admin_response=row[21],
                    admin_responded_by=row[22],
                    admin_responded_at=row[23],
                    created_at=row[24],
                    updated_at=row[25],
                    resolved_at=row[26]
                )

    @staticmethod
    def find_all_feedback(
        status: Optional[str] = None,
        feedback_type: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserFeedback]:
        """Find all feedback with filters."""
        query = """
            SELECT feedback_id, user_id, is_anonymous, email, feedback_type,
                   title, message, context_course_id, context_lesson_id,
                   context_page, context_url, context_user_agent, context_data,
                   status, priority, assigned_to, ai_summary, ai_category,
                   ai_sentiment, ai_tags, ai_processed_at, admin_response,
                   admin_responded_by, admin_responded_at, created_at,
                   updated_at, resolved_at
            FROM support_systems.user_feedback
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND status = %s"
            params.append(status)

        if feedback_type:
            query += " AND feedback_type = %s"
            params.append(feedback_type)

        if priority:
            query += " AND priority = %s"
            params.append(priority)

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    UserFeedback(
                        feedback_id=row[0],
                        user_id=row[1],
                        is_anonymous=row[2] or False,
                        email=row[3],
                        feedback_type=row[4],
                        title=row[5],
                        message=row[6],
                        context_course_id=row[7],
                        context_lesson_id=row[8],
                        context_page=row[9],
                        context_url=row[10],
                        context_user_agent=row[11],
                        context_data=row[12],
                        status=row[13] or 'new',
                        priority=row[14] or 'normal',
                        assigned_to=row[15],
                        ai_summary=row[16],
                        ai_category=row[17],
                        ai_sentiment=row[18],
                        ai_tags=row[19],
                        ai_processed_at=row[20],
                        admin_response=row[21],
                        admin_responded_by=row[22],
                        admin_responded_at=row[23],
                        created_at=row[24],
                        updated_at=row[25],
                        resolved_at=row[26]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_feedback(feedback: UserFeedback) -> UserFeedback:
        """Create new user feedback."""
        query = """
            INSERT INTO support_systems.user_feedback
            (feedback_id, user_id, is_anonymous, email, feedback_type,
             title, message, context_course_id, context_lesson_id,
             context_page, context_url, context_user_agent, context_data,
             status, priority, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING feedback_id, user_id, is_anonymous, email, feedback_type,
                      title, message, context_course_id, context_lesson_id,
                      context_page, context_url, context_user_agent, context_data,
                      status, priority, assigned_to, ai_summary, ai_category,
                      ai_sentiment, ai_tags, ai_processed_at, admin_response,
                      admin_responded_by, admin_responded_at, created_at,
                      updated_at, resolved_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    feedback.feedback_id,
                    feedback.user_id,
                    feedback.is_anonymous,
                    feedback.email,
                    feedback.feedback_type,
                    feedback.title,
                    feedback.message,
                    feedback.context_course_id,
                    feedback.context_lesson_id,
                    feedback.context_page,
                    feedback.context_url,
                    feedback.context_user_agent,
                    json.dumps(feedback.context_data) if feedback.context_data else None,
                    feedback.status,
                    feedback.priority,
                    feedback.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return UserFeedback(
                    feedback_id=row[0],
                    user_id=row[1],
                    is_anonymous=row[2] or False,
                    email=row[3],
                    feedback_type=row[4],
                    title=row[5],
                    message=row[6],
                    context_course_id=row[7],
                    context_lesson_id=row[8],
                    context_page=row[9],
                    context_url=row[10],
                    context_user_agent=row[11],
                    context_data=row[12],
                    status=row[13] or 'new',
                    priority=row[14] or 'normal',
                    assigned_to=row[15],
                    ai_summary=row[16],
                    ai_category=row[17],
                    ai_sentiment=row[18],
                    ai_tags=row[19],
                    ai_processed_at=row[20],
                    admin_response=row[21],
                    admin_responded_by=row[22],
                    admin_responded_at=row[23],
                    created_at=row[24],
                    updated_at=row[25],
                    resolved_at=row[26]
                )

    @staticmethod
    def update_feedback(feedback: UserFeedback) -> UserFeedback:
        """Update existing user feedback."""
        query = """
            UPDATE support_systems.user_feedback
            SET status = %s,
                priority = %s,
                assigned_to = %s,
                ai_summary = %s,
                ai_category = %s,
                ai_sentiment = %s,
                ai_tags = %s,
                ai_processed_at = %s,
                admin_response = %s,
                admin_responded_by = %s,
                admin_responded_at = %s,
                updated_at = %s,
                resolved_at = %s
            WHERE feedback_id = %s
            RETURNING feedback_id, user_id, is_anonymous, email, feedback_type,
                      title, message, context_course_id, context_lesson_id,
                      context_page, context_url, context_user_agent, context_data,
                      status, priority, assigned_to, ai_summary, ai_category,
                      ai_sentiment, ai_tags, ai_processed_at, admin_response,
                      admin_responded_by, admin_responded_at, created_at,
                      updated_at, resolved_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    feedback.status,
                    feedback.priority,
                    feedback.assigned_to,
                    feedback.ai_summary,
                    feedback.ai_category,
                    feedback.ai_sentiment,
                    feedback.ai_tags,
                    feedback.ai_processed_at,
                    feedback.admin_response,
                    feedback.admin_responded_by,
                    feedback.admin_responded_at,
                    feedback.updated_at or datetime.utcnow(),
                    feedback.resolved_at,
                    feedback.feedback_id
                ))

                row = cur.fetchone()
                conn.commit()

                return UserFeedback(
                    feedback_id=row[0],
                    user_id=row[1],
                    is_anonymous=row[2] or False,
                    email=row[3],
                    feedback_type=row[4],
                    title=row[5],
                    message=row[6],
                    context_course_id=row[7],
                    context_lesson_id=row[8],
                    context_page=row[9],
                    context_url=row[10],
                    context_user_agent=row[11],
                    context_data=row[12],
                    status=row[13] or 'new',
                    priority=row[14] or 'normal',
                    assigned_to=row[15],
                    ai_summary=row[16],
                    ai_category=row[17],
                    ai_sentiment=row[18],
                    ai_tags=row[19],
                    ai_processed_at=row[20],
                    admin_response=row[21],
                    admin_responded_by=row[22],
                    admin_responded_at=row[23],
                    created_at=row[24],
                    updated_at=row[25],
                    resolved_at=row[26]
                )

    # ============================================================================
    # FEEDBACK SUMMARY BATCHES
    # ============================================================================

    @staticmethod
    def find_batch_by_id(batch_id: str) -> Optional[FeedbackSummaryBatch]:
        """Find feedback summary batch by ID."""
        query = """
            SELECT batch_id, period_start, period_end, total_feedbacks,
                   questions_count, bugs_count, suggestions_count,
                   praise_count, other_count, ai_executive_summary,
                   ai_key_themes, ai_action_items, ai_sentiment_breakdown,
                   ai_top_courses, processed_at, processing_tokens, created_at
            FROM support_systems.feedback_summary_batches
            WHERE batch_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (batch_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return FeedbackSummaryBatch(
                    batch_id=row[0],
                    period_start=row[1],
                    period_end=row[2],
                    total_feedbacks=row[3] or 0,
                    questions_count=row[4] or 0,
                    bugs_count=row[5] or 0,
                    suggestions_count=row[6] or 0,
                    praise_count=row[7] or 0,
                    other_count=row[8] or 0,
                    ai_executive_summary=row[9],
                    ai_key_themes=row[10],
                    ai_action_items=row[11],
                    ai_sentiment_breakdown=row[12],
                    ai_top_courses=row[13],
                    processed_at=row[14],
                    processing_tokens=row[15] or 0,
                    created_at=row[16]
                )

    @staticmethod
    def create_batch(batch: FeedbackSummaryBatch) -> FeedbackSummaryBatch:
        """Create new feedback summary batch."""
        query = """
            INSERT INTO support_systems.feedback_summary_batches
            (batch_id, period_start, period_end, total_feedbacks,
             questions_count, bugs_count, suggestions_count,
             praise_count, other_count, ai_executive_summary,
             ai_key_themes, ai_action_items, ai_sentiment_breakdown,
             ai_top_courses, processed_at, processing_tokens, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING batch_id, period_start, period_end, total_feedbacks,
                      questions_count, bugs_count, suggestions_count,
                      praise_count, other_count, ai_executive_summary,
                      ai_key_themes, ai_action_items, ai_sentiment_breakdown,
                      ai_top_courses, processed_at, processing_tokens, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    batch.batch_id,
                    batch.period_start,
                    batch.period_end,
                    batch.total_feedbacks,
                    batch.questions_count,
                    batch.bugs_count,
                    batch.suggestions_count,
                    batch.praise_count,
                    batch.other_count,
                    batch.ai_executive_summary,
                    json.dumps(batch.ai_key_themes) if batch.ai_key_themes else None,
                    json.dumps(batch.ai_action_items) if batch.ai_action_items else None,
                    json.dumps(batch.ai_sentiment_breakdown) if batch.ai_sentiment_breakdown else None,
                    json.dumps(batch.ai_top_courses) if batch.ai_top_courses else None,
                    batch.processed_at,
                    batch.processing_tokens,
                    batch.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return FeedbackSummaryBatch(
                    batch_id=row[0],
                    period_start=row[1],
                    period_end=row[2],
                    total_feedbacks=row[3] or 0,
                    questions_count=row[4] or 0,
                    bugs_count=row[5] or 0,
                    suggestions_count=row[6] or 0,
                    praise_count=row[7] or 0,
                    other_count=row[8] or 0,
                    ai_executive_summary=row[9],
                    ai_key_themes=row[10],
                    ai_action_items=row[11],
                    ai_sentiment_breakdown=row[12],
                    ai_top_courses=row[13],
                    processed_at=row[14],
                    processing_tokens=row[15] or 0,
                    created_at=row[16]
                )

    # ============================================================================
    # FEEDBACK ATTACHMENTS
    # ============================================================================

    @staticmethod
    def find_attachments_by_feedback(feedback_id: str) -> List[FeedbackAttachment]:
        """Find all attachments for a feedback."""
        query = """
            SELECT attachment_id, feedback_id, file_name, file_type, file_size,
                   file_path, is_screenshot, ai_screenshot_description, created_at
            FROM support_systems.feedback_attachments
            WHERE feedback_id = %s
            ORDER BY created_at ASC
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (feedback_id,))
                rows = cur.fetchall()

                return [
                    FeedbackAttachment(
                        attachment_id=row[0],
                        feedback_id=row[1],
                        file_name=row[2],
                        file_type=row[3],
                        file_size=row[4],
                        file_path=row[5],
                        is_screenshot=row[6] or False,
                        ai_screenshot_description=row[7],
                        created_at=row[8]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_attachment(attachment: FeedbackAttachment) -> FeedbackAttachment:
        """Create new feedback attachment."""
        query = """
            INSERT INTO support_systems.feedback_attachments
            (attachment_id, feedback_id, file_name, file_type, file_size,
             file_path, is_screenshot, ai_screenshot_description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING attachment_id, feedback_id, file_name, file_type, file_size,
                      file_path, is_screenshot, ai_screenshot_description, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    attachment.attachment_id,
                    attachment.feedback_id,
                    attachment.file_name,
                    attachment.file_type,
                    attachment.file_size,
                    attachment.file_path,
                    attachment.is_screenshot,
                    attachment.ai_screenshot_description,
                    attachment.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return FeedbackAttachment(
                    attachment_id=row[0],
                    feedback_id=row[1],
                    file_name=row[2],
                    file_type=row[3],
                    file_size=row[4],
                    file_path=row[5],
                    is_screenshot=row[6] or False,
                    ai_screenshot_description=row[7],
                    created_at=row[8]
                )

    # ============================================================================
    # FEEDBACK NOTES
    # ============================================================================

    @staticmethod
    def find_notes_by_feedback(feedback_id: str) -> List[FeedbackNote]:
        """Find all notes for a feedback."""
        query = """
            SELECT note_id, feedback_id, author_id, note_text, is_internal, created_at
            FROM support_systems.feedback_notes
            WHERE feedback_id = %s
            ORDER BY created_at ASC
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (feedback_id,))
                rows = cur.fetchall()

                return [
                    FeedbackNote(
                        note_id=row[0],
                        feedback_id=row[1],
                        author_id=row[2],
                        note_text=row[3],
                        is_internal=row[4] if row[4] is not None else True,
                        created_at=row[5]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_note(note: FeedbackNote) -> FeedbackNote:
        """Create new feedback note."""
        query = """
            INSERT INTO support_systems.feedback_notes
            (note_id, feedback_id, author_id, note_text, is_internal, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING note_id, feedback_id, author_id, note_text, is_internal, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    note.note_id,
                    note.feedback_id,
                    note.author_id,
                    note.note_text,
                    note.is_internal,
                    note.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return FeedbackNote(
                    note_id=row[0],
                    feedback_id=row[1],
                    author_id=row[2],
                    note_text=row[3],
                    is_internal=row[4] if row[4] is not None else True,
                    created_at=row[5]
                )
