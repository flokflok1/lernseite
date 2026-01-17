"""
LernsystemX Exam Simulations - Core API

Exam simulation management (CRUD) and service layer.

Endpoints (4 total):
- POST /courses/:course_id/exam-simulations - Create new simulation
- GET /exam-simulations - List user's simulations
- GET /exam-simulations/:simulation_id - Get simulation details
- DELETE /exam-simulations/:simulation_id - Delete simulation

ISO 9001:2015 compliant - Assessment & Evaluation Layer
Split from: exam_simulations.py (Part 1/3 - Core Simulation Management)
"""

import json
from flask import Blueprint, request, jsonify
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4
from datetime import datetime

from app.middleware.auth import token_required, get_current_user
from app.services.exam_context_detector import get_exam_context_sync
from app.database.connection import fetch_one, fetch_all, execute_query

core_bp = Blueprint('exam_simulations_core', __name__, url_prefix='')
course_bp = Blueprint('exam_simulations_course', __name__, url_prefix='/courses')


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ExamSimulationCreate(BaseModel):
    """Request model for creating an exam simulation."""
    mode: str = Field(default='smart', pattern='^(smart|manual)$')
    difficulty: str = Field(default='realistic', pattern='^(easy|realistic|hard)$')
    time_limit_minutes: int = Field(default=90, ge=15, le=180)
    focus_distribution: Optional[Dict[str, int]] = None
    extra_instructions: Optional[str] = None
    selected_files: Optional[List[str]] = None
    title: Optional[str] = None

    @validator('focus_distribution')
    def validate_focus_distribution(cls, v):
        if v is not None:
            total = sum(v.values())
            if total != 100:
                raise ValueError(f"Focus distribution must sum to 100%, got {total}%")
        return v


# =============================================================================
# EXAM SERVICE - CORE METHODS
# =============================================================================

class ExamService:
    """Exam service methods for simulation and attempt management."""

    @staticmethod
    def create_simulation(
        course_id: str,
        user_id: str,
        config_data: Dict,
        context_data: Dict,
        title: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create exam simulation record.

        Args:
            course_id: Course ID
            user_id: User ID
            config_data: Simulation config (mode, difficulty, time_limit, etc)
            context_data: Exam context (topics, focus areas, etc)
            title: Optional custom title

        Returns:
            Created simulation record or None
        """
        simulation_id = str(uuid4())

        # Auto-generate title if not provided
        if not title:
            difficulty = config_data.get('difficulty', 'realistic')
            title = f"Prüfungssimulation ({difficulty})"

        query = """
            INSERT INTO exam_simulations
            (simulation_id, course_id, user_id, title, context_json, config_json, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s)
            RETURNING *
        """
        return fetch_one(query, (
            simulation_id, course_id, user_id, title,
            json.dumps(context_data), json.dumps(config_data),
            datetime.utcnow()
        ))

    @staticmethod
    def start_attempt(simulation_id: str, user_id: str) -> tuple[Optional[Dict], List[Dict]]:
        """
        Start new exam attempt.

        Args:
            simulation_id: Simulation ID
            user_id: User ID

        Returns:
            Tuple of (attempt record, questions without correct answers)

        Raises:
            ValueError: If simulation not found, not ready, or access denied
        """
        # Verify simulation is ready
        sim = fetch_one(
            "SELECT * FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

        if not sim:
            raise ValueError("Simulation not found")

        if sim['status'] != 'ready':
            raise ValueError(f"Simulation not ready (status: {sim['status']})")

        if str(sim['user_id']) != user_id:
            raise ValueError("Access denied")

        # Create attempt
        attempt_id = str(uuid4())
        result_json = sim['result_json'] if sim.get('result_json') else {}
        questions = result_json.get('questions', []) if isinstance(result_json, dict) else []

        max_score = sum(q.get('points', 1) for q in questions)

        query = """
            INSERT INTO exam_simulation_attempts
            (attempt_id, simulation_id, user_id, started_at, max_score, status, created_at)
            VALUES (%s, %s, %s, %s, %s, 'in_progress', %s)
            RETURNING *
        """
        attempt = fetch_one(query, (
            attempt_id, simulation_id, user_id,
            datetime.utcnow(), max_score, datetime.utcnow()
        ))

        # Strip correct answers from questions (for security)
        safe_questions = []
        for q in questions:
            safe_q = {k: v for k, v in q.items() if k != 'correct_answer'}
            safe_questions.append(safe_q)

        return attempt, safe_questions

    @staticmethod
    def submit_attempt(
        attempt_id: str,
        user_id: str,
        answers: List[Dict],
        time_spent_seconds: int
    ) -> Dict:
        """
        Submit and evaluate exam attempt.

        Args:
            attempt_id: Attempt ID
            user_id: User ID
            answers: List of {'question_id': 'q1', 'answer': 'A'} dicts
            time_spent_seconds: Time spent on exam

        Returns:
            Result dict with score, percentage, passed status, feedback
        """
        # Get attempt
        attempt = fetch_one(
            "SELECT * FROM exam_simulation_attempts WHERE attempt_id = %s",
            (attempt_id,)
        )

        if not attempt:
            raise ValueError("Attempt not found")

        if str(attempt['user_id']) != user_id:
            raise ValueError("Access denied")

        # Get simulation with questions and correct answers
        sim = fetch_one(
            "SELECT result_json FROM exam_simulations WHERE simulation_id = %s",
            (attempt['simulation_id'],)
        )

        result_json = sim['result_json'] if sim and sim.get('result_json') else {}
        questions = result_json.get('questions', []) if isinstance(result_json, dict) else []

        # Create answer map
        answer_map = {a['question_id']: a['answer'] for a in answers}

        # Evaluate answers
        score = 0
        max_score = attempt['max_score']
        results_by_topic = {}
        evaluated_answers = []

        for q in questions:
            q_id = q['id']
            correct = q.get('correct_answer')
            user_answer = answer_map.get(q_id)
            is_correct = user_answer == correct
            points = q.get('points', 1)

            if is_correct:
                score += points

            # Track by topic
            topic = q.get('topic', 'General')
            if topic not in results_by_topic:
                results_by_topic[topic] = {'correct': 0, 'total': 0}
            results_by_topic[topic]['total'] += 1
            if is_correct:
                results_by_topic[topic]['correct'] += 1

            evaluated_answers.append({
                'question_id': q_id,
                'user_answer': user_answer,
                'correct_answer': correct,
                'is_correct': is_correct,
                'points': points if is_correct else 0
            })

        # Calculate percentage and pass status
        percentage = (score / max_score * 100) if max_score > 0 else 0
        passed = percentage >= 60  # 60% pass threshold

        # Update attempt
        query = """
            UPDATE exam_simulation_attempts
            SET
                completed_at = %s,
                time_spent_seconds = %s,
                score = %s,
                percentage = %s,
                passed = %s,
                results_by_topic = %s,
                status = 'completed'
            WHERE attempt_id = %s
            RETURNING *
        """
        fetch_one(query, (
            datetime.utcnow(),
            time_spent_seconds,
            score,
            percentage,
            passed,
            json.dumps(results_by_topic),
            attempt_id
        ))

        # Update simulation stats
        query = """
            UPDATE exam_simulations
            SET
                attempt_count = attempt_count + 1,
                best_score = GREATEST(best_score, %s),
                avg_score = (SELECT AVG(score) FROM exam_simulation_attempts WHERE simulation_id = %s)
            WHERE simulation_id = %s
        """
        execute_query(
            query,
            (score, str(attempt['simulation_id']), str(attempt['simulation_id']))
        )

        return {
            'attempt_id': str(attempt_id),
            'score': score,
            'max_score': max_score,
            'percentage': percentage,
            'passed': passed,
            'time_spent_seconds': time_spent_seconds,
            'results_by_topic': results_by_topic,
            'evaluated_answers': evaluated_answers
        }


# =============================================================================
# SIMULATION MANAGEMENT ENDPOINTS
# =============================================================================

@course_bp.route('/<course_id>/exam-simulations', methods=['POST'])
@token_required
def create_exam_simulation(course_id: str):
    """
    Create a new exam simulation for a course.

    Request Body:
        {
            "mode": "smart" | "manual",
            "difficulty": "easy" | "realistic" | "hard",
            "time_limit_minutes": 90,
            "focus_distribution": { "Kalkulation": 35, "Netzwerk": 30, ... },
            "extra_instructions": "Optional additional instructions",
            "selected_files": ["file-id-1", ...],
            "title": "Optional custom title"
        }

    Response:
        201: Simulation created (status: pending)
        400: Validation error
        404: Course not found
    """
    try:
        from pydantic import ValidationError

        user = get_current_user()
        user_id = user['user_id']
        data = request.get_json() or {}

        # Validate with Pydantic
        sim_data = ExamSimulationCreate(**data)

        # Verify course exists
        course = fetch_one(
            "SELECT course_id, title FROM courses WHERE course_id = %s",
            (course_id,)
        )

        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get exam context
        context = get_exam_context_sync(UUID(user_id), UUID(course_id))

        # Build config
        config = {
            'mode': sim_data.mode,
            'difficulty': sim_data.difficulty,
            'time_limit_minutes': sim_data.time_limit_minutes,
            'extra_instructions': sim_data.extra_instructions,
            'selected_files': sim_data.selected_files or []
        }

        if sim_data.focus_distribution:
            config['focus_distribution'] = sim_data.focus_distribution
        elif context.get('recommended_focus'):
            config['focus_distribution'] = context['recommended_focus']

        # Create simulation
        result = ExamService.create_simulation(
            course_id=course_id,
            user_id=user_id,
            config_data=config,
            context_data=context,
            title=sim_data.title
        )

        if not result:
            return jsonify({
                'success': False,
                'error': 'Failed to create simulation'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Exam simulation created',
            'simulation': {
                'simulation_id': str(result['simulation_id']),
                'course_id': str(result['course_id']),
                'user_id': str(result['user_id']),
                'title': result['title'],
                'context': json.loads(result['context_json']) if isinstance(result['context_json'], str) else result['context_json'],
                'config': json.loads(result['config_json']) if isinstance(result['config_json'], str) else result['config_json'],
                'status': result['status'],
                'created_at': result['created_at'].isoformat() if result['created_at'] else None
            }
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create exam simulation',
            'details': str(e)
        }), 500


@core_bp.route('/exam-simulations', methods=['GET'])
@token_required
def list_exam_simulations():
    """
    List user's exam simulations.

    Query Parameters:
        course_id: Filter by course
        status: Filter by status (pending, generating, ready, failed)
        page: Page number (default: 1)
        per_page: Items per page (default: 20)

    Response:
        200: List of simulations with pagination
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        course_id = request.args.get('course_id')
        status = request.args.get('status')
        page = max(int(request.args.get('page', 1)), 1)
        per_page = min(int(request.args.get('per_page', 20)), 100)
        offset = (page - 1) * per_page

        # Build query
        conditions = ["user_id = %s"]
        params = [user_id]

        if course_id:
            conditions.append("course_id = %s")
            params.append(course_id)

        if status:
            conditions.append("status = %s")
            params.append(status)

        where_clause = " AND ".join(conditions)

        # Count total
        count_query = f"SELECT COUNT(*) as total FROM exam_simulations WHERE {where_clause}"
        count_result = fetch_one(count_query, tuple(params))
        total = count_result['total'] if count_result else 0

        # Get simulations
        query = f"""
            SELECT
                es.simulation_id, es.course_id, es.user_id, es.title,
                es.context_json, es.config_json, es.status, es.error_message,
                es.attempt_count, es.best_score, es.avg_score,
                es.created_at, es.updated_at,
                c.title as course_title
            FROM exam_simulations es
            JOIN courses c ON c.course_id = es.course_id
            WHERE {where_clause}
            ORDER BY es.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        results = fetch_all(query, tuple(params))

        simulations = []
        for r in results:
            simulations.append({
                'simulation_id': str(r['simulation_id']),
                'course_id': str(r['course_id']),
                'course_title': r['course_title'],
                'title': r['title'],
                'context': r['context_json'],
                'config': r['config_json'],
                'status': r['status'],
                'error_message': r['error_message'],
                'attempt_count': r['attempt_count'],
                'best_score': float(r['best_score']) if r['best_score'] else None,
                'avg_score': float(r['avg_score']) if r['avg_score'] else None,
                'created_at': r['created_at'].isoformat() if r['created_at'] else None,
                'updated_at': r['updated_at'].isoformat() if r['updated_at'] else None
            })

        total_pages = (total + per_page - 1) // per_page

        return jsonify({
            'success': True,
            'simulations': simulations,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list simulations',
            'details': str(e)
        }), 500


@core_bp.route('/exam-simulations/<simulation_id>', methods=['GET'])
@token_required
def get_exam_simulation(simulation_id: str):
    """
    Get exam simulation details.

    Response:
        200: Simulation details with questions (if ready)
        404: Simulation not found
        403: Access denied
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        query = """
            SELECT
                es.*, c.title as course_title
            FROM exam_simulations es
            JOIN courses c ON c.course_id = es.course_id
            WHERE es.simulation_id = %s
        """
        result = fetch_one(query, (simulation_id,))

        if not result:
            return jsonify({
                'success': False,
                'error': 'Simulation not found'
            }), 404

        # Check access (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        if str(result['user_id']) != user_id and not PermissionService.check_threshold(user, 'simulations.view_any'):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        simulation = {
            'simulation_id': str(result['simulation_id']),
            'course_id': str(result['course_id']),
            'course_title': result['course_title'],
            'user_id': str(result['user_id']),
            'title': result['title'],
            'description': result['description'],
            'context': result['context_json'],
            'config': result['config_json'],
            'result': result['result_json'],
            'status': result['status'],
            'error_message': result['error_message'],
            'generation_started_at': result['generation_started_at'].isoformat() if result['generation_started_at'] else None,
            'generation_completed_at': result['generation_completed_at'].isoformat() if result['generation_completed_at'] else None,
            'tokens_used': result['tokens_used'],
            'model_used': result['model_used'],
            'attempt_count': result['attempt_count'],
            'best_score': float(result['best_score']) if result['best_score'] else None,
            'avg_score': float(result['avg_score']) if result['avg_score'] else None,
            'created_at': result['created_at'].isoformat() if result['created_at'] else None,
            'updated_at': result['updated_at'].isoformat() if result['updated_at'] else None
        }

        return jsonify({
            'success': True,
            'simulation': simulation
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get simulation',
            'details': str(e)
        }), 500


@core_bp.route('/exam-simulations/<simulation_id>', methods=['DELETE'])
@token_required
def delete_exam_simulation(simulation_id: str):
    """
    Delete an exam simulation.

    Response:
        200: Simulation deleted
        404: Simulation not found
        403: Access denied
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Check exists and ownership
        result = fetch_one(
            "SELECT user_id FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

        if not result:
            return jsonify({
                'success': False,
                'error': 'Simulation not found'
            }), 404

        # Check access (RBAC 2.0: dynamic from DB)
        from app.services.permission_service import PermissionService
        if str(result['user_id']) != user_id and not PermissionService.check_threshold(user, 'simulations.view_any'):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Delete
        execute_query(
            "DELETE FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

        return jsonify({
            'success': True,
            'message': 'Simulation deleted'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete simulation',
            'details': str(e)
        }), 500


__all__ = ['core_bp', 'course_bp', 'ExamService', 'ExamSimulationCreate']
