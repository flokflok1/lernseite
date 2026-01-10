"""
Agents Domain - All Journeys

Exports all Agents domain journey blueprints.
"""

from .admin import agents_management_bp
from .user import (
    agents_interaction_bp,
    agents_config_bp,
    agents_knowledge_bp,
    agents_cache_bp,
    agents_audio_bp,
    agents_voice_bp,
    agents_media_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    # Admin Journey (2 endpoints)
    agents_management_bp,
    # User Journey (12 endpoints)
    agents_interaction_bp,
    agents_config_bp,
    agents_knowledge_bp,
    agents_cache_bp,
    agents_audio_bp,
    agents_voice_bp,
    agents_media_bp,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'agents_management_bp',
    'agents_interaction_bp',
    'agents_config_bp',
    'agents_knowledge_bp',
    'agents_cache_bp',
    'agents_audio_bp',
    'agents_voice_bp',
    'agents_media_bp',
]
