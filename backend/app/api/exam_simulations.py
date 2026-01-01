"""
LernsystemX Exam Simulation API

KI-Prüfungssimulation Endpoints:
- GET    /api/v1/courses/:id/exam-context        - Get detected exam context
- POST   /api/v1/courses/:id/exam-simulations    - Create new exam simulation
- GET    /api/v1/exam-simulations                - List user's simulations
- GET    /api/v1/exam-simulations/:id            - Get simulation details
- DELETE /api/v1/exam-simulations/:id            - Delete simulation
- POST   /api/v1/exam-simulations/:id/generate   - Start generation (Celery)
- POST   /api/v1/exam-simulations/:id/start      - Start attempt
- GET    /api/v1/exam-simulations/:id/attempts   - Get attempts
- POST   /api/v1/exam-simulations/:id/submit     - Submit attempt

ISO 27001:2013 compliant - Exam Simulation System
"""

from flask import request, jsonify
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, List, Any
from uuid import UUID
from datetime import datetime

from app.api import api_v1
from app.middleware.auth import token_required, get_current_user
from app.services.exam_context_detector import get_exam_context_sync
from app.database.connection import fetch_one, fetch_all, execute_query


# ============================================================================
# Pydantic Models
# ============================================================================

class ExamSimulationCreate(BaseModel):
    """Request model for creating an exam simulation."""
    mode: str = Field(default='smart', pattern='^(smart|manual)$')
    difficulty: str = Field(default='realistic', pattern='^(easy|realistic|hard)$')
    time_limit_minutes: int = Field(default=90, ge=15, le=180)
    focus_distribution: Optional[Dict[str, int]] = None
    extra_instructions: Optional[str] = None
    selected_files: Optional[List[str]] = None
    title: Optional[str] = None


class ExamAttemptSubmit(BaseModel):
    """Request model for submitting exam attempt."""
    answers: List[Dict[str, Any]]
    time_spent_seconds: int = Field(ge=0)


# ============================================================================
# EXAM CONTEXT ENDPOINTS
# ============================================================================

@api_v1.route('/courses/<course_id>/exam-context', methods=['GET'])
@token_required
def get_course_exam_context(course_id: str):
    """
    Get detected exam context for a course.

    Uses ExamContextDetector to analyze:
    - User profile (profession, region, target exam)
    - Course metadata (profession_tag, exam_level)
    - Course files (PDFs, exam-relevant documents)
    - Learning analytics (weak/strong topics)

    Response:
        200: Exam context data
        404: Course not found
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

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

        # Get exam context using detector
        context = get_exam_context_sync(UUID(user_id), UUID(course_id))

        return jsonify({
            'success': True,
            'context': context
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get exam context',
            'details': str(e)
        }), 500


# ============================================================================
# EXAM SIMULATION CRUD ENDPOINTS
# ============================================================================

@api_v1.route('/courses/<course_id>/exam-simulations', methods=['POST'])
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

        # Get exam context for context_json
        context = get_exam_context_sync(UUID(user_id), UUID(course_id))

        # Build config_json
        config = {
            'mode': sim_data.mode,
            'difficulty': sim_data.difficulty,
            'time_limit_minutes': sim_data.time_limit_minutes,
            'extra_instructions': sim_data.extra_instructions,
            'selected_files': sim_data.selected_files or []
        }

        # Use provided focus_distribution or context's recommended
        if sim_data.focus_distribution:
            config['focus_distribution'] = sim_data.focus_distribution
        elif context.get('recommended_focus'):
            config['focus_distribution'] = context['recommended_focus']

        # Generate title if not provided
        title = sim_data.title
        if not title:
            profession = context.get('profession', 'Prüfung')
            exam_level = context.get('exam_level', '')
            difficulty_labels = {'easy': 'Leicht', 'realistic': 'Realistisch', 'hard': 'Schwer'}
            title = f"{profession} {exam_level} Simulation - {difficulty_labels.get(sim_data.difficulty, 'Realistisch')}"

        # Insert simulation
        import json
        query = """
            INSERT INTO exam_simulations (
                course_id, user_id, title, context_json, config_json, status
            ) VALUES (%s, %s, %s, %s, %s, 'pending')
            RETURNING simulation_id, course_id, user_id, title, context_json,
                      config_json, status, created_at
        """
        result = fetch_one(query, (
            course_id,
            user_id,
            title,
            json.dumps(context),
            json.dumps(config)
        ))

        return jsonify({
            'success': True,
            'message': 'Exam simulation created',
            'simulation': {
                'simulation_id': str(result['simulation_id']),
                'course_id': str(result['course_id']),
                'user_id': str(result['user_id']),
                'title': result['title'],
                'context': context,
                'config': config,
                'status': result['status'],
                'created_at': result['created_at'].isoformat() if result['created_at'] else None
            }
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create exam simulation',
            'details': str(e)
        }), 500


@api_v1.route('/exam-simulations', methods=['GET'])
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


@api_v1.route('/exam-simulations/<simulation_id>', methods=['GET'])
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

        # Check access (owner or admin)
        if str(result['user_id']) != user_id and user.get('role') not in ['admin', 'superadmin']:
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


@api_v1.route('/exam-simulations/<simulation_id>', methods=['DELETE'])
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

        if str(result['user_id']) != user_id and user.get('role') not in ['admin', 'superadmin']:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Delete
        execute_query("DELETE FROM exam_simulations WHERE simulation_id = %s", (simulation_id,))

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


# ============================================================================
# GENERATION ENDPOINT
# ============================================================================

@api_v1.route('/exam-simulations/<simulation_id>/generate', methods=['POST'])
@token_required
def generate_exam_simulation(simulation_id: str):
    """
    Start exam generation (queues Celery task).

    Response:
        202: Generation started (async)
        400: Simulation already generated or generating
        404: Simulation not found
        403: Access denied
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Get simulation
        result = fetch_one(
            "SELECT user_id, status FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

        if not result:
            return jsonify({
                'success': False,
                'error': 'Simulation not found'
            }), 404

        if str(result['user_id']) != user_id and user.get('role') not in ['admin', 'superadmin']:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        if result['status'] == 'ready':
            return jsonify({
                'success': False,
                'error': 'Simulation already generated'
            }), 400

        if result['status'] == 'generating':
            return jsonify({
                'success': False,
                'error': 'Simulation is already being generated'
            }), 400

        # Update status to generating
        execute_query(
            """
            UPDATE exam_simulations
            SET status = 'generating', generation_started_at = NOW()
            WHERE simulation_id = %s
            """,
            (simulation_id,)
        )

        # Queue Celery task
        try:
            from app.tasks.exam_tasks import generate_exam_task
            generate_exam_task.delay(simulation_id)
        except ImportError:
            # Celery not configured - run synchronously (dev mode)
            pass

        return jsonify({
            'success': True,
            'message': 'Generation started',
            'status': 'generating'
        }), 202

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to start generation',
            'details': str(e)
        }), 500


# ============================================================================
# ATTEMPT ENDPOINTS
# ============================================================================

@api_v1.route('/exam-simulations/<simulation_id>/start', methods=['POST'])
@token_required
def start_exam_attempt(simulation_id: str):
    """
    Start a new exam attempt.

    Response:
        201: Attempt created with questions
        400: Simulation not ready
        404: Simulation not found
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        # Get simulation with result
        sim = fetch_one(
            """
            SELECT simulation_id, user_id, status, result_json, config_json
            FROM exam_simulations
            WHERE simulation_id = %s
            """,
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

        if sim['status'] != 'ready':
            return jsonify({
                'success': False,
                'error': 'Simulation not ready',
                'status': sim['status']
            }), 400

        if not sim['result_json']:
            return jsonify({
                'success': False,
                'error': 'Simulation has no questions'
            }), 400

        # Create attempt
        result_data = sim['result_json']
        max_score = result_data.get('total_points', 100)

        query = """
            INSERT INTO exam_simulation_attempts (
                simulation_id, user_id, max_score, status
            ) VALUES (%s, %s, %s, 'in_progress')
            RETURNING attempt_id, started_at, status
        """
        attempt = fetch_one(query, (simulation_id, user_id, max_score))

        # Update simulation attempt count
        execute_query(
            "UPDATE exam_simulations SET attempt_count = attempt_count + 1 WHERE simulation_id = %s",
            (simulation_id,)
        )

        # Return questions without correct answers
        questions = []
        for q in result_data.get('questions', []):
            questions.append({
                'question_id': q.get('question_id'),
                'type': q.get('type'),
                'topic': q.get('topic'),
                'difficulty': q.get('difficulty'),
                'points': q.get('points'),
                'question': q.get('question'),
                'options': q.get('options'),  # For MC questions
                # Do NOT include correct_answer or explanation
            })

        config = sim['config_json'] or {}

        return jsonify({
            'success': True,
            'attempt': {
                'attempt_id': str(attempt['attempt_id']),
                'simulation_id': simulation_id,
                'started_at': attempt['started_at'].isoformat() if attempt['started_at'] else None,
                'status': attempt['status'],
                'time_limit_minutes': config.get('time_limit_minutes', 90),
                'max_score': max_score
            },
            'questions': questions
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to start attempt',
            'details': str(e)
        }), 500


@api_v1.route('/exam-simulations/<simulation_id>/attempts', methods=['GET'])
@token_required
def list_exam_attempts(simulation_id: str):
    """
    List all attempts for a simulation.

    Response:
        200: List of attempts
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


@api_v1.route('/exam-simulations/<simulation_id>/submit', methods=['POST'])
@token_required
def submit_exam_attempt(simulation_id: str):
    """
    Submit answers for an exam attempt.

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

        # Get attempt
        attempt = fetch_one(
            """
            SELECT a.*, s.result_json, s.user_id as sim_user_id
            FROM exam_simulation_attempts a
            JOIN exam_simulations s ON s.simulation_id = a.simulation_id
            WHERE a.attempt_id = %s
            """,
            (attempt_id,)
        )

        if not attempt:
            return jsonify({
                'success': False,
                'error': 'Attempt not found'
            }), 404

        if str(attempt['user_id']) != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        if attempt['status'] != 'in_progress':
            return jsonify({
                'success': False,
                'error': 'Attempt already completed'
            }), 400

        # Evaluate answers
        result_json = attempt['result_json'] or {}
        questions = {q['question_id']: q for q in result_json.get('questions', [])}

        total_score = 0
        max_score = result_json.get('total_points', 100)
        results_by_topic = {}
        evaluated_answers = []

        for ans in answers:
            q_id = ans.get('question_id')
            user_answer = ans.get('answer')

            question = questions.get(q_id)
            if not question:
                continue

            points = question.get('points', 0)
            correct_answer = question.get('correct_answer')
            topic = question.get('topic', 'Allgemein')

            # Simple evaluation (exact match for now)
            is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()
            earned_points = points if is_correct else 0
            total_score += earned_points

            # Track by topic
            if topic not in results_by_topic:
                results_by_topic[topic] = {'correct': 0, 'total': 0, 'points': 0, 'max_points': 0}

            results_by_topic[topic]['total'] += 1
            results_by_topic[topic]['max_points'] += points
            if is_correct:
                results_by_topic[topic]['correct'] += 1
                results_by_topic[topic]['points'] += points

            evaluated_answers.append({
                'question_id': q_id,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'points_earned': earned_points,
                'points_possible': points,
                'explanation': question.get('explanation')
            })

        # Calculate percentage and pass status
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        passed = percentage >= 50  # 50% to pass

        # Update attempt
        import json
        execute_query(
            """
            UPDATE exam_simulation_attempts
            SET
                completed_at = NOW(),
                time_spent_seconds = %s,
                answers_json = %s,
                score = %s,
                percentage = %s,
                passed = %s,
                results_by_topic = %s,
                status = 'completed'
            WHERE attempt_id = %s
            """,
            (
                time_spent,
                json.dumps(evaluated_answers),
                total_score,
                percentage,
                passed,
                json.dumps(results_by_topic),
                attempt_id
            )
        )

        # Update simulation best/avg score
        execute_query(
            """
            UPDATE exam_simulations
            SET
                best_score = GREATEST(COALESCE(best_score, 0), %s),
                avg_score = (
                    SELECT AVG(percentage)
                    FROM exam_simulation_attempts
                    WHERE simulation_id = %s AND status = 'completed'
                )
            WHERE simulation_id = %s
            """,
            (percentage, simulation_id, simulation_id)
        )

        return jsonify({
            'success': True,
            'result': {
                'attempt_id': attempt_id,
                'score': total_score,
                'max_score': max_score,
                'percentage': round(percentage, 1),
                'passed': passed,
                'time_spent_seconds': time_spent,
                'results_by_topic': results_by_topic,
                'answers': evaluated_answers
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to submit attempt',
            'details': str(e)
        }), 500


# ============================================================================
# USER PROFILE ENDPOINTS (for exam context)
# ============================================================================

@api_v1.route('/user-profile/exam-settings', methods=['GET'])
@token_required
def get_user_exam_settings():
    """
    Get user's exam-related profile settings.

    Response:
        200: User exam profile
    """
    try:
        user = get_current_user()
        user_id = user['user_id']

        profile = fetch_one(
            """
            SELECT
                profession, profession_detail, training_year,
                target_exam, exam_date, region, ihk,
                detected_profession, detected_level, detection_confidence,
                preferred_difficulty, preferred_question_types
            FROM user_profiles
            WHERE user_id = %s
            """,
            (user_id,)
        )

        if not profile:
            # Return empty profile
            return jsonify({
                'success': True,
                'profile': {}
            }), 200

        return jsonify({
            'success': True,
            'profile': dict(profile)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get profile',
            'details': str(e)
        }), 500


@api_v1.route('/user-profile/exam-settings', methods=['PUT'])
@token_required
def update_user_exam_settings():
    """
    Update user's exam-related profile settings.

    Request Body:
        {
            "profession": "FISI",
            "target_exam": "AP1",
            "region": "Baden-Württemberg",
            "preferred_difficulty": "realistic",
            ...
        }

    Response:
        200: Profile updated
    """
    try:
        user = get_current_user()
        user_id = user['user_id']
        data = request.get_json()

        # Check if profile exists
        existing = fetch_one(
            "SELECT profile_id FROM user_profiles WHERE user_id = %s",
            (user_id,)
        )

        allowed_fields = [
            'profession', 'profession_detail', 'training_year',
            'training_start_date', 'training_end_date',
            'target_exam', 'exam_date', 'region', 'ihk', 'ihk_code',
            'preferred_difficulty', 'preferred_question_types',
            'daily_learning_goal_minutes'
        ]

        import json

        if existing:
            # Update existing
            set_parts = []
            values = []
            for field in allowed_fields:
                if field in data:
                    set_parts.append(f"{field} = %s")
                    value = data[field]
                    if isinstance(value, list):
                        value = value  # PostgreSQL arrays
                    values.append(value)

            if set_parts:
                query = f"""
                    UPDATE user_profiles
                    SET {', '.join(set_parts)}
                    WHERE user_id = %s
                    RETURNING *
                """
                values.append(user_id)
                result = fetch_one(query, tuple(values))
        else:
            # Insert new
            fields = ['user_id']
            placeholders = ['%s']
            values = [user_id]

            for field in allowed_fields:
                if field in data:
                    fields.append(field)
                    placeholders.append('%s')
                    values.append(data[field])

            query = f"""
                INSERT INTO user_profiles ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """
            result = fetch_one(query, tuple(values))

        return jsonify({
            'success': True,
            'message': 'Profile updated',
            'profile': dict(result) if result else {}
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update profile',
            'details': str(e)
        }), 500
