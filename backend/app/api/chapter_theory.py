"""
LernsystemX Chapter Theory API

User-facing endpoints for chapter theory content:
- GET /api/v1/chapters/:chapter_id/theory - Get cached theory
- POST /api/v1/chapters/:chapter_id/theory/generate - Generate theory (once)

Theory is generated via KI and stored in DB to avoid repeated token costs.
Supports multiple styles: adhs, detailed, short, exam_focus, standard.
"""

from flask import request, jsonify, g
from datetime import datetime
import logging
import json
import time

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.middleware.auth import token_required
from app.repositories.base_repository import BaseRepository


# ============================================================================
# Repository Functions
# ============================================================================

def get_chapter_theory(chapter_id: str, style: str = 'adhs') -> dict | None:
    """Get chapter theory from database."""
    query = """
        SELECT
            theory_id, chapter_id, style, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by,
            created_at, updated_at
        FROM chapter_theory
        WHERE chapter_id = %s AND style = %s
    """
    return BaseRepository.fetch_one(query, (chapter_id, style))


def save_chapter_theory(
    chapter_id: str,
    style: str,
    theory_data: dict,
    audio_url: str | None = None,
    audio_duration: int | None = None,
    tokens_used: int = 0,
    model_used: str = None,
    user_id: str = None
) -> dict:
    """Save or update chapter theory."""
    query = """
        INSERT INTO chapter_theory (
            chapter_id, style, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (chapter_id, style)
        DO UPDATE SET
            theory_data = EXCLUDED.theory_data,
            audio_url = EXCLUDED.audio_url,
            audio_duration_seconds = EXCLUDED.audio_duration_seconds,
            tokens_used = EXCLUDED.tokens_used,
            model_used = EXCLUDED.model_used,
            updated_at = NOW()
        RETURNING theory_id, chapter_id, style, created_at, updated_at
    """
    return BaseRepository.fetch_one(query, (
        chapter_id, style, json.dumps(theory_data),
        audio_url, audio_duration,
        tokens_used, model_used, user_id
    ))


def get_chapter_info(chapter_id: str) -> dict | None:
    """Get chapter with course info for context."""
    query = """
        SELECT
            c.chapter_id, c.title, c.description, c.order_index,
            co.course_id, co.title as course_title
        FROM chapters c
        JOIN courses co ON c.course_id = co.course_id
        WHERE c.chapter_id = %s
    """
    return BaseRepository.fetch_one(query, (chapter_id,))


def get_chapter_lessons(chapter_id: str) -> list:
    """Get lessons in chapter for context."""
    query = """
        SELECT lesson_id, title, order_index
        FROM lessons
        WHERE chapter_id = %s
        ORDER BY order_index
        LIMIT 15
    """
    return BaseRepository.fetch_all(query, (chapter_id,)) or []


# ============================================================================
# API Endpoints
# ============================================================================

@api_v1.route('/chapters/<chapter_id>/theory', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def get_theory(chapter_id: str):
    """
    Get chapter theory (cached from DB).

    Query params:
        style: Theory style (adhs, detailed, short, exam_focus, standard)

    Response 200:
        {
            "success": true,
            "data": {
                "hasTheory": true,
                "theory": {...},
                "audioUrl": "...",
                "style": "adhs",
                "createdAt": "..."
            }
        }
    """
    try:
        style = request.args.get('style', 'adhs')

        # Validate style
        valid_styles = ['adhs', 'detailed', 'short', 'exam_focus', 'standard']
        if style not in valid_styles:
            style = 'adhs'

        # Get from database
        theory_record = get_chapter_theory(chapter_id, style)

        if not theory_record:
            return jsonify({
                'success': True,
                'data': {
                    'hasTheory': False,
                    'theory': None,
                    'style': style,
                    'message': 'No theory generated yet for this chapter'
                }
            }), 200

        # Parse theory_data from JSONB
        theory_data = theory_record.get('theory_data', {})
        if isinstance(theory_data, str):
            theory_data = json.loads(theory_data)

        return jsonify({
            'success': True,
            'data': {
                'hasTheory': True,
                'theory': theory_data,
                'audioUrl': theory_record.get('audio_url'),
                'audioDuration': theory_record.get('audio_duration_seconds'),
                'style': style,
                'createdAt': theory_record.get('created_at').isoformat() if theory_record.get('created_at') else None,
                'tokensUsed': theory_record.get('tokens_used', 0)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting chapter theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get chapter theory',
            'message': str(e)
        }), 500


@api_v1.route('/chapters/<chapter_id>/theory/generate', methods=['POST'])
@token_required
@limiter.limit("5 per minute")
def generate_theory(chapter_id: str):
    """
    Generate chapter theory via KI.

    Only generates if theory doesn't exist yet (to save tokens).
    Use force=true to regenerate.

    Request Body:
        {
            "style": "adhs",
            "generateTts": true,
            "ttsVoice": "nova",
            "force": false
        }

    Response 200:
        {
            "success": true,
            "data": {...},
            "tokensUsed": 1234,
            "cached": false
        }
    """
    try:
        data = request.get_json() or {}
        style = data.get('style', 'adhs')
        generate_tts = data.get('generateTts', True)
        tts_voice = data.get('ttsVoice', 'nova')
        force = data.get('force', False)

        user_id = g.current_user['user_id']

        # Check if theory already exists
        existing = get_chapter_theory(chapter_id, style)
        if existing and not force:
            # Return cached version
            theory_data = existing.get('theory_data', {})
            if isinstance(theory_data, str):
                theory_data = json.loads(theory_data)

            return jsonify({
                'success': True,
                'data': theory_data,
                'audioUrl': existing.get('audio_url'),
                'style': style,
                'tokensUsed': 0,
                'cached': True,
                'message': 'Theory already exists. Use force=true to regenerate.'
            }), 200

        # Get chapter info for context
        chapter = get_chapter_info(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        lessons = get_chapter_lessons(chapter_id)
        lesson_titles = [l.get('title', '') for l in lessons]

        # Build context
        context = {
            'chapter_title': chapter.get('title', ''),
            'course_title': chapter.get('course_title', ''),
            'chapter_description': chapter.get('description', ''),
            'lesson_titles': ', '.join(lesson_titles) if lesson_titles else 'Keine Lektionen',
            'target_audience': 'Fachinformatiker Systemintegration (FISI) in Pruefungsvorbereitung'
        }

        start_time = time.time()

        # Generate theory via KI
        theory_data, tokens_used, model = _generate_theory_content(style, context)

        # Generate TTS if requested
        audio_url = None
        audio_duration = None
        if generate_tts and theory_data:
            audio_result = _generate_theory_audio(theory_data, tts_voice, chapter_id, user_id)
            if audio_result and 'url' in audio_result:
                audio_url = audio_result.get('url')
                audio_duration = audio_result.get('duration_seconds')

        # Save to database
        save_chapter_theory(
            chapter_id=chapter_id,
            style=style,
            theory_data=theory_data,
            audio_url=audio_url,
            audio_duration=audio_duration,
            tokens_used=tokens_used,
            model_used=model,
            user_id=user_id
        )

        response_time = int((time.time() - start_time) * 1000)

        logger.info(f"Generated chapter theory ({style}) for {chapter_id}, tokens: {tokens_used}")

        return jsonify({
            'success': True,
            'data': theory_data,
            'audioUrl': audio_url,
            'style': style,
            'tokensUsed': tokens_used,
            'responseTimeMs': response_time,
            'cached': False
        }), 200

    except Exception as e:
        logger.error(f"Error generating chapter theory: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to generate chapter theory',
            'message': str(e)
        }), 500


# ============================================================================
# KI Generation Functions
# ============================================================================

def _generate_theory_content(style: str, context: dict) -> tuple[dict, int, str]:
    """Generate theory content via OpenAI."""
    from app.services.ai_adapter import AIAdapter

    system_prompt, user_prompt = _get_theory_prompts(style, context)

    adapter = AIAdapter(provider='openai', model='gpt-4o-mini')

    result = adapter.send_messages(
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )

    output_text = result.get('output_text', '{}')
    tokens_used = result.get('total_tokens', 0)
    model = 'gpt-4o-mini'

    # Parse JSON response
    theory_data = _parse_json_response(output_text, context.get('chapter_title', ''))

    return theory_data, tokens_used, model


def _get_theory_prompts(style: str, context: dict) -> tuple[str, str]:
    """Get prompts for theory generation based on style."""
    chapter_title = context.get('chapter_title', '')
    course_title = context.get('course_title', '')
    chapter_description = context.get('chapter_description', '')
    lesson_titles = context.get('lesson_titles', '')

    base_context = f"""
Kontext:
- Kapitel: {chapter_title}
- Kurs: {course_title}
- Beschreibung: {chapter_description}
- Lektionen: {lesson_titles}
- Zielgruppe: Fachinformatiker Systemintegration (FISI)
- Niveau: IHK-Pruefung
"""

    if style == 'adhs':
        system = """Du bist ein erfahrener IT-Ausbilder, spezialisiert auf ADHS-freundliches Lernen.
Deine Erklaerungen sind:
- KURZ und praegnant (max. 2-3 Saetze pro Punkt)
- VISUELL strukturiert mit Aufzaehlungen
- SCHRITTWEISE aufgebaut
- Mit KONKRETEN Beispielen
- Ohne Fachjargon (oder sofort erklaert)

Du erstellst auch WHITEBOARD-ANIMATIONEN die synchron zur Erklaerung ablaufen.

Antworte NUR mit validem JSON."""

        user = f"""Erstelle ein ADHS-freundliches Theorieblatt fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "overview": "Kurze Uebersicht (2-3 Saetze)",
    "learningGoals": ["Ziel 1 (kurz!)", "Ziel 2", ...],
    "concepts": [
        {{
            "title": "Konzept",
            "emoji": "passendes Emoji",
            "oneLiner": "Ein Satz",
            "example": "Beispiel",
            "tip": "Merkhilfe"
        }}
    ],
    "terms": [{{"term": "Begriff", "simple": "Einfach erklaert", "example": "Alltagsbeispiel"}}],
    "examTips": ["Tipp 1", "Tipp 2"],
    "summary": "3 Bullet Points",
    "whiteboardActions": [
        {{
            "type": "write",
            "content": "Ueberschrift oder Text",
            "position": {{"x": 50, "y": 10}},
            "duration": 1500,
            "color": "#1f2937",
            "fontSize": 24
        }},
        {{
            "type": "schema",
            "position": {{"x": 10, "y": 25}},
            "schema": [
                {{"name": "Zeile 1", "operator": "=", "value": "Wert 1", "highlight": false}},
                {{"name": "Zeile 2", "operator": "+", "value": "Wert 2", "highlight": true}}
            ],
            "duration": 2000
        }},
        {{
            "type": "arrow",
            "position": {{"x": 30, "y": 50}},
            "endPosition": {{"x": 70, "y": 50}},
            "duration": 800,
            "color": "#3b82f6"
        }},
        {{
            "type": "highlight",
            "content": "Wichtiger Begriff",
            "position": {{"x": 50, "y": 70}},
            "duration": 500,
            "color": "#fbbf24"
        }}
    ]
}}

WICHTIG fuer whiteboardActions:
- Erstelle 5-8 Animationen die das Thema VISUELL erklaeren
- Nutze verschiedene Typen: write, schema, arrow, highlight, underline
- Position ist in Prozent (0-100)
- Bei Kalkulationen/Formeln nutze "schema" mit Zeilen
- Bei Prozessen nutze Pfeile
- Wichtiges mit "highlight" hervorheben
- Baue das Bild Schritt fuer Schritt auf"""

    elif style == 'detailed':
        system = """Du bist ein IT-Ausbilder mit akademischem Hintergrund.
Erstelle ausfuehrliche, gut strukturierte Lerninhalte mit allen Details.
Antworte NUR mit validem JSON."""

        user = f"""Erstelle ein ausfuehrliches Theorieblatt fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "overview": "Ausfuehrliche Uebersicht mit Einordnung",
    "learningGoals": ["Detailliertes Lernziel 1", ...],
    "prerequisites": ["Vorwissen 1", ...],
    "concepts": [
        {{
            "title": "Konzept",
            "description": "Ausfuehrliche Erklaerung",
            "background": "Hintergrund",
            "formula": "Formel falls relevant",
            "examples": ["Beispiel 1", "Beispiel 2"],
            "commonMistakes": ["Fehler 1"]
        }}
    ],
    "terms": [{{"term": "Begriff", "definition": "Vollstaendige Definition", "usage": "Verwendung"}}],
    "examRelevance": "Detaillierte Pruefungsrelevanz",
    "summary": "Zusammenfassung"
}}"""

    elif style == 'short':
        system = """Du bist ein IT-Ausbilder, der auf Effizienz setzt.
Erstelle extrem kompakte Zusammenfassungen - nur das Wichtigste.
Antworte NUR mit validem JSON."""

        user = f"""Erstelle eine Kurzuebersicht fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "title": "Kapiteltitel",
    "keyPoints": ["Punkt 1", "Punkt 2", "Punkt 3", "Punkt 4", "Punkt 5"],
    "mustKnowTerms": [{{"term": "Begriff", "definition": "Ein-Satz-Definition"}}],
    "examFormula": "Wichtigste Formel",
    "oneMinuteSummary": "Das Kapitel in 60 Sekunden"
}}"""

    elif style == 'exam_focus':
        system = """Du bist ein IHK-Pruefer und kennst die AP1-Pruefung genau.
Erstelle Lerninhalte mit klarem Pruefungsfokus.
Antworte NUR mit validem JSON."""

        user = f"""Erstelle ein pruefungsfokussiertes Theorieblatt fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "examRelevance": "HOCH/MITTEL/NIEDRIG",
    "typicalPoints": "Typische Punktzahl",
    "mustKnow": ["Das MUSS sitzen 1", "Das MUSS sitzen 2"],
    "typicalTasks": [
        {{
            "type": "Aufgabentyp",
            "example": "Beispielaufgabe",
            "solution": "Loesungsweg",
            "points": "Punktzahl",
            "timeMinutes": "Zeit"
        }}
    ],
    "commonMistakes": [{{"mistake": "Fehler", "consequence": "Punktabzug", "howToAvoid": "Vermeidung"}}],
    "examTips": ["Tipp 1", "Tipp 2"],
    "lastMinuteChecklist": ["Check 1", "Check 2"]
}}"""

    else:  # standard
        system = """Du bist ein erfahrener IT-Ausbilder fuer Fachinformatiker.
Erstelle strukturierte, pruefungsrelevante Lerninhalte.
Antworte NUR mit validem JSON."""

        user = f"""Erstelle ein Theorieblatt fuer "{chapter_title}".
{base_context}

JSON-Struktur:
{{
    "overview": "Uebersicht",
    "learningGoals": ["Ziel 1", "Ziel 2", ...],
    "concepts": [{{"title": "Konzept", "description": "Erklaerung", "formula": "optional"}}],
    "terms": [{{"term": "Begriff", "definition": "Definition"}}],
    "examRelevance": "Pruefungsrelevanz"
}}"""

    return system, user


def _parse_json_response(output_text: str, chapter_title: str) -> dict:
    """Parse JSON response from AI, with fallback."""
    try:
        # Clean up potential markdown code blocks
        if output_text.startswith('```'):
            output_text = output_text.split('```')[1]
            if output_text.startswith('json'):
                output_text = output_text[4:]

        return json.loads(output_text.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        return {
            'overview': f'Uebersicht fuer {chapter_title}',
            'learningGoals': ['Die Grundlagen verstehen', 'Anwendung in der Praxis'],
            'concepts': [{'title': chapter_title, 'description': 'Kerninhalt des Kapitels'}],
            'terms': [],
            'examRelevance': 'Pruefungsrelevant fuer IHK AP1'
        }


def _generate_theory_audio(theory_data: dict, voice: str, chapter_id: str, user_id: str) -> dict | None:
    """Generate TTS audio for theory content."""
    import re
    import hashlib
    from pathlib import Path
    import os

    try:
        # Build speech text from theory data
        speech_parts = []

        if theory_data.get('overview'):
            overview = re.sub('<[^<]+?>', '', str(theory_data['overview']))
            speech_parts.append(f"Uebersicht. {overview}")

        if theory_data.get('learningGoals'):
            goals = theory_data['learningGoals'][:5]
            speech_parts.append("Lernziele. " + ". ".join(goals))

        if theory_data.get('concepts'):
            speech_parts.append("Wichtige Konzepte.")
            for concept in theory_data['concepts'][:5]:
                title = concept.get('title', concept.get('emoji', ''))
                desc = concept.get('description', concept.get('oneLiner', ''))
                if title and desc:
                    speech_parts.append(f"{title}. {desc}")

        if theory_data.get('terms'):
            speech_parts.append("Wichtige Begriffe.")
            for term in theory_data['terms'][:5]:
                term_name = term.get('term', '')
                definition = term.get('definition', term.get('simple', ''))
                if term_name and definition:
                    speech_parts.append(f"{term_name}. {definition}")

        if theory_data.get('examTips'):
            speech_parts.append("Pruefungstipps.")
            for tip in theory_data['examTips'][:3]:
                speech_parts.append(tip)

        if theory_data.get('summary'):
            speech_parts.append(f"Zusammenfassung. {theory_data['summary']}")
        elif theory_data.get('oneMinuteSummary'):
            speech_parts.append(f"Zusammenfassung. {theory_data['oneMinuteSummary']}")

        speech_text = " ... ".join(speech_parts)

        # Limit text length
        if len(speech_text) > 4000:
            speech_text = speech_text[:4000] + "..."

        if len(speech_text) < 50:
            return None

        # Generate unique filename
        text_hash = hashlib.sha256(speech_text.encode()).hexdigest()[:16]

        # Storage path
        backend_root = Path(__file__).parent.parent.parent
        storage_dir = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))) / 'chapter_theory_tts' / chapter_id[:8]
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = f"theory_{text_hash}_{voice}.mp3"
        file_path = storage_dir / filename

        # Check cache
        from_cache = file_path.exists()

        if not from_cache:
            from app.services.ai_adapter import AIAdapter

            valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
            tts_voice = voice if voice in valid_voices else 'nova'

            audio_bytes = AIAdapter.text_to_speech(
                text=speech_text,
                voice=tts_voice,
                model='tts-1',
                speed=1.0
            )

            with open(file_path, 'wb') as f:
                f.write(audio_bytes)

        # Calculate duration (roughly 150 words/min, 5 chars/word)
        duration_seconds = int((len(speech_text) / 5 / 150) * 60)

        audio_id = f"{text_hash}_{voice}_100"

        return {
            'url': f"/api/v1/tts/audio/{audio_id}?path={str(file_path)}",
            'duration_seconds': duration_seconds,
            'text_length': len(speech_text),
            'from_cache': from_cache
        }

    except Exception as e:
        logger.error(f"Error generating theory audio: {e}", exc_info=True)
        return None
