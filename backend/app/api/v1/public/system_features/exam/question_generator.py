"""
Question Generator — User-facing endpoint for practice exam generation.
"""

import logging
from flask import Blueprint, jsonify, request
from app.api.middleware.auth import token_required, get_current_user

logger = logging.getLogger(__name__)

question_generator_bp = Blueprint(
    'question_generator', __name__,
    url_prefix='/exam/question-generator',
)


@question_generator_bp.route('/generate-practice', methods=['POST'])
@token_required
def generate_practice():
    """Generate a personalized practice exam."""
    user = get_current_user()
    body = request.get_json(silent=True) or {}

    exam_type = body.get('exam_type')
    if not exam_type:
        return jsonify({'success': False, 'error': 'exam_type required'}), 400

    try:
        from app.application.services.exams.question_generator_service import QuestionGeneratorService
        from app.application.services.exams.prognosis_service import PrognosisService

        questions = []
        count = body.get('question_count', 10)
        difficulty = body.get('difficulty', 'mittel')
        focus_positions = body.get('focus_positions')

        if focus_positions:
            per_position = max(count // len(focus_positions), 1)
            for pos_id in focus_positions[:5]:
                try:
                    generated = QuestionGeneratorService.generate_for_position(
                        position_id=pos_id,
                        count=per_position,
                        difficulty=difficulty,
                        provider=body.get('provider'),
                        model=body.get('model'),
                    )
                    questions.extend(generated)
                except ValueError:
                    logger.warning("Skipping position %s: no objectives", pos_id)
        else:
            # Auto-select weak positions
            weaknesses = PrognosisService.get_user_weakness_map(
                user_id=str(user['user_id']),
                exam_type_key=exam_type,
            )
            weak_positions = [
                w for w in weaknesses
                if w.get('severity') in ('critical', 'moderate')
            ][:3]

            for wp in weak_positions:
                try:
                    generated = QuestionGeneratorService.generate_for_position(
                        position_id=wp['position_id'],
                        count=max(count // 3, 2),
                        difficulty=difficulty,
                        provider=body.get('provider'),
                        model=body.get('model'),
                    )
                    questions.extend(generated)
                except ValueError:
                    logger.warning("Skipping position %s", wp.get('position_id'))

        return jsonify({
            'success': True,
            'question_count': len(questions),
            'questions': questions,
        })
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400
