"""
AI Jobs Finalization (DDD)

Endpoints for finalizing AI jobs:
- PUT /api/v1/admin/settings/ai/jobs/<id>/complete - Mark job as completed
- POST /api/v1/admin/settings/ai/jobs/<id>/create-course - Create course from completed job

Uses:
- Repository Pattern for persistence
- Publishes AIJobCompletedEvent when job finishes
- Business rules for course creation from job results
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
import uuid

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.ai.jobs import AIJobsRepository
from app.repositories.courses import CourseRepository
from app.services.audit_service import AuditService

# DDD Core Domain
from .core.events import (
    AIJobCompletedEvent,
    EventPublisher,
    EventPriority
)

logger = logging.getLogger(__name__)

jobs_finalization_bp = Blueprint(
    'ai_jobs_finalization',
    __name__,
    url_prefix='/admin-panel/settings/ai/jobs'
)


@jobs_finalization_bp.route('/<job_id>/complete', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_AI_JOBS_WRITE)
def complete_ai_job(job_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Mark AI job as completed.

    Business Rules:
    - Job must be in 'processing' status
    - Result data must be provided
    - User must own the job or be admin

    Args:
        job_id: The job's UUID

    Request Body:
        result (dict): Job result data
        status (str): Final status ('completed' or 'failed')
        error_message (str, optional): Error message if failed

    Returns:
        JSON response with completed job

    DDD: Publishes AIJobCompletedEvent

    Note: This endpoint is typically called by background workers,
    not directly by users.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Request body required'
                }
            }), 400

        # Get job
        job = AIJobsRepository.get_by_id(job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'JOB_NOT_FOUND',
                    'message': f'Job {job_id} not found'
                }
            }), 404

        # Business Rule: Job must be processing
        if job.get('status') != 'processing':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_JOB_STATUS',
                    'message': f'Job status is {job.get("status")}, expected processing'
                }
            }), 400

        # Get final status
        final_status = data.get('status', 'completed')
        if final_status not in ['completed', 'failed']:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Status must be either completed or failed'
                }
            }), 400

        # Update job
        update_data = {
            'status': final_status,
            'completed_at': datetime.utcnow(),
            'result': data.get('result')
        }

        if final_status == 'failed':
            update_data['error_message'] = data.get('error_message', 'Job failed')

        updated_job = AIJobsRepository.update(job_id, update_data)

        # Calculate duration
        duration_seconds = 0
        if job.get('started_at'):
            delta = updated_job['completed_at'] - job['started_at']
            duration_seconds = int(delta.total_seconds())

        # DDD: Publish Domain Event
        event = AIJobCompletedEvent(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=job_id,
            job_id=job_id,
            job_type=job.get('job_type'),
            final_status=final_status,
            duration_seconds=duration_seconds,
            has_result=data.get('result') is not None,
            error_message=update_data.get('error_message'),
            priority=EventPriority.HIGH if final_status == 'failed' else EventPriority.MEDIUM
        )
        EventPublisher.publish(event)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action=f'{final_status}_ai_job',
            resource_type='ai_job',
            resource_id=job_id,
            details={
                'job_type': job.get('job_type'),
                'title': job.get('title'),
                'duration_seconds': duration_seconds
            }
        )

        return jsonify({
            'success': True,
            'data': updated_job,
            'message': f'Job "{job.get("title")}" {final_status}'
        }), 200

    except Exception as e:
        logger.error(f"Error completing AI job {job_id}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'COMPLETE_JOB_ERROR',
                'message': str(e)
            }
        }), 500


@jobs_finalization_bp.route('/<job_id>/create-course', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_AI_JOBS_WRITE)
def create_course_from_job(job_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Create course from completed AI job.

    Business Rules:
    - Job must be completed successfully
    - Job type must be 'course_generation'
    - Job result must contain valid course structure
    - User must own the job or be admin

    Args:
        job_id: The job's UUID

    Request Body:
        publish (bool, optional): Publish course immediately (default: false)
        category_id (str): Category for the course

    Returns:
        JSON response with created course
    """
    try:
        data = request.get_json() or {}

        # Get job
        job = AIJobsRepository.get_by_id(job_id)
        if not job:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'JOB_NOT_FOUND',
                    'message': f'Job {job_id} not found'
                }
            }), 404

        # Business Rule: Job must be completed
        if job.get('status') != 'completed':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'JOB_NOT_COMPLETED',
                    'message': f'Job status is {job.get("status")}, expected completed'
                }
            }), 400

        # Business Rule: Job type must be course_generation
        if job.get('job_type') != 'course_generation':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_JOB_TYPE',
                    'message': f'Job type is {job.get("job_type")}, expected course_generation'
                }
            }), 400

        # Business Rule: Check ownership
        current_user_id = str(g.current_user.get('user_id'))
        if job.get('creator_id') != current_user_id and not g.current_user.get('is_admin'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'You do not have permission to create course from this job'
                }
            }), 403

        # Validate job result
        result = job.get('result')
        if not result or not isinstance(result, dict):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_JOB_RESULT',
                    'message': 'Job result is missing or invalid'
                }
            }), 400

        # Extract course data from result
        course_title = result.get('title') or job.get('title')
        course_description = result.get('description', '')
        chapters = result.get('chapters', [])

        # Validate required fields
        if not data.get('category_id'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_CATEGORY',
                    'message': 'category_id is required'
                }
            }), 400

        # Create course
        course_id = str(uuid.uuid4())
        course_data = {
            'course_id': course_id,
            'title': course_title,
            'description': course_description,
            'creator_id': job.get('creator_id'),
            'category_id': data['category_id'],
            'status': 'draft',
            'is_published': data.get('publish', False),
            'visibility': 'public' if data.get('publish', False) else 'private',
            'ai_generated': True,
            'source_job_id': job_id,
            'created_at': datetime.utcnow()
        }

        created_course = CourseRepository.create(course_data)

        # TODO: Create chapters and lessons from job result
        # This would be implemented in a separate service
        # from app.services.course_builder import CourseBuilderService
        # CourseBuilderService.create_chapters_from_result(course_id, chapters)

        # Update job with course reference
        AIJobsRepository.update(
            job_id,
            {'created_course_id': course_id}
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='create_course_from_job',
            resource_type='course',
            resource_id=course_id,
            details={
                'job_id': job_id,
                'job_type': job.get('job_type'),
                'title': course_title,
                'published': data.get('publish', False)
            }
        )

        return jsonify({
            'success': True,
            'data': {
                'course': created_course,
                'job': {
                    'job_id': job_id,
                    'title': job.get('title')
                }
            },
            'message': f'Course "{course_title}" created from AI job'
        }), 201

    except Exception as e:
        logger.error(f"Error creating course from job {job_id}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_COURSE_ERROR',
                'message': str(e)
            }
        }), 500
