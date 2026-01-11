"""
LernsystemX KI - Slot Requirements Package

Defines capability slot requirements for all Learning Methods.

Exports:
- SlotRequirement: Individual slot requirement
- LMSlotConfig: Complete LM configuration
- ALL_LM_CONFIGS: Registry of all LM configurations
- GROUP_NAMES: Mapping of group codes to names
- Utility functions for slot queries
"""

from .requirements import (
    SlotRequirement,
    LMSlotConfig,
    ALL_LM_CONFIGS,
    GROUP_NAMES
)
from .validation import (
    get_lm_config,
    get_lm_required_slots,
    get_lm_all_slots
)
from .mapping import (
    get_lms_by_slot,
    get_lms_requiring_slot,
    get_lms_by_group,
    get_all_active_lm_ids
)
from .capabilities import (
    get_slot_usage_summary,
    LMS_NEEDING_REALTIME,
    LMS_NEEDING_VISION,
    LMS_NEEDING_STT,
    LMS_NEEDING_TTS,
    LMS_NEEDING_CODE_EXEC,
    LMS_NEEDING_REASONING
)

__all__ = [
    # Core classes
    'SlotRequirement',
    'LMSlotConfig',
    'ALL_LM_CONFIGS',
    'GROUP_NAMES',
    # Validation
    'get_lm_config',
    'get_lm_required_slots',
    'get_lm_all_slots',
    # Mapping
    'get_lms_by_slot',
    'get_lms_requiring_slot',
    'get_lms_by_group',
    'get_all_active_lm_ids',
    # Capabilities
    'get_slot_usage_summary',
    'LMS_NEEDING_REALTIME',
    'LMS_NEEDING_VISION',
    'LMS_NEEDING_STT',
    'LMS_NEEDING_TTS',
    'LMS_NEEDING_CODE_EXEC',
    'LMS_NEEDING_REASONING'
]
