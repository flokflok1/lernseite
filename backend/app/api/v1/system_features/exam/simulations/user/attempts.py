"""
LernsystemX Exam Simulations - Attempts API

Exam attempt management (start, list, submit, evaluate).

Endpoints (3 total):
- POST /exam-simulations/:simulation_id/start - Start new attempt
- GET /exam-simulations/:simulation_id/attempts - List attempts for simulation
- POST /exam-simulations/:simulation_id/submit - Submit attempt answers

ISO 9001:2015 compliant - Assessment & Evaluation Layer
Split from: exam_simulations.py (Part 2/3 - Exam Attempts)
"""

from flask import Blueprint, request, jsonify

from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
from app.api.v1.system_features.exam.simulations.user.core import ExamService

attempts_bp = Blueprint('exam_simulations_attempts', __name__, url_prefix='')


# =============================================================================
# EXAM ATTEMPT ENDPOINTS
# =============================================================================

@attempts_bp.route('/exam-simulations/<simulation_id>/start', methods=['POST'])
@token_required
def start_exam_attempt(simulation_id: str):
    """
    Start a new exam attempt.

    Path Parameters:
        simulation_id: Simulation ID

    Response:
        201: Attempt created with questions (without correct answers)
             {
                 "attempt": {
                     "attempt_id": "uuid",
                     "simulation_id": "uuid",
                     "started_at": "2026-01-16T...",
                     "status": "in_progress",
                     "time_limit_minutes": 90,
                     "max_score": 100
                 },
                 "questions": [...]
             }
        400: Simulation not ready
        404: Simulation not found
        403: Access denied
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Start attempt using service
        attempt, questions = ExamService.start_attempt(
            simulation_id=simulation_id,
            user_id=user_id
        )

        if not attempt:
            return jsonify({
                'success': False,
                'error': 'Failed to start attempt'
            }), 500

        # Get config for time limit
        sim = fetch_one(
            "SELECT config_json FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )
        config = sim['config_json'] if sim else {}

        return jsonify({
            'success': True,
            'attempt': {
                'attempt_id': str(attempt['attempt_id']),
                'simulation_id': simulation_id,
                'started_at': attempt['started_at'].isoformat() if attempt['started_at'] else None,
                'status': attempt['status'],
                'time_limit_minutes': config.get('time_limit_minutes', 90),
                'max_score': attempt['max_score']
            },
            'questions': questions
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to start attempt',
            'details': str(e)
        }), 500


@attempts_bp.route('/exam-simulations/<simulation_id>/attempts', methods=['GET'])
@token_required
def list_exam_attempts(simulation_id: str):
    """
    List all attempts for a simulation.

    Path Parameters:
        simulation_id: Simulation ID

    Response:
        200: List of attempts
             {
                 "attempts": [
                     {
                         "attempt_id": "uuid",
                         "simulation_id": "uuid",
                         "started_at": "2026-01-16T...",
                         "completed_at": "2026-01-16T...",
                         "time_spent_seconds": 3600,
                         "score": 85,
                         "max_score": 100,
                         "percentage": 85.0,
                         "passed": true,
                         "results_by_topic": {...}
                     }
                 ],
                 "total": 3
             }
        404: Simulation not found
        403: Access denied
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Verify access
        sim = fetch_one(
            "SELECT user_id FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

        if not sim:
            return jsonify({
                'success': False,
                'error': 'Simulation not found'
            }), 404

        # Check access (RBAC 2.0: hierarchy-based)
        # hierarchy_level >= 8 = admin, superadmin, owner
        if str(sim['user_id']) != user_id and user.get('hierarchy_level', 0) < 8:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Get attempts
        query = """
            SELECT
                attempt_id, simulation_id, user_id,
                started_at, completed_at, time_spent_seconds,
                score, max_score, percentage, passed,
                results_by_topic, status, created_at
            FROM exam_simulation_attempts
            WHERE simulation_id = %s
            ORDER BY created_at DESC
        """
        results = fetch_all(query, (simulation_id,))

        attempts = []
        for r in results:
            attempts.append({
                'attempt_id': str(r['attempt_id']),
                'simulation_id': str(r['simulation_id']),
                'started_at': r['started_at'].isoformat() if r['started_at'] else None,
                'completed_at': r['completed_at'].isoformat() if r['completed_at'] else None,
                'time_spent_seconds': r['time_spent_seconds'],
                'score': float(r['score']) if r['score'] else None,
                'max_score': float(r['max_score']) if r['max_score'] else None,
                'percentage': float(r['percentage']) if r['percentage'] else None,
                'passed': r['passed'],
                'results_by_topic': r['results_by_topic'],
                'status': r['status']
            })

        return jsonify({
            'success': True,
            'attempts': attempts,
            'total': len(attempts)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list attempts',
            'details': str(e)
        }), 500


@attempts_bp.route('/exam-simulations/<simulation_id>/submit', methods=['POST'])
@token_required
def submit_exam_attempt(simulation_id: str):
    """
    Submit answers for an exam attempt.

    Path Parameters:
        simulation_id: Simulation ID

    Request Body:
        {
            "attempt_id": "uuid",
            "answers": [
                {"question_id": "q1", "answer": "A"},
                {"question_id": "q2", "answer": "42"},
                ...
            ],
            "time_spent_seconds": 3600
        }

    Response:
        200: Results with score and feedback
             {
                 "result": {
                     "attempt_id": "uuid",
                     "score": 85,
                     "max_score": 100,
                     "percentage": 85.0,
                     "passed": true,
                     "time_spent_seconds": 3600,
                     "results_by_topic": {
                         "Kalkulation": {"correct": 7, "total": 8},
                         "Netzwerk": {"correct": 6, "total": 8}
                     },
                     "evaluated_answers": [
                         {
                             "question_id": "q1",
                             "user_answer": "A",
                             "correct_answer": "A",
                             "is_correct": true,
                             "points": 5
                         }
                     ]
                 }
             }
        400: Invalid attempt
        404: Attempt/Simulation not found
        403: Access denied
    """
    try:
        user = get_current_user()
        user_id = user['user_id']
        data = request.get_json()

        attempt_id = data.get('attempt_id')
        answers = data.get('answers', [])
        time_spent = data.get('time_spent_seconds', 0)

        if not attempt_id:
            return jsonify({
                'success': False,
                'error': 'attempt_id required'
            }), 400

        # Submit using service
        result = ExamService.submit_attempt(
            attempt_id=attempt_id,
            user_id=user_id,
            answers=answers,
            time_spent_seconds=time_spent
        )

        return jsonify({
            'success': True,
            'result': result
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to submit attempt',
            'details': str(e)
        }), 500


__all__ = ['exam_simulations_attempts_bp']
