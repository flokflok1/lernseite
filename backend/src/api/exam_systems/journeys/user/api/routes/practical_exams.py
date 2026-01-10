"""
Exam Systems - Practical Exams Routes (User Journey)

Endpoints for taking Practical exams.

Endpoints:
  POST   /exams/practical/:exam_id/start - Start Practical exam
  POST   /exams/practical/attempts/:attempt_id/step - Submit practical step
  GET    /exams/practical/attempts/:attempt_id/results - Get results

Phase: 5.3.2 - Exam Systems Domain
Reference: 02a_System-Features.md (practical_exam_engine)
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field
from typing import Any, Dict
from datetime import datetime

from src.api.exam_systems.core.domain.repositories import ExamRepository
from src.api.exam_systems.core.domain.factories import ExamAttemptFactory


# Blueprint
practical_exams_user_bp = Blueprint('exam_systems_practical_exams_user', __name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class PracticalStepSubmit(BaseModel):
    """Request model for submitting practical step"""
    step_number: int = Field(..., ge=1, description="Step number")
    solution: Dict[str, Any] = Field(..., description="Step solution data")


# ============================================================================
# Endpoints
# ============================================================================

@practical_exams_user_bp.route('/exams/practical/<exam_id>/start', methods=['POST'])
@jwt_required()
def start_practical_exam(exam_id: str):
    """
    Start a new Practical exam attempt.

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

        if exam['exam_type'] != 'practical':
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_EXAM_TYPE", "message": "This is not a Practical exam"}
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

        # Get questions (practical steps)
        questions = ExamRepository.get_exam_questions(exam_id)
        steps_safe = [
            {
                'question_id': q['question_id'],
                'step_number': q['order_index'] + 1,
                'step_description': q['question_text'],
                'points': q['points']
            }
            for q in questions
        ]

        return jsonify({
            "success": True,
            "data": {
                **attempt,
                "time_limit_minutes": exam['time_limit_minutes'],
                "steps": steps_safe,
                "total_steps": len(steps_safe),
                "config": exam['config']
            }
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "START_EXAM_ERROR", "message": str(e)}
        }), 500


@practical_exams_user_bp.route('/exams/practical/attempts/<attempt_id>/step', methods=['POST'])
@jwt_required()
def submit_practical_step(attempt_id: str):
    """
    Submit a practical step solution.

    Args:
        attempt_id: UUID of the exam attempt

    Request Body:
        {
            "step_number": 1,
            "solution": {
                "configuration": "...",
                "commands": ["cmd1", "cmd2"],
                "output": "..."
            }
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
            step_request = PracticalStepSubmit(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        # Get questions to find the step
        questions = ExamRepository.get_exam_questions(attempt['exam_id'])
        step = next((q for q in questions if q['order_index'] + 1 == step_request.step_number), None)

        if not step:
            return jsonify({
                "success": False,
                "error": {"code": "STEP_NOT_FOUND", "message": f"Step {step_request.step_number} not found"}
            }), 404

        # For practical exams, we'd normally validate against expected solution
        # For now, just save the submission (manual grading later)
        answer_data = {
            'attempt_id': attempt_id,
            'question_id': step['question_id'],
            'answer': step_request.solution,
            'points_earned': 0,  # Will be graded later
            'is_correct': False  # Will be graded later
        }
        answer = ExamRepository.submit_answer(answer_data)

        return jsonify({
            "success": True,
            "data": {
                "answer_id": answer['answer_id'],
                "step_number": step_request.step_number,
                "submitted": True,
                "feedback": "Step submitted for grading"
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "SUBMIT_STEP_ERROR", "message": str(e)}
        }), 500


@practical_exams_user_bp.route('/exams/practical/attempts/<attempt_id>/results', methods=['GET'])
@jwt_required()
def get_practical_exam_results(attempt_id: str):
    """
    Get practical exam results.

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

        score = {
            'points_earned': float(attempt['score_points'] or 0),
            'points_total': sum(q['points'] for q in questions),
            'percentage': float(attempt['score_percentage'] or 0),
            'passed': attempt['passed']
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
                "total_steps": len(questions),
                "steps_completed": len(answers)
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_RESULTS_ERROR", "message": str(e)}
        }), 500


__all__ = ['practical_exams_user_bp']
