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
from app.database.connection import fetch_one, fetch_all, execute_query


# ============================================================================
# Repository Functions
# ============================================================================

def get_chapter_theory(chapter_id: str, style: str = 'adhs') -> dict | None:
    """Get chapter theory from database (legacy - gets first match)."""
    query = """
        SELECT
            theory_id, chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by,
            created_at, updated_at
        FROM chapter_theory
        WHERE chapter_id = %s AND style = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    return fetch_one(query, (chapter_id, style))


def get_chapter_theory_by_id(theory_id: str) -> dict | None:
    """Get chapter theory by ID."""
    query = """
        SELECT
            theory_id, chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by,
            created_at, updated_at
        FROM chapter_theory
        WHERE theory_id = %s
    """
    return fetch_one(query, (theory_id,))


def list_chapter_theories(chapter_id: str) -> list:
    """List all theories for a chapter."""
    query = """
        SELECT
            theory_id, chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by,
            created_at, updated_at
        FROM chapter_theory
        WHERE chapter_id = %s
        ORDER BY created_at DESC
    """
    return fetch_all(query, (chapter_id,)) or []


def save_chapter_theory(
    chapter_id: str,
    style: str,
    theory_data: dict,
    title: str | None = None,
    audio_url: str | None = None,
    audio_duration: int | None = None,
    tokens_used: int = 0,
    model_used: str = None,
    user_id: str = None
) -> dict:
    """Create new chapter theory (always creates new, no upsert)."""
    # Generate default title if not provided
    if not title:
        from datetime import datetime
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
        style_names = {
            'adhs': 'ADHS-freundlich',
            'detailed': 'Ausführlich',
            'short': 'Kurz & Kompakt',
            'exam_focus': 'Prüfungsfokus',
            'standard': 'Standard'
        }
        style_name = style_names.get(style, style)
        title = f"{style_name} ({timestamp})"

    query = """
        INSERT INTO chapter_theory (
            chapter_id, style, title, theory_data,
            audio_url, audio_duration_seconds,
            tokens_used, model_used, generated_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING theory_id, chapter_id, style, title, created_at, updated_at
    """
    result = fetch_one(query, (
        chapter_id, style, title, json.dumps(theory_data),
        audio_url, audio_duration,
        tokens_used, model_used, user_id
    ))
    logger.info(f"Created chapter theory: {result}")
    return result


def update_chapter_theory_title(theory_id: str, title: str) -> dict | None:
    """Update the title of a chapter theory."""
    query = """
        UPDATE chapter_theory
        SET title = %s, updated_at = NOW()
        WHERE theory_id = %s
        RETURNING theory_id, title, updated_at
    """
    return fetch_one(query, (title, theory_id))


def delete_chapter_theory_by_id(theory_id: str) -> bool:
    """Delete a specific chapter theory by ID."""
    query = """
        DELETE FROM chapter_theory
        WHERE theory_id = %s
        RETURNING theory_id
    """
    result = fetch_one(query, (theory_id,))
    return result is not None


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
    return fetch_one(query, (chapter_id,))


def get_chapter_lessons(chapter_id: str) -> list:
    """Get lessons in chapter for context."""
    query = """
        SELECT lesson_id, title, order_index
        FROM lessons
        WHERE chapter_id = %s
        ORDER BY order_index
        LIMIT 15
    """
    return fetch_all(query, (chapter_id,)) or []


# ============================================================================
# API Endpoints
# ============================================================================

@api_v1.route('/chapters/<chapter_id>/theories', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def list_theories(chapter_id: str):
    """
    List all theories for a chapter.

    Response 200:
        {
            "success": true,
            "data": {
                "theories": [
                    {
                        "theoryId": "uuid",
                        "title": "ADHS-freundlich (15.12.2025)",
                        "style": "adhs",
                        "createdAt": "...",
                        "hasAudio": true
                    },
                    ...
                ],
                "count": 3
            }
        }
    """
    try:
        theories = list_chapter_theories(chapter_id)

        theory_list = []
        for t in theories:
            theory_list.append({
                'theoryId': str(t.get('theory_id')),
                'title': t.get('title') or f"Theorieblatt ({t.get('style', 'standard')})",
                'style': t.get('style'),
                'hasAudio': bool(t.get('audio_url')),
                'tokensUsed': t.get('tokens_used', 0),
                'createdAt': t.get('created_at').isoformat() if t.get('created_at') else None,
                'updatedAt': t.get('updated_at').isoformat() if t.get('updated_at') else None
            })

        return jsonify({
            'success': True,
            'data': {
                'theories': theory_list,
                'count': len(theory_list)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing chapter theories: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list theories',
            'message': str(e)
        }), 500


@api_v1.route('/chapters/<chapter_id>/theory', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def get_theory(chapter_id: str):
    """
    Get chapter theory (cached from DB).
    Returns the most recent theory, optionally filtered by style.

    Query params:
        style: Theory style (adhs, detailed, short, exam_focus, standard)
        theory_id: Specific theory ID to fetch

    Response 200:
        {
            "success": true,
            "data": {
                "hasTheory": true,
                "theoryId": "uuid",
                "title": "...",
                "theory": {...},
                "audioUrl": "...",
                "style": "adhs",
                "createdAt": "..."
            }
        }
    """
    try:
        theory_id = request.args.get('theory_id')
        style = request.args.get('style', 'adhs')

        # If specific theory_id requested, get that one
        if theory_id:
            theory_record = get_chapter_theory_by_id(theory_id)
        else:
            # Validate style
            valid_styles = ['adhs', 'detailed', 'short', 'exam_focus', 'standard']
            if style not in valid_styles:
                style = 'adhs'

            # Get from database - try requested style first
            theory_record = get_chapter_theory(chapter_id, style)

            # Fallback: if no theory for requested style, try to find ANY available theory
            if not theory_record:
                fallback_query = """
                    SELECT
                        theory_id, chapter_id, style, title, theory_data,
                        audio_url, audio_duration_seconds,
                        tokens_used, model_used, generated_by,
                        created_at, updated_at
                    FROM chapter_theory
                    WHERE chapter_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                theory_record = fetch_one(fallback_query, (chapter_id,))
                if theory_record:
                    logger.info(f"Using fallback theory with style={theory_record.get('style')} for chapter {chapter_id}")

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

        # Return actual style from record (might be different from requested if fallback was used)
        actual_style = theory_record.get('style', style)

        return jsonify({
            'success': True,
            'data': {
                'hasTheory': True,
                'theoryId': str(theory_record.get('theory_id')),
                'title': theory_record.get('title') or f"Theorieblatt ({actual_style})",
                'theory': theory_data,
                'audioUrl': theory_record.get('audio_url'),
                'audioDuration': theory_record.get('audio_duration_seconds'),
                'style': actual_style,
                'requestedStyle': style,  # What was requested
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


@api_v1.route('/chapter-theory/<theory_id>', methods=['GET'])
@token_required
def get_theory_by_id(theory_id: str):
    """Get a specific theory by ID."""
    try:
        theory_record = get_chapter_theory_by_id(theory_id)

        if not theory_record:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

        # Parse theory_data from JSONB
        theory_data = theory_record.get('theory_data', {})
        if isinstance(theory_data, str):
            theory_data = json.loads(theory_data)

        return jsonify({
            'success': True,
            'data': {
                'theoryId': str(theory_record.get('theory_id')),
                'chapterId': str(theory_record.get('chapter_id')),
                'title': theory_record.get('title'),
                'style': theory_record.get('style'),
                'theory': theory_data,
                'audioUrl': theory_record.get('audio_url'),
                'audioDuration': theory_record.get('audio_duration_seconds'),
                'createdAt': theory_record.get('created_at').isoformat() if theory_record.get('created_at') else None,
                'tokensUsed': theory_record.get('tokens_used', 0)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting theory by ID: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get theory',
            'message': str(e)
        }), 500


@api_v1.route('/chapter-theory/<theory_id>', methods=['PATCH'])
@token_required
def update_theory(theory_id: str):
    """Update theory title."""
    try:
        data = request.get_json() or {}
        title = data.get('title')

        if not title:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400

        result = update_chapter_theory_title(theory_id, title)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'theoryId': str(result.get('theory_id')),
                'title': result.get('title'),
                'updatedAt': result.get('updated_at').isoformat() if result.get('updated_at') else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Error updating theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update theory',
            'message': str(e)
        }), 500


@api_v1.route('/chapter-theory/<theory_id>', methods=['DELETE'])
@token_required
def delete_theory_by_id_endpoint(theory_id: str):
    """Delete a specific theory by ID."""
    try:
        deleted = delete_chapter_theory_by_id(theory_id)

        if not deleted:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Theory deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete theory',
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


@api_v1.route('/chapters/<chapter_id>/theory', methods=['DELETE'])
@token_required
def delete_theory(chapter_id: str):
    """
    Delete chapter theory from database.

    Query params:
        style: Theory style (adhs, detailed, short, exam_focus, standard)
               If not specified, deletes ALL theories for this chapter

    Response 200:
        {
            "success": true,
            "message": "Theory deleted"
        }
    """
    try:
        style = request.args.get('style')

        if style:
            # Delete specific style
            query = """
                DELETE FROM chapter_theory
                WHERE chapter_id = %s AND style = %s
                RETURNING theory_id
            """
            result = fetch_one(query, (chapter_id, style))
        else:
            # Delete all theories for this chapter
            query = """
                DELETE FROM chapter_theory
                WHERE chapter_id = %s
                RETURNING theory_id
            """
            result = fetch_one(query, (chapter_id,))

        if result:
            logger.info(f"Deleted chapter theory for {chapter_id} (style={style})")
            return jsonify({
                'success': True,
                'message': f'Theory deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Theory not found'
            }), 404

    except Exception as e:
        logger.error(f"Error deleting chapter theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete theory',
            'message': str(e)
        }), 500


@api_v1.route('/chapter-theory/<chapter_id>/audio', methods=['GET'])
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
    from flask import send_file
    from pathlib import Path
    import os

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

        # If no audio URL, generate it
        if not audio_url:
            return jsonify({
                'success': False,
                'error': 'No audio available for this theory'
            }), 404

        # Find audio file in storage
        backend_root = Path(__file__).parent.parent.parent
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


def _generate_theory_audio(theory_data: dict, voice: str, chapter_id: str, user_id: str) -> dict | None:
    """Generate TTS audio for theory content using OpenAI TTS."""
    import re
    import hashlib
    from pathlib import Path
    import os

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
        backend_root = Path(__file__).parent.parent.parent
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
