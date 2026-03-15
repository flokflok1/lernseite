"""
ExamTrainer API — User-facing endpoints for exam practice.

Endpoints:
- GET  /user/exam-trainer/exams                    — List available exams
- GET  /user/exam-trainer/exams/<id>/questions      — Get questions for practice
- GET  /user/exam-trainer/topics                    — Topic overview with stats
- GET  /user/exam-trainer/topics/<topic>/questions   — Questions for a topic
- POST /user/exam-trainer/submit-answer             — Submit and grade an answer
- POST /user/exam-trainer/start-exam/<id>           — Start a timed attempt
- POST /user/exam-trainer/complete-attempt/<id>     — Complete an attempt
- POST /user/exam-trainer/practice-session          — Rotated practice session
"""

import logging

from flask import Blueprint, jsonify, request
from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.infrastructure.persistence.repositories.exams.trainer import (
    ExamTrainerRepository
)
from app.api.v1.panel.user.exams.trainer_helpers import (
    strip_solutions,
    grade_and_record,
    finalize_attempt
)

logger = logging.getLogger(__name__)

trainer_bp = Blueprint(
    'exam_trainer', __name__, url_prefix='/user/exam-trainer'
)


@trainer_bp.route('/exams', methods=['GET'])
@token_required
def list_exams():
    """
    List available archive exams for practice.

    Only returns published exams with analysis_status='ready'.

    Response 200:
        [{exam_id, title, semester, part, question_count, ...}]
    """
    try:
        exams = ExamTrainerRepository.find_published_archive_exams()
        return jsonify({'success': True, 'exams': exams}), 200
    except Exception as e:
        logger.error("Failed to list trainer exams: %s", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@trainer_bp.route('/exams/<exam_id>/questions', methods=['GET'])
@token_required
def get_exam_questions(exam_id: str):
    """
    Get all questions for an exam (practice mode).

    Solutions are stripped from the response so the user
    cannot see answers before submitting.

    Response 200:
        [{question_id, question_text, question_type, data, points, ...}]
    """
    try:
        exam = ExamRepository.find_by_id(exam_id)
        if not exam:
            return jsonify({
                'success': False, 'error': 'Exam not found'
            }), 404

        questions = ExamQuestionRepository.find_by_exam(exam_id)
        sanitized = strip_solutions(questions)

        return jsonify({
            'success': True,
            'exam': {
                'exam_id': exam['exam_id'],
                'title': exam.get('title', ''),
                'semester': exam.get('semester', ''),
                'part': exam.get('part', ''),
                'duration_minutes': exam.get('duration_minutes'),
                'passing_score': exam.get('passing_score'),
                'total_points': exam.get('total_points'),
            },
            'questions': sanitized
        }), 200
    except Exception as e:
        logger.error("Failed to get exam questions: %s", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@trainer_bp.route('/topics', methods=['GET'])
@token_required
def list_topics():
    """
    List all distinct topics across archive questions
    with per-user statistics.

    Response 200:
        [{topic, question_count, user_attempts, correct_pct}]
    """
    try:
        user = get_current_user()
        topics = ExamTrainerRepository.find_topics_with_stats(
            user['user_id']
        )
        return jsonify({'success': True, 'topics': topics}), 200
    except Exception as e:
        logger.error("Failed to list topics: %s", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@trainer_bp.route('/topics/<topic>/questions', methods=['GET'])
@token_required
def get_topic_questions(topic: str):
    """
    Get questions for a specific topic.

    Solutions are stripped from the response.

    Response 200:
        [{question_id, question_text, question_type, data, points, ...}]
    """
    try:
        questions = ExamQuestionRepository.find_by_topics([topic])
        sanitized = strip_solutions(questions)

        return jsonify({
            'success': True,
            'topic': topic,
            'questions': sanitized
        }), 200
    except Exception as e:
        logger.error("Failed to get topic questions: %s", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@trainer_bp.route('/submit-answer', methods=['POST'])
@token_required
def submit_answer():
    """
    Submit and auto-grade a single question answer.

    Body:
        {question_id, user_answer, exam_id (optional),
         attempt_id (optional)}

    Auto-grades MCQ and calculation types. Free-text is
    marked as needs_review.

    Response 200:
        {is_correct, correct_answer, explanation, points_earned}
    """
    try:
        user = get_current_user()
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False, 'error': 'Request body required'
            }), 400

        question_id = data.get('question_id')
        user_answer = data.get('user_answer')
        attempt_id = data.get('attempt_id')

        if not question_id or user_answer is None:
            return jsonify({
                'success': False,
                'error': 'question_id and user_answer are required'
            }), 400

        return grade_and_record(
            user, question_id, user_answer, attempt_id
        )
    except Exception as e:
        logger.error("Failed to submit answer: %s", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@trainer_bp.route('/start-exam/<exam_id>', methods=['POST'])
@token_required
def start_exam(exam_id: str):
    """
    Start a timed exam attempt.

    Creates an attempt record and returns all questions
    (without solutions).

    Response 200:
        {attempt_id, questions, time_limit_minutes}
    """
    try:
        user = get_current_user()
        exam = ExamRepository.find_by_id(exam_id)
        if not exam:
            return jsonify({
                'success': False, 'error': 'Exam not found'
            }), 404

        time_limit = exam.get('duration_minutes', 90)

        attempt = ExamTrainerRepository.create_attempt(
            user_id=user['user_id'],
            exam_id=exam_id,
            time_limit_minutes=time_limit
        )

        questions = ExamQuestionRepository.find_by_exam(exam_id)
        sanitized = strip_solutions(questions)

        return jsonify({
            'success': True,
            'attempt_id': attempt['attempt_id'],
            'time_limit_minutes': time_limit,
            'questions': sanitized
        }), 200
    except Exception as e:
        logger.error("Failed to start exam: %s", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@trainer_bp.route(
    '/complete-attempt/<attempt_id>', methods=['POST']
)
@token_required
def complete_attempt(attempt_id: str):
    """
    Complete an exam attempt and calculate results.

    Aggregates scores from exam_answers, creates an
    exam_results record, and returns the summary.

    Response 200:
        {score, total_points, percentage, passed, results_by_topic}
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

        if attempt.get('status') == 'completed':
            return jsonify({
                'success': False, 'error': 'Attempt already completed'
            }), 400

        return finalize_attempt(attempt, user)
    except Exception as e:
        logger.error("Failed to complete attempt: %s", e)
        return jsonify({'success': False, 'error': str(e)}), 500


@trainer_bp.route('/weaknesses', methods=['GET'])
@token_required
def get_user_weaknesses():
    """Get user weakness map sorted by severity."""
    user = get_current_user()
    exam_type = request.args.get('exam_type')
    if not exam_type:
        return jsonify({'success': False, 'error': 'exam_type parameter required'}), 400
    try:
        from app.application.services.exams.prognosis_service import PrognosisService
        weaknesses = PrognosisService.get_user_weakness_map(
            user_id=str(user['user_id']),
            exam_type_key=exam_type,
        )
        return jsonify({'success': True, 'weaknesses': weaknesses})
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400


@trainer_bp.route('/cockpit', methods=['GET'])
@token_required
def get_exam_cockpit():
    """GET /user/exam-trainer/cockpit?exam_type=FI_AP1

    Returns aggregated cockpit data for the user's exam preparation.
    """
    user = get_current_user()
    exam_type = request.args.get('exam_type')
    if not exam_type:
        return jsonify({
            'success': False, 'error': 'exam_type parameter required'
        }), 400

    try:
        from app.application.services.exams.exam_cockpit_service import (
            ExamCockpitService,
        )
        data = ExamCockpitService.get_dashboard(
            str(user['user_id']), exam_type,
        )
        return jsonify({'success': True, **data})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception:
        logger.exception(
            "Cockpit data failed for user=%s", user['user_id'],
        )
        return jsonify({
            'success': False, 'error': 'Failed to load cockpit data'
        }), 500


@trainer_bp.route('/practice-session', methods=['POST'])
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
        {questions: [...], session_info: {total, unseen, weak, review}}
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
            'success': False, 'error': 'Failed to create practice session'
        }), 500


@trainer_bp.route('/attempt/<attempt_id>/review', methods=['GET'])
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


@trainer_bp.route('/history', methods=['GET'])
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
