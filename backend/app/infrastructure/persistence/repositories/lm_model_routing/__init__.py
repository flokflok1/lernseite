"""
Learning Method Model Routing Package

Repository modules for managing Learning Method to AI Model assignments.
Implements hierarchical model resolution (System -> Course -> Chapter).

Modules:
  - assignments: Assignment retrieval and creation (system, course, chapter scopes)
  - resolver: Model resolution logic with hierarchical fallback
  - requirements: LM requirements and validation
  - bulk_operations: Bulk assignment operations

Phase KI-Architektur - Model Routing System
"""

from app.infrastructure.persistence.repositories.lm_model_routing.assignments import LMModelAssignmentRepository
from app.infrastructure.persistence.repositories.lm_model_routing.requirements import LMModelRequirementsRepository

__all__ = [
    'LMModelAssignmentRepository',
    'LMModelRequirementsRepository',
]
