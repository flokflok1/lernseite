"""
Learning Methods System Feature (DDD)

12 Content-Lernmethoden (LM00-LM11) management with AI model routing.

Package Structure:
- core/ - Core domain (Value Objects, Factories, Services, Events)
  - routing/ - Routing domain (Value Objects, Factories, Services for model assignment)
- admin/ - Admin endpoints
  - instances/ - CRUD for learning method instances (5 endpoints)
  - types/ - Get all method types (1 endpoint)
  - operations/ - Reorder, publish, unpublish (3 endpoints)
  - routing/ - AI model assignment (8 endpoints) ✅ COMPLETE

Blueprints (17 total):
Instances & Types:
- lm_instances_bp: /api/v1/admin/learning-methods/instances
- lm_types_bp: /api/v1/admin/learning-methods/types

Operations:
- lm_operations_bp: /api/v1/admin/learning-methods/operations

Routing (8 blueprints):
- lm_routing_overview_bp: Overview, unconfigured, requirements
- lm_routing_resolution_bp: Model resolution testing
- lm_routing_assignments_bp: CRUD for individual LM assignments
- lm_routing_bulk_bp: Bulk operations
- lm_routing_recommendations_bp: Model recommendations
- lm_routing_auto_setup_bp: Auto-setup with recommendations
- lm_routing_ai_setup_bp: AI-powered auto-setup
- lm_routing_slots_bp: Capability slot management

DDD Components:
Core Domain:
- Value Objects: MethodGroup, MethodStatus, KiUsage, LearningMethodType, InstancePosition
- Factories: LearningMethodInstanceFactory

Routing Domain:
- Value Objects: LMIDRange, ModelRequirement, SlotCode, CostPreset, CostLevel, AssignmentScope, RoutingStats
- Factories: ModelAssignmentFactory, SlotAssignmentFactory
- Services: RoutingResolutionService, RoutingRecommendationService, RoutingStatsService
- Events: ModelAssignedEvent, ModelUnassignedEvent, SlotPresetAppliedEvent

Old Location (to be deleted after migration):
- admin/learning_methods/ (migrated ✅)
- admin/lm_routing/ (migrated ✅)

Migration Status: ✅ COMPLETE
"""

# Admin blueprints - Instances & Types
from .admin import (
    lm_instances_bp,
    lm_types_bp,
    lm_operations_bp
)

# Admin blueprints - Routing (8 blueprints)
from .admin.routing import (
    lm_routing_overview_bp,
    lm_routing_resolution_bp,
    lm_routing_assignments_bp,
    lm_routing_bulk_bp,
    lm_routing_recommendations_bp,
    lm_routing_auto_setup_bp,
    lm_routing_ai_setup_bp,
    lm_routing_slots_bp
)

# Core domain exports (for internal use)
from .core import (
    MethodGroup,
    MethodStatus,
    KiUsage,
    LearningMethodType,
    InstancePosition,
    LearningMethodInstanceFactory,
    RoutingConfigFactory,
    MethodValidationService,
    MethodEnrichmentService
)

# Routing domain exports (for internal use)
from .core.routing import (
    LMIDRange,
    ModelRequirement,
    SlotCode,
    CostPreset,
    CostLevel,
    AssignmentScope,
    RoutingStats,
    ModelAssignmentFactory,
    SlotAssignmentFactory,
    RoutingResolutionService,
    RoutingRecommendationService,
    RoutingStatsService,
    ModelAssignedEvent,
    ModelUnassignedEvent,
    SlotPresetAppliedEvent
)

__all__ = [
    # Admin Blueprints - Instances & Types
    'lm_instances_bp',
    'lm_types_bp',
    'lm_operations_bp',
    # Admin Blueprints - Routing
    'lm_routing_overview_bp',
    'lm_routing_resolution_bp',
    'lm_routing_assignments_bp',
    'lm_routing_bulk_bp',
    'lm_routing_recommendations_bp',
    'lm_routing_auto_setup_bp',
    'lm_routing_ai_setup_bp',
    'lm_routing_slots_bp',
    # Core Domain
    'MethodGroup',
    'MethodStatus',
    'KiUsage',
    'LearningMethodType',
    'InstancePosition',
    'LearningMethodInstanceFactory',
    'RoutingConfigFactory',
    'MethodValidationService',
    'MethodEnrichmentService',
    # Routing Domain
    'LMIDRange',
    'ModelRequirement',
    'SlotCode',
    'CostPreset',
    'CostLevel',
    'AssignmentScope',
    'RoutingStats',
    'ModelAssignmentFactory',
    'SlotAssignmentFactory',
    'RoutingResolutionService',
    'RoutingRecommendationService',
    'RoutingStatsService',
    'ModelAssignedEvent',
    'ModelUnassignedEvent',
    'SlotPresetAppliedEvent'
]
