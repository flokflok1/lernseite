"""
LM Slot Repository Package

Complete repository for the Learning Method Capability Slots system:
- Capability slots (chat, vision, stt, etc.)
- LM → Slot requirements (which slots each LM needs)
- Model assignments (which model serves which slot)
- Slot model resolution (hierarchical chapter/course/system)

Modules:
- slots: CapabilitySlotRepository (CRUD for slot definitions)
- requirements: LMSlotRequirementRepository (LM-slot mapping)
- assignments: LMSlotAssignmentRepository (Model assignments, bulk ops)
- resolver: LMSlotResolverRepository (Model resolution, validation)

Author: LernsystemX Team
Date: 2025-12-29
"""

from app.repositories.lm_slot.slots import CapabilitySlotRepository
from app.repositories.lm_slot.requirements import LMSlotRequirementRepository
from app.repositories.lm_slot.assignments import LMSlotAssignmentRepository
from app.repositories.lm_slot.resolver import LMSlotResolverRepository



class LMSlotRepository(
    CapabilitySlotRepository,
    LMSlotResolverRepository
):
    """
    Unified LMSlotRepository combining all functionality
    This class uses multiple inheritance to aggregate methods from specialized modules.
    """
    pass


__all__ = [
    'CapabilitySlotRepository',
    'LMSlotRequirementRepository',
    'LMSlotAssignmentRepository',
    'LMSlotResolverRepository',
]
