"""
Course Editor - Exam Management

Feature-based exam management with permission-aware access.
Admin: Full access to all exams
User: Only access to exams in own courses

Endpoints:
- GET    /api/v1/course-editor/manual/courses/{course_id}/exams - List exams
- POST   /api/v1/course-editor/manual/courses/{course_id}/exams - Create exam
- POST   /api/v1/course-editor/manual/courses/{course_id}/exams/generate - Generate exam with AI
- GET    /api/v1/course-editor/manual/exams/{exam_id} - Get exam details
- PATCH  /api/v1/course-editor/manual/exams/{exam_id} - Update exam
- DELETE /api/v1/course-editor/manual/exams/{exam_id} - Delete exam
"""

from flask import request, jsonify, g
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

from app.api.v1.courses.editor.manual import manual_editor_bp
from app.api.v1.courses.editor.shared.permissions import check_course_permission
from app.domain.models.admin.exam import (
    ExamCreateRequest,
    ExamUpdateRequest,
    ExamGenerateRequest
)
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository
from app.infrastructure.persistence.repositories.exams.core import ExamRepository, ExamQuestionRepository
from app.application.services.system.audit.service import AuditService
from app.application.services.ai.job_service import AIJobService
from app.application.services.ai.prompts.resolver import PromptResolver
from app.api.middleware.auth import get_current_user
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response


@manual_editor_bp.route('/courses/<course_id>/exams', methods=['GET'])
@check_course_permission('read')
def list_exams(course_id: str):
    """List all exams for a course."""
    try:
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        exams = ExamRepository.find_by_course(course_id, include_unpublished=True)

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.exams.list',
            resource_type='course',
            resource_id=str(course_id),
            details={'exam_count': len(exams)}
        )

        return jsonify({'success': True, 'exams': exams}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_list_exams: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/courses/<course_id>/exams', methods=['POST'])
@check_course_permission('write')
def create_exam(course_id: str):
    """Create new exam manually (without AI)."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        exam_request = ExamCreateRequest(**data)

        exam_data = {
            'course_id': course_id,
            'exam_type': exam_request.exam_type.value,
            'title': exam_request.title,
            'description': exam_request.description,
            'duration_minutes': exam_request.duration_minutes,
            'passing_score': exam_request.passing_score,
            'total_points': exam_request.total_points,
            'settings': exam_request.settings,
            'published': exam_request.published,
            'generated_by_ai': False
        }

        exam = ExamRepository.create_exam(exam_data)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.exams.create',
            resource_type='exam',
            resource_id=str(exam['exam_id']),
            details={
                'course_id': course_id,
                'exam_title': exam['title'],
                'exam_type': exam['exam_type']
            },
            severity='medium'
        )

        return jsonify({'success': True, 'exam': exam}), 201

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})
    except Exception as e:
        logger.error(f"ERROR in admin_create_exam: {e}")
        return error_response(ErrorCode.EXAM_CREATE_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/courses/<course_id>/exams/generate', methods=['POST'])
@check_course_permission('write')
def generate_exam(course_id: str):
    """Generate exam using AI."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        generate_request = ExamGenerateRequest(**data)

        exam_data = {
            'course_id': course_id,
            'exam_type': 'ai_simulation',
            'title': generate_request.title,
            'description': generate_request.description,
            'duration_minutes': generate_request.duration_minutes,
            'passing_score': generate_request.passing_score,
            'total_points': generate_request.total_points,
            'settings': {
                'standard': generate_request.exam_standard.value,
                'difficulty': generate_request.difficulty,
                'question_distribution': generate_request.question_distribution,
                'topic_coverage': generate_request.topic_coverage,
                'source_chapters': generate_request.source_chapter_ids
            },
            'published': False,
            'generated_by_ai': True,
            'ai_model': 'gpt-4-turbo'
        }

        exam = ExamRepository.create_exam(exam_data)

        job = AIJobService.create_job(
            user_id=current_user['user_id'],
            job_type='exam_generation',
            input_file=None,
            input_prompt=f"Generate {generate_request.exam_standard.value} exam with {sum(generate_request.question_distribution.values())} questions",
            course_id=course_id
        )

        AIJobRepository.update(job['id'], {'exam_id': exam['exam_id']})

        try:
            resolved_prompt = PromptResolver.resolve(
                course_id=course_id,
                scope='exam_generation',
                language=course.get('language', 'de')
            )

            context = {
                'course_title': course['title'],
                'exam_title': generate_request.title,
                'exam_standard': generate_request.exam_standard.value,
                'difficulty': generate_request.difficulty or 'intermediate',
                'question_count': sum(generate_request.question_distribution.values()),
                'duration_minutes': generate_request.duration_minutes,
                'passing_score': generate_request.passing_score
            }

            rendered_messages = PromptResolver.resolve_and_render(
                course_id=course_id,
                scope='exam_generation',
                context=context,
                language=course.get('language', 'de')
            )

            AIJobRepository.update(job['id'], {
                'exam_id': exam['exam_id'],
                'input_prompt': f"[{resolved_prompt['source'].upper()}] Generate {generate_request.exam_standard.value} exam",
                'settings': {
                    'prompt_source': resolved_prompt['source'],
                    'rendered_messages': rendered_messages,
                    'context': context
                }
            })

        except Exception as prompt_error:
            logger.warning(f"Prompt resolution failed for course {course_id}, using fallback: {prompt_error}")

        AIJobService.update_job_status(job['id'], 'queued', progress=0)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.exams.generate',
            resource_type='exam',
            resource_id=str(exam['exam_id']),
            details={
                'course_id': course_id,
                'exam_title': exam['title'],
                'exam_standard': generate_request.exam_standard.value,
                'question_count': sum(generate_request.question_distribution.values()),
                'job_id': job['id']
            },
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': 'Exam generation started',
            'job_id': job['id'],
            'exam_id': exam['exam_id']
        }), 201

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})
    except Exception as e:
        logger.error(f"ERROR in admin_generate_exam: {e}")
        return error_response(ErrorCode.EXAM_GENERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/exams/<exam_id>', methods=['GET'])
@check_course_permission('read')
def get_exam(exam_id: str):
    """Get exam details with questions."""
    try:
        exam = ExamRepository.find_by_id(exam_id)

        if not exam:
            return error_response(ErrorCode.EXAM_NOT_FOUND, 404)

        questions = ExamQuestionRepository.find_by_exam(exam_id)
        exam['questions'] = questions

        return jsonify({'success': True, 'exam': exam}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_get_exam: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/exams/<exam_id>', methods=['PATCH'])
@check_course_permission('write')
def update_exam(exam_id: str):
    """Update exam metadata."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        existing_exam = ExamRepository.find_by_id(exam_id)
        if not existing_exam:
            return error_response(ErrorCode.EXAM_NOT_FOUND, 404)

        update_request = ExamUpdateRequest(**data)

        updated_exam = ExamRepository.update_exam(
            exam_id,
            update_request.model_dump(exclude_none=True)
        )

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.exams.update',
            resource_type='exam',
            resource_id=str(exam_id),
            details={
                'exam_title': updated_exam['title'],
                'changes': list(update_request.model_dump(exclude_none=True).keys())
            },
            severity='medium'
        )

        return jsonify({'success': True, 'exam': updated_exam}), 200

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'errors': e.errors()})
    except Exception as e:
        logger.error(f"ERROR in admin_update_exam: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@manual_editor_bp.route('/exams/<exam_id>', methods=['DELETE'])
@check_course_permission('delete')
def delete_exam(exam_id: str):
    """Delete exam and all questions."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')

        existing_exam = ExamRepository.find_by_id(exam_id)
        if not existing_exam:
            return error_response(ErrorCode.EXAM_NOT_FOUND, 404)

        ExamRepository.delete_exam(exam_id)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.exams.delete',
            resource_type='exam',
            resource_id=str(exam_id),
            details={
                'reason': reason,
                'exam_title': existing_exam['title'],
                'course_id': existing_exam['course_id']
            },
            severity='high'
        )

        return jsonify({'success': True, 'message': 'Exam deleted successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_delete_exam: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})
