"""
Feedback Service - Business logic for user feedback system.

Features:
- Feedback submission with validation
- AI-powered analysis and summarization
- Batch processing for admin reports
- Email notifications (optional)
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from app.infrastructure.persistence.repositories.feedback.core import FeedbackRepository

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for handling user feedback operations."""

    # =========================================================================
    # SUBMIT FEEDBACK
    # =========================================================================

    @staticmethod
    def submit_feedback(
        feedback_type: str,
        message: str,
        title: Optional[str] = None,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        is_anonymous: bool = False,
        context: Optional[Dict] = None
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Submit new user feedback.

        Returns:
            Tuple of (feedback_data, error_message)
        """
        # Validate type
        valid_types = ['question', 'bug', 'suggestion', 'praise', 'other']
        if feedback_type not in valid_types:
            return None, f"Invalid feedback type. Must be one of: {', '.join(valid_types)}"

        # Validate message
        if not message or len(message.strip()) < 10:
            return None, "Message must be at least 10 characters long"

        if len(message) > 10000:
            return None, "Message is too long (max 10,000 characters)"

        # Extract context
        ctx = context or {}
        course_id = ctx.get('course_id')
        lesson_id = ctx.get('lesson_id')
        page_context = ctx.get('page_context')
        url = ctx.get('url')
        user_agent = ctx.get('user_agent')

        # If anonymous, clear user info
        if is_anonymous:
            user_id = None
            email = None

        try:
            feedback = FeedbackRepository.create_feedback(
                feedback_type=feedback_type,
                message=message.strip(),
                title=title.strip() if title else None,
                user_id=user_id,
                email=email,
                is_anonymous=is_anonymous,
                context_course_id=course_id,
                context_lesson_id=lesson_id,
                context_page=page_context,
                context_url=url,
                context_user_agent=user_agent,
                context_data=ctx
            )

            if not feedback:
                return None, "Failed to save feedback"

            # Trigger async AI analysis (if configured)
            FeedbackService._schedule_ai_analysis(feedback['feedback_id'])

            logger.info(f"Feedback submitted: {feedback['feedback_id']} ({feedback_type})")
            return feedback, None

        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return None, "An error occurred while saving feedback"

    # =========================================================================
    # AI ANALYSIS
    # =========================================================================

    @staticmethod
    def _schedule_ai_analysis(feedback_id: str) -> None:
        """Schedule async AI analysis for feedback."""
        # TODO: Implement with Celery task
        # For now, we'll do it synchronously in a try/except
        try:
            FeedbackService.analyze_feedback_with_ai(feedback_id)
        except Exception as e:
            logger.warning(f"AI analysis failed for {feedback_id}: {e}")

    @staticmethod
    def analyze_feedback_with_ai(feedback_id: str) -> Optional[Dict]:
        """
        Analyze single feedback with AI.

        Extracts:
        - Summary
        - Category
        - Sentiment
        - Tags/Keywords
        """
        feedback = FeedbackRepository.get_by_id(feedback_id)
        if not feedback:
            return None

        try:
            # Import AI adapter
            from app.application.services.ai_adapter import AIAdapter

            # Build prompt
            prompt = f"""Analysiere das folgende Nutzer-Feedback und extrahiere:
1. Eine kurze Zusammenfassung (1-2 Sätze)
2. Die Hauptkategorie (technisch, inhaltlich, usability, feature-request, lob, sonstiges)
3. Die Stimmung (positive, neutral, negative, mixed)
4. 3-5 relevante Tags/Keywords

Feedback-Typ: {feedback['feedback_type']}
Titel: {feedback.get('title', 'Kein Titel')}
Nachricht: {feedback['message']}

Kontext:
- Kurs: {feedback.get('course_title', 'Keiner')}
- Seite: {feedback.get('context_page', 'Unbekannt')}

Antworte im JSON-Format:
{{
    "summary": "...",
    "category": "...",
    "sentiment": "positive|neutral|negative|mixed",
    "tags": ["tag1", "tag2", ...]
}}"""

            result = AIAdapter.generate_content(
                prompt=prompt,
                provider='anthropic',
                max_tokens=500,
                temperature=0.3
            )

            if result and result.get('content'):
                import json
                # Parse AI response
                content = result['content']

                # Try to extract JSON from response
                try:
                    # Find JSON in response
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start >= 0 and end > start:
                        analysis = json.loads(content[start:end])

                        # Update feedback with analysis
                        FeedbackRepository.update_ai_analysis(
                            feedback_id=feedback_id,
                            summary=analysis.get('summary'),
                            category=analysis.get('category'),
                            sentiment=analysis.get('sentiment'),
                            tags=analysis.get('tags', [])
                        )

                        return analysis
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse AI response for {feedback_id}")

        except Exception as e:
            logger.error(f"AI analysis error for {feedback_id}: {e}")

        return None

    @staticmethod
    def generate_summary_batch(
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Generate AI summary for a batch of feedback.

        Default: Last 7 days
        """
        if not period_end:
            period_end = datetime.utcnow()
        if not period_start:
            period_start = period_end - timedelta(days=7)

        # Get feedback in period
        feedbacks = FeedbackRepository.get_for_summary_batch(period_start, period_end)

        if not feedbacks:
            return None

        # Calculate stats
        stats = {
            'total': len(feedbacks),
            'questions': sum(1 for f in feedbacks if f['feedback_type'] == 'question'),
            'bugs': sum(1 for f in feedbacks if f['feedback_type'] == 'bug'),
            'suggestions': sum(1 for f in feedbacks if f['feedback_type'] == 'suggestion'),
            'praise': sum(1 for f in feedbacks if f['feedback_type'] == 'praise'),
            'other': sum(1 for f in feedbacks if f['feedback_type'] == 'other')
        }

        # Generate AI summary
        ai_summary = FeedbackService._generate_batch_summary(feedbacks, period_start, period_end)

        # Create batch record
        batch = FeedbackRepository.create_summary_batch(
            period_start=period_start,
            period_end=period_end,
            stats=stats,
            ai_summary=ai_summary
        )

        return batch

    @staticmethod
    def _generate_batch_summary(
        feedbacks: List[Dict],
        period_start: datetime,
        period_end: datetime
    ) -> Optional[Dict]:
        """Generate AI summary for a batch of feedbacks."""
        if not feedbacks:
            return None

        try:
            from app.application.services.ai_adapter import AIAdapter

            # Build feedback list for prompt
            feedback_texts = []
            for i, f in enumerate(feedbacks[:50], 1):  # Limit to 50 for token efficiency
                feedback_texts.append(
                    f"{i}. [{f['feedback_type'].upper()}] {f.get('title', 'Kein Titel')}: {f['message'][:200]}..."
                )

            prompt = f"""Du bist ein Analyst für Nutzer-Feedback eines Lernsystems.

Analysiere die folgenden {len(feedbacks)} Feedbacks vom Zeitraum {period_start.strftime('%d.%m.%Y')} bis {period_end.strftime('%d.%m.%Y')}:

{chr(10).join(feedback_texts)}

Erstelle eine Executive Summary mit:
1. Zusammenfassung der wichtigsten Punkte (3-5 Sätze)
2. Die 5 wichtigsten Themen/Trends mit Häufigkeit
3. Konkrete Handlungsempfehlungen (priorisiert)
4. Sentiment-Verteilung (positiv/neutral/negativ in %)

Antworte im JSON-Format:
{{
    "executive_summary": "...",
    "key_themes": [
        {{"theme": "...", "count": N, "examples": ["...", "..."]}},
        ...
    ],
    "action_items": [
        {{"priority": "high|medium|low", "action": "...", "related_count": N}},
        ...
    ],
    "sentiment_breakdown": {{
        "positive": N,
        "neutral": N,
        "negative": N
    }}
}}"""

            result = AIAdapter.generate_content(
                prompt=prompt,
                provider='anthropic',
                max_tokens=2000,
                temperature=0.3
            )

            if result and result.get('content'):
                import json
                content = result['content']
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(content[start:end])

        except Exception as e:
            logger.error(f"Batch summary generation error: {e}")

        return None

    # =========================================================================
    # RETRIEVAL
    # =========================================================================

    @staticmethod
    def get_feedback(feedback_id: str) -> Optional[Dict]:
        """Get feedback with all details."""
        feedback = FeedbackRepository.get_by_id(feedback_id)
        if feedback:
            feedback['attachments'] = FeedbackRepository.get_attachments(feedback_id)
            feedback['notes'] = FeedbackRepository.get_notes(feedback_id)
        return feedback

    @staticmethod
    def get_feedback_list(
        feedback_type: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        course_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """Get paginated feedback list."""
        offset = (page - 1) * per_page

        feedbacks = FeedbackRepository.get_all(
            feedback_type=feedback_type,
            status=status,
            priority=priority,
            course_id=course_id,
            search=search,
            limit=per_page,
            offset=offset
        )

        return {
            'feedbacks': feedbacks,
            'page': page,
            'per_page': per_page,
            'has_more': len(feedbacks) == per_page
        }

    @staticmethod
    def get_dashboard_data() -> Dict:
        """Get data for admin feedback dashboard."""
        stats = FeedbackRepository.get_dashboard_stats()
        trending = FeedbackRepository.get_trending_topics()
        by_course = FeedbackRepository.get_by_course_stats()
        new_count = FeedbackRepository.get_new_count()
        recent_batches = FeedbackRepository.get_latest_summary_batches(5)

        return {
            'stats': stats or {},
            'trending_topics': trending,
            'by_course': by_course,
            'new_count': new_count,
            'recent_summaries': recent_batches
        }

    # =========================================================================
    # ADMIN ACTIONS
    # =========================================================================

    @staticmethod
    def update_status(
        feedback_id: str,
        status: str,
        admin_id: Optional[str] = None
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Update feedback status."""
        valid_statuses = ['new', 'read', 'in_progress', 'resolved', 'closed']
        if status not in valid_statuses:
            return None, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

        feedback = FeedbackRepository.update_status(feedback_id, status, admin_id)
        if not feedback:
            return None, "Feedback not found"

        return feedback, None

    @staticmethod
    def update_priority(
        feedback_id: str,
        priority: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Update feedback priority."""
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if priority not in valid_priorities:
            return None, f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"

        feedback = FeedbackRepository.update_priority(feedback_id, priority)
        if not feedback:
            return None, "Feedback not found"

        return feedback, None

    @staticmethod
    def respond_to_feedback(
        feedback_id: str,
        response: str,
        admin_id: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Add admin response to feedback."""
        if not response or len(response.strip()) < 5:
            return None, "Response must be at least 5 characters"

        feedback = FeedbackRepository.add_admin_response(
            feedback_id=feedback_id,
            response=response.strip(),
            admin_id=admin_id
        )

        if not feedback:
            return None, "Feedback not found"

        # TODO: Send email notification to user if email provided
        return feedback, None

    @staticmethod
    def add_note(
        feedback_id: str,
        author_id: str,
        note_text: str,
        is_internal: bool = True
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Add internal note to feedback."""
        if not note_text or len(note_text.strip()) < 3:
            return None, "Note must be at least 3 characters"

        note = FeedbackRepository.create_note(
            feedback_id=feedback_id,
            author_id=author_id,
            note_text=note_text.strip(),
            is_internal=is_internal
        )

        if not note:
            return None, "Failed to add note"

        return note, None
