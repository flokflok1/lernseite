"""
Routing Core Domain

Model assignment and routing logic for learning methods.

Value Objects:
- LMIDRange: Valid learning method ID constraints (0-11)
- ModelRequirement: Requirements for AI models
- SlotCode: Capability slot identifiers
- CostPreset: Cost preset configurations
- CostLevel: Model cost levels
- AssignmentScope: Assignment scope levels

Factories:
- ModelAssignmentFactory: Create model assignments
- SlotAssignmentFactory: Create slot assignments

Services:
- RoutingResolutionService: Resolve models for LMs
- RoutingRecommendationService: Recommend models
- RoutingStatsService: Calculate routing statistics

Events:
- ModelAssignedEvent
- ModelUnassignedEvent
- SlotPresetAppliedEvent
"""

from .value_objects import (
    LMIDRange,
    ModelRequirement,
    SlotCode,
    CostPreset,
    CostLevel,
    AssignmentScope,
    RoutingStats
)

from .factory import (
    ModelAssignmentFactory,
    SlotAssignmentFactory
)

from .services import (
    RoutingResolutionService,
    RoutingRecommendationService,
    RoutingStatsService
)

from .events import (
    ModelAssignedEvent,
    ModelUnassignedEvent,
    SlotPresetAppliedEvent
)

__all__ = [
    # Value Objects
    'LMIDRange',
    'ModelRequirement',
    'SlotCode',
    'CostPreset',
    'CostLevel',
    'AssignmentScope',
    'RoutingStats',
    # Factories
    'ModelAssignmentFactory',
    'SlotAssignmentFactory',
    # Services
    'RoutingResolutionService',
    'RoutingRecommendationService',
    'RoutingStatsService',
    # Events
    'ModelAssignedEvent',
    'ModelUnassignedEvent',
    'SlotPresetAppliedEvent'
]
