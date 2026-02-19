"""
Helper utilities for lesson video service.

Functions for API key retrieval, content hashing, prompt generation, and status checks.
"""

import os
import hashlib
import json
from typing import Dict, Any, List

from app.application.services.ai.adapter import AIProviderError
from app.application.services.content.lesson_video.models import AVATAR_STYLES


def get_api_key() -> str:
    """
    Get OpenAI API key from database or environment.

    Returns:
        API key string

    Raises:
        AIProviderError: If API key not configured
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        try:
            from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
            api_key = AIProviderRepository.get_decrypted_api_key('openai')
        except Exception:
            pass

    if not api_key:
        raise AIProviderError('OpenAI API key not configured')

    return api_key


def generate_content_hash(
    lesson_id: str,
    teaching_steps: List[Dict],
    avatar_style: str,
    model: str
) -> str:
    """
    Generate a unique hash for lesson content.

    Used for cache key and deduplication.

    Args:
        lesson_id: Lesson identifier
        teaching_steps: List of teaching step dictionaries
        avatar_style: Avatar style name
        model: Sora model name

    Returns:
        SHA256 hash hexdigest
    """
    content = json.dumps({
        'lesson_id': lesson_id,
        'steps': teaching_steps,
        'avatar': avatar_style,
        'model': model
    }, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def generate_video_prompt(
    lesson_title: str,
    speech_text: str,
    whiteboard_content: str,
    avatar_style: str = 'professional_teacher',
    language: str = 'de'
) -> str:
    """
    Generate a Sora 2 video prompt for a teaching step.

    Sora 2 generates BOTH video AND synced audio, so we include
    voice instructions in the prompt.

    Args:
        lesson_title: Title of the lesson
        speech_text: What the teacher should say (will be spoken!)
        whiteboard_content: What should be written on the board
        avatar_style: Style of the avatar teacher
        language: Language for speech (default: German)

    Returns:
        Sora 2 prompt string
    """
    style = AVATAR_STYLES.get(avatar_style, AVATAR_STYLES['professional_teacher'])

    # Language-specific instructions
    lang_instruction = 'German' if language == 'de' else language.capitalize()

    prompt = f"""
Generate a professional educational video with synchronized audio:

=== VISUAL SCENE ===
SETTING: {style['description']}
TEACHER ACTIONS: {style['gestures']}
FACIAL EXPRESSION: {style['expression']}

CHALKBOARD/WHITEBOARD CONTENT:
{whiteboard_content if whiteboard_content else '(Empty board, teacher explains verbally)'}

TOPIC: {lesson_title}

=== AUDIO/SPEECH ===
The teacher speaks the following text in {lang_instruction}:
"{speech_text}"

VOICE STYLE: {style['voice_style']}

=== PRODUCTION QUALITY ===
- Style: High-quality, photorealistic (or Pixar-style if animated avatar)
- Camera: Medium shot with slight natural movement
- Lighting: Warm, well-lit classroom environment
- Audio: Clear speech, no background noise, professional recording quality
- Lip-sync: Perfect synchronization between speech and mouth movements

The video should look like a professional online learning platform (similar to Studyflix or Khan Academy).
"""
    return prompt.strip()


def combine_teaching_steps(teaching_steps: List[Dict[str, Any]]) -> tuple[str, str]:
    """
    Combine all teaching steps into unified speech and whiteboard content.

    Args:
        teaching_steps: List of step dictionaries with 'speech' and 'whiteboard' keys

    Returns:
        Tuple of (combined_speech, combined_whiteboard)
    """
    all_speech_texts = []
    all_whiteboard_content = []

    for step in teaching_steps:
        speech_text = step.get('speech', '')
        if speech_text:
            all_speech_texts.append(speech_text)

        for action in step.get('whiteboard', []):
            if action.get('type') in ['write', 'highlight']:
                content = action.get('content', '')
                if content:
                    all_whiteboard_content.append(content)

    combined_speech = ' '.join(all_speech_texts)
    combined_whiteboard = '\n'.join(all_whiteboard_content)

    return combined_speech, combined_whiteboard


def estimate_video_duration(speech_text: str, model: str = 'sora-2') -> int:
    """
    Estimate video duration based on speech length.

    Uses rough estimate of 150 words per minute.

    Args:
        speech_text: Full speech text
        model: Sora model name

    Returns:
        Estimated duration in seconds
    """
    word_count = len(speech_text.split())
    estimated = int((word_count / 150) * 60)

    # Apply model-specific limits
    if model == 'sora-2-pro':
        return max(15, min(120, estimated))
    else:
        return max(15, min(60, estimated))
