"""
Exam Systems - Chapter Completion Routes (User Journey)

Endpoints for taking Chapter Completion exams.

Endpoints:
  POST   /exams/chapter-completion/:exam_id/start - Start Chapter Completion exam
  POST   /exams/chapter-completion/attempts/:attempt_id/submit - Submit complete exam
  GET    /exams/chapter-completion/attempts/:attempt_id/results - Get results

Phase: 5.3.2 - Exam Systems Domain
Reference: 02a_System-Features.md (chapter_completion_system)
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal

from src.api.exam_systems.core.domain.repositories import ExamRepository
from src.api.exam_systems.core.domain.factories import ExamAttemptFactory
from src.api.exam_systems.core.domain.value_objects import ExamScore, GradingCriteria


# Blueprint
chapter_completion_exams_user_bp = Blueprint('exam_systems_chapter_completion_exams_user', __name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class ChapterCompletionSubmit(BaseModel):
    """Request model for submitting complete chapter exam"""
    answers: List[Dict[str, Any]] = Field(..., description="All answers")


# ============================================================================
# Endpoints
# ============================================================================

@chapter_completion_exams_user_bp.route('/exams/chapter-completion/<exam_id>/start', methods=['POST'])
@jwt_required()
def start_chapter_completion_exam(exam_id: str):
    """
    Start a new Chapter Completion exam attempt.

    Args:
        exam_id: UUID of the exam

    Response:
        201: Created
        404: Exam not found
        400: Validation error
        500: Internal server error
    """
    try:
        user_id = get_jwt_identity()

        # Get exam
        exam = ExamRepository.get_exam_by_id(exam_id)
        if not exam:
            return jsonify({
                "success": False,
                "error": {"code": "EXAM_NOT_FOUND", "message": f"Exam {exam_id} not found"}
            }), 404

        if exam['exam_type'] != 'chapter_completion':
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_EXAM_TYPE", "message": "This is not a Chapter Completion exam"}
            }), 400

        if not exam['is_active']:
            return jsonify({
                "success": False,
                "error": {"code": "EXAM_INACTIVE", "message": "This exam is not active"}
            }), 400

        # Check for existing in-progress attempts
        existing_attempts = ExamRepository.get_user_attempts(user_id, exam_id)
        for attempt in existing_attempts:
            if attempt['status'] == 'in_progress':
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "EXAM_IN_PROGRESS",
                        "message": "You already have an exam in progress",
                        "attempt_id": attempt['attempt_id']
                    }
                }), 400

        # Create attempt
        attempt_data = ExamAttemptFactory.create_attempt(
            user_id=user_id,
            exam_id=exam_id,
            time_limit_minutes=exam['time_limit_minutes']
        )

        attempt = ExamRepository.start_exam_attempt(attempt_data)

        # Get questions
        questions = ExamRepository.get_exam_questions(exam_id)
        questions_safe = [
            {
                'question_id': q['question_id'],
                'question_type': q['question_type'],
                'question_text': q['question_text'],
                'points': q['points'],
                'options': q['options'],
                'order_index': q['order_index']
            }
            for q in questions
        ]

        return jsonify({
            "success": True,
            "data": {
                **attempt,
                "time_limit_minutes": exam['time_limit_minutes'],
                "questions": questions_safe,
                "total_questions": len(questions_safe),
                "config": exam['config']
            }
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "START_EXAM_ERROR", "message": str(e)}
        }), 500


@chapter_completion_exams_user_bp.route('/exams/chapter-completion/attempts/<attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_chapter_completion_exam(attempt_id: str):
    """
    Submit complete chapter exam.

    Args:
        attempt_id: UUID of the exam attempt

    Request Body:
        {
            "answers": [
                {"question_id": "uuid", "answer": [0, 1]},
                {"question_id": "uuid", "answer": [2]},
                ...
            ]
        }

    Response:
        200: Success
        404: Attempt not found
        400: Validation error
        500: Internal server error
    """
    try:
        user_id = get_jwt_identity()

        # Get attempt
        attempt = ExamRepository.get_attempt_by_id(attempt_id)
        if not attempt:
            return jsonify({
                "success": False,
                "error": {"code": "ATTEMPT_NOT_FOUND", "message": f"Attempt {attempt_id} not found"}
            }), 404

        # Verify ownership
        if attempt['user_id'] != user_id:
            return jsonify({
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "Not your exam attempt"}
            }), 403

        # Check status
        if attempt['status'] != 'in_progress':
            return jsonify({
                "success": False,
                "error": {"code": "EXAM_NOT_IN_PROGRESS", "message": f"Exam status: {attempt['status']}"}
            }), 400

        # Check expiration
        if attempt['expires_at'] and datetime.utcnow() > attempt['expires_at']:
            return jsonify({
                "success": False,
                "error": {"code": "EXAM_EXPIRED", "message": "Time limit exceeded"}
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_REQUEST", "message": "Request body required"}
            }), 400

        try:
            submit_request = ChapterCompletionSubmit(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        # Get questions
        questions = ExamRepository.get_exam_questions(attempt['exam_id'])
        questions_map = {q['question_id']: q for q in questions}

        # Grade all answers
        total_points = Decimal("0")
        earned_points = Decimal("0")

        for answer_data in submit_request.answers:
            question_id = answer_data.get('question_id')
            user_answer = answer_data.get('answer', [])

            if question_id not in questions_map:
                continue

            question = questions_map[question_id]
            total_points += Decimal(str(question['points']))

            # Grade answer
            correct_answers = question['correct_answer']
            is_correct = sorted(correct_answers) == sorted(user_answer)

            # Partial credit allowed
            if is_correct:
                points_earned = Decimal(str(question['points']))
            elif question.get('allow_partial_credit', True):
                # Simple partial credit: half points if partially correct
                correct_set = set(correct_answers)
                user_set = set(user_answer)
                if correct_set & user_set:  # Some overlap
                    points_earned = Decimal(str(question['points'])) / 2
                else:
                    points_earned = Decimal("0")
            else:
                points_earned = Decimal("0")

            earned_points += points_earned

            # Save answer
            ExamRepository.submit_answer({
                'attempt_id': attempt_id,
                'question_id': question_id,
                'answer': user_answer,
                'points_earned': float(points_earned),
                'is_correct': is_correct
            })

        # Get exam to check passing percentage
        exam = ExamRepository.get_exam_by_id(attempt['exam_id'])
        grading_criteria = GradingCriteria.chapter_completion_standard()

        # Calculate score
        score = ExamScore.calculate(
            points_earned=earned_points,
            points_total=total_points,
            grading_criteria=grading_criteria
        )

        # Complete attempt
        score_data = {
            'points_earned': float(score.points_earned),
            'percentage': float(score.percentage),
            'passed': score.passed
        }
        completed_attempt = ExamRepository.complete_exam_attempt(attempt_id, score_data)

        return jsonify({
            "success": True,
            "data": {
                **completed_attempt,
                "total_questions": len(questions),
                "answers_submitted": len(submit_request.answers),
                "message": "Congratulations! You passed the chapter exam." if score.passed else "Exam completed. You did not pass this time."
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "SUBMIT_EXAM_ERROR", "message": str(e)}
        }), 500


@chapter_completion_exams_user_bp.route('/exams/chapter-completion/attempts/<attempt_id>/results', methods=['GET'])
@jwt_required()
def get_chapter_completion_results(attempt_id: str):
    """
    Get chapter completion exam results.

    Args:
        attempt_id: UUID of the exam attempt

    Response:
        200: Success
        404: Attempt not found
        400: Exam not completed
        500: Internal server error
    """
    try:
        user_id = get_jwt_identity()

        # Get attempt
        attempt = ExamRepository.get_attempt_by_id(attempt_id)
        if not attempt:
            return jsonify({
                "success": False,
                "error": {"code": "ATTEMPT_NOT_FOUND", "message": f"Attempt {attempt_id} not found"}
            }), 404

        # Verify ownership
        if attempt['user_id'] != user_id:
            return jsonify({
                "success": False,
                "error": {"code": "UNAUTHORIZED", "message": "Not your exam attempt"}
            }), 403

        # Check if completed
        if attempt['status'] not in ['completed', 'graded', 'passed', 'failed']:
            return jsonify({
                "success": False,
                "error": {"code": "EXAM_NOT_COMPLETED", "message": "Exam is not completed yet"}
            }), 400

        # Get answers
        answers = ExamRepository.get_attempt_answers(attempt_id)

        # Get questions
        questions = ExamRepository.get_exam_questions(attempt['exam_id'])
        questions_map = {q['question_id']: q for q in questions}

        answers_with_details = [
            {
                'question_id': ans['question_id'],
                'question_text': questions_map[ans['question_id']]['question_text'],
                'user_answer': ans['answer'],
                'correct_answer': questions_map[ans['question_id']]['correct_answer'],
                'is_correct': ans['is_correct'],
                'points_earned': ans['points_earned'],
                'points_possible': questions_map[ans['question_id']]['points'],
                'explanation': questions_map[ans['question_id']].get('explanation')
            }
            for ans in answers
        ]

        score = {
            'points_earned': float(attempt['score_points'] or 0),
            'points_total': sum(q['points'] for q in questions),
            'percentage': float(attempt['score_percentage'] or 0),
            'passed': attempt['passed'],
            'grade': ExamScore.calculate(
                Decimal(str(attempt['score_points'] or 0)),
                Decimal(str(sum(q['points'] for q in questions))),
                GradingCriteria.chapter_completion_standard()
            ).get_grade_letter()
        }

        return jsonify({
            "success": True,
            "data": {
                "attempt_id": attempt_id,
                "exam_id": attempt['exam_id'],
                "status": attempt['status'],
                "started_at": attempt['started_at'].isoformat(),
                "completed_at": attempt['completed_at'].isoformat() if attempt['completed_at'] else None,
                "score": score,
                "answers": answers_with_details,
                "total_questions": len(questions)
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_RESULTS_ERROR", "message": str(e)}
        }), 500


__all__ = ['chapter_completion_exams_user_bp']
