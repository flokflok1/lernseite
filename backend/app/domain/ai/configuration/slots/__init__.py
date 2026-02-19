"""
LernsystemX KI - Slot Configuration Package

Defines capability slot definitions and system feature mappings.

NOTE: mapping.py and validation.py reference removed LMSlotConfig/ALL_LM_CONFIGS
(deleted in hardcoding-removal commit). They are not imported to avoid errors.
"""

from .capability_slots import CapabilitySlot, get_slot_definition
from .capabilities import (
    LMS_NEEDING_REALTIME,
    LMS_NEEDING_VISION,
    LMS_NEEDING_STT,
    LMS_NEEDING_TTS,
    LMS_NEEDING_CODE_EXEC,
    LMS_NEEDING_REASONING
)

__all__ = [
    'CapabilitySlot',
    'get_slot_definition',
    'LMS_NEEDING_REALTIME',
    'LMS_NEEDING_VISION',
    'LMS_NEEDING_STT',
    'LMS_NEEDING_TTS',
    'LMS_NEEDING_CODE_EXEC',
    'LMS_NEEDING_REASONING'
]
