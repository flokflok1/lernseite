"""
AI Domain - Domain Layer

Exports all domain layer components.
"""

from .value_objects import (
    ModelCategoryEnum,
    ModelCategory,
    CapabilitySlot,
    Margin,
    PricingTier,
    ProviderHealthStatus,
    ProviderHealth,
)

from .events import (
    EventPriority,
    DomainEvent,
    AIModelSyncedEvent,
    AIJobCompletedEvent,
    AIJobCancelledEvent,
    AIProviderHealthChangedEvent,
    AIModelDefaultSetEvent,
    AIProfileUpdatedEvent,
    EventPublisher,
)

from .factories import (
    AIModelFactory,
    AIJobFactory,
    AIProviderFactory,
    AIProfileFactory,
)

__all__ = [
    # Value Objects
    'ModelCategoryEnum',
    'ModelCategory',
    'CapabilitySlot',
    'Margin',
    'PricingTier',
    'ProviderHealthStatus',
    'ProviderHealth',
    # Events
    'EventPriority',
    'DomainEvent',
    'AIModelSyncedEvent',
    'AIJobCompletedEvent',
    'AIJobCancelledEvent',
    'AIProviderHealthChangedEvent',
    'AIModelDefaultSetEvent',
    'AIProfileUpdatedEvent',
    'EventPublisher',
    # Factories
    'AIModelFactory',
    'AIJobFactory',
    'AIProviderFactory',
    'AIProfileFactory',
]
