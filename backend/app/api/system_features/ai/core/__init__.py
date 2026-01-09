"""
AI Domain - Core Layer (DDD)

This module contains the domain core following Domain-Driven Design patterns:
- Value Objects: Immutable business concepts (ModelCategory, Margin, PricingTier)
- Domain Events: State change notifications
- Factories: Complex object creation with business rules
- Services: Multi-entity business logic

Reference: Eric Evans - Domain-Driven Design (2003)
"""

from .value_objects import (
    ModelCategory,
    CapabilitySlot,
    Margin,
    PricingTier,
    ProviderHealth
)
from .events import (
    AIModelSyncedEvent,
    AIJobCompletedEvent,
    AIProviderHealthChangedEvent,
    AIModelDefaultSetEvent,
    AIJobCancelledEvent,
    AIProfileUpdatedEvent
)
from .factory import (
    AIModelFactory,
    AIJobFactory,
    AIProviderFactory,
    AIProfileFactory
)
from .services import (
    AIModelSelectionService,
    AIUsageService,
    AISyncService
)

__all__ = [
    # Value Objects
    'ModelCategory',
    'CapabilitySlot',
    'Margin',
    'PricingTier',
    'ProviderHealth',
    # Events
    'AIModelSyncedEvent',
    'AIJobCompletedEvent',
    'AIProviderHealthChangedEvent',
    'AIModelDefaultSetEvent',
    'AIJobCancelledEvent',
    'AIProfileUpdatedEvent',
    # Factories
    'AIModelFactory',
    'AIJobFactory',
    'AIProviderFactory',
    'AIProfileFactory',
    # Services
    'AIModelSelectionService',
    'AIUsageService',
    'AISyncService'
]
