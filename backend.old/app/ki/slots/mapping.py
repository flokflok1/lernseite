"""
LM Slot Requirements - Mapping Functions

Functions for mapping between slots and LMs.
"""

from typing import List
from app.ki.capability_slots import CapabilitySlot
from .requirements import LMSlotConfig, ALL_LM_CONFIGS


def get_lms_by_slot(slot: CapabilitySlot) -> List[int]:
    """Get all LM IDs that use a specific slot."""
    result = []
    for lm_id, config in ALL_LM_CONFIGS.items():
        for req in config.slots:
            if req.slot == slot:
                result.append(lm_id)
                break
    return result


def get_lms_requiring_slot(slot: CapabilitySlot) -> List[int]:
    """Get all LM IDs that REQUIRE a specific slot (not optional)."""
    result = []
    for lm_id, config in ALL_LM_CONFIGS.items():
        for req in config.slots:
            if req.slot == slot and req.is_required:
                result.append(lm_id)
                break
    return result


def get_lms_by_group(group: str) -> List[LMSlotConfig]:
    """Get all LMs in a specific group."""
    return [config for config in ALL_LM_CONFIGS.values() if config.group == group]


def get_all_active_lm_ids() -> List[int]:
    """Get list of all active LM IDs."""
    return list(ALL_LM_CONFIGS.keys())
