"""
Exam Attempt Endpoints (User).

Endpoints:
- POST /api/v1/exam-simulations/:id/start    - Start attempt
- GET  /api/v1/exam-simulations/:id/attempts - Get attempts
- POST /api/v1/exam-simulations/:id/submit   - Submit attempt
"""

from flask import Blueprint, request, jsonify

from app.middleware.auth import token_required, get_current_user
from app.database.connection import fetch_one, fetch_all

from .models import ExamAttemptSubmit
from .services import ExamService


exam_attempts_bp = Blueprint(
    'exam_attempts',
    __name__,
    url_prefix='/exam-simulations'
)


@exam_attempts_bp.route('/<simulation_id>/start', methods=['POST'])
@token_required
def start_exam_attempt(simulation_id: str):
    """
    Start a new exam attempt.

    Uses ExamService to:
    - Validate simulation is ready
    - Create attempt record
    - Return questions without correct answers

    Response:
        201: Attempt created with questions
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


@exam_attempts_bp.route('/<simulation_id>/attempts', methods=['GET'])
@token_required
def list_exam_attempts(simulation_id: str):
    """
    List all attempts for a simulation.

    Response:
        200: List of attempts
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

        if str(sim['user_id']) != user_id and user.get('role') not in ['admin', 'superadmin']:
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


@exam_attempts_bp.route('/<simulation_id>/submit', methods=['POST'])
@token_required
def submit_exam_attempt(simulation_id: str):
    """
    Submit answers for an exam attempt.

    Uses ExamService to:
    - Validate attempt
    - Evaluate answers
    - Calculate score
    - Update statistics

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
        400: Invalid attempt
        404: Attempt not found
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
