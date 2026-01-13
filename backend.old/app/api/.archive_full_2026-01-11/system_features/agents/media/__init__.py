"""
LernsystemX Agents Media Package

Media cache statistics and serving.

Endpoints:
- GET /api/v1/agents/:course_id/media/stats - Get media cache statistics
- GET /api/v1/media/tts/:media_id - Serve cached TTS audio
"""

from .handling import agents_media_bp, media_bp

__all__ = ['agents_media_bp', 'media_bp']
