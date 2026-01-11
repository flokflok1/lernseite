"""
Event Bus Module

Domain-driven event system for decoupling components.

Features:
- Publish-subscribe pattern
- Event handlers registration
- Asynchronous event processing
- Event history tracking
"""

from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Domain event types."""
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"

    # Course events
    COURSE_PUBLISHED = "course.published"
    COURSE_UPDATED = "course.updated"
    COURSE_ENROLLED = "course.enrolled"

    # Learning events
    LESSON_COMPLETED = "lesson.completed"
    CHAPTER_COMPLETED = "chapter.completed"
    EXAM_COMPLETED = "exam.completed"

    # Marketplace events
    PURCHASE_COMPLETED = "purchase.completed"
    REFUND_REQUESTED = "refund.requested"

    # System events
    SYSTEM_MAINTENANCE = "system.maintenance"
    SECURITY_ALERT = "security.alert"


@dataclass
class DomainEvent:
    """
    Base domain event.

    All domain events must inherit from this class.
    """

    event_type: EventType
    aggregate_id: str  # ID of the aggregate that produced the event
    occurred_at: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None  # For tracing related events

    def __post_init__(self):
        """Set occurred_at if not provided."""
        if not self.occurred_at:
            self.occurred_at = datetime.utcnow()


class EventBus:
    """
    In-memory event bus implementation.

    Provides publish-subscribe pattern for domain events.
    For production, consider using external message broker (RabbitMQ, Kafka).
    """

    _handlers: Dict[EventType, List[Callable]] = {}
    _event_history: List[DomainEvent] = []

    @classmethod
    def subscribe(cls, event_type: EventType, handler: Callable) -> None:
        """
        Subscribe handler to event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Callable that accepts DomainEvent
        """
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []

        if handler not in cls._handlers[event_type]:
            cls._handlers[event_type].append(handler)
            logger.info(f"Registered handler {handler.__name__} for {event_type.value}")

    @classmethod
    def unsubscribe(cls, event_type: EventType, handler: Callable) -> None:
        """
        Unsubscribe handler from event type.

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in cls._handlers:
            if handler in cls._handlers[event_type]:
                cls._handlers[event_type].remove(handler)
                logger.info(f"Unregistered handler {handler.__name__} from {event_type.value}")

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        """
        Publish event to all subscribers.

        Args:
            event: Domain event to publish
        """
        # Store in history
        cls._event_history.append(event)

        # Get handlers for this event type
        handlers = cls._handlers.get(event.event_type, [])

        if not handlers:
            logger.debug(f"No handlers registered for {event.event_type.value}")
            return

        # Execute all handlers
        for handler in handlers:
            try:
                handler(event)
                logger.debug(f"Handler {handler.__name__} executed for {event.event_type.value}")
            except Exception as e:
                logger.error(
                    f"Error executing handler {handler.__name__} for {event.event_type.value}: {e}",
                    exc_info=True
                )

    @classmethod
    def get_event_history(
        cls,
        event_type: Optional[EventType] = None,
        aggregate_id: Optional[str] = None,
        limit: int = 100
    ) -> List[DomainEvent]:
        """
        Get event history with optional filters.

        Args:
            event_type: Filter by event type
            aggregate_id: Filter by aggregate ID
            limit: Maximum number of events to return

        Returns:
            List of domain events
        """
        events = cls._event_history

        # Filter by event type
        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Filter by aggregate ID
        if aggregate_id:
            events = [e for e in events if e.aggregate_id == aggregate_id]

        # Return most recent events first
        return sorted(events, key=lambda e: e.occurred_at, reverse=True)[:limit]

    @classmethod
    def clear_history(cls) -> None:
        """Clear event history (for testing)."""
        cls._event_history = []

    @classmethod
    def clear_handlers(cls) -> None:
        """Clear all handlers (for testing)."""
        cls._handlers = {}
