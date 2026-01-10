"""
Tutor Domain Events (DDD)

Domain events for the tutor system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class EventPriority(Enum):
    """Event priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class TutorSessionStartedEvent:
    """Published when a tutor chat session starts."""
    event_id: str
    occurred_at: datetime
    aggregate_id: str           # session_id
    user_id: str
    has_context: bool
    tokens_used: int = 0
    priority: EventPriority = EventPriority.LOW


@dataclass
class ChapterTheoryGeneratedEvent:
    """Published when chapter theory is generated."""
    event_id: str
    occurred_at: datetime
    aggregate_id: str           # chapter_id
    chapter_id: str
    style: str
    tokens_used: int
    has_tts: bool
    user_id: str
    priority: EventPriority = EventPriority.MEDIUM


@dataclass
class LessonExplanationGeneratedEvent:
    """Published when lesson explanation is generated."""
    event_id: str
    occurred_at: datetime
    aggregate_id: str           # lesson_id as string
    lesson_id: int
    explanation_type: str       # 'steps' or 'detailed'
    style: str
    tokens_used: int
    has_tts: bool
    user_id: str
    priority: EventPriority = EventPriority.MEDIUM


class EventPublisher:
    """Simple event publisher (logs events for now)."""

    @staticmethod
    def publish(event) -> None:
        """Publish domain event (currently just logs)."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Domain Event: {event.__class__.__name__} - {event.aggregate_id}")
