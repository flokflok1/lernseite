"""Exam Archive Admin API — solution analysis + folder-level analysis endpoints.

Split from archive.py per G01 (500 LOC limit).
"""

import os
import logging

from flask import jsonify, request

from app.api.middleware.auth import admin_required
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.infrastructure.persistence.repositories.exams.folders import (
    ArchiveFolderRepository,
)
from app.infrastructure.tasks.exam_archive_tasks import analyze_exam_pdf_task
from app.api.v1.panel.admin.exams.archive import archive_bp

logger = logging.getLogger(__name__)


@archive_bp.route('/<exam_id>/analyze-solutions', methods=['PUT'])
@admin_required
def analyze_solutions(exam_id):
    """Analyze the solution PDF for an exam and apply to questions."""
    exam = ExamRepository.find_by_id(exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    pdf_path = exam.get('solution_pdf_path')
    if not pdf_path:
        return jsonify({'error': 'No solution PDF'}), 404

    if not os.path.exists(pdf_path):
        return jsonify({'error': 'Solution PDF file not found'}), 404

    from app.application.services.exams.solution_analyzer import (
        analyze_solution_pdf,
        apply_solutions_to_exam,
    )

    solutions = analyze_solution_pdf(pdf_path)
    if not solutions:
        return jsonify({'error': 'Analysis failed'}), 500

    count = apply_solutions_to_exam(str(exam_id), solutions)
    return jsonify({
        'status': 'done',
        'solutions_extracted': len(solutions),
        'questions_updated': count,
    }), 200


@archive_bp.route('/analyze-all-solutions', methods=['PUT'])
@admin_required
def analyze_all_solutions():
    """Analyze solution PDFs for all exams that have one."""
    from app.application.services.exams.solution_analyzer import (
        analyze_solution_pdf,
        apply_solutions_to_exam,
    )

    exams = ExamRepository.find_archive_exams(status='ready')
    total = 0
    for exam in (exams or []):
        pdf_path = exam.get('solution_pdf_path')
        if not pdf_path or not os.path.exists(pdf_path):
            continue
        solutions = analyze_solution_pdf(pdf_path)
        if solutions:
            count = apply_solutions_to_exam(
                str(exam['exam_id']), solutions,
            )
            total += count
            logger.info(
                "Solutions applied: %s → %d questions",
                exam['title'], count,
            )

    return jsonify({'status': 'done', 'total_updated': total}), 200


@archive_bp.route('/<exam_id>/generate-solutions', methods=['PUT'])
@admin_required
def generate_solutions(exam_id):
    """Generate AI solutions for questions without solution_text."""
    exam = ExamRepository.find_by_id(exam_id)
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404

    from app.application.services.exams.solution_generator import (
        generate_solutions_for_exam,
    )
    count = generate_solutions_for_exam(str(exam_id))
    return jsonify({
        'status': 'done',
        'solutions_generated': count,
    }), 200


@archive_bp.route('/generate-all-solutions', methods=['PUT'])
@admin_required
def generate_all_solutions():
    """Generate AI solutions for ALL exams with missing solutions."""
    from app.application.services.exams.solution_generator import (
        generate_solutions_for_exam,
    )
    exams = ExamRepository.find_archive_exams(status='ready')
    total = 0
    for exam in (exams or []):
        count = generate_solutions_for_exam(str(exam['exam_id']))
        if count:
            total += count
            logger.info(
                "Generated %d solutions for %s",
                count, exam.get('title'),
            )
    return jsonify({'status': 'done', 'total_generated': total}), 200


@archive_bp.route('/quality-report', methods=['GET'])
@admin_required
def quality_report():
    """Generate quality report for all ready exams."""
    from app.application.services.exams.quality_checker import (
        generate_quality_report,
    )
    report = generate_quality_report()
    return jsonify(report), 200


@archive_bp.route('/regenerate-diagrams', methods=['POST'])
@admin_required
def regenerate_diagrams():
    """Regenerate text-description diagram Anlagen as visual HTML.

    Finds Anlagen that contain prose descriptions of diagrams and
    converts them to structured HTML using diagram CSS classes.
    """
    try:
        from app.application.services.exams.diagram_regenerator import (
            regenerate_all_text_diagrams,
        )
        result = regenerate_all_text_diagrams()
        return jsonify({'success': True, **result}), 200
    except Exception:
        logger.exception("Failed to regenerate diagrams")
        return jsonify({'success': False, 'error': 'Regeneration failed'}), 500


# ── Folder-Level Analysis ──────────────────────────────────


@archive_bp.route('/folders/<folder_id>/analyze', methods=['POST'])
@admin_required
def analyze_folder(folder_id):
    """Queue AI analysis for all pending exams in a folder (recursive)."""
    files = ArchiveFolderRepository.find_files_in_folder_recursive(folder_id)
    logger.info("Folder %s: found %d total files", folder_id, len(files))
    pending = [f for f in files if f.get('analysis_status') == 'pending']
    logger.info("Folder %s: %d pending files", folder_id, len(pending))

    if not pending:
        return jsonify({'status': 'queued', 'count': 0}), 200

    body = request.get_json(silent=True) or {}
    provider = body.get('provider')
    model = body.get('model')

    count = 0
    for f in pending:
        eid = str(f['exam_id'])
        analyze_exam_pdf_task.delay(eid, provider=provider, model=model)
        count += 1

    logger.info("Folder %s: queued analysis for %d pending exams", folder_id, count)
    return jsonify({'status': 'queued', 'count': count}), 200


@archive_bp.route('/folders/<folder_id>/re-analyze', methods=['PUT'])
@admin_required
def re_analyze_folder(folder_id):
    """Re-analyze all exams in a folder (recursive) — delete questions and re-queue."""
    files = ArchiveFolderRepository.find_files_in_folder_recursive(folder_id)
    if not files:
        return jsonify({'status': 'queued', 'count': 0}), 200

    body = request.get_json(silent=True) or {}
    provider = body.get('provider')
    model = body.get('model')

    count = 0
    for f in files:
        eid = str(f['exam_id'])
        ExamQuestionRepository.delete_by_exam_id(eid)
        ExamQuestionRepository.delete_anlagen_by_exam_id(eid)
        ExamRepository.update_analysis_status(eid, 'pending')
        analyze_exam_pdf_task.delay(eid, provider=provider, model=model)
        count += 1

    logger.info("Folder %s: re-analysis queued for %d exams", folder_id, count)
    return jsonify({'status': 'queued', 'count': count}), 200
