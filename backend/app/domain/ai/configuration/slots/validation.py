"""
LM Slot Requirements - Validation Functions

Functions for validating and retrieving LM configurations.
"""

from typing import List, Optional
from app.domain.ai.configuration.slots.capability_slots import CapabilitySlot
from .requirements import LMSlotConfig, ALL_LM_CONFIGS


def get_lm_config(lm_id: int) -> Optional[LMSlotConfig]:
    """Get the slot configuration for a learning method."""
    return ALL_LM_CONFIGS.get(lm_id)


def get_lm_required_slots(lm_id: int) -> List[CapabilitySlot]:
    """Get all required slots for a learning method."""
    config = get_lm_config(lm_id)
    if config:
        return config.required_slots
    return []


def get_lm_all_slots(lm_id: int) -> List[CapabilitySlot]:
    """Get all slots (required + optional) for a learning method."""
    config = get_lm_config(lm_id)
    if config:
        return [r.slot for r in config.slots]
    return []
