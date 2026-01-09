"""
Events Core Module

Domain-driven event system for component decoupling.

Features:
- Publish-subscribe pattern
- Event handlers registration
- Event history tracking
- Domain events (User, Course, Learning, Marketplace, System)

Usage:
    from src.core.events import EventBus, EventType, DomainEvent

    # Subscribe to event
    def handle_user_created(event: DomainEvent):
        print(f"User {event.aggregate_id} created")

    EventBus.subscribe(EventType.USER_CREATED, handle_user_created)

    # Publish event
    event = DomainEvent(
        event_type=EventType.USER_CREATED,
        aggregate_id='user-123',
        occurred_at=datetime.utcnow(),
        data={'email': 'user@example.com'}
    )
    EventBus.publish(event)
"""

from src.core.events.event_bus import EventBus, EventType, DomainEvent

__all__ = [
    'EventBus',
    'EventType',
    'DomainEvent',
]
