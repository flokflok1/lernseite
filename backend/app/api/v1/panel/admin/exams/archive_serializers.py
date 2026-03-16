"""Serialization helpers for exam archive API responses (split from archive.py per G01)."""

import json as _json


def serialize_exam_list(exams: list) -> list:
    """Serialize exam records for JSON response."""
    return [{
        'exam_id': str(e.get('exam_id', '')),
        'title': e.get('title', ''),
        'semester': e.get('semester'), 'year': e.get('year'),
        'season': e.get('season'), 'part': e.get('part'),
        'profession': e.get('profession'),
        'analysis_status': e.get('analysis_status', 'pending'),
        'question_count': e.get('question_count', 0),
        'pdf_path': e.get('pdf_path'),
        'created_at': (
            e['created_at'].isoformat() if e.get('created_at') else None
        ),
    } for e in exams]


def serialize_question_list(questions: list) -> list:
    """Serialize question records for JSON response."""
    result = []
    for q in questions:
        data = q.get('data')
        if isinstance(data, str):
            try:
                data = _json.loads(data)
            except (ValueError, TypeError):
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
