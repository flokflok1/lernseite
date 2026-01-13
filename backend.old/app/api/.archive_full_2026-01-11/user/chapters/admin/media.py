"""
LernsystemX Chapter Theory Audio (Admin)

TTS audio generation and serving for chapter theory content.

Endpoints:
- GET /api/v1/chapter-theory/:chapter_id/audio - Serve cached TTS audio

Functions:
- generate_theory_audio: Generate TTS audio for theory content

DDD Refactored: 2026-01-08 - Moved from media/audio.py
Admin context (audio generation is triggered by admin generation)
"""

from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
import hashlib
import logging
import os
import re
from typing import Optional

from app.middleware.auth import token_required

from ..core.repository import get_chapter_theory

logger = logging.getLogger(__name__)

# Blueprint for audio endpoints
chapter_theory_audio_bp = Blueprint(
    'chapter_theory_audio',
    __name__,
    url_prefix=''
)


@chapter_theory_audio_bp.route('/chapter-theory/<chapter_id>/audio', methods=['GET'])
@token_required
def get_theory_audio(chapter_id: str):
    """
    Serve cached TTS audio for chapter theory.

    Query params:
        v: voice (nova, alloy, echo, etc.)
        style: theory style (adhs, detailed, etc.)

    Returns:
        Audio file (audio/mpeg)
    """
    try:
        voice = request.args.get('v', 'nova')
        style = request.args.get('style', 'adhs')

        # Get theory record to find audio file
        theory_record = get_chapter_theory(chapter_id, style)

        if not theory_record:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

        audio_url = theory_record.get('audio_url')

        # If no audio URL, return error
        if not audio_url:
            return jsonify({
                'success': False,
                'error': 'No audio available for this theory'
            }), 404

        # Find audio file in storage
        backend_root = Path(__file__).parent.parent.parent.parent.parent
        cache_base = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache')))
        storage_dir = cache_base / 'chapter_theory_tts' / chapter_id[:8]

        # Look for any audio file matching voice
        audio_file = None
        if storage_dir.exists():
            for f in storage_dir.glob(f'theory_*_{voice}.mp3'):
                audio_file = f
                break

        if not audio_file or not audio_file.exists():
            return jsonify({
                'success': False,
                'error': 'Audio file not found'
            }), 404

        return send_file(
            str(audio_file),
            mimetype='audio/mpeg',
            as_attachment=False
        )

    except Exception as e:
        logger.error(f"Error serving theory audio: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to serve audio'
        }), 500


def generate_theory_audio(
    theory_data: dict,
    voice: str,
    chapter_id: str,
    user_id: str
) -> Optional[dict]:
    """Generate TTS audio for theory content using OpenAI TTS.

    Args:
        theory_data: Theory content dict
        voice: TTS voice (nova, alloy, echo, etc.)
        chapter_id: UUID of the chapter
        user_id: UUID of the requesting user

    Returns:
        Dict with url, duration_seconds, etc. or None on error
    """
    try:
        # Build speech text from theory data - comprehensive explanation
        speech_parts = []

        # Title and intro
        speech_parts.append("Willkommen zu diesem Theorieblatt.")

        if theory_data.get('overview'):
            overview = re.sub('<[^<]+?>', '', str(theory_data['overview']))
            speech_parts.append(f"Ueberblick. {overview}")

        if theory_data.get('learningGoals'):
            goals = theory_data['learningGoals']
            speech_parts.append("Die Lernziele fuer dieses Kapitel sind:")
            for i, goal in enumerate(goals[:5], 1):
                speech_parts.append(f"Erstens: {goal}" if i == 1 else f"Ausserdem: {goal}")

        if theory_data.get('concepts'):
            speech_parts.append("Schauen wir uns die wichtigsten Konzepte an.")
            for concept in theory_data['concepts'][:6]:
                title = concept.get('title', concept.get('emoji', ''))
                desc = concept.get('description', concept.get('oneLiner', ''))
                example = concept.get('example', '')
                tip = concept.get('tip', '')

                if title and desc:
                    speech_parts.append(f"{title}. {desc}")
                    if example:
                        speech_parts.append(f"Ein Beispiel dazu: {example}")
                    if tip:
                        speech_parts.append(f"Merke dir: {tip}")

        if theory_data.get('terms'):
            speech_parts.append("Nun zu den wichtigen Fachbegriffen.")
            for term in theory_data['terms'][:6]:
                term_name = term.get('term', '')
                definition = term.get('definition', term.get('simple', ''))
                if term_name and definition:
                    speech_parts.append(f"{term_name} bedeutet: {definition}")

        if theory_data.get('examTips'):
            speech_parts.append("Fuer die Pruefung solltest du dir merken:")
            for tip in theory_data['examTips'][:4]:
                speech_parts.append(tip)

        if theory_data.get('summary'):
            speech_parts.append(f"Zusammenfassend laesst sich sagen: {theory_data['summary']}")
        elif theory_data.get('oneMinuteSummary'):
            speech_parts.append(f"Die Zusammenfassung: {theory_data['oneMinuteSummary']}")

        speech_parts.append("Das war die Erklaerung zu diesem Kapitel. Viel Erfolg beim Lernen!")

        speech_text = " ... ".join(speech_parts)

        # Limit text length for TTS
        if len(speech_text) > 4000:
            speech_text = speech_text[:3900] + " ... Das war eine verkuerzte Erklaerung."

        if len(speech_text) < 50:
            logger.warning(f"Speech text too short ({len(speech_text)} chars), skipping TTS")
            return None

        logger.info(f"Generating TTS audio: {len(speech_text)} chars, voice={voice}")

        # Generate unique filename based on content + voice
        text_hash = hashlib.sha256(speech_text.encode()).hexdigest()[:16]

        # Storage path - use chapter_id subfolder for organization
        backend_root = Path(__file__).parent.parent.parent.parent.parent
        cache_base = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache')))
        storage_dir = cache_base / 'chapter_theory_tts' / chapter_id[:8]
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = f"theory_{text_hash}_{voice}.mp3"
        file_path = storage_dir / filename

        # Check if already cached
        from_cache = file_path.exists()

        if not from_cache:
            from app.services.ai_adapter import AIAdapter

            valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
            tts_voice = voice if voice in valid_voices else 'nova'

            logger.info(f"Calling OpenAI TTS with voice={tts_voice}")

            audio_bytes = AIAdapter.text_to_speech(
                text=speech_text,
                voice=tts_voice,
                model='tts-1',
                speed=1.0
            )

            with open(file_path, 'wb') as f:
                f.write(audio_bytes)

            logger.info(f"Saved TTS audio to {file_path} ({len(audio_bytes)} bytes)")
        else:
            logger.info(f"Using cached TTS audio: {file_path}")

        # Calculate approximate duration (OpenAI TTS: ~150 words/min, avg 5 chars/word)
        word_count = len(speech_text.split())
        duration_seconds = int((word_count / 150) * 60)

        # Audio ID for the TTS endpoint (text_hash_voice_speed)
        audio_id = f"chtheory_{chapter_id[:8]}_{text_hash}_{voice}_100"

        # Return URL using chapter_theory specific endpoint
        return {
            'url': f"/api/v1/chapter-theory/{chapter_id}/audio?v={voice}",
            'duration_seconds': max(duration_seconds, 30),  # Minimum 30s
            'text_length': len(speech_text),
            'word_count': word_count,
            'from_cache': from_cache,
            'file_path': str(file_path)  # Store for internal use
        }

    except Exception as e:
        logger.error(f"Error generating theory audio: {e}", exc_info=True)
        return None
