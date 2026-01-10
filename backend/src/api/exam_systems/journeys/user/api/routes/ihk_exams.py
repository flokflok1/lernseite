"""
Exam Systems - IHK Exams Routes (User Journey)

Endpoints for taking IHK exams.

Endpoints:
  POST   /exams/ihk/:exam_id/start - Start IHK exam attempt
  POST   /exams/ihk/attempts/:attempt_id/answer - Submit answer
  GET    /exams/ihk/attempts/:attempt_id/results - Get exam results

Phase: 5.3.2 - Exam Systems Domain
Reference: 02a_System-Features.md (ihk_exam_system)
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field
from typing import Any, List
from datetime import datetime
from decimal import Decimal

from src.api.exam_systems.core.domain.repositories import ExamRepository
from src.api.exam_systems.core.domain.factories import ExamAttemptFactory
from src.api.exam_systems.core.domain.value_objects import ExamScore, GradingCriteria


# Blueprint
ihk_exams_user_bp = Blueprint('exam_systems_ihk_exams_user', __name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class AnswerSubmit(BaseModel):
    """Request model for submitting answer"""
    question_id: str = Field(..., description="Question UUID")
    answer: List[int] = Field(..., description="Selected answer indices")


# ============================================================================
# Endpoints
# ============================================================================

@ihk_exams_user_bp.route('/exams/ihk/<exam_id>/start', methods=['POST'])
@jwt_required()
def start_ihk_exam(exam_id: str):
    """
    Start a new IHK exam attempt.

    Args:
        exam_id: UUID of the exam

    Response:
        201: Created
            {
                "success": true,
                "data": {
                    "attempt_id": "uuid",
                    "exam_id": "uuid",
                    "started_at": "2024-01-10T12:00:00Z",
                    "expires_at": "2024-01-10T13:00:00Z",
                    "time_limit_minutes": 60,
                    "questions": [...]
                }
            }
        404: Exam not found
        400: Exam already in progress
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

        if exam['exam_type'] != 'ihk':
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_EXAM_TYPE", "message": "This is not an IHK exam"}
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

        # Create attempt using factory
        attempt_data = ExamAttemptFactory.create_attempt(
            user_id=user_id,
            exam_id=exam_id,
            time_limit_minutes=exam['time_limit_minutes']
        )

        # Save attempt
        attempt = ExamRepository.start_exam_attempt(attempt_data)

        # Get questions (without correct answers)
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
                "total_questions": len(questions_safe)
            }
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "START_EXAM_ERROR", "message": str(e)}
        }), 500


@ihk_exams_user_bp.route('/exams/ihk/attempts/<attempt_id>/answer', methods=['POST'])
@jwt_required()
def submit_ihk_answer(attempt_id: str):
    """
    Submit an answer for a question.

    Args:
        attempt_id: UUID of the exam attempt

    Request Body:
        {
            "question_id": "uuid",
            "answer": [0, 2]  // selected indices
        }

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "answer_id": "uuid",
                    "question_id": "uuid",
                    "submitted": true
                }
            }
        404: Attempt not found
        400: Exam expired or already completed
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
            answer_request = AnswerSubmit(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        # Get question to check correct answer
        questions = ExamRepository.get_exam_questions(attempt['exam_id'])
        question = next((q for q in questions if q['question_id'] == answer_request.question_id), None)

        if not question:
            return jsonify({
                "success": False,
                "error": {"code": "QUESTION_NOT_FOUND", "message": "Question not found in this exam"}
            }), 404

        # Grade answer
        correct_answers = question['correct_answer']
        user_answers = sorted(answer_request.answer)
        is_correct = sorted(correct_answers) == user_answers
        points_earned = question['points'] if is_correct else 0

        # Save answer
        answer_data = {
            'attempt_id': attempt_id,
            'question_id': answer_request.question_id,
            'answer': answer_request.answer,
            'points_earned': points_earned,
            'is_correct': is_correct
        }
        answer = ExamRepository.submit_answer(answer_data)

        return jsonify({
            "success": True,
            "data": {
                "answer_id": answer['answer_id'],
                "question_id": answer['question_id'],
                "submitted": True,
                "feedback": "Answer recorded" if not is_correct else "Answer recorded"
                # Don't reveal correctness immediately for IHK exams
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "SUBMIT_ANSWER_ERROR", "message": str(e)}
        }), 500


@ihk_exams_user_bp.route('/exams/ihk/attempts/<attempt_id>/results', methods=['GET'])
@jwt_required()
def get_ihk_exam_results(attempt_id: str):
    """
    Get exam results (only available after completion).

    Args:
        attempt_id: UUID of the exam attempt

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "attempt_id": "uuid",
                    "exam_id": "uuid",
                    "status": "completed",
                    "score": {
                        "points_earned": 45,
                        "points_total": 50,
                        "percentage": 90.0,
                        "passed": true,
                        "grade": "A"
                    },
                    "answers": [
                        {
                            "question_id": "uuid",
                            "user_answer": [0, 1],
                            "correct_answer": [0, 1],
                            "is_correct": true,
                            "points_earned": 1
                        },
                        ...
                    ]
                }
            }
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

        # Get questions to show correct answers
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

        # Calculate score
        score = {
            'points_earned': float(attempt['score_points'] or 0),
            'points_total': sum(q['points'] for q in questions),
            'percentage': float(attempt['score_percentage'] or 0),
            'passed': attempt['passed'],
            'grade': ExamScore.calculate(
                Decimal(str(attempt['score_points'] or 0)),
                Decimal(str(sum(q['points'] for q in questions))),
                GradingCriteria.ihk_standard()
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


__all__ = ['ihk_exams_user_bp']
