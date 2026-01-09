"""
Feedback Summary Batch Entity (DDD Domain Entity)

Represents periodic AI summaries of feedback batches.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class FeedbackSummaryBatch:
    """
    Feedback Summary Batch domain entity.

    Periodic AI-generated summaries of feedback batches for management overview.

    Attributes:
        batch_id: UUID
        period_start: Start of summary period
        period_end: End of summary period
        total_feedbacks: Total number of feedbacks in batch
        questions_count: Number of questions
        bugs_count: Number of bug reports
        suggestions_count: Number of suggestions
        praise_count: Number of praise feedback
        other_count: Number of other feedback
        ai_executive_summary: AI-generated executive summary
        ai_key_themes: JSONB array of key themes [{theme, count, examples}]
        ai_action_items: JSONB array of action items [{priority, action, related_feedbacks}]
        ai_sentiment_breakdown: JSONB sentiment breakdown {positive: n, neutral: n, negative: n}
        ai_top_courses: JSONB top courses with feedback [{course_id, course_name, feedback_count}]
        processed_at: When AI processing completed
        processing_tokens: AI tokens used for processing
        created_at: Batch creation timestamp
    """

    batch_id: str
    period_start: datetime
    period_end: datetime
    total_feedbacks: int = 0
    questions_count: int = 0
    bugs_count: int = 0
    suggestions_count: int = 0
    praise_count: int = 0
    other_count: int = 0
    ai_executive_summary: Optional[str] = None
    ai_key_themes: Optional[List[Dict[str, Any]]] = None
    ai_action_items: Optional[List[Dict[str, Any]]] = None
    ai_sentiment_breakdown: Optional[Dict[str, int]] = None
    ai_top_courses: Optional[List[Dict[str, Any]]] = None
    processed_at: Optional[datetime] = None
    processing_tokens: int = 0
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate feedback summary batch entity."""
        if not self.batch_id or not self.batch_id.strip():
            raise ValueError("Batch ID cannot be empty")

        if self.period_end <= self.period_start:
            raise ValueError("Period end must be after period start")

        if self.total_feedbacks < 0:
            raise ValueError("Total feedbacks cannot be negative")

        # Validate counts sum
        counts_sum = (self.questions_count + self.bugs_count + self.suggestions_count +
                     self.praise_count + self.other_count)
        if counts_sum != self.total_feedbacks:
            raise ValueError("Type counts must sum to total feedbacks")

    def is_processed(self) -> bool:
        """Check if AI processing has been completed."""
        return self.processed_at is not None

    def get_period_days(self) -> int:
        """Get number of days in summary period."""
        return (self.period_end - self.period_start).days

    def get_feedbacks_per_day(self) -> float:
        """Get average feedbacks per day."""
        days = self.get_period_days()
        if days == 0:
            return float(self.total_feedbacks)
        return self.total_feedbacks / days

    def get_bug_percentage(self) -> float:
        """Get percentage of bug reports."""
        if self.total_feedbacks == 0:
            return 0.0
        return (self.bugs_count / self.total_feedbacks) * 100

    def get_praise_percentage(self) -> float:
        """Get percentage of praise feedback."""
        if self.total_feedbacks == 0:
            return 0.0
        return (self.praise_count / self.total_feedbacks) * 100

    def get_positive_sentiment_percentage(self) -> float:
        """Get percentage of positive sentiment."""
        if not self.ai_sentiment_breakdown or self.total_feedbacks == 0:
            return 0.0

        positive = self.ai_sentiment_breakdown.get('positive', 0)
        return (positive / self.total_feedbacks) * 100

    def get_negative_sentiment_percentage(self) -> float:
        """Get percentage of negative sentiment."""
        if not self.ai_sentiment_breakdown or self.total_feedbacks == 0:
            return 0.0

        negative = self.ai_sentiment_breakdown.get('negative', 0)
        return (negative / self.total_feedbacks) * 100

    def has_action_items(self) -> bool:
        """Check if batch has action items."""
        return self.ai_action_items is not None and len(self.ai_action_items) > 0

    def get_urgent_action_items(self) -> List[Dict[str, Any]]:
        """Get urgent action items."""
        if not self.ai_action_items:
            return []

        return [
            item for item in self.ai_action_items
            if item.get('priority') in ('urgent', 'high')
        ]
