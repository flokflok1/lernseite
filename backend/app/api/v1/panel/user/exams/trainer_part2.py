"""
ExamTrainer API Part 2 — Advanced endpoints.

Continuation of trainer.py for G01 compliance (max 500 LOC per file).

Endpoints:
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

    @bp.route('/programs', methods=['GET'])
    @token_required
    def get_programs():
        """List available exam training programs.

        Returns courses that have learning chapters, along with
        question pool statistics for the current user.

        Response 200:
            {programs: [{course_id, title, description, total_questions,
                         seen_questions, mastered_questions, chapter_count}]}
        """
        try:
            user = get_current_user()
            programs = ExamTrainerRepository.find_programs(user['user_id'])
            return jsonify({'success': True, 'programs': programs}), 200
        except Exception:
            logger.exception("Failed to load programs")
            return jsonify({
                'success': False, 'error': 'Failed to load programs'
            }), 500

    # NOTE: POST /practice-session moved to practice.py (configurable practice mode)

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

    @bp.route('/practice-single', methods=['POST'])
    @token_required
    def practice_single_question():
        """Start a 1-question practice session for a specific question.

        Body:
            {question_id: str}

        Response 200:
            {attempt_id, questions: [single question], duration_minutes: 0,
             total_points, question_count: 1}
        """
        try:
            user = get_current_user()
            data = request.get_json(silent=True) or {}
            question_id = data.get('question_id')
            if not question_id:
                return jsonify({
                    'success': False, 'error': 'question_id required',
                }), 400

            from app.infrastructure.persistence.repositories.exams.questions import (
                ExamQuestionRepository,
            )
            questions = ExamQuestionRepository.find_by_ids([question_id])
            if not questions:
                return jsonify({
                    'success': False, 'error': 'Question not found',
                }), 404

            q = questions[0]
            # Create an adaptive attempt for tracking
            attempt = ExamTrainerRepository.create_adaptive_attempt(
                user_id=user['user_id'],
                duration_minutes=0,
                total_points=int(q.get('points', 5)),
            )
            # Strip solution for the response
            sanitized = strip_solutions([q])
            return jsonify({
                'success': True,
                'attempt_id': attempt['attempt_id'],
                'questions': sanitized,
                'duration_minutes': 0,
                'total_points': float(q.get('points', 5)),
                'question_count': 1,
            }), 200
        except Exception:
            logger.exception("Failed to start single question practice")
            return jsonify({
                'success': False,
                'error': 'Failed to start practice',
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

        Query params:
            course_id: Optional course UUID to load chapters for

        Response 200:
            {pool: {total_questions, seen_questions, mastered_questions},
             topics: [...], recent_attempts: [...], chapters: [...]}
        """
        try:
            user = get_current_user()
            user_id = user['user_id']

            pool_stats = ExamTrainerRepository.count_pool_stats(user_id)
            topics = ExamTrainerRepository.find_topics_with_stats(user_id)
            exam_type_key = request.args.get('exam_type_key')

            # Use aggregated topic stats if hierarchy exists
            from app.application.services.topics.topic_hierarchy_service import (
                TopicHierarchyService,
            )
            hierarchy = TopicHierarchyService.get_hierarchy()
            if hierarchy:
                topics = TopicHierarchyService.get_aggregated_stats(
                    user_id, exam_type_key=exam_type_key,
                )

            history = ExamTrainerRepository.get_user_attempt_history(
                user_id, limit=5,
            )

            # Top topics from exam questions (no course dependency)
            exam_topics = ExamTrainerRepository.find_exam_topics()

            return jsonify({
                'success': True,
                'pool': pool_stats,
                'topics': topics,
                'recent_attempts': history,
                'chapters': exam_topics,
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
        """Return Anlagen for an exam from the exam_anlagen table.

        Response 200:
            {anlagen: [{number, title, type, content_html, data}]}
        """
        try:
            from app.infrastructure.persistence.repositories.exams.questions import (
                ExamQuestionRepository,
            )
            rows = ExamQuestionRepository.get_anlagen(exam_id)
            anlagen = [
                {
                    'number': r['number'],
                    'title': r['title'],
                    'type': 'html',
                    'content_html': r['content_html'],
                    'data': {},
                }
                for r in rows
            ]
            return jsonify({'success': True, 'anlagen': anlagen}), 200
        except Exception:
            logger.exception(
                "Failed to extract Anlagen for exam %s", exam_id,
            )
            return jsonify({
                'success': False, 'error': 'Failed to extract Anlagen'
            }), 500

    @bp.route('/questions/browse', methods=['GET'])
    @token_required
    def browse_questions():
        """Browse all exam questions with filters.

        Query params: topic, exam_id, status (all|unseen|weak|mastered),
                      page, per_page
        """
        try:
            user = get_current_user()
            filters = {
                'topic': request.args.get('topic'),
                'exam_id': request.args.get('exam_id'),
                'exam_type_key': request.args.get('exam_type_key'),
                'status': request.args.get('status', 'all'),
                'page': int(request.args.get('page', 1)),
                'per_page': int(request.args.get('per_page', 20)),
            }
            result = ExamTrainerRepository.find_questions_browse(
                user['user_id'], filters,
            )
            for q in result['questions']:
                q.pop('solution', None)
                q.pop('solution_text', None)
            return jsonify({'success': True, **result}), 200
        except Exception:
            logger.exception("Failed to browse questions")
            return jsonify({
                'success': False, 'error': 'Failed to browse questions',
            }), 500

    @bp.route('/topic-frequency', methods=['GET'])
    @token_required
    def get_topic_frequency():
        """Get topic frequency analysis across all exams.

        Shows which topics appear most often — useful for exam prep focus.

        Response 200:
            {topics: [{topic, exam_count, question_count, latest_year,
                       frequency_pct}]}
        """
        try:
            rows = ExamTrainerRepository.get_topic_frequency()
            # Count actual distinct exams for percentage
            from app.infrastructure.persistence.repositories.exams.core import (
                ExamRepository,
            )
            all_exams = ExamRepository.find_archive_exams(status='ready')
            exam_total = len(all_exams) if all_exams else 1

            # Build display_name lookup from topic nodes
            from app.infrastructure.persistence.repositories.exams.topic_nodes import (
                TopicNodeRepository,
            )
            all_nodes = TopicNodeRepository.find_all()
            node_map = {n['topic_key']: n for n in all_nodes}

            # Aggregate by root parent if hierarchy exists
            aggregated: dict = {}
            for r in rows:
                topic_key = r['topic']
                node = node_map.get(topic_key)
                # Find root: if has parent, use parent
                root_key = topic_key
                if node and node.get('parent_key'):
                    root_key = node['parent_key']

                if root_key not in aggregated:
                    root_node = node_map.get(root_key)
                    aggregated[root_key] = {
                        'topic': root_key,
                        'display_name': root_node.get('display_name', {}) if root_node else {},
                        'exam_count': 0,
                        'question_count': 0,
                        'latest_year': None,
                    }
                agg = aggregated[root_key]
                agg['exam_count'] = max(agg['exam_count'], r['exam_count'])
                agg['question_count'] += r['question_count']
                if r.get('latest_year'):
                    if not agg['latest_year'] or r['latest_year'] > agg['latest_year']:
                        agg['latest_year'] = r['latest_year']

            topics = sorted(aggregated.values(), key=lambda x: x['exam_count'], reverse=True)
            for t_item in topics:
                t_item['frequency_pct'] = round(
                    t_item['exam_count'] / exam_total * 100, 1,
                )

            return jsonify({
                'success': True,
                'total_exams': exam_total,
                'topics': topics,
            }), 200
        except Exception:
            logger.exception("Failed to get topic frequency")
            return jsonify({
                'success': False, 'error': 'Failed to load topic frequency',
            }), 500
