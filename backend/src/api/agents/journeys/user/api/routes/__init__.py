"""
Agents Domain - User Journey Routes

User-facing agent interaction endpoints.
"""

from .interaction import (
    agents_interaction_bp,
    agents_config_bp,
)
from .knowledge import (
    agents_knowledge_bp,
    agents_cache_bp,
)
from .audio import (
    agents_audio_bp,
    agents_voice_bp,
)
from .media import (
    agents_media_bp,
)

__all__ = [
    'agents_interaction_bp',
    'agents_config_bp',
    'agents_knowledge_bp',
    'agents_cache_bp',
    'agents_audio_bp',
    'agents_voice_bp',
    'agents_media_bp',
]
