"""
Exam Generation Endpoint (Admin).

Endpoint:
- POST /api/v1/exam-simulations/:id/generate - Start generation (Celery)
"""

from flask import Blueprint, jsonify

from app.middleware.auth import token_required, get_current_user
from app.database.connection import fetch_one

from ..core.services import ExamGenerationService


exam_generation_bp = Blueprint(
    'exam_generation',
    __name__,
    url_prefix='/exam-simulations'
)


@exam_generation_bp.route('/<simulation_id>/generate', methods=['POST'])
@token_required
def generate_exam_simulation(simulation_id: str):
    """
    Start exam generation (queues Celery task).

    Uses ExamGenerationService to:
    - Validate simulation status
    - Update status to 'generating'
    - Queue Celery task for AI generation

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

        # Start generation using service
        ExamGenerationService.start_generation(simulation_id)

        return jsonify({
            'success': True,
            'message': 'Generation started',
            'status': 'generating'
        }), 202

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to start generation',
            'details': str(e)
        }), 500
