"""
AI Domain - Core Layer

Complete DDD implementation with Domain, Application, and Infrastructure layers.
"""

# Domain Layer
from .domain import (
    # Value Objects
    ModelCategoryEnum,
    ModelCategory,
    CapabilitySlot,
    Margin,
    PricingTier,
    ProviderHealthStatus,
    ProviderHealth,
    # Events
    EventPriority,
    DomainEvent,
    AIModelSyncedEvent,
    AIJobCompletedEvent,
    AIJobCancelledEvent,
    AIProviderHealthChangedEvent,
    AIModelDefaultSetEvent,
    AIProfileUpdatedEvent,
    EventPublisher,
    # Factories
    AIModelFactory,
    AIJobFactory,
    AIProviderFactory,
    AIProfileFactory,
)

# Application Layer
from .application import (
    AIModelSelectionService,
    AIUsageService,
    AISyncService,
    AIHealthMonitoringService,
)

__all__ = [
    # Domain - Value Objects
    'ModelCategoryEnum',
    'ModelCategory',
    'CapabilitySlot',
    'Margin',
    'PricingTier',
    'ProviderHealthStatus',
    'ProviderHealth',
    # Domain - Events
    'EventPriority',
    'DomainEvent',
    'AIModelSyncedEvent',
    'AIJobCompletedEvent',
    'AIJobCancelledEvent',
    'AIProviderHealthChangedEvent',
    'AIModelDefaultSetEvent',
    'AIProfileUpdatedEvent',
    'EventPublisher',
    # Domain - Factories
    'AIModelFactory',
    'AIJobFactory',
    'AIProviderFactory',
    'AIProfileFactory',
    # Application - Services
    'AIModelSelectionService',
    'AIUsageService',
    'AISyncService',
    'AIHealthMonitoringService',
]
