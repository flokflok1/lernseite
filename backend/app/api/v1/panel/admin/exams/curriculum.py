"""
Curriculum Framework Admin API

Endpoints for managing curriculum frameworks:
- CRUD for frameworks (list, get tree, create, delete)
- AI-powered PDF import (parse preview + confirm)
- Link framework to exam type
- Auto-map questions to curriculum objectives via AI
- Question curriculum tagging (get, add, remove)
- Coverage and relevance statistics

All endpoints require admin authentication.
"""

import json
import logging
import threading
import time
from flask import Blueprint, jsonify, request, Response, stream_with_context

from app.api.middleware.auth import admin_required
from app.infrastructure.persistence.repositories.exams.curriculum import (
    CurriculumFrameworkRepository,
)
from app.application.services.exams.curriculum_service import CurriculumService

logger = logging.getLogger(__name__)

curriculum_bp = Blueprint(
    'curriculum_admin',
    __name__,
    url_prefix='/admin/curriculum',
)


# --- Frameworks ---

@curriculum_bp.route('/frameworks', methods=['GET'])
@admin_required
def list_frameworks():
    """List all curriculum frameworks."""
    frameworks = CurriculumFrameworkRepository.find_all_frameworks()
    return jsonify({
        'success': True,
        'count': len(frameworks),
        'frameworks': frameworks,
    })


@curriculum_bp.route('/frameworks/<int:framework_id>', methods=['GET'])
@admin_required
def get_framework(framework_id):
    """Get a framework with full tree (sections/positions/objectives)."""
    tree = CurriculumFrameworkRepository.load_framework_tree(framework_id)
    if not tree:
        return jsonify({'success': False, 'error': 'Framework not found'}), 404
    return jsonify({'success': True, 'framework': tree})


@curriculum_bp.route('/frameworks', methods=['POST'])
@admin_required
def create_framework():
    """Create a new curriculum framework."""
    body = request.get_json(silent=True) or {}
    if not body.get('name'):
        return jsonify({
            'success': False,
            'error': 'name is required',
        }), 400
    framework = CurriculumFrameworkRepository.create_framework(body)
    return jsonify({'success': True, 'framework': framework}), 201


@curriculum_bp.route('/frameworks/<int:framework_id>', methods=['DELETE'])
@admin_required
def delete_framework(framework_id):
    """Delete a curriculum framework (cascades to children)."""
    CurriculumFrameworkRepository.delete_framework(framework_id)
    return jsonify({'success': True})


# --- AI PDF Import ---

@curriculum_bp.route('/frameworks/import-pdf', methods=['POST'])
@admin_required
def import_pdf_preview():
    """Parse PDF text with AI and return a preview of the structure."""
    body = request.get_json(silent=True) or {}
    pdf_text = body.get('pdf_text', '')
    if len(pdf_text) < 100:
        return jsonify({
            'success': False,
            'error': 'pdf_text must be at least 100 characters',
        }), 400

    provider = body.get('provider')
    model = body.get('model')

    try:
        preview = CurriculumService.parse_pdf_with_ai(
            pdf_text, provider=provider, model=model,
        )
        return jsonify({'success': True, 'preview': preview})
    except ValueError as exc:
        logger.exception("AI PDF parse failed")
        return jsonify({'success': False, 'error': str(exc)}), 422
    except Exception:
        logger.exception("Unexpected error during PDF AI parse")
        return jsonify({
            'success': False,
            'error': 'AI processing failed',
        }), 500


@curriculum_bp.route('/frameworks/import-pdf-upload', methods=['POST'])
@admin_required
def import_pdf_upload():
    """Upload a PDF file, extract text, and parse with AI.

    Streams SSE progress events to the client:
    - extracting: PDF text extraction started
    - extracted: PDF text extracted (with char/page counts)
    - ai_started: AI analysis started
    - ai_progress: Periodic heartbeat during AI processing
    - complete: Final result with preview data
    - error: Error occurred at any stage
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file uploaded',
        }), 400

    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return jsonify({
            'success': False,
            'error': 'Only PDF files are allowed',
        }), 400

    provider = request.form.get('provider')
    model = request.form.get('model')
    filename = file.filename

    # Read file bytes before streaming (request context needed)
    pdf_bytes = file.read()
    logger.info(
        "PDF upload: filename=%s, bytes=%d, content_type=%s",
        filename, len(pdf_bytes), file.content_type,
    )

    def generate():
        yield _sse('log', {'message': f'PDF-Upload empfangen: {filename}'})
        yield _sse('extracting', {'filename': filename})
        yield _sse('log', {'message': 'Text-Extraktion gestartet (PyMuPDF)...'})

        try:
            pdf_text = _extract_text_from_bytes(pdf_bytes)
        except Exception:
            logger.exception("PDF text extraction failed")
            yield _sse('log', {'message': 'FEHLER: Text-Extraktion fehlgeschlagen'})
            yield _sse('error', {'message': 'Failed to extract text from PDF'})
            return

        char_count = len(pdf_text.strip())
        page_count = pdf_text.count('\f') + 1
        word_count = len(pdf_text.split())

        if char_count < 100:
            yield _sse('error', {
                'message': 'PDF contains too little text (min 100 chars)',
            })
            return

        yield _sse('log', {
            'message': f'Extrahiert: {char_count:,} Zeichen, '
                       f'~{page_count} Seiten, ~{word_count:,} Wörter',
        })
        yield _sse('extracted', {
            'chars': char_count,
            'pages': page_count,
        })

        used_provider = provider or 'default'
        used_model = model or 'default'
        yield _sse('log', {
            'message': f'KI-Anfrage wird gesendet an '
                       f'{used_provider} / {used_model}...',
        })
        yield _sse('ai_started', {
            'provider': used_provider,
            'model': used_model,
        })
        yield _sse('log', {
            'message': 'Warte auf KI-Antwort '
                       '(kann 1-3 Minuten dauern bei großen Dokumenten)...',
        })

        # Run AI call in thread so we can send heartbeats
        ai_result = {'preview': None, 'error': None}
        ai_done = threading.Event()

        def run_ai():
            try:
                ai_result['preview'] = CurriculumService.parse_pdf_with_ai(
                    pdf_text, provider=provider, model=model,
                )
            except ValueError as exc:
                logger.exception("AI PDF parse failed")
                ai_result['error'] = str(exc)
            except Exception:
                logger.exception("Unexpected error during PDF AI parse")
                ai_result['error'] = 'AI processing failed'
            finally:
                ai_done.set()

        ai_thread = threading.Thread(target=run_ai, daemon=True)
        ai_thread.start()

        heartbeat_messages = [
            'KI verarbeitet Dokument...',
            'Struktur wird analysiert...',
            'Abschnitte und Positionen werden erkannt...',
            'Lernziele werden extrahiert...',
            'Kompetenzstufen werden zugeordnet...',
            'JSON-Struktur wird aufgebaut...',
            'KI arbeitet noch...',
        ]
        heartbeat_idx = 0
        seconds_waited = 0

        while not ai_done.wait(timeout=10):
            seconds_waited += 10
            msg = heartbeat_messages[
                min(heartbeat_idx, len(heartbeat_messages) - 1)
            ]
            yield _sse('log', {
                'message': f'[{seconds_waited}s] {msg}',
            })
            yield _sse('ai_progress', {'seconds': seconds_waited})
            heartbeat_idx += 1

        if ai_result['error']:
            yield _sse('log', {
                'message': f'FEHLER: {ai_result["error"]}',
            })
            yield _sse('error', {'message': ai_result['error']})
        else:
            preview_data = ai_result['preview']
            sections = preview_data.get('sections', [])
            total_positions = sum(
                len(s.get('positions', [])) for s in sections
            )
            total_objectives = sum(
                len(p.get('objectives', []))
                for s in sections
                for p in s.get('positions', [])
            )
            yield _sse('log', {
                'message': f'KI-Analyse abgeschlossen: '
                           f'{len(sections)} Abschnitte, '
                           f'{total_positions} Positionen, '
                           f'{total_objectives} Lernziele erkannt',
            })
            yield _sse('complete', {'preview': preview_data})

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        },
    )


@curriculum_bp.route('/frameworks/import-confirm', methods=['POST'])
@admin_required
def import_confirm():
    """Persist an AI-parsed curriculum structure."""
    body = request.get_json(silent=True) or {}
    try:
        framework = CurriculumService.import_from_ai_result(
            ai_result=body.get('ai_result', body),
            source_document=body.get('source_document'),
        )
        return jsonify({'success': True, 'framework': framework}), 201
    except Exception:
        logger.exception("Failed to import curriculum from AI result")
        return jsonify({
            'success': False,
            'error': 'Import failed',
        }), 500


# --- Framework <-> Exam Type Linking ---

@curriculum_bp.route(
    '/frameworks/<int:framework_id>/link/<exam_type_key>',
    methods=['POST'],
)
@admin_required
def link_framework_to_exam_type(framework_id, exam_type_key):
    """Link a curriculum framework to an exam type."""
    try:
        CurriculumFrameworkRepository.link_framework_to_exam_type(
            framework_id, exam_type_key,
        )
        return jsonify({'success': True})
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400


# --- Auto-mapping ---

@curriculum_bp.route('/auto-map/<exam_type_key>', methods=['POST'])
@admin_required
def auto_map_questions(exam_type_key):
    """Auto-map unmapped questions to curriculum objectives via AI."""
    try:
        body = request.get_json(silent=True) or {}
        stats = CurriculumService.auto_map_questions(
            exam_type_key,
            provider=body.get('provider'),
            model=body.get('model'),
        )
        return jsonify({'success': True, 'stats': stats})
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception:
        logger.exception("Auto-mapping failed for %s", exam_type_key)
        return jsonify({
            'success': False,
            'error': 'Auto-mapping failed',
        }), 500


# --- Question Curriculum Tags ---

@curriculum_bp.route('/questions/<question_id>/tags', methods=['GET'])
@admin_required
def get_question_tags(question_id):
    """Get curriculum tags for a question."""
    tags = CurriculumFrameworkRepository.find_tags_by_question(
        question_id,
    )
    return jsonify({'success': True, 'tags': tags})


@curriculum_bp.route('/questions/<question_id>/tags', methods=['POST'])
@admin_required
def add_question_tag(question_id):
    """Add a curriculum tag to a question."""
    body = request.get_json(silent=True) or {}
    objective_id = body.get('objective_id')
    if not objective_id:
        return jsonify({
            'success': False,
            'error': 'objective_id is required',
        }), 400
    tag = CurriculumFrameworkRepository.tag_question(
        question_id=question_id,
        objective_id=objective_id,
        confidence=body.get('confidence', 1.0),
        tagged_by='admin',
    )
    return jsonify({'success': True, 'tag': tag}), 201


@curriculum_bp.route(
    '/questions/<question_id>/tags/<int:objective_id>',
    methods=['DELETE'],
)
@admin_required
def remove_question_tag(question_id, objective_id):
    """Remove a curriculum tag from a question."""
    CurriculumFrameworkRepository.remove_question_tag(
        question_id, objective_id,
    )
    return jsonify({'success': True})


# --- Coverage & Relevance Stats ---

@curriculum_bp.route(
    '/frameworks/<int:framework_id>/coverage', methods=['GET'],
)
@admin_required
def get_coverage(framework_id):
    """Get coverage statistics for a curriculum framework."""
    rows = CurriculumFrameworkRepository.get_curriculum_coverage_stats(
        framework_id,
    )
    total_objectives = sum(r.get('objective_count', 0) for r in rows)
    # Count objectives in positions that have at least one mapped question
    mapped_objectives = sum(
        r.get('objective_count', 0) for r in rows
        if r.get('question_count', 0) > 0
    )
    coverage_pct = (
        round(mapped_objectives / total_objectives * 100)
        if total_objectives else 0
    )
    return jsonify({
        'success': True,
        'coverage': {
            'total_objectives': total_objectives,
            'mapped_objectives': mapped_objectives,
            'coverage_percent': coverage_pct,
            'unmapped_count': total_objectives - mapped_objectives,
            'positions': rows,
        },
    })


@curriculum_bp.route(
    '/frameworks/<int:framework_id>/relevance', methods=['GET'],
)
@admin_required
def get_relevance(framework_id):
    """Get relevance weights for a curriculum framework."""
    weights = CurriculumService.get_exam_relevance_weights(framework_id)
    return jsonify({'success': True, 'relevance': weights})


@curriculum_bp.route('/frameworks/<int:framework_id>/coverage-report', methods=['GET'])
@admin_required
def get_coverage_report(framework_id):
    """Combined coverage + gap report for a curriculum framework."""
    report = CurriculumService.get_coverage_report(framework_id)
    return jsonify({'success': True, **report})


@curriculum_bp.route('/frameworks/<int:framework_id>/prognosis', methods=['GET'])
@admin_required
def get_prognosis(framework_id):
    """Get exam prognosis for all positions in a framework."""
    from app.application.services.exams.prognosis_service import PrognosisService
    predictions = PrognosisService.predict_all(framework_id)
    return jsonify({'success': True, 'predictions': predictions})


@curriculum_bp.route('/positions/<int:position_id>/generate-questions', methods=['POST'])
@admin_required
def generate_questions(position_id):
    """Generate AI exam questions for a curriculum position."""
    body = request.get_json(silent=True) or {}
    try:
        from app.application.services.exams.question_generator_service import QuestionGeneratorService
        questions = QuestionGeneratorService.generate_for_position(
            position_id=position_id,
            count=body.get('count', 3),
            difficulty=body.get('difficulty', 'mittel'),
            style=body.get('style', 'multiple_choice'),
            provider=body.get('provider'),
            model=body.get('model'),
        )
        return jsonify({'success': True, 'questions': questions})
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400


# --- Helpers ---

def _sse(event: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extract text from raw PDF bytes.

    Uses PyMuPDF (fitz) as primary extractor for robust handling of
    complex PDFs, with PyPDF2 as fallback.
    """
    import io

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        doc.close()
        return '\n'.join(pages)
    except ImportError:
        pass

    from PyPDF2 import PdfReader
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = [page.extract_text() or '' for page in reader.pages]
    return '\n'.join(pages)
