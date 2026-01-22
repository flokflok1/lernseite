"""
AI Jobs Management (DDD)

Endpoints for managing AI jobs:
- GET /api/v1/admin/settings/ai/jobs - List all jobs
- GET /api/v1/admin/settings/ai/jobs/<id> - Get job details
- PUT /api/v1/admin/settings/ai/jobs/<id>/cancel - Cancel job
- DELETE /api/v1/admin/settings/ai/jobs/<id> - Delete job

Uses:
- Repository Pattern for persistence
- Publishes AIJobCancelledEvent when job is cancelled
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
from datetime import datetime
import logging
import uuid

from app.api.middleware.auth import token_required
from app.infrastructure.security.permissions import require_permission, Permissions
from app.infrastructure.persistence.repositories.ai.jobs import AIJobsRepository
from app.application.services.audit_service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

# DDD Core Domain
from .core.events import (
    AIJobCancelledEvent,
    EventPublisher,
    EventPriority
)

logger = logging.getLogger(__name__)

jobs_management_bp = Blueprint(
    'ai_jobs_management',
    __name__,
    url_prefix='/admin-panel/settings/ai/jobs'
)


@jobs_management_bp.route('', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_AI_JOBS_READ)
def list_ai_jobs() -> Tuple[Dict[str, Any], int]:
    """
    List all AI jobs with filtering.

    Query Parameters:
        status (str): Filter by status (pending, processing, completed, failed, cancelled)
        job_type (str): Filter by job type
        creator_id (str): Filter by creator
        limit (int): Results per page (default: 50, max: 200)
        offset (int): Offset for pagination (default: 0)

    Returns:
        JSON response with jobs list
    """
    try:
        # Get filters
        filters = {
            'status': request.args.get('status'),
            'job_type': request.args.get('job_type'),
            'creator_id': request.args.get('creator_id')
        }

        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        # Pagination
        limit = min(int(request.args.get('limit', 50)), 200)
        offset = int(request.args.get('offset', 0))

        # Get jobs
        jobs = AIJobsRepository.get_all(
            filters=filters,
            limit=limit,
            offset=offset
        )

        # Get total count
        total_count = AIJobsRepository.count(filters=filters)

        return jsonify({
            'success': True,
            'data': {
                'jobs': jobs,
                'count': len(jobs),
                'total': total_count,
                'limit': limit,
                'offset': offset
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing AI jobs: {e}")
        return error_response(ErrorCode.LIST_PLANS_ERROR, 500, details={'error': str(e)})


@jobs_management_bp.route('/<job_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_AI_JOBS_READ)
def get_ai_job(job_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get AI job details.

    Args:
        job_id: The job's UUID

    Returns:
        JSON response with job details including:
        - Job metadata
        - Configuration
        - Progress information
        - Result (if completed)
    """
    try:
        job = AIJobsRepository.get_by_id(job_id)

        if not job:
            return error_response(ErrorCode.AI_JOB_NOT_FOUND, 404, details={'job_id': job_id})

        # Calculate duration if job is completed
        duration = None
        if job.get('started_at') and job.get('completed_at'):
            delta = job['completed_at'] - job['started_at']
            duration = {
                'seconds': int(delta.total_seconds()),
                'minutes': round(delta.total_seconds() / 60, 2)
            }

        return jsonify({
            'success': True,
            'data': {
                **job,
                'duration': duration
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting AI job {job_id}: {e}")
        return error_response(ErrorCode.AI_JOB_NOT_FOUND, 500, details={'error': str(e)})


@jobs_management_bp.route('/<job_id>/cancel', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_AI_JOBS_WRITE)
def cancel_ai_job(job_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Cancel AI job.

    Business Rules:
    - Only jobs in 'pending' or 'processing' status can be cancelled
    - User must own the job or be admin

    Args:
        job_id: The job's UUID

    Returns:
        JSON response with cancelled job

    DDD: Publishes AIJobCancelledEvent
    """
    try:
        # Get job
        job = AIJobsRepository.get_by_id(job_id)
        if not job:
            return error_response(ErrorCode.AI_JOB_NOT_FOUND, 404, details={'job_id': job_id})

        # Business Rule: Check status
        if job.get('status') not in ['pending', 'processing']:
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400, details={'message': f'Job with status {job.get("status")} cannot be cancelled'})

        # Business Rule: Check ownership
        current_user_id = str(g.current_user.get('user_id'))
        if job.get('creator_id') != current_user_id and not g.current_user.get('is_admin'):
            return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403, details={'message': 'You do not have permission to cancel this job'})

        # Cancel job
        updated_job = AIJobsRepository.update(
            job_id,
            {
                'status': 'cancelled',
                'completed_at': datetime.utcnow(),
                'error_message': 'Cancelled by user'
            }
        )

        # DDD: Publish Domain Event
        event = AIJobCancelledEvent(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=job_id,
            job_id=job_id,
            job_type=job.get('job_type'),
            cancelled_by=current_user_id,
            previous_status=job.get('status'),
            priority=EventPriority.MEDIUM
        )
        EventPublisher.publish(event)

        # TODO: Cancel Celery task if running
        # from app.infrastructure.tasks.ai_jobs import cancel_ai_job_task
        # cancel_ai_job_task.delay(job_id)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='cancel_ai_job',
            resource_type='ai_job',
            resource_id=job_id,
            details={
                'job_type': job.get('job_type'),
                'title': job.get('title'),
                'previous_status': job.get('status')
            }
        )

        return jsonify({
            'success': True,
            'data': updated_job,
            'message': f'Job "{job.get("title")}" cancelled'
        }), 200

    except Exception as e:
        logger.error(f"Error cancelling AI job {job_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})


@jobs_management_bp.route('/<job_id>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_AI_JOBS_WRITE)
def delete_ai_job(job_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Delete AI job.

    Business Rules:
    - Only failed or cancelled jobs can be deleted
    - Completed jobs should not be deleted (audit trail)
    - User must own the job or be admin

    Args:
        job_id: The job's UUID

    Returns:
        JSON response confirming deletion
    """
    try:
        # Get job
        job = AIJobsRepository.get_by_id(job_id)
        if not job:
            return error_response(ErrorCode.AI_JOB_NOT_FOUND, 404, details={'job_id': job_id})

        # Business Rule: Check status
        if job.get('status') not in ['failed', 'cancelled']:
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400, details={'message': f'Job with status {job.get("status")} cannot be deleted. Only failed or cancelled jobs can be deleted.'})

        # Business Rule: Check ownership
        current_user_id = str(g.current_user.get('user_id'))
        if job.get('creator_id') != current_user_id and not g.current_user.get('is_admin'):
            return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403, details={'message': 'You do not have permission to delete this job'})

        # Delete job
        AIJobsRepository.delete(job_id)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='delete_ai_job',
            resource_type='ai_job',
            resource_id=job_id,
            details={
                'job_type': job.get('job_type'),
                'title': job.get('title'),
                'status': job.get('status')
            }
        )

        return jsonify({
            'success': True,
            'message': f'Job "{job.get("title")}" deleted'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting AI job {job_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500, details={'error': str(e)})
