"""
Admin AI Job Management API

Endpoints:
- POST /api/v1/admin/ai/jobs - Create AI job
- GET  /api/v1/admin/ai/jobs/{job_id} - Get AI job status
- POST /api/v1/admin/ai/jobs/{job_id}/cancel - Cancel AI job
- POST /api/v1/admin/ai/jobs/{job_id}/finalize - Finalize AI job (create course)
"""

from flask import request, jsonify
from pydantic import ValidationError
import logging
import os
import uuid as uuid_module
import threading

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.repositories.course_repository import CourseRepository
from app.repositories.chapter_repository import ChapterRepository
from app.repositories.lesson_repository import LessonRepository
from app.services.audit_service import AuditService
from app.services.ai_job_service import AIJobService
from app.middleware.auth import get_current_user
from app.security.permissions import require_permission, Permissions
from app.models.admin_ai import AIJobFinalizeRequest
from app.ai import run_ai_course_generation


@api_v1.route('/admin/ai/jobs', methods=['POST'])
@require_permission(Permissions.ADMIN_AI_JOBS_WRITE)
def admin_create_ai_job():
    """Create new AI job."""
    try:
        current_user = get_current_user()

        # Handle both FormData and JSON requests
        if request.content_type and 'multipart/form-data' in request.content_type:
            job_type = request.form.get('type', 'course_from_pdf')
            prompt = request.form.get('prompt', '')
            prompt_id = request.form.get('prompt_id')
            course_id = request.form.get('course_id')
            model = request.form.get('model')

            file_name = None
            storage_path = None
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    allowed_extensions = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'}
                    file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                    if file_ext not in allowed_extensions:
                        return jsonify({
                            'success': False,
                            'error': f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'
                        }), 400

                    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'ai_jobs')
                    os.makedirs(upload_dir, exist_ok=True)

                    unique_filename = f"{uuid_module.uuid4().hex}_{file.filename}"
                    storage_path = os.path.join(upload_dir, unique_filename)
                    file.save(storage_path)
                    file_name = file.filename
        else:
            data = request.get_json() or {}
            job_type = data.get('type', 'course_from_pdf')
            prompt = data.get('prompt', '')
            prompt_id = data.get('prompt_id')
            course_id = data.get('course_id')
            file_name = data.get('file_name')
            model = data.get('model')
            storage_path = None

        job = AIJobService.create_job(
            user_id=current_user['user_id'],
            job_type=job_type,
            input_file=file_name,
            input_prompt=prompt,
            course_id=course_id,
            prompt_id=prompt_id,
            storage_path=storage_path,
            model=model
        )

        # Start AI generation in background
        thread = threading.Thread(target=run_ai_course_generation, args=(job['id'],))
        thread.daemon = True
        thread.start()

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.ai.job.create',
            resource_type='ai_job',
            resource_id=str(job['id']),
            details={'type': job_type, 'file_name': file_name},
            severity='info'
        )

        job_response = {
            'id': job['id'],
            'status': job.get('status', 'pending'),
            'progress': job.get('progress_percentage', 0),
            'file_name': file_name,
            'output_data': None,
            'error_message': None
        }

        return jsonify({'success': True, 'job': job_response}), 201

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"ERROR in admin_create_ai_job: {e}")
        return jsonify({'success': False, 'error': 'Failed to create AI job', 'details': str(e)}), 500


@api_v1.route('/admin/ai/jobs/<job_id>', methods=['GET'])
@limiter.exempt
@require_permission(Permissions.ADMIN_AI_JOBS_READ)
def admin_get_ai_job(job_id: str):
    """Get AI job status."""
    try:
        job = AIJobService.get_job(job_id)

        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        return jsonify({'success': True, 'job': job}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_get_ai_job: {e}")
        return jsonify({'success': False, 'error': 'Failed to get AI job', 'details': str(e)}), 500


@api_v1.route('/admin/ai/jobs/<job_id>/cancel', methods=['POST'])
@require_permission(Permissions.ADMIN_AI_JOBS_EXECUTE)
def admin_cancel_ai_job(job_id: str):
    """Cancel AI job."""
    try:
        current_user = get_current_user()

        job = AIJobService.cancel_job(job_id)

        if not job:
            return jsonify({'success': False, 'error': 'Job not found or already completed'}), 404

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.ai.job.cancel',
            resource_type='ai_job',
            resource_id=str(job_id),
            severity='medium'
        )

        return jsonify({'success': True, 'message': 'Job cancelled successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in admin_cancel_ai_job: {e}")
        return jsonify({'success': False, 'error': 'Failed to cancel AI job', 'details': str(e)}), 500


@api_v1.route('/admin/ai/jobs/<job_id>/finalize', methods=['POST'])
@require_permission(Permissions.ADMIN_AI_JOBS_EXECUTE)
def admin_finalize_ai_job(job_id: str):
    """Finalize AI job - create actual course/chapters/lessons from AI output."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        finalize_request = AIJobFinalizeRequest(**data)

        job = AIJobService.get_job(job_id)

        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        if job['status'] != 'completed':
            return jsonify({
                'success': False,
                'error': f'Job must be completed (current status: {job["status"]})'
            }), 400

        if not job.get('output_data'):
            return jsonify({'success': False, 'error': 'No output data available'}), 400

        output_data = job['output_data']
        course_data = output_data.get('course', {})
        chapters_data = output_data.get('chapters', [])

        if finalize_request.create_course:
            new_course = CourseRepository.admin_create_course(
                course_data={
                    'title': course_data.get('title', 'AI Generated Course'),
                    'description': course_data.get('description', ''),
                    'creator_id': job['user_id'],
                    'category': course_data.get('category', 'other'),
                    'level': course_data.get('level', 'beginner'),
                    'language': course_data.get('language', 'de'),
                    'is_public': False
                },
                created_by_admin=current_user['user_id']
            )

            course_id = new_course['course_id']
            AIJobService.attach_course(job_id, course_id)

            chapters_created = 0
            lessons_created = 0

            if finalize_request.create_chapters:
                for chapter_data in chapters_data:
                    chapter = ChapterRepository.create({
                        'course_id': course_id,
                        'title': chapter_data.get('title', 'Modul'),
                        'description': chapter_data.get('description', ''),
                        'duration_minutes': chapter_data.get('duration_minutes', 60)
                    })
                    chapters_created += 1

                    if finalize_request.create_lessons and chapter_data.get('lessons'):
                        for lesson_data in chapter_data['lessons']:
                            LessonRepository.create({
                                'chapter_id': chapter['chapter_id'],
                                'title': lesson_data.get('title', 'Lektion'),
                                'lesson_type': lesson_data.get('lesson_type', 'text'),
                                'duration_minutes': lesson_data.get('duration_minutes', 15)
                            })
                            lessons_created += 1

            AuditService.log_action(
                user_id=current_user['user_id'],
                action='admin.ai.job.finalize',
                resource_type='ai_job',
                resource_id=str(job_id),
                details={
                    'course_id': course_id,
                    'chapters_created': chapters_created,
                    'lessons_created': lessons_created
                },
                severity='high'
            )

            return jsonify({
                'success': True,
                'course_id': course_id,
                'chapters_created': chapters_created,
                'lessons_created': lessons_created
            }), 200

        else:
            return jsonify({'success': False, 'error': 'create_course must be true'}), 400

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"ERROR in admin_finalize_ai_job: {e}")
        return jsonify({'success': False, 'error': 'Failed to finalize AI job', 'details': str(e)}), 500
