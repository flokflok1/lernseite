"""
Exam Course Generator API — Admin endpoints for auto-generating
structured courses from real IHK exam questions.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.api.middleware.auth import admin_required
from app.application.services.exams.course_generator_service import (
    ExamCourseGeneratorService,
)

course_gen_bp = Blueprint(
    'exam_course_generator',
    __name__,
    url_prefix='/admin/exam-courses',
)


@course_gen_bp.route('/preview', methods=['POST'])
@admin_required
def preview_course():
    """
    Preview course plan without creating anything.

    Body: {exam_type: str, region?: str}
    Returns: {plan: {...chapters, total_questions, total_points}}
    """
    data = request.get_json() or {}
    exam_type = data.get('exam_type')
    if not exam_type:
        return jsonify({'error': 'exam_type is required'}), 400

    region = data.get('region', 'alle')
    language = data.get('language', 'de')
    framework_id = data.get('framework_id')
    sort_mode = data.get('sort_mode', 'relevance')
    grouping_strategy = data.get('grouping_strategy', 'exam_practice')
    user_id = get_jwt_identity()

    plan = ExamCourseGeneratorService.preview(
        exam_type, region, language,
        framework_id=framework_id,
        sort_mode=sort_mode,
        user_id=user_id,
        grouping_strategy=grouping_strategy,
    )

    return jsonify({
        'success': True,
        'plan': plan.to_dict(),
    }), 200


@course_gen_bp.route('/generate', methods=['POST'])
@admin_required
def generate_course():
    """
    Generate a full course from exam questions.

    Body: {exam_type: str, region?: str, options?: {provider, model}}
    Returns: {course_id, chapters_count, lm_count, tokens_used}
    """
    data = request.get_json() or {}
    exam_type = data.get('exam_type')
    if not exam_type:
        return jsonify({'error': 'exam_type is required'}), 400

    region = data.get('region', 'alle')
    options = data.get('options', {})
    language = data.get('language', 'de')
    options.setdefault('language', language)
    user_id = get_jwt_identity()
    framework_id = data.get('framework_id')
    sort_mode = data.get('sort_mode', 'relevance')
    grouping_strategy = data.get('grouping_strategy', 'exam_practice')

    # First generate the plan (with intelligence scoring)
    plan = ExamCourseGeneratorService.preview(
        exam_type, region, language,
        framework_id=framework_id,
        sort_mode=sort_mode,
        user_id=user_id,
        grouping_strategy=grouping_strategy,
    )

    if not plan.chapters:
        return jsonify({
            'error': 'No questions found for given type and region',
        }), 404

    # Then persist it
    result = ExamCourseGeneratorService.generate(
        plan=plan,
        creator_user_id=user_id,
        options=options,
    )

    return jsonify({
        'success': True,
        **result,
    }), 201


@course_gen_bp.route('/courses/<course_id>/generation-progress', methods=['GET'])
@admin_required
def get_course_generation_progress(course_id):
    """
    Get real-time generation progress for a course.

    Reads from Redis (set by the Celery background task).
    Returns: {total, completed, failed, status}
    """
    progress = ExamCourseGeneratorService.get_generation_progress(course_id)
    return jsonify({'success': True, 'data': progress}), 200


# ── Cluster Intelligence ──────────────────────────────────────


@course_gen_bp.route('/clusters/suggest', methods=['POST'])
@admin_required
def suggest_clusters():
    """AI-powered cluster suggestion for an exam type."""
    from app.application.services.exams.cluster_intelligence import (
        ClusterIntelligenceService,
    )
    data = request.get_json(silent=True) or {}
    exam_type_key = data.get('exam_type_key')
    if not exam_type_key:
        return jsonify({'error': 'exam_type_key required'}), 400

    result = ClusterIntelligenceService.suggest_clusters(
        exam_type_key,
        region=data.get('region', 'alle'),
        options={
            'provider': data.get('provider'),
            'model': data.get('model'),
        },
    )
    return jsonify(result)


@course_gen_bp.route('/clusters/apply', methods=['POST'])
@admin_required
def apply_clusters():
    """Save admin-approved clusters to DB."""
    from app.application.services.exams.cluster_intelligence import (
        ClusterIntelligenceService,
    )
    data = request.get_json(silent=True) or {}
    exam_type_key = data.get('exam_type_key')
    clusters = data.get('clusters')
    if not exam_type_key or not clusters:
        return jsonify({
            'error': 'exam_type_key and clusters required',
        }), 400

    count = ClusterIntelligenceService.apply_suggestion(
        exam_type_key, clusters,
    )
    return jsonify({'saved': count, 'exam_type_key': exam_type_key})


@course_gen_bp.route('/clusters', methods=['GET'])
@admin_required
def get_clusters():
    """Get current clusters for an exam type."""
    from app.infrastructure.persistence.repositories.exams.topic_clusters import (
        ExamTopicClusterRepository,
    )
    exam_type_key = request.args.get('exam_type_key')
    if not exam_type_key:
        return jsonify({'error': 'exam_type_key required'}), 400

    clusters = ExamTopicClusterRepository.find_by_exam_type(
        exam_type_key,
    )
    return jsonify({
        'clusters': clusters,
        'exam_type_key': exam_type_key,
    })
