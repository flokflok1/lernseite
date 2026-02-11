"""
TTS API Package

Text-to-Speech synthesis, audio management, and pronunciation rules.

Structure:
- user/ - User TTS endpoints (synthesis, audio, pronunciations, core helpers)

Consolidated from: tts/ root files (Batch 5, Phase 7)

Endpoints (User - @token_required):
- POST /tts/speak - Generate TTS audio with caching
- GET /tts/audio/:audio_id - Get cached TTS audio
- POST /tts/speak-stream - Stream TTS audio (no caching)
- GET /tts/voices - List available voices/models
- POST /tts/tutor-script - Generate complete tutor script
- GET/POST /tts/pronunciations - Manage pronunciation rules

All endpoints require authentication (@token_required)
ISO 27001:2013 compliant - TTS security and caching
"""

from app.api.v1.tts.user.pronunciations import pronunciations_bp
from app.api.v1.tts.user.synthesis import synthesis_bp
from app.api.v1.tts.user.audio import audio_bp

__all__ = ['pronunciations_bp', 'synthesis_bp', 'audio_bp']
