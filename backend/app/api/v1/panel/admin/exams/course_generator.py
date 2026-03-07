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

    plan = ExamCourseGeneratorService.preview(
        exam_type, region, language,
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

    # First generate the plan
    plan = ExamCourseGeneratorService.preview(
        exam_type, region, language,
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
