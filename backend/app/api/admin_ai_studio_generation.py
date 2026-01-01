"""
LernsystemX Admin AI Studio - Content Generation API

Source data and content generation endpoints:
- POST   /api/v1/admin/ai-studio/sessions/{id}/source    - Set source data
- POST   /api/v1/admin/ai-studio/sessions/{id}/generate  - Generate content
- POST   /api/v1/admin/ai-studio/sessions/{id}/finalize  - Finalize and create chapter
- POST   /api/v1/admin/ai-studio/upload-pdf              - Upload and analyze PDF
- GET    /api/v1/admin/ai-studio/templates               - Get available templates
- GET    /api/v1/admin/ai-studio/stats                   - Get user stats

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
Module split according to 35_Developer-Guide-KI-Prompts.md guidelines
"""

from flask import request, jsonify, g
from pydantic import ValidationError
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.models.ai_studio import (
    AIStudioSourceDataRequest,
    AIStudioGenerateRequest,
    AIStudioFinalizeRequest
)
from app.repositories.ai_studio_repository import (
    AIStudioRepository,
    AIStudioAnalyticsRepository,
    AIGenerationVariantRepository,
    AIAuthoringTemplateRepository
)
from app.services.ai_studio_service import (
    AiStudioService,
    AiStudioServiceError
)
from app.services.audit_service import AuditService
from app.security.permissions import require_permission, Permissions


# ============================================================================
# Source Data & Content Generation
# ============================================================================

@api_v1.route('/admin/ai-studio/sessions/<session_id>/source', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def set_ai_studio_source(session_id: str):
    """
    Set source data for session

    Request Body:
        {
            "source_type": "pdf",
            "source_data": {
                "text": "Extracted PDF text...",
                "metadata": {...}
            }
        }
    """
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()
        req = AIStudioSourceDataRequest(**data)

        update_data = {
            'source_type': req.source_type.value,
            'source_data': req.source_data
        }

        updated = AIStudioRepository.update_session(session_id, update_data)

        # Mark step as completed
        steps_completed = session.get('steps_completed', [])
        if isinstance(steps_completed, str):
            steps_completed = json.loads(steps_completed)
        if 'source_selection' not in steps_completed:
            steps_completed.append('source_selection')

        AIStudioRepository.update_step(session_id, 'theory_generation', steps_completed)

        # Log analytics
        AIStudioAnalyticsRepository.log_event({
            'session_id': session_id,
            'user_id': user_id,
            'event_type': 'source_set',
            'event_data': {'source_type': req.source_type.value},
            'step_name': 'source_selection'
        })

        return jsonify({
            'success': True,
            'session': updated
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error setting source data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to set source data',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>/generate', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("5 per minute")
def generate_ai_studio_content(session_id: str):
    """
    Generate AI content

    Request Body:
        {
            "content_type": "theory",
            "prompt": "Custom prompt...",
            "generate_variants": 2
        }

    Response 202:
        {
            "success": true,
            "message": "Generation started",
            "job_id": "uuid"
        }

    Note: This starts an async job. Use WebSocket or polling to get results.
    """
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json()
        req = AIStudioGenerateRequest(**data)

        # Update session status
        AIStudioRepository.update_status(session_id, 'in_progress')

        # Log analytics - generation started
        start_time = datetime.utcnow()
        AIStudioAnalyticsRepository.log_event({
            'session_id': session_id,
            'user_id': user_id,
            'event_type': 'generation_started',
            'event_data': {
                'content_type': req.content_type.value,
                'variants_requested': req.generate_variants
            },
            'step_name': f'{req.content_type.value}_generation'
        })

        # Use AI Studio Service for generation
        # Service uses prompt registry (NOT hardcoded prompts)
        service = AiStudioService()

        # Build context from session data
        source_data = session.get('source_data', {})
        generated_content = session.get('generated_content', {})

        context = {
            'target_audience': source_data.get('target_audience', 'Allgemein'),
            'difficulty': source_data.get('difficulty', 'mittel'),
            'target_language': source_data.get('target_language', 'de'),
            'learning_objectives': json.dumps(source_data.get('learning_objectives', [])),
        }

        # Add step-specific context
        step = req.content_type.value
        if step == 'theory':
            context['max_theory_variants'] = str(req.generate_variants or 4)
            context['pdf_analysis'] = json.dumps(generated_content.get('pdf_analysis', source_data.get('pdf_analysis', {})))
            context['selected_didactic_angle'] = generated_content.get('selected_didactic_angle', '')
        elif step == 'lesson':
            context['max_lessons'] = str(5)
            context['pdf_analysis'] = json.dumps(generated_content.get('pdf_analysis', {}))
            context['selected_theory_variant'] = json.dumps(generated_content.get('selected_theory_variant', {}))
        elif step == 'method':
            context['method_preferences'] = json.dumps(source_data.get('method_preferences', []))
            context['lessons'] = json.dumps(generated_content.get('lessons', []))

        # Generate content using the service
        result = service.generate_for_step(
            step=step,
            session_id=session_id,
            context=context,
            user_id=user_id
        )

        # Parse AI output and store variant
        try:
            output_data = json.loads(result.get('output_text', '{}'))
        except json.JSONDecodeError:
            output_data = {'raw_output': result.get('output_text')}

        # Store as variant
        variant_data = {
            'session_id': session_id,
            'variant_type': step,
            'variant_index': 0,
            'content': output_data,
            'metadata': {
                'prompt_code': result.get('prompt_code'),
                'model': result.get('model'),
                'provider': result.get('provider'),
                'tokens': result.get('total_tokens'),
                'cost_eur': result.get('cost_eur')
            }
        }
        variant_id = AIGenerationVariantRepository.create(variant_data)

        # Update session generated_content
        generated_content[step] = output_data
        AIStudioRepository.update(session_id, {'generated_content': generated_content})

        return jsonify({
            'success': True,
            'message': 'Generation complete',
            'step': step,
            'variant_id': variant_id,
            'prompt_code': result.get('prompt_code'),
            'tokens_used': result.get('total_tokens'),
            'cost_eur': result.get('cost_eur'),
            'data': output_data
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except AiStudioServiceError as e:
        logger.error(f"AI Studio service error: {str(e)}")
        AIStudioRepository.update_status(session_id, 'error')
        return jsonify({
            'success': False,
            'error': 'AI generation failed',
            'message': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        AIStudioRepository.update_status(session_id, 'error')
        return jsonify({
            'success': False,
            'error': 'Failed to generate content',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/sessions/<session_id>/finalize', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("5 per minute")
def finalize_ai_studio_session(session_id: str):
    """
    Finalize session and create chapter with content

    Request Body:
        {
            "create_chapter": true,
            "create_lessons": true,
            "create_methods": true,
            "chapter_title": "Kapitel 1: Einfuehrung",
            "publish_immediately": false
        }

    Response 200:
        {
            "success": true,
            "message": "Session finalized successfully",
            "chapter_id": "uuid",
            "lesson_ids": ["uuid1", "uuid2"],
            "method_ids": ["uuid1", "uuid2", "uuid3"],
            "stats": {
                "chapters_created": 1,
                "lessons_created": 2,
                "methods_created": 3
            }
        }
    """
    try:
        session = AIStudioRepository.find_by_id(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        user_id = g.current_user['user_id']
        if session['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        data = request.get_json() or {}
        req = AIStudioFinalizeRequest(**data)

        # Use AI Studio Service to finalize session and create content
        from app.services.ai_studio_service import AiStudioService, AiStudioServiceError

        service = AiStudioService()
        result = service.finalize_session(
            session_id=session_id,
            create_chapter=req.create_chapter,
            create_lessons=req.create_lessons,
            create_methods=req.create_methods,
            chapter_title=req.chapter_title,
            publish_immediately=req.publish_immediately,
            user_id=user_id
        )

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='ai_studio_session_finalized',
            resource_type='ai_authoring_session',
            resource_id=session_id,
            details={
                'course_id': session['course_id'],
                'chapter_id': result.get('chapter_id'),
                'lessons_created': result['stats']['lessons_created'],
                'methods_created': result['stats']['methods_created']
            }
        )

        return jsonify({
            'success': True,
            'message': 'Session finalized successfully',
            'chapter_id': result.get('chapter_id'),
            'lesson_ids': result.get('lesson_ids', []),
            'method_ids': result.get('method_ids', []),
            'stats': result.get('stats', {})
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except AiStudioServiceError as e:
        logger.error(f"AI Studio service error finalizing session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Finalization failed',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error finalizing session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to finalize session',
            'message': str(e)
        }), 500


# ============================================================================
# PDF Upload & Templates
# ============================================================================

@api_v1.route('/admin/ai-studio/upload-pdf', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def upload_ai_studio_pdf():
    """
    Upload and analyze PDF file

    Form Data:
        file: PDF file

    Response 200:
        {
            "success": true,
            "file_hash": "sha256...",
            "extracted_text": "...",
            "page_count": 10,
            "structure_analysis": {...}
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']

        if not file.filename or not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': 'File must be a PDF'
            }), 400

        # Read file content
        file_content = file.read()

        # Validate PDF
        from app.services.pdf_service import PDFService, PDFExtractionError, PDFPasswordProtectedError

        is_valid, error_msg = PDFService.validate_pdf(file_content)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg or 'Invalid PDF file'
            }), 400

        # Extract text and analyze structure
        try:
            result = PDFService.extract_for_ai(file_content, file.filename)

            return jsonify({
                'success': True,
                'file_hash': result['file_hash'],
                'original_filename': result['filename'],
                'file_size_bytes': len(file_content),
                'page_count': result['page_count'],
                'extracted_text': result['main_text'],
                'structure_analysis': result['structure'],
                'metadata': result['metadata'],
                'summary': result['summary'],
                'recommendations': result['recommendations'],
                'word_count': result['word_count'],
                'estimated_reading_time': result['estimated_reading_time'],
                'from_cache': False
            }), 200

        except PDFPasswordProtectedError:
            return jsonify({
                'success': False,
                'error': 'PDF ist passwortgeschuetzt'
            }), 400

        except PDFExtractionError as e:
            return jsonify({
                'success': False,
                'error': f'PDF-Extraktion fehlgeschlagen: {str(e)}'
            }), 400

    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process PDF',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/templates', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_ai_studio_templates():
    """
    Get available authoring templates

    Query Parameters:
        category: Filter by category
    """
    try:
        category = request.args.get('category')

        if category:
            templates = AIAuthoringTemplateRepository.get_by_category(category)
        else:
            templates = AIAuthoringTemplateRepository.get_all_active()

        return jsonify({
            'success': True,
            'templates': templates
        }), 200

    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get templates',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/stats', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_ai_studio_stats():
    """Get user's AI Studio statistics"""
    try:
        user_id = g.current_user['user_id']

        # Get session counts
        all_sessions = AIStudioRepository.find_by_user(user_id, limit=1000)
        active_sessions = [s for s in all_sessions if s['status'] in ['draft', 'in_progress', 'review']]
        completed_sessions = [s for s in all_sessions if s['status'] == 'completed']

        # Get analytics stats
        analytics_stats = AIStudioAnalyticsRepository.get_user_stats(user_id)

        return jsonify({
            'success': True,
            'stats': {
                'total_sessions': len(all_sessions),
                'active_sessions': len(active_sessions),
                'completed_sessions': len(completed_sessions),
                'total_chapters_created': len(completed_sessions),  # Simplified for now
                'total_tokens_used': analytics_stats.get('total_tokens', 0),
                'avg_generation_time_ms': analytics_stats.get('avg_generation_time', 0)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get stats',
            'message': str(e)
        }), 500


# ============================================================================
# KI-Prüfungsgenerator (AI Studio Exams Tab)
# ============================================================================

@api_v1.route('/admin/ai/generate-exam', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_exam_chat():
    """
    Generate exam via AI for the KI-Studio Exams Tab (synchronous/chat-based).

    This endpoint generates exam questions immediately and returns them,
    suitable for the interactive chat-based workflow in KI-Studio.

    Supports using course files (PDF, TXT, etc.) as source material for context.

    Request Body:
        {
            "course_id": "uuid" (required),
            "chapter_id": "uuid" (optional),
            "prompt": "Erstelle 10 MC-Fragen zur Kalkulation",
            "exam_type": "mixed",
            "question_count": 10,
            "duration_minutes": 30,
            "difficulty": "medium",
            "source_files": ["course_file_id_1", "course_file_id_2"] (optional, max 5)
        }

    Response 200:
        {
            "success": true,
            "data": {
                "title": "Prüfung: Kalkulation",
                "description": "...",
                "duration_minutes": 30,
                "difficulty": "medium",
                "questions": [
                    {
                        "type": "mc",
                        "question": "Was ist der Listenverkaufspreis?",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 0,
                        "points": 1,
                        "difficulty": "medium"
                    },
                    ...
                ],
                "tokens_used": 1500,
                "cost_eur": 0.0045,
                "generation_time_ms": 3200,
                "files_used": [{"id": "uuid", "name": "Script.pdf"}, ...]
            }
        }
    """
    try:
        user_id = g.current_user['user_id']
        data = request.get_json() or {}

        course_id = data.get('course_id')
        chapter_id = data.get('chapter_id')
        prompt = data.get('prompt', '')
        exam_type = data.get('exam_type', 'mixed')
        question_count = data.get('question_count', 10)
        duration_minutes = data.get('duration_minutes', 30)
        source_files = data.get('source_files', [])  # List of course_file_ids
        difficulty = data.get('difficulty', 'medium')

        if not course_id:
            return jsonify({
                'success': False,
                'error': 'course_id is required'
            }), 400

        # Get course info for context
        from app.repositories.course_repository import CourseRepository
        from app.repositories.chapter_repository import ChapterRepository
        from app.repositories.course_file_repository import CourseFileRepository

        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get chapter info if provided
        chapter_context = ""
        if chapter_id:
            chapter = ChapterRepository.find_by_id(chapter_id)
            if chapter:
                chapter_context = f"\nKapitel: {chapter['title']}"

                # Get lessons for more context
                from app.repositories.lesson_repository import LessonRepository
                lessons = LessonRepository.find_by_chapter(chapter_id)
                if lessons:
                    lesson_titles = [l['title'] for l in lessons[:10]]
                    chapter_context += f"\nLektionen: {', '.join(lesson_titles)}"

        # Get file content for context
        file_context = ""
        files_used = []
        if source_files:
            for file_id in source_files[:5]:  # Limit to 5 files
                file_record = CourseFileRepository.find_by_id(file_id)
                if file_record and file_record.get('course_id') == course_id:
                    files_used.append({
                        'id': file_id,
                        'name': file_record.get('display_name') or file_record.get('file_name')
                    })

                    # Use already extracted text if available
                    if file_record.get('ai_extracted_text'):
                        extracted = file_record['ai_extracted_text']
                        # Limit text per file to prevent context overflow
                        if len(extracted) > 8000:
                            extracted = extracted[:8000] + "...[gekürzt]"
                        file_context += f"\n\n--- Datei: {file_record.get('display_name', file_record['file_name'])} ---\n{extracted}"

                    # For PDFs without extracted text, try to extract on-the-fly
                    elif file_record.get('file_type') == 'pdf' and file_record.get('storage_path'):
                        try:
                            import os
                            from app.services.pdf_service import PDFService

                            storage_path = file_record['storage_path']
                            if os.path.exists(storage_path):
                                with open(storage_path, 'rb') as f:
                                    pdf_content = f.read()

                                pdf_result = PDFService.extract_text(pdf_content, file_record['file_name'])
                                extracted = pdf_result.get('extracted_text', '')

                                if extracted:
                                    # Cache the extracted text for future use
                                    CourseFileRepository.mark_ai_processed(
                                        file_id,
                                        extracted_text=extracted[:50000]  # Limit stored text
                                    )

                                    if len(extracted) > 8000:
                                        extracted = extracted[:8000] + "...[gekürzt]"
                                    file_context += f"\n\n--- Datei: {file_record.get('display_name', file_record['file_name'])} ---\n{extracted}"
                        except Exception as pdf_err:
                            logger.warning(f"Could not extract PDF {file_id}: {str(pdf_err)}")

                    # For text files
                    elif file_record.get('file_type') in ['txt', 'md'] and file_record.get('storage_path'):
                        try:
                            import os
                            storage_path = file_record['storage_path']
                            if os.path.exists(storage_path):
                                with open(storage_path, 'r', encoding='utf-8') as f:
                                    text_content = f.read()
                                if len(text_content) > 8000:
                                    text_content = text_content[:8000] + "...[gekürzt]"
                                file_context += f"\n\n--- Datei: {file_record.get('display_name', file_record['file_name'])} ---\n{text_content}"
                        except Exception as txt_err:
                            logger.warning(f"Could not read text file {file_id}: {str(txt_err)}")

        # Build AI prompt
        import time
        start_time = time.time()

        # Build source material section
        source_material = ""
        if file_context:
            source_material = f"""

QUELLMATERIAL (basiere die Fragen auf diesem Inhalt):
{file_context}

"""

        system_prompt = f"""Du bist ein Prüfungsexperte für IT-Ausbildungen (IHK FISI, FIAE, etc.).
Erstelle Prüfungsfragen basierend auf dem Kurs: {course['title']}{chapter_context}{source_material}

Ausgabeformat: JSON mit folgender Struktur:
{{
    "title": "Titel der Prüfung",
    "description": "Kurze Beschreibung",
    "questions": [
        {{
            "type": "mc",
            "question": "Fragetext",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "points": 1,
            "difficulty": "medium"
        }},
        {{
            "type": "free_text",
            "question": "Fragetext für Freitext",
            "sample_answer": "Musterantwort",
            "points": 3,
            "difficulty": "hard"
        }}
    ]
}}

Fragentypen:
- mc: Multiple Choice (4 Optionen, correct_answer = Index 0-3)
- free_text: Freitext mit Musterantwort
- matching: Zuordnung (options = items, correct_answer = mapping)
- fill_blank: Lückentext (question mit ___ für Lücken)

Schwierigkeiten: easy, medium, hard"""

        user_prompt = f"""Erstelle {question_count} Prüfungsfragen.
Prüfungstyp: {exam_type}
Schwierigkeit: {difficulty}
Dauer: {duration_minutes} Minuten

Benutzeranfrage: {prompt}

{"WICHTIG: Basiere die Fragen primär auf dem bereitgestellten Quellmaterial!" if file_context else ""}

Antworte NUR mit dem JSON-Objekt, ohne zusätzlichen Text."""

        # Call AI service
        from app.services.ai_adapter import AIAdapter

        try:
            result = AIAdapter.generate_content(
                provider='anthropic',
                prompt=user_prompt,
                system_prompt=system_prompt,
                user_id=user_id,
                max_tokens=4000
            )

            generation_time_ms = int((time.time() - start_time) * 1000)

            # Parse response
            response_text = result.get('content', '{}')

            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                exam_data = json.loads(json_match.group())
            else:
                exam_data = {'title': 'Generierte Prüfung', 'questions': []}

            # Ensure questions have required fields
            for q in exam_data.get('questions', []):
                if 'points' not in q:
                    q['points'] = 1
                if 'difficulty' not in q:
                    q['difficulty'] = 'medium'

            # Calculate tokens and cost
            tokens_used = result.get('tokens_used', 0)
            cost_eur = tokens_used * 0.000003  # Approximate Claude cost

            # Log analytics
            AIStudioAnalyticsRepository.log_event({
                'session_id': None,
                'user_id': user_id,
                'event_type': 'exam_generated',
                'event_data': {
                    'course_id': course_id,
                    'chapter_id': chapter_id,
                    'question_count': len(exam_data.get('questions', [])),
                    'exam_type': exam_type,
                    'difficulty': difficulty,
                    'files_used': [f['id'] for f in files_used],
                    'tokens_used': tokens_used
                },
                'tokens_used': tokens_used,
                'step_name': 'exam_generation'
            })

            return jsonify({
                'success': True,
                'data': {
                    'title': exam_data.get('title', f'Prüfung: {course["title"]}'),
                    'description': exam_data.get('description', ''),
                    'duration_minutes': duration_minutes,
                    'difficulty': difficulty,
                    'questions': exam_data.get('questions', []),
                    'tokens_used': tokens_used,
                    'cost_eur': cost_eur,
                    'generation_time_ms': generation_time_ms,
                    'files_used': files_used
                }
            }), 200

        except Exception as ai_error:
            logger.error(f"AI generation error: {str(ai_error)}")
            return jsonify({
                'success': False,
                'error': 'AI generation failed',
                'message': str(ai_error)
            }), 500

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        logger.error(f"Error generating exam: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate exam',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai/regenerate-question', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("20 per minute")
def regenerate_exam_question():
    """
    Regenerate a single exam question.

    Request Body:
        {
            "course_id": "uuid",
            "chapter_id": "uuid" (optional),
            "question_type": "mc",
            "context": "Original question text for context"
        }

    Response 200:
        {
            "success": true,
            "data": {
                "question": { ... },
                "tokens_used": 300
            }
        }
    """
    try:
        user_id = g.current_user['user_id']
        data = request.get_json() or {}

        course_id = data.get('course_id')
        chapter_id = data.get('chapter_id')
        question_type = data.get('question_type', 'mc')
        context = data.get('context', '')

        if not course_id:
            return jsonify({
                'success': False,
                'error': 'course_id is required'
            }), 400

        # Get course info
        from app.repositories.course_repository import CourseRepository
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Build prompt for single question
        type_instructions = {
            'mc': 'Multiple Choice mit 4 Optionen',
            'free_text': 'Freitext mit Musterantwort',
            'matching': 'Zuordnungsaufgabe',
            'fill_blank': 'Lückentext'
        }

        system_prompt = f"""Du bist ein Prüfungsexperte. Erstelle eine neue {type_instructions.get(question_type, 'Multiple Choice')} Frage.
Kurs: {course['title']}

Ausgabe als JSON:
{{
    "type": "{question_type}",
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct_answer": 0,
    "points": 1,
    "difficulty": "medium"
}}"""

        user_prompt = f"Erstelle eine alternative Frage zu diesem Thema: {context}\n\nAntwort NUR als JSON."

        # Call AI
        from app.services.ai_adapter import AIAdapter

        result = AIAdapter.generate_content(
            provider='anthropic',
            prompt=user_prompt,
            system_prompt=system_prompt,
            user_id=user_id,
            max_tokens=1000
        )

        # Parse response
        import re
        response_text = result.get('content', '{}')
        json_match = re.search(r'\{[\s\S]*\}', response_text)

        if json_match:
            question = json.loads(json_match.group())
        else:
            question = {
                'type': question_type,
                'question': 'Frage konnte nicht generiert werden',
                'options': ['A', 'B', 'C', 'D'] if question_type == 'mc' else None,
                'correct_answer': 0,
                'points': 1,
                'difficulty': 'medium'
            }

        tokens_used = result.get('tokens_used', 0)

        return jsonify({
            'success': True,
            'data': {
                'question': question,
                'tokens_used': tokens_used
            }
        }), 200

    except Exception as e:
        logger.error(f"Error regenerating question: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to regenerate question',
            'message': str(e)
        }), 500


@api_v1.route('/admin/exams', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def create_exam():
    """
    Create/save an exam from generated content.

    Request Body:
        {
            "course_id": "uuid",
            "chapter_id": "uuid" (optional),
            "title": "Prüfung: Kalkulation",
            "description": "...",
            "duration_minutes": 30,
            "questions": [...],
            "exam_type": "ai_generated"
        }

    Response 201:
        {
            "success": true,
            "data": {
                "exam_id": "uuid"
            }
        }
    """
    try:
        user_id = g.current_user['user_id']
        data = request.get_json() or {}

        course_id = data.get('course_id')
        if not course_id:
            return jsonify({
                'success': False,
                'error': 'course_id is required'
            }), 400

        # Create exam record
        from app.database.connection import insert_returning

        exam_data = {
            'course_id': course_id,
            'chapter_id': data.get('chapter_id'),
            'title': data.get('title', 'Generierte Prüfung'),
            'description': data.get('description', ''),
            'duration_minutes': data.get('duration_minutes', 30),
            'exam_type': data.get('exam_type', 'quiz'),
            'questions': json.dumps(data.get('questions', [])),
            'settings': json.dumps({
                'created_by': user_id,
                'ai_generated': True,
                'question_count': len(data.get('questions', []))
            }),
            'published': False,
            'passing_score': 50,
            'total_points': sum(q.get('points', 1) for q in data.get('questions', []))
        }

        result = insert_returning('exams', exam_data)

        if result:
            # Audit log
            AuditService.log_action(
                user_id=user_id,
                action='exam_created',
                resource_type='exam',
                resource_id=str(result['exam_id']),
                details={
                    'course_id': course_id,
                    'title': exam_data['title'],
                    'question_count': len(data.get('questions', []))
                }
            )

            return jsonify({
                'success': True,
                'data': {
                    'exam_id': str(result['exam_id'])
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create exam'
            }), 500

    except Exception as e:
        logger.error(f"Error creating exam: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create exam',
            'message': str(e)
        }), 500
