"""Exam Quality Checker — validates completeness of exam data.

Checks question text, solutions, points, types, and anlagen references.
"""
import logging
import re
from typing import Dict, List

from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.infrastructure.persistence.repositories.exams.core import (
    ExamRepository,
)

logger = logging.getLogger(__name__)

# Minimum thresholds
_MIN_TEXT_LENGTH = 20
_VALID_TYPES = {
    'mcq', 'multiple_choice', 'true_false', 'fill_blank',
    'essay', 'code', 'case_study', 'calculation',
    'drag_drop', 'matching', 'ordering', 'short_answer',
}


def generate_quality_report() -> Dict:
    """Generate a full quality report for all ready exams."""
    questions = ExamQuestionRepository.get_quality_report_data()
    anlagen_rows = ExamQuestionRepository.get_anlagen_numbers_by_exam()
    anlagen_map = {
        str(r['exam_id']): set(r['numbers'])
        for r in anlagen_rows
    }

    exams = ExamRepository.find_archive_exams(status='ready')
    exam_question_counts = {}
    for q in questions:
        eid = str(q['exam_id'])
        exam_question_counts[eid] = exam_question_counts.get(eid, 0) + 1

    issues = []
    for q in questions:
        issues.extend(_check_question(q, anlagen_map))

    # Check for exams with 0 questions
    for exam in (exams or []):
        eid = str(exam['exam_id'])
        if exam_question_counts.get(eid, 0) == 0:
            issues.append({
                'exam_id': eid,
                'exam_title': exam.get('title', ''),
                'question_id': None,
                'question_number': None,
                'issue_type': 'empty_exam',
                'detail': 'Exam has 0 questions',
            })

    summary = _build_summary(issues, len(exams or []), len(questions))
    return {
        'total_exams': len(exams or []),
        'total_questions': len(questions),
        'issue_count': len(issues),
        'issues': issues,
        'summary': summary,
    }


def _check_question(q: Dict, anlagen_map: Dict) -> List[Dict]:
    """Run all checks on a single question."""
    issues = []
    base = {
        'exam_id': str(q['exam_id']),
        'exam_title': q.get('exam_title', ''),
        'question_id': str(q['question_id']),
        'question_number': q.get('question_number', ''),
    }

    text = q.get('question_text') or ''
    if len(text) < _MIN_TEXT_LENGTH:
        issues.append({**base, 'issue_type': 'short_text',
                       'detail': f'question_text only {len(text)} chars'})

    sol = q.get('solution_text') or ''
    if not sol:
        has_pdf = bool(q.get('solution_pdf_path'))
        issues.append({**base, 'issue_type': 'missing_solution',
                       'detail': f'No solution_text (PDF: {"yes" if has_pdf else "no"})'})

    points = q.get('points')
    if not points or float(points) <= 0:
        issues.append({**base, 'issue_type': 'missing_points',
                       'detail': 'points is NULL or 0'})

    q_type = q.get('question_type') or ''
    if q_type not in _VALID_TYPES:
        issues.append({**base, 'issue_type': 'invalid_type',
                       'detail': f'question_type "{q_type}" not valid'})

    # Check anlagen references (e.g. "Anlage 3" in text)
    refs = re.findall(r'Anlage\s+(\d+)', text, re.IGNORECASE)
    if refs:
        eid = str(q['exam_id'])
        available = anlagen_map.get(eid, set())
        for ref_num in refs:
            if int(ref_num) not in available:
                issues.append({
                    **base, 'issue_type': 'missing_anlage',
                    'detail': f'References Anlage {ref_num} but not in DB',
                })

    return issues


def _build_summary(issues: List[Dict], total_exams: int, total_q: int) -> Dict:
    """Aggregate issue counts by type."""
    counts = {}
    for issue in issues:
        t = issue['issue_type']
        counts[t] = counts.get(t, 0) + 1
    return {
        'missing_solutions': counts.get('missing_solution', 0),
        'missing_points': counts.get('missing_points', 0),
        'short_text': counts.get('short_text', 0),
        'invalid_type': counts.get('invalid_type', 0),
        'missing_anlage': counts.get('missing_anlage', 0),
        'empty_exams': counts.get('empty_exam', 0),
    }
