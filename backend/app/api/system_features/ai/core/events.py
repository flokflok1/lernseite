"""
AI Domain - Domain Events (DDD)

Domain events represent significant state changes in the AI domain.
Events are immutable and should be published to interested parties.

Reference: Eric Evans - Domain-Driven Design, Chapter 8
Pattern: Event Sourcing, Domain Events
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class EventPriority(str, Enum):
    """Event priority levels."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.

    All domain events are immutable and contain:
    - event_id: Unique identifier
    - occurred_at: When the event occurred
    - aggregate_id: ID of the aggregate that generated the event
    - priority: Event priority level
    """
    event_id: str
    occurred_at: datetime
    aggregate_id: str
    priority: EventPriority = EventPriority.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_id': self.event_id,
            'event_type': self.__class__.__name__,
            'occurred_at': self.occurred_at.isoformat(),
            'aggregate_id': self.aggregate_id,
            'priority': self.priority.value
        }


@dataclass(frozen=True)
class AIModelSyncedEvent(DomainEvent):
    """
    Event: AI model synchronization completed.

    Published when models are synced from a provider.
    Interested parties: Analytics, Audit, Cache invalidation
    """
    provider_id: str
    provider_name: str
    models_added: int
    models_updated: int
    models_deactivated: int
    sync_duration_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            'provider_id': self.provider_id,
            'provider_name': self.provider_name,
            'models_added': self.models_added,
            'models_updated': self.models_updated,
            'models_deactivated': self.models_deactivated,
            'sync_duration_seconds': self.sync_duration_seconds
        })
        return base


@dataclass(frozen=True)
class AIJobCompletedEvent(DomainEvent):
    """
    Event: AI job completed successfully.

    Published when an AI generation job completes.
    Interested parties: User notifications, Analytics, Billing
    """
    job_id: str
    job_type: str  # course_from_pdf, module_autogen, lesson_autogen
    user_id: str
    tokens_used: int
    duration_seconds: float
    output_size_kb: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            'job_id': self.job_id,
            'job_type': self.job_type,
            'user_id': self.user_id,
            'tokens_used': self.tokens_used,
            'duration_seconds': self.duration_seconds,
            'output_size_kb': self.output_size_kb
        })
        return base


@dataclass(frozen=True)
class AIJobCancelledEvent(DomainEvent):
    """
    Event: AI job was cancelled.

    Published when a user or system cancels a running job.
    Interested parties: User notifications, Analytics, Resource cleanup
    """
    job_id: str
    job_type: str
    user_id: str
    cancelled_by: str  # user_id or 'system'
    reason: Optional[str] = None
    tokens_used_before_cancel: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            'job_id': self.job_id,
            'job_type': self.job_type,
            'user_id': self.user_id,
            'cancelled_by': self.cancelled_by,
            'reason': self.reason,
            'tokens_used_before_cancel': self.tokens_used_before_cancel
        })
        return base


@dataclass(frozen=True)
class AIProviderHealthChangedEvent(DomainEvent):
    """
    Event: Provider health status changed.

    Published when a provider's operational status changes.
    Interested parties: Monitoring, Alerting, Failover logic
    """
    provider_id: str
    provider_name: str
    old_status: str  # healthy, degraded, down
    new_status: str
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            'provider_id': self.provider_id,
            'provider_name': self.provider_name,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'response_time_ms': self.response_time_ms,
            'error_message': self.error_message
        })
        return base

    @property
    def is_critical(self) -> bool:
        """Check if this is a critical health change (going down)."""
        return self.new_status == 'down'


@dataclass(frozen=True)
class AIModelDefaultSetEvent(DomainEvent):
    """
    Event: Default model changed for a category.

    Published when the default model for a category is updated.
    Interested parties: Cache invalidation, Model selection service
    """
    model_id: str
    model_name: str
    category: str  # chat, reasoning, audio, etc.
    previous_default_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            'model_id': self.model_id,
            'model_name': self.model_name,
            'category': self.category,
            'previous_default_id': self.previous_default_id
        })
        return base


@dataclass(frozen=True)
class AIProfileUpdatedEvent(DomainEvent):
    """
    Event: AI profile configuration updated.

    Published when a model profile is created or updated.
    Interested parties: Model selection service, Cache invalidation
    """
    profile_id: str
    profile_name: str
    updated_by: str  # user_id
    slots_changed: Dict[str, Any]  # slot_name -> model_id mappings
    is_default: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            'profile_id': self.profile_id,
            'profile_name': self.profile_name,
            'updated_by': self.updated_by,
            'slots_changed': self.slots_changed,
            'is_default': self.is_default
        })
        return base


class EventPublisher:
    """
    Simple event publisher for domain events.

    In a production system, this would integrate with:
    - Message queue (RabbitMQ, Kafka)
    - Event store
    - WebSocket for real-time updates
    """

    _handlers: Dict[str, list] = {}

    @classmethod
    def subscribe(cls, event_type: type, handler: callable) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The event class to subscribe to
            handler: Callable that accepts the event
        """
        event_name = event_type.__name__
        if event_name not in cls._handlers:
            cls._handlers[event_name] = []
        cls._handlers[event_name].append(handler)

    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        """
        Publish a domain event to all subscribers.

        Args:
            event: The domain event to publish
        """
        event_name = event.__class__.__name__
        handlers = cls._handlers.get(event_name, [])

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # In production: log error, don't fail the entire publish
                print(f"Error in event handler for {event_name}: {e}")

    @classmethod
    def clear_handlers(cls) -> None:
        """Clear all event handlers (useful for testing)."""
        cls._handlers.clear()
