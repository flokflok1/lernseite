"""
ExamTrainer Helpers — Grading, solution stripping, and attempt finalization.

Extracted from trainer.py for G01 compliance (max 500 LOC per file).
"""

import json as _json
import logging

from flask import jsonify
from app.infrastructure.persistence.repositories.exams.core import (
    ExamRepository
)
from app.infrastructure.persistence.repositories.exams.trainer import (
    ExamTrainerRepository
)

logger = logging.getLogger(__name__)


def strip_solutions(questions: list) -> list:
    """
    Remove solution fields from question records.

    Strips solution_text, solution, and correctAnswers from
    the response so users cannot see answers.

    Args:
        questions: List of question dicts

    Returns:
        Sanitized question list
    """
    sanitized = []
    for q in questions:
        clean = {
            'question_id': q.get('question_id'),
            'exam_id': q.get('exam_id'),
            'question_text': q.get('question_text', ''),
            'question_type': q.get('question_type', ''),
            'data': q.get('data'),
            'points': q.get('points', 1),
            'scenario_title': q.get('scenario_title', ''),
            'scenario_text': q.get('scenario_text', ''),
            'question_number': q.get('question_number', ''),
            'topics': q.get('topics', []),
            'order_index': q.get('order_index', 0),
        }
        # Also include exam metadata if joined
        if 'exam_title' in q:
            clean['exam_title'] = q['exam_title']
            clean['semester'] = q.get('semester', '')
            clean['year'] = q.get('year')
            clean['part'] = q.get('part', '')
        sanitized.append(clean)
    return sanitized


def grade_answer(question: dict, user_answer) -> dict:
    """
    Auto-grade an answer based on question type.

    Supports MCQ (compare correctAnswers), calculation
    (compare numeric answer), and marks free-text as
    needs_review.

    Args:
        question: Full question record (with solution)
        user_answer: User's submitted answer

    Returns:
        {is_correct, points_earned, needs_review,
         correct_answer, explanation}
    """
    q_type = question.get('question_type', '')
    points = question.get('points', 1)
    solution = question.get('solution') or {}
    solution_text = question.get('solution_text', '')
    data = question.get('data') or {}

    if isinstance(solution, str):
        try:
            solution = _json.loads(solution)
        except (ValueError, TypeError):
            solution = {}

    if isinstance(data, str):
        try:
            data = _json.loads(data)
        except (ValueError, TypeError):
            data = {}

    # MCQ / single-choice / multi-choice grading
    if q_type in (
        'mcq', 'single_choice', 'multi_choice', 'multiple_choice'
    ):
        return _grade_mcq(data, solution, user_answer, points)

    # Calculation / numeric grading
    if q_type in ('calculation', 'numeric'):
        return _grade_calculation(
            solution, user_answer, points, solution_text
        )

    # Free-text / essay — needs manual review
    return {
        'is_correct': None,
        'points_earned': 0,
        'needs_review': True,
        'correct_answer': solution_text or None,
        'explanation': solution_text
    }


def _grade_mcq(data, solution, user_answer, points):
    """Grade multiple-choice question."""
    correct = set()
    if 'correctAnswers' in data:
        correct = set(data['correctAnswers'])
    elif 'correctAnswers' in solution:
        correct = set(solution['correctAnswers'])
    elif 'correct_answer' in solution:
        correct = {solution['correct_answer']}

    if isinstance(user_answer, list):
        user_set = set(user_answer)
    else:
        user_set = {user_answer}

    is_correct = user_set == correct
    return {
        'is_correct': is_correct,
        'points_earned': points if is_correct else 0,
        'needs_review': False,
        'correct_answer': list(correct),
        'explanation': solution.get('explanation', '')
    }


def _grade_calculation(solution, user_answer, points, solution_text):
    """Grade calculation / numeric question."""
    correct_val = solution.get('answer') or solution.get('value')
    if correct_val is None:
        return {
            'is_correct': None,
            'points_earned': 0,
            'needs_review': True,
            'correct_answer': None,
            'explanation': solution_text
        }

    try:
        is_correct = float(user_answer) == float(correct_val)
    except (ValueError, TypeError):
        is_correct = (
            str(user_answer).strip() == str(correct_val).strip()
        )

    return {
        'is_correct': is_correct,
        'points_earned': points if is_correct else 0,
        'needs_review': False,
        'correct_answer': correct_val,
        'explanation': solution_text or solution.get('explanation', '')
    }


def grade_and_record(user, question_id, user_answer, attempt_id):
    """
    Grade an answer, record it, and update topic stats.

    Args:
        user: Current user dict
        question_id: Question UUID
        user_answer: User's answer
        attempt_id: Optional attempt UUID

    Returns:
        Flask JSON response tuple
    """
    from app.infrastructure.persistence.database.connection import fetch_one

    # Fetch full question (with solution) for grading
    query = """
        SELECT * FROM assessments.exam_questions
        WHERE question_id = %s
    """
    question = fetch_one(query, (question_id,))

    if not question:
        return jsonify({
            'success': False, 'error': 'Question not found'
        }), 404

    result = grade_answer(question, user_answer)

    # Record answer if part of an attempt
    if attempt_id:
        ExamTrainerRepository.record_answer(
            attempt_id=attempt_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=result['is_correct'],
            points_earned=result['points_earned'],
            needs_review=result['needs_review']
        )

    # Update topic stats for each topic on the question
    topics = question.get('topics') or []
    for topic in topics:
        ExamTrainerRepository.upsert_topic_stats(
            user_id=user['user_id'],
            topic=topic,
            is_correct=bool(result['is_correct']),
            total_points=question.get('points', 1),
            earned_points=result['points_earned']
        )

    # Track per-question stats for rotation algorithm
    ExamTrainerRepository.upsert_question_stats(
        user_id=str(user['user_id']),
        question_id=question_id,
        is_correct=bool(result['is_correct']),
    )

    return jsonify({
        'success': True,
        'is_correct': result['is_correct'],
        'correct_answer': result['correct_answer'],
        'explanation': result['explanation'],
        'points_earned': result['points_earned'],
        'needs_review': result['needs_review']
    }), 200


def finalize_attempt(attempt, user):
    """
    Calculate final scores and create result record.

    Args:
        attempt: Attempt record dict
        user: Current user dict

    Returns:
        Flask JSON response with results
    """
    answers = ExamTrainerRepository.get_attempt_answers(
        attempt['attempt_id']
    )

    total_points = 0
    earned_points = 0.0
    topic_stats = {}

    for ans in answers:
        max_pts = ans.get('max_points', 1)
        earned = ans.get('points_earned', 0) or 0
        total_points += max_pts
        earned_points += earned

        for topic in (ans.get('topics') or []):
            if topic not in topic_stats:
                topic_stats[topic] = {
                    'total': 0, 'earned': 0, 'correct': 0, 'count': 0
                }
            topic_stats[topic]['total'] += max_pts
            topic_stats[topic]['earned'] += earned
            topic_stats[topic]['count'] += 1
            if ans.get('is_correct'):
                topic_stats[topic]['correct'] += 1

    percentage = round(
        (earned_points / total_points * 100) if total_points > 0 else 0, 1
    )

    exam = ExamRepository.find_by_id(attempt['exam_id'])
    passing_score = (exam or {}).get('passing_score', 50)
    passed = percentage >= passing_score

    # Update attempt status
    ExamTrainerRepository.complete_attempt(
        attempt_id=attempt['attempt_id'],
        score=earned_points,
        total_points=total_points,
        passed=passed
    )

    # Create result record
    ExamTrainerRepository.create_exam_result(
        attempt_id=attempt['attempt_id'],
        user_id=user['user_id'],
        exam_id=attempt['exam_id'],
        score=earned_points,
        total_points=total_points,
        percentage=percentage,
        passed=passed,
        results_by_topic=topic_stats
    )

    return jsonify({
        'success': True,
        'score': earned_points,
        'total_points': total_points,
        'percentage': percentage,
        'passed': passed,
        'results_by_topic': topic_stats
    }), 200
