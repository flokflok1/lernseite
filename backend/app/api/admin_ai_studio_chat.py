"""
LernsystemX Admin AI Studio - Chat Interface API

Chat and learning method generation endpoints:
- POST   /api/v1/admin/ai-studio/chat        - Chat with AI for content creation
- POST   /api/v1/admin/ai-studio/generate-lm - Generate learning method content

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
Module split according to 35_Developer-Guide-KI-Prompts.md guidelines
"""

from flask import request, jsonify, g
import logging
import json

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.repositories.ai_studio_repository import AIStudioRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.chapter_repository import ChapterRepository
from app.repositories.lm_slot_repository import LMSlotResolverRepository
from app.services.ai_studio_service import (
    AiStudioService,
    AiStudioServiceError
)
from app.security.permissions import require_permission, Permissions

# Import helper functions
from app.api.admin_ai_studio_utils import (
    build_chat_context,
    analyze_chat_intent,
    get_info_response,
    get_fallback_response,
    generate_chat_actions
)


# ============================================================================
# Chat Interface
# ============================================================================

@api_v1.route('/admin/ai-studio/chat', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def ai_studio_chat():
    """
    Chat with AI for content creation assistance

    Request Body:
        {
            "message": "Erstelle ein Kapitel ueber Python Grundlagen",
            "course_id": "uuid",
            "context": {
                "mode": "new_chapters" | "edit_existing",
                "chapter_id": "uuid" (optional),
                "file_ids": ["uuid", ...],
                "session_id": "uuid" (optional)
            }
        }

    Response 200:
        {
            "success": true,
            "response": {
                "content": "AI response text...",
                "actions": [
                    {"id": "action1", "type": "primary", "label": "Create", "action": "create_chapter"}
                ],
                "data": {...} (optional structured data)
            },
            "tokens_used": 1234,
            "cost_eur": 0.02
        }
    """
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400

        user_id = g.current_user['user_id']
        message = data.get('message', '').strip()
        course_id = data.get('course_id')
        context = data.get('context', {})

        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400

        # Build context for AI
        ai_context = build_chat_context(user_id, course_id, context)

        # Check if this is a simple question or action request
        intent = analyze_chat_intent(message)

        if intent['type'] == 'info':
            # Return helpful information without AI call
            response = get_info_response(intent['topic'], ai_context)
            return jsonify({
                'success': True,
                'response': response,
                'tokens_used': 0,
                'cost_eur': 0
            }), 200

        # For generation requests, use AI
        try:
            service = AiStudioService()

            # Build prompt based on intent
            prompt_context = {
                'user_message': message,
                'course_title': ai_context.get('course_title', 'Unbekannter Kurs'),
                'chapter_title': ai_context.get('chapter_title', ''),
                'selected_files': json.dumps(ai_context.get('files', [])),
                'existing_chapters': json.dumps(ai_context.get('chapters', [])),
                'mode': context.get('mode', 'new_chapters'),
                'target_language': 'de'
            }

            # Use a chat-specific prompt or fallback to generic
            result = service.generate_for_step(
                step='theory',  # Use theory step for general chat
                session_id=context.get('session_id', f'chat-{user_id}'),
                context=prompt_context,
                user_id=user_id
            )

            # Parse response
            ai_text = result.get('output_text', '')

            # Extract structured data if present
            response_data = None
            try:
                if ai_text.strip().startswith('{'):
                    response_data = json.loads(ai_text)
                    ai_text = response_data.get('message', ai_text)
            except json.JSONDecodeError:
                pass

            # Generate action buttons based on content
            actions = generate_chat_actions(message, ai_text, ai_context)

            return jsonify({
                'success': True,
                'response': {
                    'content': ai_text,
                    'actions': actions,
                    'data': response_data
                },
                'tokens_used': result.get('total_tokens', 0),
                'cost_eur': result.get('cost_eur', 0)
            }), 200

        except AiStudioServiceError as e:
            logger.error(f"AI Studio chat error: {str(e)}")
            # Return a helpful fallback response
            return jsonify({
                'success': True,
                'response': {
                    'content': get_fallback_response(message, ai_context),
                    'actions': generate_chat_actions(message, '', ai_context)
                },
                'tokens_used': 0,
                'cost_eur': 0,
                'note': 'Fallback response due to AI service unavailability'
            }), 200

    except Exception as e:
        logger.error(f"Error in AI Studio chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Chat failed',
            'message': str(e)
        }), 500


# ============================================================================
# Learning Method Content Generation
# ============================================================================

@api_v1.route('/admin/ai-studio/generate-lm', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("20 per minute")
def generate_learning_method_content():
    """
    Generate learning method content for a lesson

    Used by batch generation to create content for individual lessons.

    Request Body:
        {
            "lesson_id": "uuid",
            "lm_type": "LM12",
            "topic": "Bezugskalkulation",
            "course_id": "uuid",
            "chapter_id": "uuid",
            "context": {
                "pruefungs_relevanz": "SEHR HOCH",
                "dauer_min": 10
            }
        }

    Response 200:
        {
            "success": true,
            "lesson_id": "uuid",
            "lm_type": "LM12",
            "content_generated": true,
            "tokens_used": 500,
            "cost_eur": 0.01
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
        lm_type = data.get('lm_type', 'LM00')
        topic = data.get('topic', '')
        course_id = data.get('course_id')
        chapter_id = data.get('chapter_id')
        context = data.get('context', {})

        if not lesson_id:
            return jsonify({
                'success': False,
                'error': 'lesson_id is required'
            }), 400

        user_id = g.current_user['user_id']

        # Verify lesson exists
        from app.repositories.lesson_repository import LessonRepository
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Build context for generation - include all required variables
        generation_context = {
            'lesson_id': lesson_id,
            'lesson_title': lesson.get('title', topic),
            'lm_type': lm_type,
            'topic': topic,
            'pruefungs_relevanz': context.get('pruefungs_relevanz', 'mittel'),
            'dauer_min': str(context.get('dauer_min', 10)),
            'target_language': 'de',
            # Required by AI Studio prompts
            'target_audience': 'Fachinformatiker Systemintegration (FISI) in Pruefungsvorbereitung',
            'difficulty': 'IHK-Pruefungsniveau',
            'lessons': json.dumps([{'title': lesson.get('title', topic), 'topic': topic}]),
            'method_preferences': json.dumps([lm_type]),
            'learning_objectives': json.dumps([f'Verstaendnis von {topic}', f'Anwendung in IHK-Pruefung']),
            'pdf_analysis': json.dumps({'topics': [topic], 'key_concepts': [topic]}),
            'selected_theory_variant': json.dumps({'title': topic, 'content': ''})
        }

        # Get course info for context
        if course_id:
            course = CourseRepository.find_by_id(course_id)
            if course:
                generation_context['course_title'] = course.get('title', '')

        # Get chapter info for context
        if chapter_id:
            chapter = ChapterRepository.find_by_id(chapter_id)
            if chapter:
                generation_context['chapter_title'] = chapter.get('title', '')

        # Use AI Studio Service for generation
        try:
            # Extract LM number from type (e.g., "LM12" -> 12)
            lm_number = int(lm_type.replace('LM', '')) if lm_type.startswith('LM') else 0

            # Use Capability Slots System to get the configured model for 'chat' slot
            # This supports multiple models per LM (chat, tts, stt, realtime, etc.)
            chat_slot = LMSlotResolverRepository.resolve_slot(
                learning_method_id=lm_number,
                slot_code='chat',
                chapter_id=chapter_id,
                course_id=course_id
            )

            # Get provider and model from slot assignment, with fallback
            # Note: provider_name must be lowercase (openai, not OpenAI)
            if chat_slot and chat_slot.get('is_configured'):
                provider_name = chat_slot.get('provider_name', 'openai').lower()
                model_name = chat_slot.get('model_name', 'gpt-4o-mini')
            else:
                # Fallback if no slot assignment exists
                provider_name = 'openai'
                model_name = 'gpt-4o-mini'
                logger.warning(f"No chat slot configured for LM{lm_number}, using fallback: {provider_name}/{model_name}")

            logger.info(f"Capability Slots resolved for LM{lm_number} (chat): provider={provider_name}, model={model_name}")

            # Use AIAdapter directly for batch generation (no session tracking required)
            from app.services.ai_adapter import AIAdapter

            adapter = AIAdapter(provider=provider_name, model=model_name)

            # Build prompt based on LM type
            lm_prompts = _get_lm_prompts(topic)
            prompt = lm_prompts.get(lm_type, f"""Erstelle Lerninhalt zum Thema "{topic}" fuer Lernmethode {lm_type}.
Zielgruppe: Fachinformatiker Systemintegration (FISI) in Pruefungsvorbereitung.
Sprache: Deutsch. IHK-Pruefungsniveau.""")

            messages = [
                {'role': 'system', 'content': 'Du bist ein erfahrener IT-Ausbilder fuer Fachinformatiker. Erstelle pruefungsrelevante Lerninhalte.'},
                {'role': 'user', 'content': prompt}
            ]

            result = adapter.send_messages(
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )

            # Log the generation
            logger.info(f"Generated {lm_type} content for lesson {lesson_id} using {provider_name}/{model_name}")

            # Save generated content to learning_methods table
            output_text = result.get('output_text', '')

            # Try to parse as JSON, otherwise store as raw text
            try:
                parsed_data = json.loads(output_text)
            except json.JSONDecodeError:
                parsed_data = {'raw_content': output_text}

            from app.extensions import db_pool
            from psycopg.rows import dict_row
            import psycopg

            with db_pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    # Check if method already exists for this lesson
                    cur.execute("""
                        SELECT method_id FROM learning_methods
                        WHERE lesson_id = %s AND method_type = %s
                    """, (lesson_id, lm_number))
                    existing = cur.fetchone()

                    if existing:
                        # Update existing method
                        cur.execute("""
                            UPDATE learning_methods SET
                                data = %s,
                                instructions = %s,
                                title = %s,
                                updated_at = NOW()
                            WHERE method_id = %s
                            RETURNING method_id
                        """, (
                            psycopg.types.json.Jsonb(parsed_data),
                            prompt,
                            f"{lm_type}: {topic}",
                            existing['method_id']
                        ))
                        saved_method = cur.fetchone()
                        logger.info(f"Updated learning method {saved_method['method_id']} in database")
                    else:
                        # Insert new method
                        cur.execute("""
                            INSERT INTO learning_methods (
                                lesson_id, chapter_id, method_type, title,
                                instructions, data, tier, difficulty, order_index, published
                            ) VALUES (
                                %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s
                            )
                            RETURNING method_id
                        """, (
                            lesson_id,
                            chapter_id,
                            lm_number,
                            f"{lm_type}: {topic}",
                            prompt,
                            psycopg.types.json.Jsonb(parsed_data),
                            'basic',
                            'medium',
                            0,
                            False
                        ))
                        saved_method = cur.fetchone()
                        logger.info(f"Saved new learning method {saved_method['method_id']} to database")

                    conn.commit()

            return jsonify({
                'success': True,
                'lesson_id': lesson_id,
                'lm_type': lm_type,
                'content_generated': True,
                'tokens_used': result.get('total_tokens', 0),
                'cost_eur': result.get('cost_eur', 0),
                'provider': provider_name,
                'model': model_name,
                'data': output_text[:1000] + '...' if len(output_text) > 1000 else output_text
            }), 200

        except Exception as e:
            logger.error(f"AI generation error for lesson {lesson_id}: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'AI generation failed',
                'message': str(e)
            }), 500

    except Exception as e:
        logger.error(f"Error generating LM content: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate content',
            'message': str(e)
        }), 500


def _get_lm_prompts(topic: str) -> dict:
    """
    Get learning method specific prompts.

    Uses prompt templates optimized for each LM type according to
    02_Lernmethoden.md specification.

    Args:
        topic: The topic for content generation

    Returns:
        Dictionary mapping LM type codes to prompts
    """
    return {
        'LM00': f"""Erstelle eine detaillierte Erklaerung fuer das Thema "{topic}" fuer FISI-Pruefungsvorbereitung.
Struktur: 1. Einleitung, 2. Kernkonzepte, 3. Praxisbeispiele, 4. Zusammenfassung.
Zielgruppe: Fachinformatiker Systemintegration. Sprache: Deutsch.""",

        'LM09': f"""Erstelle eine Code-Sandbox-Aufgabe zum Thema "{topic}" fuer FISI-Pruefungsvorbereitung.
Format: JSON mit Feldern: task, starter_code, solution, hints.
Zielgruppe: Fachinformatiker Systemintegration.""",

        'LM12': f"""Erstelle eine interaktive Mathe-Aufgabe zum Thema "{topic}".
Format: JSON mit Feldern: question, steps, solution, explanation.
Fuer IHK-Pruefungsvorbereitung.""",

        'LM13': f"""Erstelle 5 Flashcards zum Thema "{topic}" fuer FISI-Pruefungsvorbereitung.
Format: JSON Array mit Objekten: front (Frage), back (Antwort).
Fokus auf IHK-relevante Inhalte.""",

        'LM14': f"""Erstelle eine Drag & Drop Uebung zum Thema "{topic}".
Format: JSON mit: items (zu sortierende Elemente), categories (Zielkategorien), correct_mapping.
Fuer FISI-Pruefungsvorbereitung.""",

        'LM16': f"""Erstelle eine Fehleranalyse-Aufgabe zum Thema "{topic}".
Format: JSON mit: code_with_errors, error_descriptions, corrected_code, explanation.
Fuer FISI-Pruefungsvorbereitung.""",

        'LM22': f"""Erstelle 5 Multiple-Choice-Fragen zum Thema "{topic}" fuer FISI-Pruefungsvorbereitung.
Format: JSON Array mit: question, options (4 Stueck), correct_index, explanation.
IHK-Pruefungsniveau.""",
    }
