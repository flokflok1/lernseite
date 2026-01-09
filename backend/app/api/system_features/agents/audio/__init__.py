"""
LernsystemX Agents Audio Package

Audio and TTS endpoints for voice interaction.

Endpoints:
- POST /api/v1/agents/:course_id/ask/audio - Ask with TTS audio response
- POST /api/v1/agents/:course_id/ask/voice - Ask via voice input
"""

from .processing import agents_audio_bp

__all__ = ['agents_audio_bp']
