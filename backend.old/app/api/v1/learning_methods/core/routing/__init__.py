"""
Learning Methods Core Routing Domain Logic

Routing domain logic and services.

Files:
- events.py: Routing events (157 LOC)
- factory.py: Routing factory (206 LOC)
- services.py: Routing services (287 LOC)
- value_objects.py: Routing value objects (238 LOC)

Total: ~888 LOC

This is a TRUE FEATURE SUBDIRECTORY (subdomain) - kept separate.
"""

# Import modules
from app.api.v1.learning_methods.core.routing import (
    events,
    factory,
    services,
    value_objects
)

# Import commonly used classes for easier access (barrel export pattern)
from app.api.v1.learning_methods.core.routing.value_objects import (
    LMIDRange,
    CostLevel,
    CostPreset,
    AssignmentScope,
    ModelRequirement,
    SlotCode,
    RoutingStats
)

from app.api.v1.learning_methods.core.routing.factory import (
    ModelAssignmentFactory,
    SlotAssignmentFactory,
    ModelRequirementFactory
)

from app.api.v1.learning_methods.core.routing.services import (
    RoutingResolutionService,
    RoutingRecommendationService,
    RoutingStatsService
)

from app.api.v1.learning_methods.core.routing.events import (
    ModelAssignedEvent,
    ModelUnassignedEvent,
    SlotPresetAppliedEvent
)

__all__ = [
    # Modules
    'events',
    'factory',
    'services',
    'value_objects',
    # Value Objects
    'LMIDRange',
    'CostLevel',
    'CostPreset',
    'AssignmentScope',
    'ModelRequirement',
    'SlotCode',
    'RoutingStats',
    # Factories
    'ModelAssignmentFactory',
    'SlotAssignmentFactory',
    'ModelRequirementFactory',
    # Services
    'RoutingResolutionService',
    'RoutingRecommendationService',
    'RoutingStatsService',
    # Events
    'ModelAssignedEvent',
    'ModelUnassignedEvent',
    'SlotPresetAppliedEvent',
]
