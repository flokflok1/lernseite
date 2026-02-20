"""
LernsystemX Exam Simulations - Core API (Part 2)

Simulation management route endpoints.

Endpoints (4 total):
- POST /courses/:course_id/exam-simulations - Create new simulation
- GET /exam-simulations - List user's simulations
- GET /exam-simulations/:simulation_id - Get simulation details
- DELETE /exam-simulations/:simulation_id - Delete simulation

ISO 9001:2015 compliant - Assessment & Evaluation Layer
Continuation of: core.py (Part 2 - Route Endpoints)
"""

import json
from flask import request, jsonify
from uuid import UUID

from app.api.middleware.auth import token_required, get_current_user
from app.application.services.ai import get_exam_context_sync
from app.infrastructure.persistence.repositories.exams.simulations import ExamSimulationRepository
from app.infrastructure.persistence.repositories.courses.crud import CourseRepositoryCRUD

from app.api.v1.public.system_features.exam.simulations.user.core import (
    core_bp,
    course_bp,
    ExamService,
    ExamSimulationCreate,
)


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
        course = CourseRepositoryCRUD.get_by_id_simple(course_id)

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

        # Count total
        total = ExamSimulationRepository.count_simulations(
            user_id, course_id=course_id, status=status
        )

        # Get simulations
        results = ExamSimulationRepository.list_simulations(
            user_id, course_id=course_id, status=status,
            per_page=per_page, offset=offset
        )

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

        result = ExamSimulationRepository.get_simulation(simulation_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Simulation not found'
            }), 404

        # Check access (RBAC 2.0: dynamic from DB)
        from app.application.services.system.auth.permission import PermissionService
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
        result = ExamSimulationRepository.get_simulation_owner(simulation_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Simulation not found'
            }), 404

        # Check access (RBAC 2.0: dynamic from DB)
        from app.application.services.system.auth.permission import PermissionService
        if str(result['user_id']) != user_id and not PermissionService.check_threshold(user, 'simulations.view_any'):
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403

        # Delete
        ExamSimulationRepository.delete_simulation(simulation_id)

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
