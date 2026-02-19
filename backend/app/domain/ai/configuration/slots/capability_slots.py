"""
Capability Slots System for Multi-Model LM Routing

This module defines the capability slots that Learning Methods can use.
Each LM can have multiple models assigned to different slots (chat, tts, stt, vision, etc.)

Example:
    LM24 (Mündliche Erklärung) needs:
    - chat: gpt-4o (text analysis)
    - stt: whisper-1 (speech-to-text)
    - tts: tts-1 (text-to-speech)
    - realtime: gpt-4o-realtime (live dialog) - optional

Author: LernsystemX Team
Date: 2025-12-04
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class CapabilitySlot(str, Enum):
    """
    Available capability slots for Learning Method model routing.

    Each slot represents a specific AI capability that can be assigned
    independently to each Learning Method.
    """

    # Text/Chat capabilities
    CHAT = "chat"           # Standard text generation and chat completions
    REASONING = "reasoning" # Complex reasoning tasks (o1, o3 models)

    # Vision capabilities
    VISION = "vision"       # Image analysis and visual understanding

    # Audio capabilities
    STT = "stt"             # Speech-to-Text (Whisper)
    TTS = "tts"             # Text-to-Speech

    # Real-time capabilities
    REALTIME = "realtime"   # Bidirectional audio streaming (OpenAI Realtime API)

    # Code capabilities
    CODE_EXEC = "code_exec" # Code interpreter and execution sandbox

    # Image generation
    IMAGE_GEN = "image_gen" # Image creation (DALL-E)

    # Utility capabilities
    EMBEDDING = "embedding"   # Text embeddings for semantic search
    MODERATION = "moderation" # Content safety and moderation


@dataclass
class SlotDefinition:
    """
    Definition of a capability slot with metadata.

    Attributes:
        code: Unique slot code (matches CapabilitySlot enum)
        display_name: Human-readable name for UI
        description: Description of what this slot is for
        required_category: Primary ai_models.category this slot accepts
        accepted_categories: Additional categories that can be assigned
        icon: Icon name for UI
        sort_order: Display order in UI
    """
    code: str
    display_name: str
    description: str
    required_category: str
    accepted_categories: List[str]
    icon: str
    sort_order: int


# Slot definitions with full metadata
SLOT_DEFINITIONS: dict[CapabilitySlot, SlotDefinition] = {
    CapabilitySlot.CHAT: SlotDefinition(
        code="chat",
        display_name="Chat/Text",
        description="Standard text generation and chat completions",
        required_category="chat",
        accepted_categories=["reasoning", "multimodal"],
        icon="message-square",
        sort_order=10
    ),
    CapabilitySlot.REASONING: SlotDefinition(
        code="reasoning",
        display_name="Reasoning",
        description="Complex reasoning and analysis tasks (o1, o3)",
        required_category="reasoning",
        accepted_categories=["chat"],
        icon="brain",
        sort_order=20
    ),
    CapabilitySlot.VISION: SlotDefinition(
        code="vision",
        display_name="Vision",
        description="Image analysis and visual understanding",
        required_category="chat",  # Vision uses chat models with vision capability
        accepted_categories=["multimodal"],
        icon="eye",
        sort_order=30
    ),
    CapabilitySlot.STT: SlotDefinition(
        code="stt",
        display_name="Speech-to-Text",
        description="Audio transcription (Whisper)",
        required_category="audio",
        accepted_categories=[],
        icon="mic",
        sort_order=40
    ),
    CapabilitySlot.TTS: SlotDefinition(
        code="tts",
        display_name="Text-to-Speech",
        description="Voice synthesis (TTS)",
        required_category="audio",
        accepted_categories=[],
        icon="volume-2",
        sort_order=50
    ),
    CapabilitySlot.REALTIME: SlotDefinition(
        code="realtime",
        display_name="Realtime",
        description="Bidirectional audio streaming for live conversations",
        required_category="realtime",
        accepted_categories=[],
        icon="radio",
        sort_order=60
    ),
    CapabilitySlot.CODE_EXEC: SlotDefinition(
        code="code_exec",
        display_name="Code Execution",
        description="Code interpreter and execution sandbox",
        required_category="chat",  # Uses chat models for code generation
        accepted_categories=["reasoning"],
        icon="terminal",
        sort_order=70
    ),
    CapabilitySlot.IMAGE_GEN: SlotDefinition(
        code="image_gen",
        display_name="Image Generation",
        description="Image creation (DALL-E)",
        required_category="image",
        accepted_categories=[],
        icon="image",
        sort_order=80
    ),
    CapabilitySlot.EMBEDDING: SlotDefinition(
        code="embedding",
        display_name="Embedding",
        description="Text embeddings for semantic search",
        required_category="embedding",
        accepted_categories=[],
        icon="layers",
        sort_order=90
    ),
    CapabilitySlot.MODERATION: SlotDefinition(
        code="moderation",
        display_name="Moderation",
        description="Content safety and moderation",
        required_category="moderation",
        accepted_categories=[],
        icon="shield",
        sort_order=100
    ),
}


def get_slot_definition(slot: CapabilitySlot) -> SlotDefinition:
    """Get the definition for a capability slot."""
    return SLOT_DEFINITIONS[slot]


def get_all_slot_definitions() -> List[SlotDefinition]:
    """Get all slot definitions sorted by sort_order."""
    return sorted(SLOT_DEFINITIONS.values(), key=lambda s: s.sort_order)


def get_slot_by_code(code: str) -> Optional[CapabilitySlot]:
    """Get a CapabilitySlot enum by its code string."""
    try:
        return CapabilitySlot(code)
    except ValueError:
        return None


def is_model_compatible_with_slot(model_category: str, slot: CapabilitySlot) -> bool:
    """
    Check if a model category is compatible with a slot.

    Args:
        model_category: The ai_models.category value
        slot: The capability slot to check

    Returns:
        True if the model can be assigned to this slot
    """
    definition = SLOT_DEFINITIONS[slot]
    return (
        model_category == definition.required_category or
        model_category in definition.accepted_categories
    )


# Model category constants (for reference)
class ModelCategory(str, Enum):
    """AI model categories from ai_models.category"""
    CHAT = "chat"
    REASONING = "reasoning"
    REALTIME = "realtime"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    EMBEDDING = "embedding"
    MODERATION = "moderation"
    MULTIMODAL = "multimodal"


# Slot to model name hints (default models for each slot)
SLOT_DEFAULT_MODELS: dict[CapabilitySlot, List[str]] = {
    CapabilitySlot.CHAT: ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022"],
    CapabilitySlot.REASONING: ["o1", "o1-mini", "o1-preview"],
    CapabilitySlot.VISION: ["gpt-4o", "gpt-4-turbo"],  # Models with vision capability
    CapabilitySlot.STT: ["whisper-1"],
    CapabilitySlot.TTS: ["tts-1", "tts-1-hd"],
    CapabilitySlot.REALTIME: ["gpt-4o-realtime-preview"],
    CapabilitySlot.CODE_EXEC: ["gpt-4o"],  # Any chat model can do code gen
    CapabilitySlot.IMAGE_GEN: ["dall-e-3", "dall-e-2"],
    CapabilitySlot.EMBEDDING: ["text-embedding-3-large", "text-embedding-3-small"],
    CapabilitySlot.MODERATION: ["omni-moderation-latest"],
}
