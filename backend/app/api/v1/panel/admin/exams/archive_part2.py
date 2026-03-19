"""Exam Archive Admin API — solution analysis endpoints.

Split from archive.py per G01 (500 LOC limit).
"""

import os
import logging

from flask import jsonify, request

from app.api.middleware.auth import admin_required
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
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


@archive_bp.route('/quality-report', methods=['GET'])
@admin_required
def quality_report():
    """Generate quality report for all ready exams."""
    from app.application.services.exams.quality_checker import (
        generate_quality_report,
    )
    report = generate_quality_report()
    return jsonify(report), 200
