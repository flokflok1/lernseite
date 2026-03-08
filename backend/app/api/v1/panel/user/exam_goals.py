"""
User Exam Goals API

Endpoints for managing personal exam preparation goals.
Users can have multiple active goals for different exam types.
"""

import logging
from flask import Blueprint, jsonify, request

from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.persistence.repositories.exams.user_exam_goals import (
    UserExamGoalsRepository,
)
from app.infrastructure.persistence.repositories.exams.exam_type_registry import (
    ExamTypeRegistryRepository,
)
from app.application.services.exams.intelligence_service import (
    ExamIntelligenceService,
)

logger = logging.getLogger(__name__)

exam_goals_bp = Blueprint(
    'user_exam_goals',
    __name__,
    url_prefix='/user/exam-goals',
)


@exam_goals_bp.route('/', methods=['GET'])
@token_required
def list_goals():
    """List all exam goals for the current user."""
    user = get_current_user()
    goals = UserExamGoalsRepository.find_by_user(user['user_id'])
    return jsonify({'success': True, 'count': len(goals), 'goals': goals})


@exam_goals_bp.route('/', methods=['POST'])
@token_required
def create_goal():
    """Create or update an exam goal."""
    user = get_current_user()
    body = request.get_json(silent=True) or {}
    exam_type = body.get('exam_type')
    if not exam_type:
        return jsonify({'success': False, 'error': 'exam_type required'}), 400
    if not ExamTypeRegistryRepository.find_by_type(exam_type):
        return jsonify({'success': False, 'error': 'Unknown exam type'}), 404
    result = UserExamGoalsRepository.create(
        user_id=user['user_id'],
        exam_type=exam_type,
        target_date=body.get('target_date'),
        status=body.get('status', 'active'),
    )
    return jsonify({'success': True, 'goal': result}), 201


@exam_goals_bp.route('/<goal_id>/status', methods=['PUT'])
@token_required
def update_goal_status(goal_id):
    """Update goal status (active, passed, paused, planned)."""
    body = request.get_json(silent=True) or {}
    status = body.get('status')
    if status not in ('active', 'passed', 'paused', 'planned'):
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    result = UserExamGoalsRepository.update_status(goal_id, status)
    if not result:
        return jsonify({'success': False, 'error': 'Goal not found'}), 404
    return jsonify({'success': True, 'goal': result})


@exam_goals_bp.route('/<goal_id>', methods=['DELETE'])
@token_required
def delete_goal(goal_id):
    """Delete a goal."""
    UserExamGoalsRepository.delete(goal_id)
    return jsonify({'success': True})


@exam_goals_bp.route('/available-types', methods=['GET'])
@token_required
def available_exam_types():
    """List all available exam types for goal creation."""
    types = ExamTypeRegistryRepository.find_all()
    return jsonify({'success': True, 'exam_types': types})


@exam_goals_bp.route('/weakness-profile/<exam_type>', methods=['GET'])
@token_required
def get_weakness_profile(exam_type):
    """Get weakness profile for a specific exam type."""
    user = get_current_user()
    profile = ExamIntelligenceService.get_weakness_profile(
        user['user_id'], exam_type
    )
    return jsonify({'success': True, 'profile': profile.to_dict()})


@exam_goals_bp.route('/curriculum-profile/<exam_type_key>', methods=['GET'])
@token_required
def get_curriculum_profile(exam_type_key):
    """Get user performance aggregated by curriculum position."""
    from app.application.services.exams.curriculum_service import CurriculumService

    user = get_current_user()
    try:
        profile = CurriculumService.get_user_curriculum_profile(
            user['user_id'], exam_type_key,
        )
        return jsonify({'success': True, 'profile': profile})
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 404
    except Exception:
        logger.exception(
            "Failed to load curriculum profile for user %s",
            user['user_id'],
        )
        return jsonify({
            'success': False,
            'error': 'Failed to load curriculum profile',
        }), 500
