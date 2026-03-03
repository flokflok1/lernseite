"""
Exam Archive Admin API

Endpoints for managing the real IHK exam archive:
- Scan filesystem for exam PDFs
- Import PDFs into the database
- Queue AI analysis for question extraction
- List archive exams and their questions

All endpoints require admin authentication.
"""

import os
import logging
from flask import Blueprint, jsonify, request

from app.api.middleware.auth import admin_required
from app.application.services.exams.archive_service import ExamArchiveService
from app.infrastructure.persistence.repositories.exams.core import (
    ExamRepository,
    ExamQuestionRepository,
)
from app.infrastructure.tasks.exam_archive_tasks import analyze_exam_pdf_task

logger = logging.getLogger(__name__)

archive_bp = Blueprint(
    'exam_archive_admin',
    __name__,
    url_prefix='/admin/exam-archive',
)

# Default AP1 folder — resolved relative to backend/ directory
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
_DEFAULT_AP1_FOLDER = os.path.normpath(
    os.path.join(_BACKEND_DIR, '..', 'AP 1')
)


def _get_ap1_folder() -> str:
    """
    Get the AP1 folder path from query param or default.

    Query param: ?folder=/absolute/path
    Default: <project_root>/AP 1/
    """
    folder = request.args.get('folder')
    if folder and os.path.isabs(folder):
        return folder
    return _DEFAULT_AP1_FOLDER


@archive_bp.route('/scan', methods=['GET'])
@admin_required
def scan_folder():
    """
    Scan the AP1 folder for exam PDFs without importing.

    Returns list of found papers with parsed metadata.
    Query param: ?folder=/path (optional, defaults to AP 1/)
    """
    folder = _get_ap1_folder()

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
    Scan and import all exam PDFs from the AP1 folder into the DB.

    Skips duplicates (by pdf_path). Extracts text from each PDF.
    Query param: ?folder=/path (optional, defaults to AP 1/)
    """
    folder = _get_ap1_folder()

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
        'exams': _serialize_exam_list(exams),
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
        'questions': _serialize_question_list(questions),
    })


def _serialize_exam_list(exams: list) -> list:
    """Serialize exam records for JSON response."""
    result = []
    for e in exams:
        result.append({
            'exam_id': str(e.get('exam_id', '')),
            'title': e.get('title', ''),
            'semester': e.get('semester'),
            'year': e.get('year'),
            'season': e.get('season'),
            'part': e.get('part'),
            'profession': e.get('profession'),
            'analysis_status': e.get('analysis_status', 'pending'),
            'question_count': e.get('question_count', 0),
            'pdf_path': e.get('pdf_path'),
            'created_at': (
                e['created_at'].isoformat()
                if e.get('created_at') else None
            ),
        })
    return result


def _serialize_question_list(questions: list) -> list:
    """Serialize question records for JSON response."""
    result = []
    for q in questions:
        data = q.get('data')
        if isinstance(data, str):
            try:
                import json
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                pass

        result.append({
            'question_id': str(q.get('question_id', '')),
            'question_number': q.get('question_number', ''),
            'question_type': q.get('question_type', ''),
            'question_text': q.get('question_text', ''),
            'points': q.get('points', 0),
            'order_index': q.get('order_index', 0),
            'scenario_title': q.get('scenario_title', ''),
            'scenario_text': q.get('scenario_text', ''),
            'topics': q.get('topics', []),
            'solution_text': q.get('solution_text', ''),
            'renderer_data': data,
        })
    return result
