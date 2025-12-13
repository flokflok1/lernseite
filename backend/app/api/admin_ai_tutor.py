"""
LernsystemX Admin AI Tutor API

Tutor content generation endpoints:
- POST /api/v1/admin/ai/generate-chapter-theory - Generate theory sheet for chapter
- POST /api/v1/admin/ai/generate-lesson-steps - Generate step-by-step lesson explanation

Features:
- Multiple styles: ADHS-freundlich, Ausfuehrlich, Kurz, Pruefungsfokus
- DB-basierte Prompt-Templates (editierbar im KI-Studio)
- Optionale TTS-Generierung fuer Audio-Version

Phase KI-Studio - Tutor Content Generation
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
from app.security.permissions import require_permission, Permissions
from app.repositories.chapter_repository import ChapterRepository


@api_v1.route('/admin/ai/generate-chapter-theory', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_chapter_theory():
    """
    Generate comprehensive theory sheet for a chapter using AI.

    Request Body:
        {
            "chapter_id": "uuid",
            "chapter_title": "IT1: Beschaffung & Kalkulation",
            "course_title": "AP1 Pruefungsvorbereitung",
            "style": "adhs",           // Optional: adhs, detailed, short, exam_focus (default: adhs)
            "generate_tts": false,     // Optional: Generate audio version
            "tts_voice": "alloy"       // Optional: TTS voice (alloy, echo, fable, onyx, nova, shimmer)
        }

    Response 200:
        {
            "success": true,
            "data": {...},
            "style": "adhs",
            "tokens_used": 1234,
            "cost_eur": 0.02,
            "audio": {                 // Only if generate_tts=true
                "url": "...",
                "duration_seconds": 120,
                "cost_eur": 0.01
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        chapter_id = data.get('chapter_id')
        chapter_title = data.get('chapter_title', '')
        course_title = data.get('course_title', '')
        style = data.get('style', 'adhs')  # Default to ADHS-friendly
        generate_tts = data.get('generate_tts', False)
        tts_voice = data.get('tts_voice', 'alloy')

        if not chapter_id or not chapter_title:
            return jsonify({
                'success': False,
                'error': 'chapter_id and chapter_title are required'
            }), 400

        user_id = g.current_user['user_id']
        start_time = time.time()

        # Get chapter info for additional context
        chapter = ChapterRepository.find_by_id(chapter_id) if chapter_id else None
        chapter_description = chapter.get('description', '') if chapter else ''

        # Get lessons in this chapter for context
        from app.repositories.lesson_repository import LessonRepository
        lessons = LessonRepository.find_by_chapter(chapter_id) if chapter_id else []
        lesson_titles = [l.get('title', '') for l in lessons[:10]]

        # Try to get prompt template from DB, fall back to code-based
        prompt_template = None
        template_id = None

        try:
            from app.ki import get_prompt_with_style
            prompt_template = get_prompt_with_style('theory', style)
        except Exception as e:
            logger.debug(f"Could not get prompt template for theory/{style}: {e}")

        # Build context for template
        context = {
            'chapter_title': chapter_title,
            'course_title': course_title,
            'chapter_description': chapter_description,
            'lesson_titles': ', '.join(lesson_titles) if lesson_titles else 'Keine spezifischen Lektionen',
            'target_audience': 'Fachinformatiker Systemintegration (FISI) in Pruefungsvorbereitung'
        }

        # Use template if available
        if prompt_template:
            messages = prompt_template.render(context)
            model = prompt_template.model or 'gpt-4o-mini'
            temperature = prompt_template.temperature or 0.7
            max_tokens = prompt_template.max_tokens or 4000
        else:
            # Fallback to hardcoded prompt based on style
            system_prompt, user_prompt = _get_theory_prompt_for_style(style, context)
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
            model = 'gpt-4o-mini'
            temperature = 0.7
            max_tokens = 4000

        # Use AIAdapter for generation
        from app.services.ai_adapter import AIAdapter

        adapter = AIAdapter(provider='openai', model=model)

        result = adapter.send_messages(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        output_text = result.get('output_text', '{}')

        # Parse JSON response
        theory_data = _parse_json_response(output_text, chapter_title)

        response_time_ms = int((time.time() - start_time) * 1000)

        # Log usage if template was from DB
        if prompt_template and hasattr(prompt_template, 'code'):
            try:
                from app.repositories.prompt_template_repository import PromptTemplateRepository
                db_template = PromptTemplateRepository.find_by_code(prompt_template.code)
                if db_template:
                    template_id = db_template.get('template_id')
                    PromptTemplateRepository.log_usage(
                        template_id=template_id,
                        user_id=user_id,
                        content_type='chapter_theory',
                        content_id=chapter_id,
                        tokens_input=result.get('prompt_tokens'),
                        tokens_output=result.get('completion_tokens'),
                        cost_eur=result.get('cost_eur'),
                        response_time_ms=response_time_ms,
                        context_data=context
                    )
            except Exception as e:
                logger.debug(f"Could not log prompt usage: {e}")

        logger.info(f"Generated chapter theory ({style}) for {chapter_id}, tokens: {result.get('total_tokens', 0)}")

        # Generate TTS if requested
        audio_url = None
        audio_duration = None
        audio_result = None
        if generate_tts:
            audio_result = _generate_theory_tts(theory_data, tts_voice, chapter_id, user_id)
            if audio_result:
                audio_url = audio_result.get('url')
                audio_duration = audio_result.get('duration_seconds')

        # Save to chapter_theory table for caching
        try:
            _save_chapter_theory(
                chapter_id=chapter_id,
                style=style,
                theory_data=theory_data,
                audio_url=audio_url,
                audio_duration=audio_duration,
                tokens_used=result.get('total_tokens', 0),
                model_used=model,
                user_id=user_id
            )
            logger.info(f"Saved chapter theory to DB for {chapter_id}")
        except Exception as save_err:
            logger.warning(f"Could not save chapter theory to DB: {save_err}")

        response = {
            'success': True,
            'data': theory_data,
            'style': style,
            'tokens_used': result.get('total_tokens', 0),
            'cost_eur': result.get('cost_eur', 0),
            'response_time_ms': response_time_ms
        }

        if audio_result:
            response['audio'] = audio_result

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error generating chapter theory: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate chapter theory',
            'message': str(e)
        }), 500


def _get_theory_prompt_for_style(style: str, context: dict) -> tuple:
    """
    Get system and user prompts for a specific style.

    Returns fallback prompts when DB template not available.
    """
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
        system = """Du bist ein erfahrener IHK-Pruefer und IT-Ausbilder fuer Fachinformatiker.
Du kennst die AP1-Pruefung in- und auswendig und weisst genau, was gefragt wird.

Deine Erklaerungen sind ADHS-freundlich:
- KURZ aber VOLLSTAENDIG (alle wichtigen Infos muessen drin sein!)
- VISUELL strukturiert mit Aufzaehlungen und Emojis
- Mit KONKRETEN Zahlenbeispielen aus echten IHK-Pruefungen
- Formeln und Rechenwege IMMER mit Beispielrechnung
- Fachbegriffe IMMER mit einfacher Erklaerung

WICHTIG: Du generierst UMFANGREICHE Inhalte, nicht nur Platzhalter!
- Mindestens 4-6 Konzepte mit echten Beispielen
- Mindestens 5-8 Fachbegriffe mit Definitionen
- Mindestens 4 konkrete Pruefungstipps
- Whiteboard-Animationen mit echten Formeln/Schemas

Antworte NUR mit validem JSON."""

        user = f"""Erstelle ein UMFANGREICHES, ADHS-freundliches Theorieblatt fuer "{chapter_title}".
{base_context}

WICHTIG: Generiere ECHTE, DETAILLIERTE Inhalte - keine Platzhalter!

Fuer das Thema "{chapter_title}" brauchst du:
- Die KOMPLETTEN Formeln mit Beispielrechnungen
- ALLE relevanten Fachbegriffe die in der Pruefung vorkommen
- KONKRETE Zahlenbeispiele (z.B. Listeneinkaufspreis 1000 EUR, Rabatt 10%, etc.)
- Typische IHK-Aufgabenstellungen und wie man sie loest

JSON-Struktur:
{{
    "overview": "2-3 Saetze die das Thema zusammenfassen und erklaeren WARUM es pruefungsrelevant ist",
    "learningGoals": [
        "Konkretes Lernziel 1 (z.B. 'Bezugskalkulation sicher durchrechnen koennen')",
        "Konkretes Lernziel 2",
        "Konkretes Lernziel 3",
        "Konkretes Lernziel 4"
    ],
    "concepts": [
        {{
            "title": "Konzeptname (z.B. 'Bezugskalkulation')",
            "emoji": "passendes Emoji",
            "oneLiner": "Ein Satz der das Konzept erklaert",
            "description": "Ausfuehrlichere Erklaerung (2-3 Saetze) mit dem WIE und WARUM",
            "formula": "Die Formel falls relevant (z.B. 'Bezugspreis = LEP - Rabatt - Skonto + Bezugskosten')",
            "example": "Konkretes Zahlenbeispiel: LEP 1000 EUR - 10% Rabatt = 900 EUR - 2% Skonto = 882 EUR + 50 EUR Fracht = 932 EUR Bezugspreis",
            "tip": "Merkhilfe oder Eselsbruecke"
        }}
    ],
    "terms": [
        {{
            "term": "Fachbegriff",
            "simple": "Einfache Erklaerung in einem Satz",
            "example": "Konkretes Beispiel aus der Praxis",
            "pruefungsrelevanz": "Wie kommt das in der Pruefung vor?"
        }}
    ],
    "examTips": [
        "Konkreter Pruefungstipp 1 (z.B. 'Immer zuerst Rabatt, dann Skonto abziehen!')",
        "Konkreter Pruefungstipp 2",
        "Konkreter Pruefungstipp 3",
        "Konkreter Pruefungstipp 4"
    ],
    "commonMistakes": [
        "Typischer Fehler 1 (z.B. 'Skonto auf Listenpreis statt auf Zieleinkaufspreis berechnen')",
        "Typischer Fehler 2"
    ],
    "summary": "Zusammenfassung in 3-4 Bullet Points mit den wichtigsten Takeaways",
    "whiteboardActions": [
        {{
            "type": "write",
            "content": "Titel oder wichtiger Text",
            "position": {{"x": 50, "y": 10}},
            "duration": 1500,
            "color": "#1f2937",
            "fontSize": 28,
            "speech": "Was der Tutor dazu sagt (1-2 Saetze)"
        }},
        {{
            "type": "schema",
            "position": {{"x": 10, "y": 25}},
            "schema": [
                {{"name": "Listeneinkaufspreis", "operator": "", "value": "1.000,00 EUR", "highlight": false}},
                {{"name": "- Lieferantenrabatt 10%", "operator": "=", "value": "100,00 EUR", "highlight": false}},
                {{"name": "= Zieleinkaufspreis", "operator": "", "value": "900,00 EUR", "highlight": true}},
                {{"name": "- Lieferantenskonto 2%", "operator": "=", "value": "18,00 EUR", "highlight": false}},
                {{"name": "= Bareinkaufspreis", "operator": "", "value": "882,00 EUR", "highlight": true}},
                {{"name": "+ Bezugskosten", "operator": "", "value": "50,00 EUR", "highlight": false}},
                {{"name": "= Bezugspreis", "operator": "", "value": "932,00 EUR", "highlight": true}}
            ],
            "duration": 4000,
            "speech": "Das ist das Schema der Bezugskalkulation. Wir starten mit dem Listeneinkaufspreis..."
        }},
        {{
            "type": "highlight",
            "content": "Wichtiger Merksatz oder Begriff",
            "position": {{"x": 50, "y": 80}},
            "duration": 1000,
            "color": "#fbbf24",
            "speech": "Das musst du dir unbedingt merken!"
        }}
    ]
}}

GENERIERE MINDESTENS:
- 4-6 concepts mit echten Formeln und Zahlenbeispielen
- 5-8 terms mit Definitionen und Pruefungsrelevanz
- 4-6 examTips die wirklich helfen
- 2-3 commonMistakes
- 6-10 whiteboardActions die das Schema Schritt fuer Schritt aufbauen"""

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
            'overview': f'<p>Uebersicht fuer {chapter_title}</p>',
            'learningGoals': ['Die Grundlagen verstehen', 'Anwendung in der Praxis'],
            'concepts': [{'title': chapter_title, 'description': 'Kerninhalt des Kapitels'}],
            'terms': [],
            'examRelevance': '<p>Pruefungsrelevant fuer IHK AP1</p>'
        }


def _save_chapter_theory(
    chapter_id: str,
    style: str,
    theory_data: dict,
    audio_url: str = None,
    audio_duration: int = None,
    tokens_used: int = 0,
    model_used: str = None,
    user_id: str = None
) -> dict:
    """Save chapter theory to database for caching."""
    from app.repositories.base_repository import BaseRepository

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


def _generate_theory_tts(theory_data: dict, voice: str, chapter_id: str, user_id: str) -> dict:
    """
    Generate TTS audio for the theory sheet.

    Converts the theory content to speech-friendly text and generates audio.
    Uses OpenAI TTS-1 for high-quality German speech synthesis.
    """
    import re
    import hashlib
    from pathlib import Path
    import os

    try:
        # Build speech text from theory data
        speech_parts = []

        if theory_data.get('overview'):
            # Strip HTML tags for TTS
            overview = re.sub('<[^<]+?>', '', theory_data['overview'])
            speech_parts.append(f"Uebersicht. {overview}")

        if theory_data.get('learningGoals'):
            goals = theory_data['learningGoals'][:5]  # Limit to 5
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

        speech_text = " ... ".join(speech_parts)  # Add pauses between sections

        # Preprocess for better German TTS (compound words)
        speech_text = _preprocess_tts_text(speech_text)

        # Limit text length (OpenAI max ~4096 chars)
        if len(speech_text) > 4000:
            speech_text = speech_text[:4000] + "..."

        # Generate unique filename based on content
        text_hash = hashlib.sha256(speech_text.encode()).hexdigest()[:16]

        # Storage path
        backend_root = Path(__file__).parent.parent.parent
        storage_dir = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))) / 'theory_tts' / chapter_id[:8]
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = f"theory_{text_hash}_{voice}.mp3"
        file_path = storage_dir / filename

        # Check if already cached
        from_cache = file_path.exists()

        if not from_cache:
            # Generate TTS using AIAdapter
            from app.services.ai_adapter import AIAdapter

            logger.info(f"Generating TTS for chapter {chapter_id}, {len(speech_text)} chars, voice={voice}")

            # Validate voice
            valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
            tts_voice = voice if voice in valid_voices else 'nova'

            audio_bytes = AIAdapter.text_to_speech(
                text=speech_text,
                voice=tts_voice,
                model='tts-1',  # Use tts-1-hd for higher quality
                speed=1.0
            )

            # Save to file
            with open(file_path, 'wb') as f:
                f.write(audio_bytes)

            logger.info(f"TTS saved to {file_path}")

        # Calculate estimated duration (roughly 150 words/min, 5 chars/word)
        duration_seconds = int((len(speech_text) / 5 / 150) * 60)

        # Calculate cost (tts-1: $0.015 per 1K chars)
        cost_eur = (len(speech_text) / 1000) * 0.015 * 0.92  # USD to EUR

        # Audio URL for retrieval
        audio_id = f"{text_hash}_{voice}_100"
        audio_url = f"/api/v1/tts/audio/{audio_id}?path={str(file_path)}"

        return {
            'url': audio_url,
            'file_path': str(file_path),
            'duration_seconds': duration_seconds,
            'text_length': len(speech_text),
            'voice': voice,
            'from_cache': from_cache,
            'cost_eur': round(cost_eur, 4) if not from_cache else 0
        }

    except Exception as e:
        logger.error(f"Error generating TTS: {e}", exc_info=True)
        return {
            'error': str(e),
            'status': 'failed'
        }


def _preprocess_tts_text(text: str) -> str:
    """
    Preprocess text for better German TTS pronunciation.

    - Splits compound words for clearer pronunciation
    - Converts abbreviations
    - Adds pauses at sentence boundaries
    """
    import re

    # German compound word replacements for clearer TTS
    replacements = {
        # Business/Calculation terms
        'Listeneinkaufspreis': 'Listen Einkaufs Preis',
        'Zieleinkaufspreis': 'Ziel Einkaufs Preis',
        'Bareinkaufspreis': 'Bar Einkaufs Preis',
        'Bezugskalkulation': 'Bezugs Kalkulation',
        'Handelskalkulation': 'Handels Kalkulation',
        'Verkaufspreis': 'Verkaufs Preis',
        'Selbstkostenpreis': 'Selbstkosten Preis',
        'Bezugskosten': 'Bezugs Kosten',
        'Lieferantenrabatt': 'Lieferanten Rabatt',
        'Handlungskosten': 'Handlungs Kosten',
        'Gewinnzuschlag': 'Gewinn Zuschlag',
        'Mehrwertsteuer': 'Mehrwert Steuer',
        # IT terms
        'Systemintegration': 'System Integration',
        'Fachinformatiker': 'Fach Informatiker',
        'Netzwerktechnik': 'Netzwerk Technik',
        'Datenbank': 'Daten Bank',
        'Betriebssystem': 'Betriebs System',
        'Anwendungsentwicklung': 'Anwendungs Entwicklung',
        # Common abbreviations
        'z.B.': 'zum Beispiel',
        'd.h.': 'das heisst',
        'bzw.': 'beziehungsweise',
        'ca.': 'zirka',
        'inkl.': 'inklusive',
        'exkl.': 'exklusive',
        'zzgl.': 'zuzueglich',
        'LEP': 'Listen Einkaufs Preis',
        'ZEP': 'Ziel Einkaufs Preis',
        'BEP': 'Bar Einkaufs Preis',
        'VKP': 'Verkaufs Preis',
        'MwSt': 'Mehrwert Steuer',
        # Symbols
        '€': ' Euro ',
        '%': ' Prozent ',
        '×': ' mal ',
        '÷': ' geteilt durch ',
        '+': ' plus ',
        '−': ' minus ',
        '=': ' gleich ',
    }

    processed = text

    # Apply word replacements (case-insensitive for longer words)
    for original, replacement in replacements.items():
        if len(original) > 3:
            pattern = re.compile(r'\b' + re.escape(original) + r'\b', re.IGNORECASE)
            processed = pattern.sub(replacement, processed)
        else:
            processed = processed.replace(original, replacement)

    # Number with decimals: "35.67" -> "35 Komma 67"
    processed = re.sub(r'(\d+)[.,](\d+)', r'\1 Komma \2', processed)

    # Clean up multiple spaces
    processed = re.sub(r'\s+', ' ', processed).strip()

    return processed


@api_v1.route('/admin/ai/generate-lesson-steps', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_lesson_steps():
    """
    Generate step-by-step explanation for a lesson using AI.

    Request Body:
        {
            "lesson_id": "uuid",
            "lesson_title": "Bezugskalkulation: Das Muster",
            "lm_type": "LM12",
            "chapter_title": "IT1: Beschaffung & Kalkulation",
            "style": "adhs",           // Optional: adhs, detailed, short, exam_focus (default: adhs)
            "generate_tts": false,     // Optional: Generate audio version
            "tts_voice": "nova"        // Optional: TTS voice
        }

    Response 200:
        {
            "success": true,
            "data": {
                "steps": [...]
            },
            "style": "adhs",
            "tokens_used": 1234,
            "audio": {...}  // Only if generate_tts=true
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        lesson_id = data.get('lesson_id')
        lesson_title = data.get('lesson_title', '')
        lm_type = data.get('lm_type', 'LM00')
        chapter_title = data.get('chapter_title', '')
        style = data.get('style', 'adhs')
        generate_tts = data.get('generate_tts', False)
        tts_voice = data.get('tts_voice', 'nova')

        if not lesson_id or not lesson_title:
            return jsonify({
                'success': False,
                'error': 'lesson_id and lesson_title are required'
            }), 400

        user_id = g.current_user['user_id']

        # Get style-specific instructions
        style_instructions = _get_lesson_style_instructions(style)

        # Build prompt for AI
        include_whiteboard = style == 'adhs'

        whiteboard_schema = ""
        if include_whiteboard:
            whiteboard_schema = """,
            "whiteboardActions": [
                {{
                    "type": "write",
                    "content": "Text auf Whiteboard",
                    "position": {{"x": 50, "y": 20}},
                    "duration": 1000,
                    "fontSize": 20,
                    "color": "#1f2937"
                }},
                {{
                    "type": "schema",
                    "schema": [
                        {{"name": "Zeile", "operator": "=", "value": "Wert", "highlight": true}}
                    ],
                    "duration": 1500
                }}
            ]"""

        prompt = f"""Erstelle eine Schritt-fuer-Schritt Erklaerung fuer die Lektion "{lesson_title}" (Typ: {lm_type}).

Kontext:
- Lektion: {lesson_title}
- Lernmethode: {lm_type}
- Kapitel: {chapter_title}
- Zielgruppe: Fachinformatiker Systemintegration (FISI) in Pruefungsvorbereitung
- Stil: {style_instructions['name']}

{style_instructions['instructions']}

Erstelle ein JSON-Objekt mit folgender Struktur:
{{
    "steps": [
        {{
            "title": "Kurzer Titel des Schritts",
            "speech": "Was der Tutor erklaert (freundlich, motivierend, einfach)",
            "calculator": "Optionale Taschenrechner-Eingabe falls relevant (z.B. '960 × 80,14')",
            "result": "Optionales Ergebnis (z.B. '76.934,40 Euro')",
            "schema": [
                {{
                    "name": "Bezeichnung der Zeile",
                    "operator": "Operator (+, -, =, x)",
                    "value": "Wert",
                    "highlight": false
                }}
            ]{whiteboard_schema}
        }}
    ]
}}

Wichtig:
{style_instructions['rules']}
"""

        # Use AIAdapter for generation
        from app.services.ai_adapter import AIAdapter

        adapter = AIAdapter(provider='openai', model='gpt-4o-mini')

        messages = [
            {'role': 'system', 'content': style_instructions['system_prompt']},
            {'role': 'user', 'content': prompt}
        ]

        result = adapter.send_messages(
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )

        output_text = result.get('output_text', '{}')

        # Parse JSON response
        steps_data = _parse_json_response(output_text, lesson_title)

        # Ensure steps key exists
        if 'steps' not in steps_data:
            steps_data = {
                'steps': [
                    {
                        'title': 'Einfuehrung',
                        'speech': f'Lass uns gemeinsam {lesson_title} durchgehen!',
                        'schema': []
                    }
                ]
            }

        logger.info(f"Generated lesson steps ({style}) for {lesson_id}, tokens: {result.get('total_tokens', 0)}")

        response = {
            'success': True,
            'data': steps_data,
            'style': style,
            'tokens_used': result.get('total_tokens', 0),
            'cost_eur': result.get('cost_eur', 0)
        }

        # Generate TTS for each step if requested
        if generate_tts and steps_data.get('steps'):
            audio_results = _generate_steps_tts(steps_data['steps'], tts_voice, lesson_id, user_id)
            if audio_results:
                response['audio'] = audio_results

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error generating lesson steps: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate lesson steps',
            'message': str(e)
        }), 500


def _get_lesson_style_instructions(style: str) -> dict:
    """Get style-specific instructions for lesson generation."""

    styles = {
        'adhs': {
            'name': 'ADHS-freundlich (kurz, visuell, Schritt fuer Schritt)',
            'system_prompt': 'Du bist ein freundlicher, geduldiger Tutor fuer Fachinformatiker. Erklaere Schritt fuer Schritt in einfacher Sprache. Du erstellst auch Whiteboard-Animationen. Antworte NUR mit validem JSON.',
            'instructions': 'Erstelle KURZE, VISUELLE Erklaerungen. Jeder Schritt maximal 2-3 Saetze. JEDER Schritt hat auch whiteboardActions fuer visuelle Animation!',
            'rules': '''- 5-8 kurze Schritte
- Jeder Schritt maximal 2-3 Saetze
- "speech" sollte wie ein freundlicher Tutor klingen
- Einfache Sprache, keine Fachbegriffe ohne Erklaerung
- JEDER Schritt hat "whiteboardActions" Array mit 1-3 Animationen:
  * type: "write" (Text schreiben), "schema" (Tabelle/Schema), "arrow" (Pfeil), "highlight" (hervorheben)
  * position: {x: 0-100, y: 0-100} in Prozent
  * duration: ms fuer Animation
  * content: Text oder bei schema ein Array von Zeilen
- Baue das Whiteboard Schritt fuer Schritt auf'''
        },
        'detailed': {
            'name': 'Ausfuehrlich (mit Hintergrund und Details)',
            'system_prompt': 'Du bist ein erfahrener IT-Ausbilder mit akademischem Hintergrund. Erklaere gruendlich und vollstaendig. Antworte NUR mit validem JSON.',
            'instructions': 'Erstelle AUSFUEHRLICHE Erklaerungen mit Hintergrundwissen.',
            'rules': '''- 8-12 detaillierte Schritte
- Jeder Schritt mit Erklaerung WARUM
- Hintergrundwissen einbauen
- Formeln und Zusammenhaenge erklaeren
- Pruefungsrelevante Details hervorheben'''
        },
        'short': {
            'name': 'Kurz & Kompakt (Essentials only)',
            'system_prompt': 'Du bist ein effizienter Tutor. Nur das Wichtigste, keine Umschweife. Antworte NUR mit validem JSON.',
            'instructions': 'Erstelle MINIMALE Erklaerungen. Nur das Wesentliche.',
            'rules': '''- 4-6 kompakte Schritte
- Jeder Schritt maximal 1-2 Saetze
- Nur die wichtigsten Punkte
- Keine Wiederholungen
- Formeln ohne lange Erklaerung'''
        },
        'exam_focus': {
            'name': 'Pruefungsfokus (IHK AP1)',
            'system_prompt': 'Du bist ein IHK-Pruefer und kennst die AP1-Pruefung genau. Fokussiere auf pruefungsrelevante Aspekte. Antworte NUR mit validem JSON.',
            'instructions': 'Erstelle PRUEFUNGSORIENTIERTE Erklaerungen. Was kommt in der Pruefung dran?',
            'rules': '''- 6-8 pruefungsrelevante Schritte
- Typische Pruefungsfragen ansprechen
- Haeufige Fehler warnen
- Punkteverteilung erwaehnen
- Zeitmanagement-Tipps'''
        },
        'standard': {
            'name': 'Standard',
            'system_prompt': 'Du bist ein freundlicher Tutor fuer Fachinformatiker. Erklaere verstaendlich. Antworte NUR mit validem JSON.',
            'instructions': 'Erstelle ausgewogene Erklaerungen.',
            'rules': '''- 5-8 Schritte
- Verstaendliche Erklaerungen
- Praktische Beispiele
- Schema schrittweise aufbauen'''
        }
    }

    return styles.get(style, styles['standard'])


def _generate_steps_tts(steps: list, voice: str, lesson_id: str, user_id: str) -> dict:
    """Generate TTS audio for lesson steps."""
    import hashlib
    from pathlib import Path
    import os

    try:
        from app.services.ai_adapter import AIAdapter

        # Validate voice
        valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
        tts_voice = voice if voice in valid_voices else 'nova'

        backend_root = Path(__file__).parent.parent.parent
        storage_dir = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))) / 'lesson_tts' / lesson_id[:8]
        storage_dir.mkdir(parents=True, exist_ok=True)

        audio_files = []
        total_duration = 0

        for idx, step in enumerate(steps):
            speech_text = step.get('speech', '')
            if not speech_text:
                continue

            # Preprocess for TTS
            speech_text = _preprocess_tts_text(speech_text)

            # Generate unique filename
            text_hash = hashlib.sha256(speech_text.encode()).hexdigest()[:12]
            filename = f"step_{idx}_{text_hash}_{voice}.mp3"
            file_path = storage_dir / filename

            # Check cache
            if not file_path.exists():
                audio_bytes = AIAdapter.text_to_speech(
                    text=speech_text,
                    voice=tts_voice,
                    model='tts-1',
                    speed=1.0
                )
                with open(file_path, 'wb') as f:
                    f.write(audio_bytes)

            # Estimate duration
            duration = int((len(speech_text) / 5 / 150) * 60)
            total_duration += duration

            audio_files.append({
                'step_index': idx,
                'url': f"/api/v1/tts/audio/{text_hash}_{voice}_100?path={str(file_path)}",
                'duration_seconds': duration
            })

        return {
            'files': audio_files,
            'total_duration_seconds': total_duration,
            'voice': voice,
            'count': len(audio_files)
        }

    except Exception as e:
        logger.error(f"Error generating steps TTS: {e}")
        return None
