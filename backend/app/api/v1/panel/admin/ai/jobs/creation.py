"""
AI Jobs Creation (DDD)

Endpoints for creating AI jobs:
- POST /api/v1/admin/settings/ai/jobs - Create new AI job
- POST /api/v1/admin/settings/ai/jobs/<id>/submit - Submit job for processing

Uses:
- AIJobFactory for job creation with business rules
- Repository Pattern for persistence

Job Types:
    - course_generation: Generate entire course
    - chapter_generation: Generate chapter content
    - lesson_generation: Generate lesson content
    - exam_generation: Generate exam questions
    - translation: Translate content
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
import uuid

from app.api.middleware.auth import token_required, permission_required
from app.infrastructure.persistence.repositories.ai.tracking.jobs import AIJobsRepository
from app.application.services.system.audit.service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain

logger = logging.getLogger(__name__)

jobs_creation_bp = Blueprint(
    'ai_jobs_creation',
    __name__,
    url_prefix='/panel/settings/ai/jobs'
)


# Valid job types
VALID_JOB_TYPES = {
    'course_generation',
    'chapter_generation',
    'lesson_generation',
    'exam_generation',
    'translation'
}


@jobs_creation_bp.route('', methods=['POST'])
@permission_required('admin.ai-jobs:write')
def create_ai_job() -> Tuple[Dict[str, Any], int]:
    """
    Create a new AI job.

    Request Body:
        job_type (str): Type of job (course_generation, chapter_generation, etc.)
        title (str): Job title
        description (str, optional): Job description
        configuration (dict): Job-specific configuration
        priority (int, optional): Job priority (1-10, default: 5)

    Returns:
        JSON response with created job

    DDD: Uses AIJobFactory to create job with business rules
    """
    try:
        data = request.get_json()
        if not data:
            return error_response(ErrorCode.VALIDATION_REQUEST_BODY_REQUIRED, 400)

        # Validate required fields
        required_fields = ['job_type', 'title', 'configuration']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400,
                details={'missing_fields': missing_fields})

        # Validate job type
        if data['job_type'] not in VALID_JOB_TYPES:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400,
                details={'field': 'job_type', 'valid_values': list(VALID_JOB_TYPES)})

        # DDD: Create job data (factory logic inlined)
        job_data = {
            'job_id': str(uuid.uuid4()),
            'job_type': data['job_type'],
            'title': data['title'],
            'description': data.get('description'),
            'creator_id': str(g.current_user.get('user_id')),
            'configuration': data['configuration'],
            'priority': data.get('priority', 5),
            'status': 'pending',
            'progress': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Persist to repository
        created_job = AIJobsRepository.create(job_data)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='create_ai_job',
            resource_type='ai_job',
            resource_id=created_job.get('job_id'),
            details={
                'job_type': created_job.get('job_type'),
                'title': created_job.get('title')
            }
        )

        return jsonify({
            'success': True,
            'data': created_job,
            'message': f'AI job "{created_job.get("title")}" created'
        }), 201

    except Exception as e:
        logger.error(f"Error creating AI job: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@jobs_creation_bp.route('/<job_id>/submit', methods=['POST'])
@permission_required('admin.ai-jobs:write')
def submit_ai_job(job_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Submit AI job for processing.

    Business Rules:
    - Job must be in 'pending' status
    - Job configuration must be valid
    - Required AI models must be available

    Args:
        job_id: The job's UUID

    Returns:
        JSON response with submitted job

    DDD: Uses business rules to validate submission
    """
    try:
        # Get job
        job = AIJobsRepository.get_by_id(job_id)
        if not job:
            return error_response(ErrorCode.AI_JOB_NOT_FOUND, 404, details={'job_id': job_id})

        # Business Rule: Job must be in pending status
        if job.get('status') != 'pending':
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400,
                details={'message': f'Job status is {job.get("status")}, expected pending'})

        # Business Rule: User must own the job or be admin
        current_user_id = str(g.current_user.get('user_id'))
        if job.get('creator_id') != current_user_id and not g.current_user.get('is_admin'):
            return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403,
                details={'message': 'You do not have permission to submit this job'})

        # Validate job configuration
        validation_result = _validate_job_configuration(
            job.get('job_type'),
            job.get('configuration', {})
        )

        if not validation_result['is_valid']:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400,
                details={'message': validation_result['error']})

        # Update job status to processing
        updated_job = AIJobsRepository.update(
            job_id,
            {
                'status': 'processing',
                'started_at': datetime.utcnow()
            }
        )

        # TODO: Enqueue job to Celery queue for background processing
        # from app.infrastructure.tasks.ai_jobs import process_ai_job
        # process_ai_job.delay(job_id)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='submit_ai_job',
            resource_type='ai_job',
            resource_id=job_id,
            details={
                'job_type': job.get('job_type'),
                'title': job.get('title')
            }
        )

        return jsonify({
            'success': True,
            'data': updated_job,
            'message': f'Job "{job.get("title")}" submitted for processing'
        }), 200

    except Exception as e:
        logger.error(f"Error submitting AI job {job_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


def _validate_job_configuration(job_type: str, configuration: dict) -> Dict[str, Any]:
    """
    Validate job configuration based on job type.

    Args:
        job_type: Type of job
        configuration: Job configuration

    Returns:
        Validation result with is_valid and error fields
    """
    # Course generation requires: subject, level, topics
    if job_type == 'course_generation':
        required = ['subject', 'level', 'topics']
        missing = [f for f in required if f not in configuration]
        if missing:
            return {
                'is_valid': False,
                'error': f'Course generation requires: {", ".join(missing)}'
            }

        # Validate topics is a list
        if not isinstance(configuration.get('topics'), list):
            return {
                'is_valid': False,
                'error': 'Topics must be a list'
            }

    # Chapter generation requires: course_id, chapter_title, content_outline
    elif job_type == 'chapter_generation':
        required = ['course_id', 'chapter_title', 'content_outline']
        missing = [f for f in required if f not in configuration]
        if missing:
            return {
                'is_valid': False,
                'error': f'Chapter generation requires: {", ".join(missing)}'
            }

    # Lesson generation requires: chapter_id, lesson_title, learning_methods
    elif job_type == 'lesson_generation':
        required = ['chapter_id', 'lesson_title', 'learning_methods']
        missing = [f for f in required if f not in configuration]
        if missing:
            return {
                'is_valid': False,
                'error': f'Lesson generation requires: {", ".join(missing)}'
            }

    # Exam generation requires: course_id, difficulty, question_count
    elif job_type == 'exam_generation':
        required = ['course_id', 'difficulty', 'question_count']
        missing = [f for f in required if f not in configuration]
        if missing:
            return {
                'is_valid': False,
                'error': f'Exam generation requires: {", ".join(missing)}'
            }

    # Translation requires: content_id, source_language, target_language
    elif job_type == 'translation':
        required = ['content_id', 'source_language', 'target_language']
        missing = [f for f in required if f not in configuration]
        if missing:
            return {
                'is_valid': False,
                'error': f'Translation requires: {", ".join(missing)}'
            }

    return {'is_valid': True}
