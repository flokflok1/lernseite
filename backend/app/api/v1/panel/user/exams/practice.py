"""
Practice Session API — configurable practice mode with sequential/mixed ordering.

DDD Layer: API — delegates to RotationService, no business logic here.
"""

import logging
from flask import jsonify, request
from app.api.middleware.auth import token_required, get_current_user
from app.application.services.exams.rotation_service import RotationService
from app.domain.models.practice_session import (
    PracticeConfig, PracticeMode, PracticeOrder,
)

logger = logging.getLogger(__name__)

VALID_MODES = {m.value for m in PracticeMode}
VALID_ORDERS = {o.value for o in PracticeOrder}


def register_practice_routes(bp):
    """Register practice session routes on the exam trainer blueprint."""

    @bp.route('/practice-config/count', methods=['GET'])
    @token_required
    def practice_question_count():
        """Get available question count for practice config panel."""
        from app.infrastructure.persistence.repositories.exams.trainer import (
            ExamTrainerRepository,
        )
        exam_filter = request.args.getlist('exam_filter')
        topic_filter = request.args.getlist('topic_filter')
        count = ExamTrainerRepository.count_available_questions(
            exam_filter=exam_filter or None,
            topic_filter=topic_filter or None,
        )
        return jsonify({'success': True, 'count': count})

    @bp.route('/practice-session', methods=['POST'])
    @token_required
    def start_practice_session():
        """
        Start a configurable practice session.

        Body: {mode, order, question_count, time_limit_minutes, exam_filter, topic_filter}
        """
        user = get_current_user()
        data = request.get_json(silent=True) or {}

        mode_str = data.get('mode', 'discover')
        order_str = data.get('order', 'sequential')

        if mode_str not in VALID_MODES:
            return jsonify({
                'success': False, 'error': 'INVALID_CONFIG',
                'detail': f'Invalid mode: {mode_str}',
            }), 400

        if order_str not in VALID_ORDERS:
            return jsonify({
                'success': False, 'error': 'INVALID_CONFIG',
                'detail': f'Invalid order: {order_str}',
            }), 400

        config = PracticeConfig(
            mode=PracticeMode(mode_str),
            order=PracticeOrder(order_str),
            question_count=data.get('question_count'),
            time_limit_minutes=data.get('time_limit_minutes'),
            exam_filter=data.get('exam_filter', []),
            topic_filter=data.get('topic_filter', []),
        )

        try:
            result = RotationService.generate_practice_session(
                user_id=user['user_id'], config=config,
            )
        except Exception:
            logger.exception(
                "Practice session creation failed for user=%s",
                user['user_id'],
            )
            return jsonify({
                'success': False, 'error': 'SESSION_CREATION_FAILED',
            }), 500

        if not result.get('questions'):
            return jsonify({
                'success': False, 'error': 'NO_QUESTIONS',
                'total_available': result.get('total_available', 0),
            }), 400

        return jsonify({'success': True, **result})
