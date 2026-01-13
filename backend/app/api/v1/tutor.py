"""
LernsystemX Tutor API - Consolidated

AI-Powered Tutor System:
- User Chat: Context-aware AI tutoring
- TTS: Text-to-speech for accessibility
- Admin Generation: AI-powered content generation

User Endpoints:
- POST /tutor/chat - Chat with AI tutor
- POST /tutor/tts - Generate TTS audio
- GET /tutor/voices - Get available TTS voices

Admin Endpoints:
- POST /admin/tutor/generate-chapter-theory - Generate chapter theory sheet
- POST /admin/tutor/generate-lesson-steps - Generate step-by-step lesson
- POST /admin/tutor/generate-lesson-detailed - Generate detailed lesson explanation

All routes: /api/v1/tutor/* (user), /api/v1/admin/tutor/* (admin)
ISO 9001:2015 compliant - AI Tutor Core Layer
"""

from flask import Blueprint, request, jsonify, Response, g
from typing import Dict, Any, Tuple, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging
import time
import uuid
import json

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.services.ai_adapter import AIAdapter
from app.services.tutor_knowledge_service import TutorKnowledgeService as BaseTutorKnowledgeService
from app.repositories.courses.chapters import ChapterRepository
from app.repositories.courses.lessons import LessonRepository

# Blueprints
tutor_bp = Blueprint('tutor', __name__, url_prefix='/tutor')
tutor_admin_bp = Blueprint('tutor_admin', __name__, url_prefix='/admin/tutor')

__all__ = ['tutor_bp', 'tutor_admin_bp']

logger = logging.getLogger(__name__)


# =============================================================================
# VALUE OBJECTS & ENUMS
# =============================================================================

class GenerationStyle(Enum):
    """
    Available generation styles for AI tutor content.

    Value Object: Immutable, defines valid style values.
    """
    ADHS = "adhs"              # ADHS-friendly: Short, structured, emoji
    DETAILED = "detailed"       # Detailed: Comprehensive explanations
    SHORT = "short"            # Short: Brief summaries
    EXAM_FOCUS = "exam_focus"  # Exam-focused: Practice-oriented

    @classmethod
    def from_string(cls, style_str: str) -> 'GenerationStyle':
        """
        Convert string to GenerationStyle enum.

        Args:
            style_str: Style string (e.g., "adhs")

        Returns:
            GenerationStyle enum

        Raises:
            ValueError: If style is invalid
        """
        try:
            return cls(style_str.lower())
        except ValueError:
            raise ValueError(
                f"Invalid generation style: {style_str}. "
                f"Valid options: {', '.join([s.value for s in cls])}"
            )

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        names = {
            self.ADHS: "ADHS-freundlich",
            self.DETAILED: "Ausführlich",
            self.SHORT: "Kurz & Knapp",
            self.EXAM_FOCUS: "Prüfungsfokus"
        }
        return names.get(self, self.value)

    @property
    def description(self) -> str:
        """Style description."""
        descriptions = {
            self.ADHS: "Strukturiert, kurz, mit Emojis - optimal für ADHS",
            self.DETAILED: "Umfassende Erklärungen mit vielen Details",
            self.SHORT: "Kompakte Zusammenfassungen auf den Punkt",
            self.EXAM_FOCUS: "Fokus auf Prüfungsvorbereitung und Übungen"
        }
        return descriptions.get(self, "")


@dataclass(frozen=True)
class TutorContext:
    """
    Context for tutor interactions.

    Value Object: Immutable context data for tutor sessions.
    """
    user_id: str
    course_id: Optional[str] = None
    chapter_id: Optional[str] = None
    lesson_id: Optional[int] = None
    method_id: Optional[str] = None
    page_context: Optional[str] = None

    def has_course_context(self) -> bool:
        """Check if context has course-related information."""
        return any([self.course_id, self.chapter_id, self.lesson_id, self.method_id])

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'course_id': self.course_id,
            'chapter_id': self.chapter_id,
            'lesson_id': self.lesson_id,
            'method_id': self.method_id,
            'page_context': self.page_context
        }


@dataclass(frozen=True)
class TTSVoice:
    """
    Text-to-Speech voice configuration.

    Value Object: Immutable voice settings.
    """
    voice_id: str
    display_name: str
    description: str
    display_name_de: Optional[str] = None
    language: str = "en"
    gender: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'voice_id': self.voice_id,
            'display_name': self.display_name,
            'display_name_de': self.display_name_de or self.display_name,
            'description': self.description,
            'language': self.language,
            'gender': self.gender
        }


# Initialize OpenAI voices
AVAILABLE_VOICES = [
    TTSVoice("alloy", "Alloy", "Neutral, balanced voice"),
    TTSVoice("echo", "Echo", "Clear, articulate voice", gender="male"),
    TTSVoice("fable", "Fable", "Warm, expressive voice", gender="female"),
    TTSVoice("onyx", "Onyx", "Deep, authoritative voice", gender="male"),
    TTSVoice("nova", "Nova", "Energetic, upbeat voice", gender="female"),
    TTSVoice("shimmer", "Shimmer", "Soft, gentle voice", display_name_de="Schimmer", gender="female")
]


# =============================================================================
# CONSTANTS & PROMPTS
# =============================================================================

DEFAULT_TUTOR_PROMPT = """Du bist ein freundlicher und hilfreicher KI-Tutor auf LernsystemX.
Du begleitest Lernende durch ihre Lernreise und hilfst bei Fragen zu Kursen und Lernmethoden.
Du bist geduldig, ermutigend und erklärst Konzepte klar und verständlich.
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.
Halte deine Antworten prägnant aber hilfreich - idealerweise 2-4 Sätze.

Wenn der User Fragen zum aktuellen Lerninhalt hat, beziehe dich auf den bereitgestellten Kurs-Kontext.
Du kannst Konzepte erklären, Beispiele geben und bei Übungen helfen."""


# Style configurations for content generation
STYLE_CONFIGS = {
    GenerationStyle.ADHS: {
        'temperature': 0.7,
        'max_tokens': 2000,
        'instructions': [
            'Verwende kurze Sätze (max. 10-15 Wörter)',
            'Strukturiere klar mit Aufzählungen und Absätzen',
            'Verwende relevante Emojis zur Auflockerung (max. 3 pro Abschnitt)',
            'Hebe Schlüsselwörter hervor (Fettdruck)',
            'Verwende Eselsbrücken und Merkhilfen'
        ]
    },
    GenerationStyle.DETAILED: {
        'temperature': 0.6,
        'max_tokens': 3500,
        'instructions': [
            'Erkläre Konzepte ausführlich und detailliert',
            'Verwende Beispiele zur Veranschaulichung',
            'Erläutere Zusammenhänge und Hintergründe',
            'Gehe auf Randthemen und Details ein',
            'Verwende Fachbegriffe und erkläre sie'
        ]
    },
    GenerationStyle.SHORT: {
        'temperature': 0.5,
        'max_tokens': 1000,
        'instructions': [
            'Fasse dich kurz und prägnant',
            'Konzentriere dich auf die Kernpunkte',
            'Verwende Stichpunkte statt langer Texte',
            'Verzichte auf Beispiele wenn nicht essentiell',
            'Maximal 3-4 Sätze pro Abschnitt'
        ]
    },
    GenerationStyle.EXAM_FOCUS: {
        'temperature': 0.6,
        'max_tokens': 2500,
        'instructions': [
            'Fokus auf prüfungsrelevante Inhalte',
            'Verwende Prüfungssprache und -format',
            'Betone wichtige Konzepte für IHK-Prüfung',
            'Füge Übungsfragen hinzu',
            'Verwende Checklisten für Lernziele'
        ]
    }
}


# =============================================================================
# HELPER FUNCTIONS (Factory & Service Logic)
# =============================================================================

def create_chat_session(
    user_id: str,
    message: str,
    context: Optional[TutorContext] = None,
    history: Optional[list] = None
) -> Dict[str, Any]:
    """
    Create tutor chat session configuration.

    Factory method with business rules:
    - History limited to last 10 messages
    - Context is optional
    - Session ID is generated
    """
    session_id = str(uuid.uuid4())

    # Limit history to last 10 messages
    if history and len(history) > 10:
        history = history[-10:]

    return {
        'session_id': session_id,
        'user_id': user_id,
        'message': message,
        'context': context.to_dict() if context else {},
        'history': history or [],
        'created_at': datetime.utcnow(),
        'has_context': context is not None and context.has_course_context() if context else False
    }


def create_tts_request(user_id: str, text: str, voice: str = 'alloy') -> Dict[str, Any]:
    """
    Create TTS request configuration.

    Business Rules:
    - Text limited to 4096 characters
    - Voice must be valid
    """
    # Validate text length
    if len(text) > 4096:
        raise ValueError("Text too long (max 4096 characters)")

    # Validate voice
    valid_voices = [v.voice_id for v in AVAILABLE_VOICES]
    if voice not in valid_voices:
        raise ValueError(f"Invalid voice: {voice}. Valid voices: {', '.join(valid_voices)}")

    return {
        'user_id': user_id,
        'text': text.strip(),
        'voice': voice
    }


def build_context_for_chat(
    context: TutorContext,
    include_files: bool = True,
    include_progress: bool = True
) -> str:
    """
    Build knowledge context for tutor chat.

    Loads course/chapter/lesson content if IDs provided.
    """
    if not context.has_course_context():
        return "Kein spezifischer Kurs-Kontext verfügbar."

    try:
        knowledge_context = BaseTutorKnowledgeService.build_tutor_context_prompt(
            course_id=context.course_id,
            chapter_id=context.chapter_id,
            lesson_id=context.lesson_id,
            method_id=context.method_id,
            user_id=context.user_id,
            include_files=include_files,
            include_progress=include_progress
        )
        return knowledge_context
    except Exception as e:
        logger.warning(f"Could not load tutor knowledge context: {e}")
        return "Kein spezifischer Kurs-Kontext verfügbar."


def build_context_for_generation(
    course_title: str,
    chapter_title: str,
    chapter_description: Optional[str] = None,
    lesson_titles: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Build context for content generation (theory, explanations).
    """
    return {
        'course_title': course_title,
        'chapter_title': chapter_title,
        'chapter_description': chapter_description or '',
        'lesson_titles': ', '.join(lesson_titles) if lesson_titles else 'Keine spezifischen Lektionen',
        'target_audience': 'Fachinformatiker Systemintegration (FISI) in Prüfungsvorbereitung'
    }


def parse_json_response(output_text: str, fallback_title: str = "Generierter Inhalt") -> dict:
    """
    Parse JSON response from AI, with fallback for malformed JSON.
    """
    try:
        # Try direct JSON parse
        data = json.loads(output_text)
        return data
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        if '```json' in output_text:
            start = output_text.find('```json') + 7
            end = output_text.find('```', start)
            json_str = output_text[start:end].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Fallback: Return as plain text
        logger.warning("Could not parse AI response as JSON, using fallback")
        return {
            'title': fallback_title,
            'introduction': '',
            'sections': [{
                'title': 'Inhalt',
                'content': output_text,
                'subsections': []
            }],
            'summary': '',
            'key_points': []
        }


def get_style_config(style: GenerationStyle) -> dict:
    """Get style configuration for AI generation."""
    return STYLE_CONFIGS.get(style, STYLE_CONFIGS[GenerationStyle.ADHS])


def save_chapter_theory(chapter_id: str, style: str, theory_data: dict, tokens_used: int, user_id: str):
    """Save generated theory to database."""
    try:
        from app.repositories.chapter_theory import ChapterTheoryRepository
        ChapterTheoryRepository.create({
            'chapter_id': chapter_id,
            'style': style,
            'theory_data': theory_data,
            'title': theory_data.get('title'),
            'tokens_used': tokens_used,
            'created_by': user_id
        })
    except Exception as e:
        logger.warning(f"Could not save chapter theory to DB: {e}")


# =============================================================================
# USER ENDPOINTS - TUTOR CHAT & TTS
# =============================================================================

@tutor_bp.route('/chat', methods=['POST'])
@token_required
@limiter.limit("30 per minute")
def tutor_chat() -> Tuple[Dict[str, Any], int]:
    """
    Chat with the AI Tutor (context-aware).

    Request Body:
        message (str): User's message
        context (str): Page context (optional)
        systemPrompt (str): Custom system prompt (optional)
        history (list): Chat history (optional, max 10 messages)
        courseId (str): Current course ID (optional)
        chapterId (str): Current chapter ID (optional)
        lessonId (int): Current lesson ID (optional)
        methodId (str): Current learning method ID (optional)

    Response:
        200: Tutor response with message, tokens used, context status
        400: Invalid request
        500: Server error
    """
    try:
        user_id = g.current_user['user_id']
        data = request.get_json()

        if not data or not data.get('message'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Message is required'
                }
            }), 400

        message = data['message']
        page_context = data.get('context', '')
        custom_system_prompt = data.get('systemPrompt', DEFAULT_TUTOR_PROMPT)
        history = data.get('history', [])

        # Create TutorContext value object
        context = TutorContext(
            user_id=user_id,
            course_id=data.get('courseId'),
            chapter_id=data.get('chapterId'),
            lesson_id=data.get('lessonId'),
            method_id=data.get('methodId'),
            page_context=page_context
        )

        # Create session
        session = create_chat_session(
            user_id=user_id,
            message=message,
            context=context,
            history=history
        )

        # Build knowledge context
        knowledge_context = ''
        context_used = False

        if context.has_course_context():
            knowledge_context = build_context_for_chat(
                context=context,
                include_files=True,
                include_progress=True
            )
            if knowledge_context and knowledge_context != "Kein spezifischer Kurs-Kontext verfügbar.":
                context_used = True
                logger.debug(f"Loaded tutor context for course={context.course_id}, chapter={context.chapter_id}")

        # Build the full system prompt with context
        system_prompt = custom_system_prompt

        # Add page context (where user is in the app)
        if page_context:
            system_prompt += f"\n\nAktueller Seitenkontext: {page_context}"

        # Add knowledge context from DB (course/chapter/lesson content)
        if knowledge_context:
            system_prompt += f"\n\n{knowledge_context}"

        # Build messages for the AI
        messages = []

        # Add history (limit already applied by factory)
        for msg in session['history']:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Add current message
        messages.append({
            'role': 'user',
            'content': message
        })

        # Call AI
        response = AIAdapter.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            model='gpt-4o-mini',  # Use fast model for chat
            max_tokens=800 if context_used else 500,  # More tokens when using context
            temperature=0.7,
            user_id=user_id
        )

        return jsonify({
            'success': True,
            'data': {
                'message': response.get('content', ''),
                'tokens_used': response.get('usage', {}).get('total_tokens', 0),
                'context_used': context_used,
                'session_id': session['session_id']
            }
        }), 200

    except Exception as e:
        logger.error(f"Tutor chat error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'CHAT_ERROR',
                'message': str(e)
            }
        }), 500


@tutor_bp.route('/tts', methods=['POST'])
@token_required
@limiter.limit("20 per minute")
def tutor_tts() -> Response:
    """
    Generate TTS audio for text using OpenAI TTS.

    Request Body:
        text (str): Text to convert to speech
        voice (str): Voice ID (alloy, echo, fable, onyx, nova, shimmer)

    Response:
        200: audio/mpeg binary data
        400: Invalid request
        500: Server error
    """
    try:
        user_id = g.current_user['user_id']
        data = request.get_json()

        if not data or not data.get('text'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Text is required'
                }
            }), 400

        text = data['text']
        voice = data.get('voice', 'alloy')

        # Create TTS request (validates and sanitizes)
        tts_request = create_tts_request(
            user_id=user_id,
            text=text,
            voice=voice
        )

        # Generate TTS using OpenAI
        audio_data = AIAdapter.text_to_speech(
            text=tts_request['text'],
            voice=tts_request['voice'],
            model='tts-1'  # Use standard model (tts-1-hd for higher quality)
        )

        if not audio_data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TTS_ERROR',
                    'message': 'Failed to generate audio'
                }
            }), 500

        return Response(
            audio_data,
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': 'inline',
                'Cache-Control': 'no-cache'
            }
        )

    except ValueError as ve:
        # Factory validation error
        logger.warning(f"TTS validation error: {ve}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(ve)
            }
        }), 400

    except Exception as e:
        logger.error(f"Tutor TTS error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'TTS_ERROR',
                'message': str(e)
            }
        }), 500


@tutor_bp.route('/voices', methods=['GET'])
@token_required
def get_tts_voices() -> Tuple[Dict[str, Any], int]:
    """
    Get available TTS voices.

    Response:
        200: List of available voices
        500: Server error
    """
    try:
        return jsonify({
            'success': True,
            'data': {
                'voices': [voice.to_dict() for voice in AVAILABLE_VOICES]
            }
        }), 200

    except Exception as e:
        logger.error(f"Get voices error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VOICES_ERROR',
                'message': str(e)
            }
        }), 500


# =============================================================================
# ADMIN ENDPOINTS - CONTENT GENERATION
# =============================================================================

@tutor_admin_bp.route('/generate-chapter-theory', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_chapter_theory() -> Tuple[Dict[str, Any], int]:
    """
    Generate comprehensive theory sheet for a chapter using AI.

    Request Body:
        chapter_id (str): Chapter UUID
        chapter_title (str): Chapter title
        course_title (str): Course title
        style (str): Generation style (adhs, detailed, short, exam_focus)
        generate_tts (bool): Generate audio version (optional)
        tts_voice (str): TTS voice ID (optional)

    Response:
        200: Theory data with title, sections, summary, key points
        400: Invalid request
        500: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        # Validate required fields
        chapter_id = data.get('chapter_id')
        chapter_title = data.get('chapter_title', '')
        course_title = data.get('course_title', '')

        if not chapter_id or not chapter_title:
            return jsonify({
                'success': False,
                'error': 'chapter_id and chapter_title are required'
            }), 400

        # Parse style
        try:
            style = GenerationStyle.from_string(data.get('style', 'adhs'))
        except ValueError as ve:
            return jsonify({'success': False, 'error': str(ve)}), 400

        user_id = g.current_user['user_id']
        start_time = time.time()

        # Get chapter context
        chapter = ChapterRepository.find_by_id(chapter_id)
        chapter_description = chapter.get('description', '') if chapter else ''

        # Get lesson titles for context
        lessons = LessonRepository.find_by_chapter(chapter_id)
        lesson_titles = [l.get('title', '') for l in lessons[:10]]

        # Build context
        context = build_context_for_generation(
            course_title=course_title,
            chapter_title=chapter_title,
            chapter_description=chapter_description,
            lesson_titles=lesson_titles
        )

        # Get style configuration
        style_config = get_style_config(style)

        # Build AI prompt
        instructions = '\n'.join(f'- {instr}' for instr in style_config['instructions'])

        system_prompt = f"""Du bist ein KI-Tutor für Fachinformatiker Systemintegration (FISI).
Erstelle ein umfassendes Theorie-Sheet im {style.display_name}-Stil.

Formatierungs-Anforderungen:
{instructions}

Ausgabe-Format (JSON):
{{
    "title": "Titel des Theorie-Sheets",
    "introduction": "Kurze Einführung (2-3 Sätze)",
    "sections": [
        {{
            "title": "Abschnittstitel",
            "content": "Inhalt des Abschnitts",
            "subsections": []
        }}
    ],
    "summary": "Zusammenfassung der wichtigsten Punkte",
    "key_points": ["Punkt 1", "Punkt 2", ...]
}}"""

        user_prompt = f"""Erstelle ein Theorie-Sheet für:

Kurs: {context['course_title']}
Kapitel: {context['chapter_title']}
Beschreibung: {context['chapter_description']}
Lektionen im Kapitel: {context['lesson_titles']}

Zielgruppe: {context['target_audience']}"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        # Call AI
        result = AIAdapter.chat_completion(
            messages=messages,
            model='gpt-4o-mini',
            temperature=style_config['temperature'],
            max_tokens=style_config['max_tokens'],
            user_id=user_id
        )

        # Parse response
        output_text = result.get('content', '{}')
        theory_data = parse_json_response(output_text, chapter_title)

        response_time_ms = int((time.time() - start_time) * 1000)

        # Save to database
        save_chapter_theory(
            chapter_id=chapter_id,
            style=style.value,
            theory_data=theory_data,
            tokens_used=result.get('usage', {}).get('total_tokens', 0),
            user_id=user_id
        )

        return jsonify({
            'success': True,
            'data': theory_data,
            'style': style.value,
            'tokens_used': result.get('usage', {}).get('total_tokens', 0),
            'response_time_ms': response_time_ms
        }), 200

    except Exception as e:
        logger.error(f"Error generating chapter theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate chapter theory',
            'message': str(e)
        }), 500


@tutor_admin_bp.route('/generate-lesson-steps', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_lesson_steps() -> Tuple[Dict[str, Any], int]:
    """
    Generate step-by-step lesson explanation.

    Request Body:
        lesson_id (str): Lesson ID
        lesson_title (str): Lesson title
        chapter_title (str): Chapter title (optional)
        course_title (str): Course title (optional)
        style (str): Generation style (adhs, detailed, short, exam_focus)

    Response:
        200: Lesson explanation with steps
        400: Invalid request
        500: Server error
    """
    return _generate_lesson_explanation('steps')


@tutor_admin_bp.route('/generate-lesson-detailed', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_lesson_detailed() -> Tuple[Dict[str, Any], int]:
    """
    Generate detailed lesson explanation.

    Request Body:
        lesson_id (str): Lesson ID
        lesson_title (str): Lesson title
        chapter_title (str): Chapter title (optional)
        course_title (str): Course title (optional)
        style (str): Generation style (adhs, detailed, short, exam_focus)

    Response:
        200: Detailed lesson explanation
        400: Invalid request
        500: Server error
    """
    return _generate_lesson_explanation('detailed')


def _generate_lesson_explanation(explanation_type: str) -> Tuple[Dict[str, Any], int]:
    """Generate lesson explanation (steps or detailed)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        lesson_id = data.get('lesson_id')
        if not lesson_id:
            return jsonify({'success': False, 'error': 'lesson_id required'}), 400

        # Parse style
        try:
            style = GenerationStyle.from_string(data.get('style', 'adhs'))
        except ValueError as ve:
            return jsonify({'success': False, 'error': str(ve)}), 400

        user_id = g.current_user['user_id']

        # Get style config
        style_config = get_style_config(style)

        # Build prompt
        instructions = '\n'.join(f'- {instr}' for instr in style_config['instructions'])

        if explanation_type == 'steps':
            format_description = """{{
    "title": "Titel",
    "steps": [
        {{
            "step_number": 1,
            "title": "Schritt-Titel",
            "content": "Beschreibung",
            "tips": ["Tipp 1", "Tipp 2"]
        }}
    ]
}}"""
        else:  # detailed
            format_description = """{{
    "title": "Titel",
    "introduction": "Einführung",
    "main_content": "Hauptinhalt",
    "examples": ["Beispiel 1", "Beispiel 2"],
    "summary": "Zusammenfassung"
}}"""

        system_prompt = f"""Du bist ein KI-Tutor. Erstelle eine {explanation_type}-Erklärung im {style.display_name}-Stil.

Formatierungs-Anforderungen:
{instructions}

Formatiere als JSON:
{format_description}"""

        user_prompt = f"""Erstelle eine {explanation_type}-Erklärung für:

Kurs: {data.get('course_title', 'Unbekannt')}
Kapitel: {data.get('chapter_title', 'Unbekannt')}
Lektion: {data.get('lesson_title', 'Unbekannt')}

Zielgruppe: Fachinformatiker Systemintegration (FISI)"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        # Call AI
        result = AIAdapter.chat_completion(
            messages=messages,
            model='gpt-4o-mini',
            temperature=style_config['temperature'],
            max_tokens=style_config['max_tokens'],
            user_id=user_id
        )

        # Parse response
        output_text = result.get('content', '{}')
        explanation_data = parse_json_response(output_text, data.get('lesson_title', 'Lektion'))

        return jsonify({
            'success': True,
            'data': explanation_data,
            'style': style.value,
            'explanation_type': explanation_type,
            'tokens_used': result.get('usage', {}).get('total_tokens', 0)
        }), 200

    except Exception as e:
        logger.error(f"Error generating lesson explanation: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate lesson explanation',
            'message': str(e)
        }), 500
