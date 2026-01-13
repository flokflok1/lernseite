"""
Learning Methods Core Domain

Domain-Driven Design (DDD) core components for Learning Methods.

Components:
- Value Objects: MethodGroup, MethodStatus, KiUsage, LearningMethodType, InstancePosition
- Factories: LearningMethodInstanceFactory, RoutingConfigFactory
- Services: MethodValidationService, MethodEnrichmentService
"""

from .value_objects import (
    MethodGroup,
    MethodStatus,
    KiUsage,
    LearningMethodType,
    InstancePosition
)
from .factory import (
    LearningMethodInstanceFactory,
    RoutingConfigFactory
)
from .services import (
    MethodValidationService,
    MethodEnrichmentService
)

__all__ = [
    # Value Objects
    'MethodGroup',
    'MethodStatus',
    'KiUsage',
    'LearningMethodType',
    'InstancePosition',
    # Factories
    'LearningMethodInstanceFactory',
    'RoutingConfigFactory',
    # Services
    'MethodValidationService',
    'MethodEnrichmentService'
]
