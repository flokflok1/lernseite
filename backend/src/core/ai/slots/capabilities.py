"""
LM Slot Requirements - Capability Analysis

Functions for analyzing slot usage and capability requirements.
"""

from typing import Dict, List
from src.ki.capability_slots import CapabilitySlot
from .mapping import get_lms_by_slot, get_lms_requiring_slot


def get_slot_usage_summary() -> Dict[CapabilitySlot, Dict[str, int]]:
    """
    Get usage statistics for each slot across all LMs.

    Returns dict like:
    {
        CapabilitySlot.CHAT: {'required': 28, 'optional': 3, 'total': 31},
        CapabilitySlot.STT: {'required': 1, 'optional': 0, 'total': 1},
        ...
    }
    """
    summary = {}
    for slot in CapabilitySlot:
        required = len(get_lms_requiring_slot(slot))
        total = len(get_lms_by_slot(slot))
        summary[slot] = {
            'required': required,
            'optional': total - required,
            'total': total
        }
    return summary


# Quick reference for LMs needing specific capabilities
LMS_NEEDING_REALTIME: List[int] = [4, 24]  # Sokratisch, Muendlich
LMS_NEEDING_VISION: List[int] = [8, 10, 12, 16]  # Whiteboard, Network, Mathe, Fehleranalyse
LMS_NEEDING_STT: List[int] = [24]  # Muendlich
LMS_NEEDING_TTS: List[int] = [0, 24]  # Deep Explanation, Muendlich
LMS_NEEDING_CODE_EXEC: List[int] = [9, 11, 16, 17, 20, 31]  # Sandbox, IT, Fehler, Lab, MultiStep, Projekt
LMS_NEEDING_REASONING: List[int] = [4, 18, 27]  # Sokratisch, Freitext, Team-Case
