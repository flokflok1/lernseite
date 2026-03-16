"""
ExamTrainer API Part 2 — Advanced endpoints.

Continuation of trainer.py for G01 compliance (max 500 LOC per file).

Endpoints:
- POST /user/exam-trainer/practice-session     — Rotated practice session
- GET  /user/exam-trainer/attempt/<id>/review   — Review completed attempt
- GET  /user/exam-trainer/history               — Attempt history
- POST /user/exam-trainer/generate-exam         — Adaptive exam generation
- GET  /user/exam-trainer/dashboard             — Adaptive trainer dashboard
- GET  /user/exam-trainer/exams/<id>/anlagen    — Exam Anlagen extraction
"""

import logging

from flask import jsonify, request
from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.trainer import (
    ExamTrainerRepository
)
from app.api.v1.panel.user.exams.trainer_helpers import strip_solutions

logger = logging.getLogger(__name__)


def register_advanced_routes(bp):
    """Register advanced trainer routes on the given blueprint."""

    @bp.route('/practice-session', methods=['POST'])
    @token_required
    def practice_session():
        """Create a rotated practice session with intelligent question selection.

        Body:
            {exam_type: str, topic?: str, count?: int (default 15)}

        Uses rotation algorithm:
        - ~40% never-seen questions
        - ~30% weak questions (wrong answers)
        - ~30% review questions (not seen in >7 days)

        Response 200:
            {questions: [...], session_info: {total, topic}}
        """
        try:
            user = get_current_user()
            data = request.get_json() or {}
            exam_type = data.get('exam_type')
            if not exam_type:
                return jsonify({
                    'success': False, 'error': 'exam_type is required'
                }), 400

            topic = data.get('topic')
            count = min(data.get('count', 15), 30)

            from app.application.services.exams.rotation_service import (
                RotationService,
            )
            questions = RotationService.build_practice_session(
                user_id=str(user['user_id']),
                exam_type=exam_type,
                topic=topic,
                count=count,
            )
            sanitized = strip_solutions(questions)

            return jsonify({
                'success': True,
                'questions': sanitized,
                'session_info': {
                    'total': len(sanitized),
                    'topic': topic,
                },
            }), 200
        except Exception:
            logger.exception("Failed to create practice session")
            return jsonify({
                'success': False,
                'error': 'Failed to create practice session',
            }), 500

    @bp.route('/attempt/<attempt_id>/review', methods=['GET'])
    @token_required
    def get_attempt_review(attempt_id: str):
        """Get full review data for a completed attempt (with solutions).

        Response 200:
            {questions: [{question_id, question_text, user_answer,
                          is_correct, solution, points_earned, max_points, ...}]}
        """
        try:
            user = get_current_user()
            attempt = ExamTrainerRepository.find_attempt(attempt_id)
            if not attempt:
                return jsonify({
                    'success': False, 'error': 'Attempt not found'
                }), 404
            if attempt['user_id'] != user['user_id']:
                return jsonify({
                    'success': False, 'error': 'Not your attempt'
                }), 403
            if attempt.get('status') != 'completed':
                return jsonify({
                    'success': False, 'error': 'Attempt not yet completed'
                }), 400

            review = ExamTrainerRepository.get_attempt_review(attempt_id)
            return jsonify({'success': True, 'questions': review}), 200
        except Exception:
            logger.exception("Failed to get attempt review")
            return jsonify({
                'success': False, 'error': 'Failed to load review'
            }), 500

    @bp.route('/history', methods=['GET'])
    @token_required
    def get_attempt_history():
        """Get user's past attempt history for progress tracking.

        Response 200:
            {attempts: [{attempt_id, exam_title, score, percentage,
                         passed, completed_at, ...}]}
        """
        try:
            user = get_current_user()
            limit = min(int(request.args.get('limit', 20)), 50)
            attempts = ExamTrainerRepository.get_user_attempt_history(
                str(user['user_id']), limit,
            )
            return jsonify({'success': True, 'attempts': attempts}), 200
        except Exception:
            logger.exception("Failed to get attempt history")
            return jsonify({
                'success': False, 'error': 'Failed to load history'
            }), 500

    @bp.route('/generate-exam', methods=['POST'])
    @token_required
    def generate_adaptive_exam():
        """Generate an adaptive exam using rotation algorithm.

        Body:
            {question_count?: int (default 20, max 40),
             duration_minutes?: int (default 90)}

        Response 200:
            {attempt_id, questions, duration_minutes, total_points,
             question_count}
        """
        try:
            user = get_current_user()
            data = request.get_json(silent=True) or {}
            question_count = min(int(data.get('question_count', 20)), 40)
            duration_minutes = int(data.get('duration_minutes', 90))

            from app.application.services.exams.rotation_service import (
                RotationService,
            )
            result = RotationService.generate_adaptive_exam(
                user_id=str(user['user_id']),
                question_count=question_count,
                duration_minutes=duration_minutes,
            )

            if not result:
                return jsonify({
                    'success': False,
                    'error': 'No questions available in pool',
                }), 404

            return jsonify({'success': True, **result}), 200
        except Exception:
            logger.exception("Failed to generate adaptive exam")
            return jsonify({
                'success': False,
                'error': 'Failed to generate adaptive exam',
            }), 500

    @bp.route('/dashboard', methods=['GET'])
    @token_required
    def get_dashboard():
        """Get adaptive trainer dashboard data.

        Response 200:
            {pool: {total_questions, seen_questions, mastered_questions},
             topics: [...], recent_attempts: [...]}
        """
        try:
            user = get_current_user()
            user_id = user['user_id']

            pool_stats = ExamTrainerRepository.count_pool_stats(user_id)
            topics = ExamTrainerRepository.find_topics_with_stats(user_id)
            history = ExamTrainerRepository.get_user_attempt_history(
                user_id, limit=5,
            )

            return jsonify({
                'success': True,
                'pool': pool_stats,
                'topics': topics,
                'recent_attempts': history,
            }), 200
        except Exception:
            logger.exception("Failed to load dashboard data")
            return jsonify({
                'success': False,
                'error': 'Failed to load dashboard data',
            }), 500

    @bp.route('/exams/<exam_id>/anlagen', methods=['GET'])
    @token_required
    def get_exam_anlagen(exam_id: str):
        """Extract and return structured Anlagen for an exam.

        Parses exam raw_text to find Anlage sections, classifies each
        (offer, api_reference, info_document, generic), and returns
        structured data for the frontend AnlageViewer.

        Response 200:
            {anlagen: [{number, title, type, raw_text, data}]}
        """
        try:
            exam = ExamRepository.find_by_id(exam_id)
            if not exam:
                return jsonify({
                    'success': False, 'error': 'Exam not found'
                }), 404

            from app.application.services.exams.anlage_extractor import (
                extract_anlagen,
            )
            anlagen = extract_anlagen(exam.get('raw_text', ''))
            return jsonify({'success': True, 'anlagen': anlagen}), 200
        except Exception:
            logger.exception(
                "Failed to extract Anlagen for exam %s", exam_id,
            )
            return jsonify({
                'success': False, 'error': 'Failed to extract Anlagen'
            }), 500
