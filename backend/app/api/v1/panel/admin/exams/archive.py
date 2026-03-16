"""Exam Archive Admin API — scan, import, analyze, CRUD for exam sessions."""

import os
import logging
from flask import Blueprint, jsonify, request

from app.api.middleware.auth import admin_required
from app.application.services.exams.archive_service import ExamArchiveService
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.infrastructure.persistence.repositories.exams.sessions import (
    ExamSessionRepository,
)
from app.infrastructure.tasks.exam_archive_tasks import analyze_exam_pdf_task
from app.api.v1.panel.admin.exams.archive_serializers import (
    serialize_exam_list,
    serialize_question_list,
)

logger = logging.getLogger(__name__)

archive_bp = Blueprint(
    'exam_archive_admin',
    __name__,
    url_prefix='/admin/exam-archive',
)

# Default exam folder — resolved relative to backend/ directory
_BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
            )
        )
    )
)
_DEFAULT_EXAM_FOLDER = os.path.normpath(
    os.path.join(_BACKEND_DIR, '..', 'AP 1')
)


def _get_exam_folder() -> str:
    """
    Get the exam folder path from query param or default.

    Query param: ?folder=/absolute/path
    Default: <project_root>/AP 1/
    """
    folder = request.args.get('folder')
    if folder and os.path.isabs(folder):
        return folder
    return _DEFAULT_EXAM_FOLDER


@archive_bp.route('/scan', methods=['GET'])
@admin_required
def scan_folder():
    """
    Scan the exam folder for PDFs and images without importing.

    Returns list of found papers with parsed metadata.
    Query param: ?folder=/path (optional, defaults to AP 1/)
    """
    folder = _get_exam_folder()

    if not os.path.isdir(folder):
        return jsonify({
            'success': False,
            'error': f'Folder not found: {folder}',
        }), 404

    papers = ExamArchiveService.scan_folder(folder)

    return jsonify({
        'success': True,
        'folder': folder,
        'count': len(papers),
        'papers': [
            {
                'filename': p['filename'],
                'filepath': p['filepath'],
                'parent_folder': p['parent_folder'],
                'meta': p['meta'],
                'has_solution': p.get('solution_filepath') is not None,
            }
            for p in papers
        ],
    })


@archive_bp.route('/import', methods=['POST'])
@admin_required
def import_folder():
    """
    Scan and import all exam files from the exam folder into the DB.

    Skips duplicates (by pdf_path). Extracts text from each PDF.
    Query param: ?folder=/path (optional, defaults to AP 1/)
    """
    folder = _get_exam_folder()

    if not os.path.isdir(folder):
        return jsonify({
            'success': False,
            'error': f'Folder not found: {folder}',
        }), 404

    summary = ExamArchiveService.import_folder(folder)

    return jsonify({
        'success': True,
        'folder': folder,
        'summary': summary,
    })


@archive_bp.route('/analyze/<exam_id>', methods=['POST'])
@admin_required
def analyze_exam(exam_id):
    """
    Queue AI analysis for a single exam.

    Extracts scenarios and questions from the exam's raw_text.
    Optional JSON body: {"provider": "openai", "model": "gpt-4o"}
    """
    exam = ExamRepository.find_by_id(exam_id)
    if not exam:
        return jsonify({
            'success': False,
            'error': 'Exam not found',
        }), 404

    # Allow caller to specify provider/model (G07: no hardcoding)
    body = request.get_json(silent=True) or {}
    provider = body.get('provider', 'openai')
    model = body.get('model', 'gpt-4o')

    task = analyze_exam_pdf_task.delay(
        exam_id, provider=provider, model=model
    )

    return jsonify({
        'success': True,
        'exam_id': exam_id,
        'task_id': task.id,
        'message': 'Analysis queued',
    })


@archive_bp.route('/analyze-all', methods=['POST'])
@admin_required
def analyze_all():
    """
    Queue AI analysis for all pending archive exams.

    Only queues exams with analysis_status='pending'.
    Optional JSON body: {"provider": "openai", "model": "gpt-4o"}
    """
    body = request.get_json(silent=True) or {}
    provider = body.get('provider', 'openai')
    model = body.get('model', 'gpt-4o')

    pending_exams = ExamRepository.find_archive_exams(status='pending')
    task_ids = []

    for exam in pending_exams:
        eid = exam.get('exam_id')
        if not eid:
            continue
        task = analyze_exam_pdf_task.delay(
            str(eid), provider=provider, model=model
        )
        task_ids.append({
            'exam_id': str(eid),
            'task_id': task.id,
        })

    return jsonify({
        'success': True,
        'queued_count': len(task_ids),
        'tasks': task_ids,
    })


@archive_bp.route('/list', methods=['GET'])
@admin_required
def list_archive_exams():
    """
    List all archive exams with status and question counts.

    Query param: ?status=pending|analyzing|ready|failed (optional)
    """
    status = request.args.get('status')
    exams = ExamRepository.find_archive_exams(status=status)

    return jsonify({
        'success': True,
        'count': len(exams),
        'exams': serialize_exam_list(exams),
    })


@archive_bp.route('/<exam_id>/questions', methods=['GET'])
@admin_required
def get_exam_questions(exam_id):
    """
    Get all extracted questions for an archive exam.

    Returns questions ordered by order_index.
    """
    exam = ExamRepository.find_by_id(exam_id)
    if not exam:
        return jsonify({
            'success': False,
            'error': 'Exam not found',
        }), 404

    questions = ExamQuestionRepository.find_by_exam(exam_id)

    return jsonify({
        'success': True,
        'exam_id': exam_id,
        'exam_title': exam.get('title', ''),
        'count': len(questions),
        'questions': serialize_question_list(questions),
    })


@archive_bp.route('/regions', methods=['GET'])
@admin_required
def list_regions():
    """List all available exam regions."""
    regions = ExamSessionRepository.find_all_regions()
    return jsonify({'regions': regions}), 200


@archive_bp.route('/sessions', methods=['GET'])
@admin_required
def list_sessions():
    """Flat session rows for client-side tree building.

    Returns all sessions with full metadata (program, region, exam_type,
    year, season, counts). The frontend builds the tree hierarchy based
    on user-configured group levels.
    """
    program_key = request.args.get('program_key')
    rows = ExamSessionRepository.find_sessions_grouped(program_key)

    return jsonify({
        'rows': [
            {
                'program_key': r['program_key'] or '_unknown',
                'program_name': r['program_name'] or {},
                'provider': r['provider'] or '',
                'icon': r['icon'] or '',
                'program_sort': r['program_sort'] or 0,
                'region': r['region'] or 'alle',
                'region_name': r['region_name'] or {},
                'exam_type': r['exam_type'],
                'type_display_name': r['type_display_name'] or {},
                'type_sort': r['type_sort'] or 0,
                'session_id': str(r['session_id']),
                'year': r['year'],
                'season': r['season'],
                'exam_count': r['exam_count'] or 0,
                'ready_count': r['ready_count'] or 0,
                'total_questions': r['total_questions'] or 0,
            }
            for r in rows
        ],
    }), 200


@archive_bp.route('/sessions/<session_id>/exams', methods=['GET'])
@admin_required
def list_session_exams(session_id):
    """List individual exams (GA1, GA2, WK) within a session."""
    exams = ExamSessionRepository.find_exams_by_session(session_id)
    return jsonify({
        'exams': [
            {
                'exam_id': str(e['exam_id']),
                'title': e.get('title', ''),
                'part': e.get('part'),
                'analysis_status': e.get('analysis_status', 'pending'),
                'upload_source': e.get('upload_source', 'admin'),
                'question_count': e.get('question_count', 0),
            }
            for e in exams
        ],
    }), 200


@archive_bp.route('/sessions/<session_id>/tags', methods=['PATCH'])
@admin_required
def update_session_tags(session_id):
    """Update tags on a session."""
    data = request.get_json()
    tags = data.get('tags', [])
    updated = ExamSessionRepository.update_tags(session_id, tags)
    if not updated:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify({'session_id': str(updated['session_id'])}), 200


@archive_bp.route('/<exam_id>/review', methods=['POST'])
@admin_required
def review_upload(exam_id):
    """
    Moderate a community upload: approve or reject.

    JSON body: {"action": "approve"|"reject", "notes": "..."}
    Approve -> analysis_status='pending' (enters AI pipeline)
    Reject  -> analysis_status='rejected'
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    action = data.get('action')
    notes = data.get('notes', '')

    if action not in ('approve', 'reject'):
        return jsonify({'error': 'action must be approve or reject'}), 400

    exam = ExamRepository.find_by_id(exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    if exam.get('analysis_status') != 'pending_review':
        return jsonify({'error': 'Exam is not pending review'}), 400

    new_status = 'pending' if action == 'approve' else 'rejected'
    ExamRepository.update_analysis_status(exam_id, new_status)

    from app.infrastructure.persistence.database.connection import (
        execute_query,
    )
    execute_query(
        "UPDATE assessments.exams SET moderation_notes = %s WHERE exam_id = %s",
        [notes, exam_id],
    )

    logger.info(
        "Moderation: exam=%s action=%s by admin", exam_id, action
    )
    return jsonify({'status': action + 'd', 'exam_id': str(exam_id)}), 200


@archive_bp.route('/sessions', methods=['POST'])
@admin_required
def create_session():
    """Create a new exam session (folder).

    JSON body: {exam_type_key, year, season, region?}
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    exam_type_key = data.get('exam_type_key')
    year = data.get('year')
    season = data.get('season')
    region = data.get('region', 'alle')

    if not exam_type_key or not year or not season:
        return jsonify({
            'error': 'exam_type_key, year, season required',
        }), 400

    try:
        session = ExamSessionRepository.find_or_create(
            exam_type_key, region, int(year), season,
        )
    except Exception:
        logger.exception("Failed to create session")
        return jsonify({'error': f'Invalid exam_type_key: {exam_type_key}'}), 400

    return jsonify({
        'session_id': str(session['session_id']),
        'exam_type_key': session['exam_type_key'],
        'year': session['year'],
        'season': session['season'],
    }), 201


@archive_bp.route('/sessions/<session_id>', methods=['DELETE'])
@admin_required
def delete_session(session_id):
    """Delete an empty session (folder). Fails if exams exist."""
    session = ExamSessionRepository.find_by_id(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    ok = ExamSessionRepository.delete_session(session_id)
    if not ok:
        return jsonify({
            'error': 'Session has exams — remove them first',
        }), 409
    return jsonify({'deleted': True}), 200


@archive_bp.route('/exams/<exam_id>/move', methods=['PATCH'])
@admin_required
def move_exam(exam_id):
    """Move an exam to a different session.

    JSON body: {target_session_id}
    """
    data = request.get_json()
    if not data or not data.get('target_session_id'):
        return jsonify({'error': 'target_session_id required'}), 400

    exam = ExamRepository.find_by_id(exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    target_id = data['target_session_id']
    target = ExamSessionRepository.find_by_id(target_id)
    if not target:
        return jsonify({'error': 'Target session not found'}), 404

    result = ExamSessionRepository.move_exam(exam_id, target_id)
    return jsonify({
        'exam_id': str(result['exam_id']),
        'session_id': str(result['session_id']),
    }), 200


@archive_bp.route('/<exam_id>/re-analyze', methods=['PUT'])
@admin_required
def re_analyze_exam(exam_id):
    """Delete existing questions and re-queue Vision AI analysis."""
    exam = ExamRepository.find_by_id(exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    ExamQuestionRepository.delete_by_exam_id(exam_id)
    ExamRepository.update_analysis_status(exam_id, 'pending')

    body = request.get_json(silent=True) or {}
    analyze_exam_pdf_task.delay(
        str(exam_id), provider=body.get('provider'), model=body.get('model'),
    )
    logger.info("Re-analysis queued for exam %s", exam_id)
    return jsonify({'status': 'queued', 'exam_id': str(exam_id)}), 200


@archive_bp.route('/re-analyze-all', methods=['PUT'])
@admin_required
def re_analyze_all():
    """Re-analyze all ready exams — delete questions and re-queue."""
    exams = ExamRepository.find_archive_exams(status='ready')
    if not exams:
        return jsonify({'status': 'queued', 'count': 0}), 200

    body = request.get_json(silent=True) or {}
    provider, model = body.get('provider'), body.get('model')

    count = 0
    for exam in exams:
        eid = str(exam.get('exam_id'))
        ExamQuestionRepository.delete_by_exam_id(eid)
        ExamRepository.update_analysis_status(eid, 'pending')
        analyze_exam_pdf_task.delay(eid, provider=provider, model=model)
        count += 1

    logger.info("Re-analysis queued for %d exams", count)
    return jsonify({'status': 'queued', 'count': count}), 200


@archive_bp.route('/exams/<exam_id>', methods=['DELETE'])
@admin_required
def delete_exam(exam_id):
    """Delete an exam and its questions."""
    exam = ExamRepository.find_by_id(exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    ExamSessionRepository.delete_exam(exam_id)
    logger.info("Deleted exam=%s by admin", exam_id)
    return jsonify({'deleted': True}), 200


