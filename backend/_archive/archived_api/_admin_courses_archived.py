"""
LernsystemX Admin Course Management API

Comprehensive course administration endpoints:
- GET    /api/v1/admin/courses - List all courses with filters
- GET    /api/v1/admin/courses/{course_id} - Get course details
- POST   /api/v1/admin/courses - Create course
- PATCH  /api/v1/admin/courses/{course_id} - Update course metadata
- POST   /api/v1/admin/courses/{course_id}/status - Change course status
- DELETE /api/v1/admin/courses/{course_id} - Archive course

Phase B24-02 - Admin Course Management - ISO 27001:2013 compliant
Based on Dok 24 (Admin-System.md) and Dok 04 (Kurs-Architektur.md)
"""

from flask import request, jsonify, g
from pydantic import ValidationError
from datetime import datetime
from typing import Optional
import logging
import os

# Initialize logger
logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.models.admin_course import (
    AdminCourseListItem,
    AdminCourseDetail,
    AdminCourseCreateRequest,
    AdminCourseUpdateRequest,
    AdminCourseStatusUpdateRequest
)
from app.models.admin_exam import (
    ExamListItem,
    ExamDetailResponse,
    ExamCreateRequest,
    ExamUpdateRequest,
    ExamGenerateRequest,
    ExamQuestionResponse
)
from app.models.course_prompt import (
    CoursePromptResponse,
    CoursePromptCreateRequest,
    CoursePromptUpdateRequest,
    CoursePromptResolveRequest,
    CoursePromptResolveResponse,
    BulkResetRequest,
    PromptScope
)
from app.repositories.course_repository import CourseRepository
from app.repositories.chapter_repository import ChapterRepository
from app.repositories.lesson_repository import LessonRepository
from app.repositories.ai_job_repository import AIJobRepository
from app.repositories.exam_repository import ExamRepository, ExamQuestionRepository
from app.repositories.course_prompt_repository import CoursePromptRepository
from app.repositories.course_file_repository import CourseFileRepository
from app.services.audit_service import AuditService
from app.services.ai_job_service import AIJobService
from app.services.prompt_resolver import PromptResolver
from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions
from app.models.admin_ai import AIJobCreateRequest, AIJobResponse, AIJobFinalizeRequest
from app.ai import run_ai_course_generation


@api_v1.route('/admin/courses', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_courses():
    """
    List all courses with advanced filtering and pagination.

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 50, max: 100)
        status: Filter by status (draft, published, archived, all)
        search: Search in title and description
        creator_id: Filter by creator user ID
        organisation_id: Filter by organisation ID
        category: Filter by category
        level: Filter by level (beginner, intermediate, advanced, expert)
        language: Filter by language (de, en, fr, es, it)
        sort: Sort field (created_at, updated_at, title, enrollment_count)
        order: Sort order (asc, desc)

    Response:
        200: Course list
        {
            "success": true,
            "courses": [
                {
                    "course_id": 1,
                    "title": "Python Grundlagen",
                    "creator_id": 5,
                    "creator_name": "Max Mustermann",
                    "organisation_id": null,
                    "status": "published",
                    "is_public": true,
                    "enrollment_count": 150,
                    "chapter_count": 8,
                    "created_at": "2025-01-15T10:00:00Z",
                    "updated_at": "2025-11-19T10:00:00Z",
                    "published_at": "2025-01-20T10:00:00Z"
                }
            ],
            "pagination": {
                "total": 1234,
                "page": 1,
                "per_page": 50,
                "total_pages": 25
            }
        }

        401: Unauthorized
        403: Forbidden (requires ADMIN_COURSE_READ)
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        status = request.args.get('status', 'all')
        search = request.args.get('search')
        creator_id = request.args.get('creator_id')
        organisation_id = request.args.get('organisation_id')
        category = request.args.get('category')
        category_id = request.args.get('category_id')
        level = request.args.get('level')
        language = request.args.get('language')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        # Get courses from repository
        result = CourseRepository.admin_list_courses(
            page=page,
            per_page=per_page,
            status=status,
            search=search,
            creator_id=int(creator_id) if creator_id else None,
            organisation_id=int(organisation_id) if organisation_id else None,
            category=category,
            category_id=int(category_id) if category_id else None,
            level=level,
            language=language,
            sort=sort,
            order=order
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.courses.list',
            resource_type='course',
            details={
                'filters': {
                    'status': status,
                    'search': search,
                    'creator_id': creator_id,
                    'organisation_id': organisation_id
                }
            }
        )

        return jsonify({
            'success': True,
            'courses': result['courses'],
            'pagination': result['pagination']
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400

    except Exception as e:
        import traceback
        from flask import current_app
        current_app.logger.error(f"ERROR in admin_list_courses: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Failed to list courses',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_course_details(course_id: str):
    """
    Get detailed information about a specific course.

    Path Parameters:
        course_id: Course ID

    Response:
        200: Course details
        {
            "success": true,
            "course": {
                "course_id": 1,
                "title": "Python Grundlagen",
                "description": "Lerne Python von Grund auf",
                "creator_id": 5,
                "creator_name": "Max Mustermann",
                "creator_email": "max@example.com",
                "organisation_id": null,
                "organisation_name": null,
                "category": "programming",
                "level": "beginner",
                "language": "de",
                "price": 49.99,
                "is_public": true,
                "status": "published",
                "thumbnail_url": "https://...",
                "preview_video_url": null,
                "tags": ["python", "beginner", "programming"],
                "chapter_count": 8,
                "enrollment_count": 150,
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-11-19T10:00:00Z",
                "published_at": "2025-01-20T10:00:00Z",
                "archived_at": null
            }
        }

        404: Course not found
        401: Unauthorized
        403: Forbidden
    """
    try:
        # Get comprehensive course details
        course_details = CourseRepository.admin_get_course_by_id(course_id)

        if not course_details:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.courses.view',
            resource_type='course',
            resource_id=str(course_id)
        )

        return jsonify({
            'success': True,
            'course': course_details
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get course details',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_create_course():
    """
    Create a new course as admin.

    Request Body:
        {
            "title": "Python Grundlagen",
            "description": "Lerne Python von Grund auf",
            "creator_id": 5,
            "organisation_id": null,
            "category": "programming",
            "level": "beginner",
            "language": "de",
            "price": 49.99,
            "is_public": false,
            "tags": ["python", "beginner"]
        }

    Response:
        201: Course created
        {
            "success": true,
            "message": "Course created successfully",
            "course": {
                "course_id": 123,
                "title": "Python Grundlagen",
                ...
            }
        }

        400: Validation error
        404: Creator not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Validate request
        course_request = AdminCourseCreateRequest(**data)

        # Create course via repository
        new_course = CourseRepository.admin_create_course(
            course_data=course_request.model_dump(exclude_none=True),
            created_by_admin=current_user['user_id']
        )

        if not new_course:
            return jsonify({
                'success': False,
                'error': 'Failed to create course'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.courses.create',
            resource_type='course',
            resource_id=str(new_course['course_id']),
            details={
                'title': new_course['title'],
                'creator_id': course_request.creator_id,
                'organisation_id': course_request.organisation_id
            },
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': 'Course created successfully',
            'course': new_course
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        import traceback
        from flask import current_app
        current_app.logger.error(f"ERROR in admin_create_course: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to create course',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_course(course_id: str):
    """
    Update course metadata (title, description, category, etc).

    Path Parameters:
        course_id: Course ID

    Request Body (all fields optional):
        {
            "title": "Python Grundlagen - Aktualisiert",
            "description": "Neue Beschreibung",
            "category": "programming",
            "level": "intermediate",
            "language": "en",
            "price": 59.99,
            "is_public": true,
            "thumbnail_url": "https://...",
            "tags": ["python", "intermediate"]
        }

    Response:
        200: Course updated
        {
            "success": true,
            "message": "Course updated successfully",
            "course": {...}
        }

        404: Course not found
        400: Validation error
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Debug logging
        print(f"[DEBUG] admin_update_course: course_id={course_id}, data={data}")

        # Validate request
        update_request = AdminCourseUpdateRequest(**data)

        # Check if course exists
        existing_course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not existing_course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Update course
        updated_course = CourseRepository.admin_update_course(
            course_id=course_id,
            update_data=update_request.model_dump(exclude_none=True),
            updated_by_admin=current_user['user_id']
        )

        if not updated_course:
            return jsonify({
                'success': False,
                'error': 'Failed to update course'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.courses.update',
            resource_type='course',
            resource_id=str(course_id),
            details={
                'updated_fields': list(update_request.model_dump(exclude_none=True).keys()),
                'old_title': existing_course['title'],
                'new_title': updated_course.get('title', existing_course['title'])
            },
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'Course updated successfully',
            'course': updated_course
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to update course',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/status', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_course_status(course_id: str):
    """
    Change course status (publish, unpublish, archive, unarchive).

    Path Parameters:
        course_id: Course ID

    Request Body:
        {
            "action": "publish",  // or "unpublish", "archive", "unarchive"
            "reason": "Quality approved by admin"
        }

    Response:
        200: Status changed
        {
            "success": true,
            "message": "Course published successfully",
            "status": "published"
        }

        404: Course not found
        400: Invalid action or state transition
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Validate request
        status_request = AdminCourseStatusUpdateRequest(**data)

        # Check if course exists
        existing_course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not existing_course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Execute status action
        result = None
        new_status = None

        if status_request.action == 'publish':
            result = CourseRepository.publish(course_id)
            new_status = 'published'
        elif status_request.action == 'unpublish':
            result = CourseRepository.unpublish(course_id)
            new_status = 'draft'
        elif status_request.action == 'archive':
            result = CourseRepository.archive(course_id)
            new_status = 'archived'
        elif status_request.action == 'unarchive':
            result = CourseRepository.unarchive(course_id)
            new_status = 'draft'
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid action',
                'message': f'Action must be one of: publish, unpublish, archive, unarchive'
            }), 400

        if not result:
            return jsonify({
                'success': False,
                'error': 'Failed to change course status',
                'message': 'Status change may have been invalid for current course state'
            }), 400

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action=f'admin.courses.{status_request.action}',
            resource_type='course',
            resource_id=str(course_id),
            details={
                'action': status_request.action,
                'reason': status_request.reason,
                'course_title': existing_course['title']
            },
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': f'Course {status_request.action}ed successfully',
            'status': new_status
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to change course status',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_DELETE)
def admin_delete_course(course_id: str):
    """
    Archive a course (soft delete).

    Note: This is a soft delete. The course will be archived, not permanently deleted.
    To permanently delete, contact database administrator.

    Path Parameters:
        course_id: Course ID

    Request Body:
        {
            "reason": "Copyright violation reported"
        }

    Response:
        200: Course archived
        {
            "success": true,
            "message": "Course archived successfully"
        }

        404: Course not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')

        # Check if course exists
        existing_course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not existing_course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Archive course (soft delete)
        result = CourseRepository.archive(course_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Failed to archive course'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.courses.delete',
            resource_type='course',
            resource_id=str(course_id),
            details={
                'reason': reason,
                'course_title': existing_course['title'],
                'creator_id': existing_course.get('creator_user_id')
            },
            severity='critical'
        )

        return jsonify({
            'success': True,
            'message': 'Course archived successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to archive course',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/permanent', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_DELETE)
def admin_permanent_delete_course(course_id: str):
    """
    Permanently delete a course (hard delete).

    WARNING: This permanently deletes the course and all related data!
    This action cannot be undone.

    Path Parameters:
        course_id: Course ID

    Request Body:
        {
            "confirm": true,
            "reason": "Test course no longer needed"
        }

    Response:
        200: Course permanently deleted
        {
            "success": true,
            "message": "Course permanently deleted"
        }

        400: Missing confirmation
        404: Course not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        # Require explicit confirmation
        if not data.get('confirm', False):
            return jsonify({
                'success': False,
                'error': 'Confirmation required',
                'message': 'You must set "confirm": true to permanently delete a course'
            }), 400

        reason = data.get('reason', 'Permanently deleted by admin')

        # Check if course exists
        existing_course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not existing_course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Store course info for audit log before deletion
        course_title = existing_course['title']
        creator_id = existing_course.get('creator_user_id')

        # Permanently delete course
        result = CourseRepository.delete(course_id)

        if not result:
            return jsonify({
                'success': False,
                'error': 'Failed to permanently delete course'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.courses.permanent_delete',
            resource_type='course',
            resource_id=str(course_id),
            details={
                'reason': reason,
                'course_title': course_title,
                'creator_id': creator_id,
                'permanent': True
            },
            severity='critical'
        )

        return jsonify({
            'success': True,
            'message': 'Course permanently deleted'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to permanently delete course',
            'details': str(e)
        }), 500


# ============================================================================
# ADMIN MODULE MANAGEMENT ENDPOINTS (Phase B24-03)
# ============================================================================

@api_v1.route('/admin/courses/<course_id>/chapters', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_course_chapters(course_id: str):
    """
    List all chapters for a course.

    Path Parameters:
        course_id: Course ID

    Response:
        200: Module list
        {
            "success": true,
            "chapters": [
                {
                    "chapter_id": 1,
                    "course_id": 1,
                    "title": "Einführung",
                    "description": "Grundlagen...",
                    "order_index": 1,
                    "duration_minutes": 45,
                    "has_video": true,
                    "has_quiz": true,
                    "has_exam": false,
                    "lesson_count": 5,
                    "created_at": "2025-01-15T10:00:00Z"
                }
            ]
        }

        404: Course not found
        403: Forbidden
    """
    try:
        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get chapters
        chapters = ChapterRepository.find_by_course(course_id)

        return jsonify({
            'success': True,
            'chapters': chapters
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to load chapters',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/chapters', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_create_chapter(course_id: str):
    """
    Create a new chapter for a course.

    Path Parameters:
        course_id: Course ID

    Request Body:
        {
            "title": "Modul 1: Grundlagen",
            "description": "Einführung in...",
            "duration_minutes": 45,
            "has_video": true,
            "has_quiz": true,
            "has_exam": false
        }

    Response:
        201: Module created
        {
            "success": true,
            "chapter": {
                "chapter_id": 1,
                "course_id": 1,
                "title": "Modul 1: Grundlagen",
                ...
            }
        }

        404: Course not found
        400: Validation error
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Validate required fields
        if not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400

        # Create chapter
        chapter_data = {
            'course_id': course_id,
            'title': data['title'],
            'description': data.get('description'),
            'duration_minutes': data.get('duration_minutes', 0),
            'has_video': data.get('has_video', False),
            'has_quiz': data.get('has_quiz', False),
            'has_exam': data.get('has_exam', False)
        }

        chapter = ChapterRepository.create(chapter_data)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.chapters.create',
            resource_type='chapter',
            resource_id=str(chapter['chapter_id']),
            details={
                'course_id': course_id,
                'chapter_title': chapter['title'],
                'course_title': course['title']
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'chapter': chapter
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to create chapter',
            'details': str(e)
        }), 500


@api_v1.route('/admin/chapters/<chapter_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_chapter(chapter_id: str):
    """
    Update a chapter.

    Path Parameters:
        chapter_id: Module ID

    Request Body:
        {
            "title": "Updated title",
            "description": "Updated description",
            "duration_minutes": 60,
            "has_video": true,
            "has_quiz": false,
            "has_exam": true
        }

    Response:
        200: Module updated
        {
            "success": true,
            "chapter": {...}
        }

        404: Module not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if chapter exists
        existing_chapter = ChapterRepository.find_by_id(chapter_id)
        if not existing_chapter:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        # Update chapter
        updated_chapter = ChapterRepository.update(chapter_id, data)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.chapters.update',
            resource_type='chapter',
            resource_id=str(chapter_id),
            details={
                'chapter_title': updated_chapter['title'],
                'course_id': updated_chapter['course_id'],
                'changes': data
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'chapter': updated_chapter
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to update chapter',
            'details': str(e)
        }), 500


@api_v1.route('/admin/chapters/<chapter_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_DELETE)
def admin_delete_chapter(chapter_id: str):
    """
    Delete a chapter.

    Path Parameters:
        chapter_id: Module ID

    Request Body (optional):
        {
            "reason": "Duplicate content"
        }

    Response:
        200: Module deleted
        {
            "success": true,
            "message": "Module deleted successfully"
        }

        404: Module not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')

        # Check if chapter exists
        existing_chapter = ChapterRepository.find_by_id(chapter_id)
        if not existing_chapter:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        # Delete chapter
        ChapterRepository.delete(chapter_id)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.chapters.delete',
            resource_type='chapter',
            resource_id=str(chapter_id),
            details={
                'reason': reason,
                'chapter_title': existing_chapter['title'],
                'course_id': existing_chapter['course_id']
            },
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': 'Module deleted successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to delete chapter',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/chapters/reorder', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_reorder_chapters(course_id: str):
    """
    Reorder chapters in a course.

    Path Parameters:
        course_id: Course ID

    Request Body:
        {
            "chapter_ids": [3, 1, 2, 4]  // New order (chapter_ids in desired sequence)
        }

    Response:
        200: Modules reordered
        {
            "success": true,
            "message": "Modules reordered successfully"
        }

        404: Course not found
        400: Invalid chapter IDs
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Validate request
        chapter_ids = data.get('chapter_ids', [])
        if not chapter_ids or not isinstance(chapter_ids, list):
            return jsonify({
                'success': False,
                'error': 'chapter_ids must be a non-empty array'
            }), 400

        # Build chapter order list
        chapter_orders = []
        for index, chapter_id in enumerate(chapter_ids, start=1):
            chapter_orders.append({
                'chapter_id': chapter_id,
                'order_index': index
            })

        # Reorder chapters
        ChapterRepository.reorder(course_id, chapter_orders)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.chapters.reorder',
            resource_type='course',
            resource_id=str(course_id),
            details={
                'course_title': course['title'],
                'new_order': chapter_ids
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'message': 'Modules reordered successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to reorder chapters',
            'details': str(e)
        }), 500


# ============================================================================
# ADMIN LESSON MANAGEMENT ENDPOINTS (Phase B24-04)
# ============================================================================

@api_v1.route('/admin/chapters/<chapter_id>/lessons', methods=['GET'])
@require_permission(Permissions.ADMIN_LESSON_READ)
def admin_list_lessons(chapter_id: str):
    """
    List all lessons for a chapter.

    Path Parameters:
        chapter_id: Module ID

    Response:
        200: Lesson list
        {
            "success": true,
            "lessons": [
                {
                    "lesson_id": "uuid",
                    "chapter_id": "uuid",
                    "title": "Einführung in Python",
                    "lesson_type": "video",
                    "duration_minutes": 15,
                    "order_index": 1,
                    "published": true,
                    "free_preview": false,
                    "created_at": "2025-01-15T10:00:00Z",
                    "updated_at": "2025-11-19T10:00:00Z"
                }
            ]
        }

        404: Module not found
        403: Forbidden
    """
    try:
        # Check if chapter exists
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        # Get lessons
        lessons = LessonRepository.find_by_chapter(chapter_id)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.lessons.list',
            resource_type='chapter',
            resource_id=str(chapter_id),
            details={
                'lesson_count': len(lessons),
                'chapter_title': chapter['title']
            }
        )

        return jsonify({
            'success': True,
            'lessons': lessons
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to load lessons',
            'details': str(e)
        }), 500


@api_v1.route('/admin/chapters/<chapter_id>/lessons', methods=['POST'])
@require_permission(Permissions.ADMIN_LESSON_WRITE)
def admin_create_lesson(chapter_id: str):
    """
    Create a new lesson for a chapter.

    Path Parameters:
        chapter_id: Module ID

    Request Body:
        {
            "title": "Einführung in Python",
            "lesson_type": "video",
            "content": {
                "video_url": "https://...",
                "transcript": "..."
            },
            "duration_minutes": 15,
            "published": false,
            "free_preview": false
        }

    Response:
        201: Lesson created
        {
            "success": true,
            "lesson": {
                "lesson_id": "uuid",
                "chapter_id": "uuid",
                "title": "Einführung in Python",
                ...
            }
        }

        404: Module not found
        400: Validation error
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if chapter exists
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        # Validate required fields
        if not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400

        # Validate lesson_type
        valid_types = ['text', 'video', 'quiz', 'interactive', 'assignment', 'discussion']
        lesson_type = data.get('lesson_type', 'text')
        if lesson_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid lesson_type. Must be one of: {", ".join(valid_types)}'
            }), 400

        # Create lesson
        lesson_data = {
            'chapter_id': chapter_id,
            'title': data['title'],
            'lesson_type': lesson_type,
            'content': data.get('content'),
            'duration_minutes': data.get('duration_minutes', 0),
            'published': data.get('published', False),
            'free_preview': data.get('free_preview', False)
        }

        lesson = LessonRepository.create(lesson_data)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.lessons.create',
            resource_type='lesson',
            resource_id=str(lesson['lesson_id']),
            details={
                'chapter_id': chapter_id,
                'lesson_title': lesson['title'],
                'lesson_type': lesson_type,
                'chapter_title': chapter['title']
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'lesson': lesson
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to create lesson',
            'details': str(e)
        }), 500


@api_v1.route('/admin/lessons/<lesson_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_LESSON_WRITE)
def admin_update_lesson(lesson_id: str):
    """
    Update a lesson.

    Path Parameters:
        lesson_id: Lesson UUID

    Request Body (all fields optional):
        {
            "title": "Updated title",
            "lesson_type": "video",
            "content": {...},
            "duration_minutes": 20,
            "published": true,
            "free_preview": false
        }

    Response:
        200: Lesson updated
        {
            "success": true,
            "lesson": {...}
        }

        404: Lesson not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if lesson exists
        existing_lesson = LessonRepository.find_by_id(lesson_id)
        if not existing_lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Validate lesson_type if provided
        if 'lesson_type' in data:
            valid_types = ['text', 'video', 'quiz', 'interactive', 'assignment', 'discussion']
            if data['lesson_type'] not in valid_types:
                return jsonify({
                    'success': False,
                    'error': f'Invalid lesson_type. Must be one of: {", ".join(valid_types)}'
                }), 400

        # Update lesson
        updated_lesson = LessonRepository.update(lesson_id, data)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.lessons.update',
            resource_type='lesson',
            resource_id=str(lesson_id),
            details={
                'lesson_title': updated_lesson['title'],
                'chapter_id': updated_lesson['chapter_id'],
                'changes': list(data.keys())
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'lesson': updated_lesson
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to update lesson',
            'details': str(e)
        }), 500


@api_v1.route('/admin/lessons/<lesson_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_LESSON_DELETE)
def admin_delete_lesson(lesson_id: str):
    """
    Delete a lesson.

    Path Parameters:
        lesson_id: Lesson UUID

    Request Body (optional):
        {
            "reason": "Outdated content"
        }

    Response:
        200: Lesson deleted
        {
            "success": true,
            "message": "Lesson deleted successfully"
        }

        404: Lesson not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')

        # Check if lesson exists
        existing_lesson = LessonRepository.find_by_id(lesson_id)
        if not existing_lesson:
            return jsonify({
                'success': False,
                'error': 'Lesson not found'
            }), 404

        # Delete lesson
        LessonRepository.delete(lesson_id)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.lessons.delete',
            resource_type='lesson',
            resource_id=str(lesson_id),
            details={
                'reason': reason,
                'lesson_title': existing_lesson['title'],
                'chapter_id': existing_lesson['chapter_id']
            },
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': 'Lesson deleted successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to delete lesson',
            'details': str(e)
        }), 500


@api_v1.route('/admin/chapters/<chapter_id>/lessons/reorder', methods=['POST'])
@require_permission(Permissions.ADMIN_LESSON_WRITE)
def admin_reorder_lessons(chapter_id: str):
    """
    Reorder lessons in a chapter.

    Path Parameters:
        chapter_id: Module ID

    Request Body:
        {
            "lesson_ids": ["uuid1", "uuid2", "uuid3"]  // New order
        }

    Response:
        200: Lessons reordered
        {
            "success": true,
            "message": "Lessons reordered successfully"
        }

        404: Module not found
        400: Invalid lesson IDs
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if chapter exists
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404

        # Validate request
        lesson_ids = data.get('lesson_ids', [])
        if not lesson_ids or not isinstance(lesson_ids, list):
            return jsonify({
                'success': False,
                'error': 'lesson_ids must be a non-empty array'
            }), 400

        # Build lesson order list
        lesson_orders = []
        for index, lesson_id in enumerate(lesson_ids, start=1):
            lesson_orders.append({
                'lesson_id': lesson_id,
                'order_index': index
            })

        # Reorder lessons
        LessonRepository.reorder(chapter_id, lesson_orders)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.lessons.reorder',
            resource_type='chapter',
            resource_id=str(chapter_id),
            details={
                'chapter_title': chapter['title'],
                'new_order': lesson_ids
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'message': 'Lessons reordered successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to reorder lessons',
            'details': str(e)
        }), 500


# ============================================================================
# ADMIN AI JOB MANAGEMENT ENDPOINTS (Phase B24-05)
# ============================================================================

@api_v1.route('/admin/ai/jobs', methods=['POST'])
@require_permission(Permissions.ADMIN_AI_JOBS_WRITE)
def admin_create_ai_job():
    """
    Create new AI job

    Request Body:
        {
            "type": "course_from_pdf",
            "file_name": "example.pdf",
            "prompt": "Create a Python course",
            "course_id": "uuid" (optional)
        }

    Response:
        201: Job created
        {
            "success": true,
            "job_id": "uuid"
        }
    """
    try:
        import os
        import uuid as uuid_module

        current_user = get_current_user()

        # Handle both FormData and JSON requests
        if request.content_type and 'multipart/form-data' in request.content_type:
            # FormData request (from frontend with file upload)
            job_type = request.form.get('type', 'course_from_pdf')
            prompt = request.form.get('prompt', '')
            prompt_id = request.form.get('prompt_id')
            course_id = request.form.get('course_id')
            model = request.form.get('model')  # Phase C3.4: AI Model Override

            # Handle file upload
            file_name = None
            storage_path = None
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    # Validate file type
                    allowed_extensions = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'}
                    file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                    if file_ext not in allowed_extensions:
                        return jsonify({
                            'success': False,
                            'error': f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'
                        }), 400

                    # Save file temporarily
                    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'ai_jobs')
                    os.makedirs(upload_dir, exist_ok=True)

                    unique_filename = f"{uuid_module.uuid4().hex}_{file.filename}"
                    storage_path = os.path.join(upload_dir, unique_filename)
                    file.save(storage_path)
                    file_name = file.filename
        else:
            # JSON request (legacy support)
            data = request.get_json() or {}
            job_type = data.get('type', 'course_from_pdf')
            prompt = data.get('prompt', '')
            prompt_id = data.get('prompt_id')
            course_id = data.get('course_id')
            file_name = data.get('file_name')
            model = data.get('model')  # Phase C3.4: AI Model Override
            storage_path = None

        # Create job
        job = AIJobService.create_job(
            user_id=current_user['user_id'],
            job_type=job_type,
            input_file=file_name,
            input_prompt=prompt,
            course_id=course_id,
            prompt_id=prompt_id,
            storage_path=storage_path,
            model=model  # Phase C3.4: AI Model Override
        )

        # Start AI generation in background
        import threading
        thread = threading.Thread(target=run_ai_course_generation, args=(job['id'],))
        thread.daemon = True
        thread.start()

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.ai.job.create',
            resource_type='ai_job',
            resource_id=str(job['id']),
            details={
                'type': job_type,
                'file_name': file_name
            },
            severity='info'
        )

        # Return job info in expected format
        job_response = {
            'id': job['id'],
            'status': job.get('status', 'pending'),
            'progress': job.get('progress_percentage', 0),
            'file_name': file_name,
            'output_data': None,
            'error_message': None
        }

        return jsonify({
            'success': True,
            'job': job_response
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to create AI job',
            'details': str(e)
        }), 500


@api_v1.route('/admin/ai/jobs/<job_id>', methods=['GET'])
@limiter.exempt  # Exempt from rate limiting - needed for frequent polling during AI job progress tracking
@require_permission(Permissions.ADMIN_AI_JOBS_READ)
def admin_get_ai_job(job_id: str):
    """
    Get AI job status

    Response:
        200: Job status
        {
            "success": true,
            "job": {
                "id": "uuid",
                "status": "processing",
                "progress": 50,
                "output_data": {...}
            }
        }
    """
    try:
        job = AIJobService.get_job(job_id)

        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404

        return jsonify({
            'success': True,
            'job': job
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get AI job',
            'details': str(e)
        }), 500


@api_v1.route('/admin/ai/jobs/<job_id>/cancel', methods=['POST'])
@require_permission(Permissions.ADMIN_AI_JOBS_EXECUTE)
def admin_cancel_ai_job(job_id: str):
    """
    Cancel AI job

    Response:
        200: Job cancelled
        {
            "success": true,
            "message": "Job cancelled"
        }
    """
    try:
        current_user = get_current_user()

        job = AIJobService.cancel_job(job_id)

        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found or already completed'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.ai.job.cancel',
            resource_type='ai_job',
            resource_id=str(job_id),
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'Job cancelled successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to cancel AI job',
            'details': str(e)
        }), 500


@api_v1.route('/admin/ai/jobs/<job_id>/finalize', methods=['POST'])
@require_permission(Permissions.ADMIN_AI_JOBS_EXECUTE)
def admin_finalize_ai_job(job_id: str):
    """
    Finalize AI job - create actual course/chapters/lessons from AI output

    Request Body:
        {
            "create_course": true,
            "create_chapters": true,
            "create_lessons": true
        }

    Response:
        200: Course created
        {
            "success": true,
            "course_id": "uuid",
            "chapters_created": 3,
            "lessons_created": 15
        }
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        # Validate request
        finalize_request = AIJobFinalizeRequest(**data)

        # Get job
        job = AIJobService.get_job(job_id)

        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404

        if job['status'] != 'completed':
            return jsonify({
                'success': False,
                'error': f'Job must be completed (current status: {job["status"]})'
            }), 400

        if not job.get('output_data'):
            return jsonify({
                'success': False,
                'error': 'No output data available'
            }), 400

        output_data = job['output_data']
        course_data = output_data.get('course', {})
        chapters_data = output_data.get('chapters', [])

        # Create course
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

            # Attach course to job
            AIJobService.attach_course(job_id, course_id)

            chapters_created = 0
            lessons_created = 0

            # Create chapters
            if finalize_request.create_chapters:
                for chapter_data in chapters_data:
                    chapter = ChapterRepository.create({
                        'course_id': course_id,
                        'title': chapter_data.get('title', 'Modul'),
                        'description': chapter_data.get('description', ''),
                        'duration_minutes': chapter_data.get('duration_minutes', 60)
                    })
                    chapters_created += 1

                    # Create lessons
                    if finalize_request.create_lessons and chapter_data.get('lessons'):
                        for lesson_data in chapter_data['lessons']:
                            LessonRepository.create({
                                'chapter_id': chapter['chapter_id'],
                                'title': lesson_data.get('title', 'Lektion'),
                                'lesson_type': lesson_data.get('lesson_type', 'text'),
                                'duration_minutes': lesson_data.get('duration_minutes', 15)
                            })
                            lessons_created += 1

            # Audit log
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
            return jsonify({
                'success': False,
                'error': 'create_course must be true'
            }), 400

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to finalize AI job',
            'details': str(e)
        }), 500


# ============================================================================
# ADMIN EXAM MANAGEMENT ENDPOINTS (Phase C1.3)
# ============================================================================

@api_v1.route('/admin/courses/<course_id>/exams', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_exams(course_id: str):
    """
    List all exams for a course

    Path Parameters:
        course_id: Course UUID

    Response:
        200: Exam list
        {
            "success": true,
            "exams": [
                {
                    "exam_id": "uuid",
                    "course_id": "uuid",
                    "exam_type": "ai_simulation",
                    "title": "IHK FISI AP1 Simulation",
                    "duration_minutes": 90,
                    "passing_score": 50,
                    "question_count": 40,
                    "generated_by_ai": true,
                    "published": false,
                    "created_at": "2025-01-15T10:00:00Z"
                }
            ]
        }

        404: Course not found
        403: Forbidden
    """
    try:
        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get exams (admins see all, including unpublished)
        exams = ExamRepository.find_by_course(course_id, include_unpublished=True)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.exams.list',
            resource_type='course',
            resource_id=str(course_id),
            details={'exam_count': len(exams)}
        )

        return jsonify({
            'success': True,
            'exams': exams
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to load exams',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/exams', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_create_exam(course_id: str):
    """
    Create new exam manually (without AI)

    Path Parameters:
        course_id: Course UUID

    Request Body:
        {
            "title": "Python Basics Test",
            "description": "Test covering chapters 1-3",
            "exam_type": "practice",
            "duration_minutes": 60,
            "passing_score": 70,
            "total_points": 100,
            "published": false
        }

    Response:
        201: Exam created
        {
            "success": true,
            "exam": {...}
        }

        404: Course not found
        400: Validation error
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Validate request
        exam_request = ExamCreateRequest(**data)

        # Create exam
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

        # Audit log
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

        return jsonify({
            'success': True,
            'exam': exam
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to create exam',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/exams/generate', methods=['POST'])
@require_permission(Permissions.ADMIN_AI_JOBS_WRITE)
def admin_generate_exam(course_id: str):
    """
    Generate exam using AI (Phase C1.3 - KI-Prüfungs-Generator)

    Path Parameters:
        course_id: Course UUID

    Request Body:
        {
            "title": "IHK FISI AP1 Simulation",
            "description": "Simulierte Abschlussprüfung",
            "exam_standard": "IHK_FISI_AP1",
            "difficulty": "intermediate",
            "duration_minutes": 90,
            "passing_score": 50,
            "total_points": 100,
            "question_distribution": {
                "mcq": 25,
                "fill_blanks": 10,
                "short_answer": 3,
                "case_study": 2
            },
            "topic_coverage": {
                "netzwerke": 40,
                "hardware": 20,
                "software": 20,
                "security": 20
            },
            "source_chapter_ids": ["uuid1", "uuid2", "uuid3"]
        }

    Response:
        201: AI job created
        {
            "success": true,
            "message": "Exam generation started",
            "job_id": "uuid",
            "exam_id": "uuid"
        }

        404: Course not found
        400: Validation error
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Validate request
        generate_request = ExamGenerateRequest(**data)

        # Create placeholder exam first
        exam_data = {
            'course_id': course_id,
            'exam_type': 'ai_simulation',  # AI-generated exams are simulations
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
            'ai_model': 'gpt-4-turbo'  # Default model for exam generation
        }

        exam = ExamRepository.create_exam(exam_data)

        # Create AI job for exam generation
        job = AIJobService.create_job(
            user_id=current_user['user_id'],
            job_type='exam_generation',
            input_file=None,
            input_prompt=f"Generate {generate_request.exam_standard.value} exam with {sum(generate_request.question_distribution.values())} questions",
            course_id=course_id
        )

        # Link exam to job
        AIJobRepository.update(job['id'], {'exam_id': exam['exam_id']})

        # Resolve prompt for exam generation (Phase C1.4 - Course-specific prompts)
        try:
            resolved_prompt = PromptResolver.resolve(
                course_id=course_id,
                scope='exam_generation',
                language=course.get('language', 'de')
            )

            # Build context for prompt rendering
            context = {
                'course_title': course['title'],
                'exam_title': generate_request.title,
                'exam_standard': generate_request.exam_standard.value,
                'difficulty': generate_request.difficulty or 'intermediate',
                'question_count': sum(generate_request.question_distribution.values()),
                'duration_minutes': generate_request.duration_minutes,
                'passing_score': generate_request.passing_score
            }

            # Render prompt with context
            rendered_messages = PromptResolver.resolve_and_render(
                course_id=course_id,
                scope='exam_generation',
                context=context,
                language=course.get('language', 'de')
            )

            # Update AI job with resolved prompt info
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
            # Fallback to basic prompt if resolution fails
            import traceback
            traceback.print_exc()
            logger.warning(
                f"Prompt resolution failed for course {course_id}, using fallback: {prompt_error}"
            )

        # Start AI generation in background
        # TODO (Future Enhancement): Implement Celery worker for async AI exam generation
        #       Current: Job is marked as 'queued' but requires manual completion
        #       Target: Auto-process queued jobs via background worker
        #       Tracked in: Phase C2 (AI Generation Workers)
        AIJobService.update_job_status(job['id'], 'queued', progress=0)

        # Audit log
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
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to generate exam',
            'details': str(e)
        }), 500


@api_v1.route('/admin/exams/<exam_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_exam(exam_id: str):
    """
    Get exam details with questions

    Path Parameters:
        exam_id: Exam UUID

    Response:
        200: Exam details
        {
            "success": true,
            "exam": {
                "exam_id": "uuid",
                "course_id": "uuid",
                "exam_type": "ai_simulation",
                "title": "IHK FISI AP1 Simulation",
                "duration_minutes": 90,
                "passing_score": 50,
                "total_points": 100,
                "settings": {...},
                "questions": [...]
            }
        }

        404: Exam not found
        403: Forbidden
    """
    try:
        # Get exam
        exam = ExamRepository.find_by_id(exam_id)

        if not exam:
            return jsonify({
                'success': False,
                'error': 'Exam not found'
            }), 404

        # Get questions
        questions = ExamQuestionRepository.find_by_exam(exam_id)
        exam['questions'] = questions

        return jsonify({
            'success': True,
            'exam': exam
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get exam',
            'details': str(e)
        }), 500


@api_v1.route('/admin/exams/<exam_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_exam(exam_id: str):
    """
    Update exam metadata

    Path Parameters:
        exam_id: Exam UUID

    Request Body (all fields optional):
        {
            "title": "Updated title",
            "description": "Updated description",
            "duration_minutes": 120,
            "passing_score": 60,
            "published": true
        }

    Response:
        200: Exam updated
        {
            "success": true,
            "exam": {...}
        }

        404: Exam not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        # Check if exam exists
        existing_exam = ExamRepository.find_by_id(exam_id)
        if not existing_exam:
            return jsonify({
                'success': False,
                'error': 'Exam not found'
            }), 404

        # Validate request
        update_request = ExamUpdateRequest(**data)

        # Update exam
        updated_exam = ExamRepository.update_exam(
            exam_id,
            update_request.model_dump(exclude_none=True)
        )

        # Audit log
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

        return jsonify({
            'success': True,
            'exam': updated_exam
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to update exam',
            'details': str(e)
        }), 500


@api_v1.route('/admin/exams/<exam_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_DELETE)
def admin_delete_exam(exam_id: str):
    """
    Delete exam and all questions

    Path Parameters:
        exam_id: Exam UUID

    Request Body (optional):
        {
            "reason": "Outdated content"
        }

    Response:
        200: Exam deleted
        {
            "success": true,
            "message": "Exam deleted successfully"
        }

        404: Exam not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')

        # Check if exam exists
        existing_exam = ExamRepository.find_by_id(exam_id)
        if not existing_exam:
            return jsonify({
                'success': False,
                'error': 'Exam not found'
            }), 404

        # Delete exam (cascade to questions)
        ExamRepository.delete_exam(exam_id)

        # Audit log
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

        return jsonify({
            'success': True,
            'message': 'Exam deleted successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to delete exam',
            'details': str(e)
        }), 500


# ============================================================================
# COURSE PROMPTS API (Phase C1.4)
# ============================================================================

@api_v1.route('/admin/courses/<course_id>/prompts', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_course_prompts(course_id: str):
    """
    List all custom prompts for a specific course.

    Path Parameters:
        course_id: Course UUID

    Query Parameters:
        include_inactive: Include inactive prompts (default: false)

    Response:
        200: List of course prompts
        {
            "success": true,
            "prompts": [
                {
                    "course_prompt_id": "uuid",
                    "scope": "chapter_generation",
                    "language": "de",
                    "prompt_system": "...",
                    "prompt_user_template": "...",
                    "metadata": {},
                    "is_active": true,
                    "created_at": "...",
                    "updated_at": "..."
                }
            ]
        }

        404: Course not found
        403: Forbidden
    """
    try:
        # Check if course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get query parameters
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

        # Fetch prompts
        prompts = CoursePromptRepository.find_by_course(
            course_id=course_id,
            include_inactive=include_inactive
        )

        # Convert to response models
        prompt_responses = [
            CoursePromptResponse(**prompt).model_dump(mode='json')
            for prompt in prompts
        ]

        return jsonify({
            'success': True,
            'prompts': prompt_responses
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to list course prompts',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/prompts/<scope>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_course_prompt(course_id: str, scope: str):
    """
    Get a specific prompt for a course and scope.

    Path Parameters:
        course_id: Course UUID
        scope: Prompt scope (chapter_generation, exam_generation, etc.)

    Query Parameters:
        language: Optional language code (default: null)

    Response:
        200: Course prompt data
        {
            "success": true,
            "prompt": {
                "course_prompt_id": "uuid",
                "scope": "chapter_generation",
                "language": "de",
                "prompt_system": "...",
                "prompt_user_template": "...",
                "metadata": {},
                "is_active": true,
                "created_at": "...",
                "updated_at": "..."
            }
        }

        404: Prompt not found (returns global/fallback instead)
        403: Forbidden
    """
    try:
        # Check if course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get query parameters
        language = request.args.get('language', None)

        # Try to find course-specific prompt
        course_prompt = CoursePromptRepository.find_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=language
        )

        if course_prompt:
            # Return course-specific prompt
            prompt_response = CoursePromptResponse(**course_prompt).model_dump(mode='json')
            return jsonify({
                'success': True,
                'prompt': prompt_response,
                'source': 'course_specific'
            }), 200
        else:
            # Return resolved prompt (global or fallback)
            resolved = PromptResolver.resolve(
                course_id=course_id,
                scope=scope,
                language=language
            )
            return jsonify({
                'success': True,
                'prompt': None,  # No course-specific prompt
                'resolved': resolved,
                'source': resolved['source']
            }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get course prompt',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/prompts/<scope>', methods=['PUT'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_upsert_course_prompt(course_id: str, scope: str):
    """
    Create or update a course-specific prompt (UPSERT).

    Path Parameters:
        course_id: Course UUID
        scope: Prompt scope

    Request Body:
        {
            "language": "de",  // optional
            "prompt_system": "Du bist ein Experte...",
            "prompt_user_template": "Erstelle ein Modul über {{topic}}",
            "metadata": {"temperature": 0.7},
            "is_active": true
        }

    Response:
        200: Prompt created/updated
        {
            "success": true,
            "prompt": {...},
            "created": false  // true if new, false if updated
        }

        400: Invalid request
        404: Course not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()

        # Check if course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Parse request body
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        # Validate with Pydantic
        try:
            update_request = CoursePromptUpdateRequest(**data)
        except ValidationError as ve:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': ve.errors()
            }), 400

        # Check if prompt exists
        existing_prompt = CoursePromptRepository.find_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=data.get('language')
        )

        # Upsert prompt
        prompt = CoursePromptRepository.upsert(
            course_id=course_id,
            scope=scope,
            language=data.get('language'),
            prompt_system=data.get('prompt_system'),
            prompt_user_template=data.get('prompt_user_template'),
            metadata=data.get('metadata', {}),
            is_active=data.get('is_active', True),
            created_by=current_user['user_id']
        )

        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Failed to create/update prompt'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_prompts.upsert',
            resource_type='course_prompt',
            resource_id=prompt['course_prompt_id'],
            details={
                'course_id': course_id,
                'scope': scope,
                'language': data.get('language'),
                'created': existing_prompt is None
            },
            severity='medium'
        )

        # Convert to response model
        prompt_response = CoursePromptResponse(**prompt).model_dump(mode='json')

        return jsonify({
            'success': True,
            'prompt': prompt_response,
            'created': existing_prompt is None
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to upsert course prompt',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/prompts/<scope>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_delete_course_prompt(course_id: str, scope: str):
    """
    Delete a course-specific prompt (reset to global default).

    Path Parameters:
        course_id: Course UUID
        scope: Prompt scope

    Query Parameters:
        language: Optional language code

    Response:
        200: Prompt deleted (reset to default)
        {
            "success": true,
            "message": "Prompt reset to global default"
        }

        404: Prompt not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()

        # Get query parameters
        language = request.args.get('language', None)

        # Check if prompt exists
        existing_prompt = CoursePromptRepository.find_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=language
        )

        if not existing_prompt:
            return jsonify({
                'success': False,
                'error': 'Course prompt not found (already using global default)'
            }), 404

        # Delete prompt
        deleted = CoursePromptRepository.delete_by_course_and_scope(
            course_id=course_id,
            scope=scope,
            language=language
        )

        if not deleted:
            return jsonify({
                'success': False,
                'error': 'Failed to delete prompt'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_prompts.delete',
            resource_type='course_prompt',
            resource_id=existing_prompt['course_prompt_id'],
            details={
                'course_id': course_id,
                'scope': scope,
                'language': language
            },
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'Prompt reset to global default'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to delete course prompt',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/prompts/reset', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_bulk_reset_course_prompts(course_id: str):
    """
    Bulk reset course prompts to global defaults.

    Path Parameters:
        course_id: Course UUID

    Request Body:
        {
            "scopes": ["chapter_generation", "exam_generation"],  // optional (all if null)
            "confirm": true  // required
        }

    Response:
        200: Prompts reset
        {
            "success": true,
            "message": "2 prompts reset to global defaults"
        }

        400: Invalid request
        404: Course not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()

        # Check if course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Parse request body
        data = request.get_json() or {}

        # Validate with Pydantic
        try:
            reset_request = BulkResetRequest(**data)
        except ValidationError as ve:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': ve.errors()
            }), 400

        # Bulk reset
        deleted_count = CoursePromptRepository.bulk_reset_by_course(
            course_id=course_id,
            scopes=reset_request.scopes
        )

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_prompts.bulk_reset',
            resource_type='course',
            resource_id=course_id,
            details={
                'scopes': reset_request.scopes,
                'deleted_count': deleted_count
            },
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': f'{deleted_count} prompt(s) reset to global defaults'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to reset course prompts',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/prompts/resolve', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_resolve_course_prompt(course_id: str):
    """
    Resolve a prompt for a specific course and scope (for testing/preview).

    This endpoint uses the PromptResolver service to show which prompt
    would be used for a specific operation.

    Path Parameters:
        course_id: Course UUID

    Request Body:
        {
            "scope": "chapter_generation",
            "language": "de"  // optional
        }

    Response:
        200: Resolved prompt
        {
            "success": true,
            "resolved": {
                "source": "course_specific" | "global" | "hardcoded_fallback",
                "scope": "chapter_generation",
                "language": "de",
                "prompt_system": "...",
                "prompt_user_template": "...",
                "metadata": {}
            }
        }

        400: Invalid request
        404: Course not found
        403: Forbidden
    """
    try:
        # Check if course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Parse request body
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        # Validate with Pydantic
        try:
            resolve_request = CoursePromptResolveRequest(
                course_id=course_id,
                **data
            )
        except ValidationError as ve:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': ve.errors()
            }), 400

        # Resolve prompt
        resolved = PromptResolver.resolve(
            course_id=course_id,
            scope=resolve_request.scope.value,
            language=resolve_request.language
        )

        # Convert to response model
        resolve_response = CoursePromptResolveResponse(**resolved).model_dump(mode='json')

        return jsonify({
            'success': True,
            'resolved': resolve_response
        }), 200

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to resolve course prompt',
            'details': str(e)
        }), 500


# ============================================================================
# COURSE FILES MANAGEMENT API (Phase C2.x)
# ============================================================================

@api_v1.route('/admin/courses/<course_id>/files', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_list_course_files(course_id: str):
    """
    List all files for a course.

    Path Parameters:
        course_id: Course UUID

    Query Parameters:
        category: Filter by category (script, material, exercise, solution, reference, template, other)
        limit: Max number of files (default: 100)
        offset: Offset for pagination (default: 0)

    Response:
        200: File list
        {
            "success": true,
            "files": [...],
            "total": 5,
            "categories_summary": [{"category": "script", "count": 1, "total_size": 1024000}]
        }

        404: Course not found
        403: Forbidden
    """
    try:
        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Get query parameters
        category = request.args.get('category', None)
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))

        # Get files
        files = CourseFileRepository.find_by_course(
            course_id=course_id,
            category=category,
            limit=limit,
            offset=offset
        )

        # Get total count
        total = CourseFileRepository.count_by_course(course_id, category)

        # Get categories summary
        categories_summary = CourseFileRepository.get_categories_summary(course_id)

        return jsonify({
            'success': True,
            'files': files,
            'total': total,
            'categories_summary': categories_summary
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to list course files',
            'details': str(e)
        }), 500


@api_v1.route('/admin/course-files/<file_id>/serve', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_serve_course_file(file_id: str):
    """
    Serve a course file for preview/download.

    Path Parameters:
        file_id: Course File UUID

    Response:
        200: File content
        404: File not found
    """
    try:
        from flask import send_file

        # Get file record
        file_record = CourseFileRepository.find_by_id(file_id)
        if not file_record:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        storage_path = file_record.get('storage_path')
        if not storage_path or not os.path.exists(storage_path):
            return jsonify({
                'success': False,
                'error': 'File not found on disk'
            }), 404

        mime_type = file_record.get('mime_type', 'application/octet-stream')
        filename = file_record.get('display_name') or file_record.get('file_name') or 'file'

        return send_file(
            storage_path,
            mimetype=mime_type,
            as_attachment=False,
            download_name=filename
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to serve file',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/files', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_upload_course_file(course_id: str):
    """
    Upload a file to a course.

    Path Parameters:
        course_id: Course UUID

    Request Body (multipart/form-data):
        file: File to upload
        display_name: Optional display name
        description: Optional description
        file_category: Category (script, material, exercise, solution, reference, template, other)
        is_public: Whether file is publicly accessible (default: false)

    Response:
        201: File uploaded
        {
            "success": true,
            "file": {...}
        }

        400: Invalid file or request
        404: Course not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()

        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Validate file type
        allowed_extensions = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'zip'}
        file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'
            }), 400

        # Determine file type category
        ext_to_type = {
            'pdf': 'pdf',
            'doc': 'docx', 'docx': 'docx',
            'ppt': 'pptx', 'pptx': 'pptx',
            'xls': 'xlsx', 'xlsx': 'xlsx',
            'txt': 'txt',
            'png': 'image', 'jpg': 'image', 'jpeg': 'image', 'gif': 'image',
            'mp4': 'video',
            'mp3': 'audio',
            'zip': 'archive'
        }
        file_type = ext_to_type.get(file_ext, 'other')

        # Get form data
        display_name = request.form.get('display_name', file.filename)
        description = request.form.get('description', None)
        file_category = request.form.get('file_category', 'material')
        is_public = request.form.get('is_public', 'false').lower() == 'true'

        # Validate file_category
        valid_categories = {'script', 'material', 'exercise', 'solution', 'reference', 'template', 'other'}
        if file_category not in valid_categories:
            file_category = 'other'

        # Get file size from stream without saving yet
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        # Check for duplicate file (same name + same size for this course)
        existing_file = CourseFileRepository.find_existing_duplicate(
            course_id=course_id,
            original_name=file.filename,
            size_bytes=file_size
        )

        if existing_file:
            # Return the existing file info with already_exists flag
            return jsonify({
                'success': True,
                'file': existing_file,
                'already_exists': True,
                'message': f'Datei "{file.filename}" ist bereits für diesen Kurs vorhanden.'
            }), 200

        # Save file to disk (using uploads directory)
        import os
        import uuid
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'courses', course_id)
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        storage_path = os.path.join(upload_dir, unique_filename)
        file.save(storage_path)

        # Create database entry (file_size already calculated above)
        course_file = CourseFileRepository.create_file(
            course_id=course_id,
            file_name=file.filename,
            file_type=file_type,
            uploaded_by=current_user['user_id'],
            file_size_bytes=file_size,
            mime_type=file.content_type,
            display_name=display_name,
            description=description,
            file_category=file_category,
            storage_path=storage_path,
            is_public=is_public,
            requires_enrollment=not is_public
        )

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_files.upload',
            resource_type='course_file',
            resource_id=course_file['course_file_id'],
            details={
                'course_id': course_id,
                'file_name': file.filename,
                'file_category': file_category,
                'file_size': file_size
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'file': course_file
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to upload file',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/files/<file_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_READ)
def admin_get_course_file(course_id: str, file_id: str):
    """
    Get single course file details.

    Path Parameters:
        course_id: Course UUID
        file_id: Course file UUID

    Response:
        200: File details
        {
            "success": true,
            "file": {...}
        }

        404: File not found
        403: Forbidden
    """
    try:
        # Get file
        course_file = CourseFileRepository.find_by_id(file_id)

        if not course_file:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        # Verify course match
        if str(course_file['course_id']) != str(course_id):
            return jsonify({
                'success': False,
                'error': 'File does not belong to this course'
            }), 404

        return jsonify({
            'success': True,
            'file': course_file
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get file',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/files/<file_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_update_course_file(course_id: str, file_id: str):
    """
    Update course file metadata.

    Path Parameters:
        course_id: Course UUID
        file_id: Course file UUID

    Request Body (all fields optional):
        {
            "display_name": "Updated name",
            "description": "Updated description",
            "file_category": "exercise",
            "is_public": true
        }

    Response:
        200: File updated
        {
            "success": true,
            "file": {...}
        }

        404: File not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        # Get existing file
        existing_file = CourseFileRepository.find_by_id(file_id)
        if not existing_file:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        # Verify course match
        if str(existing_file['course_id']) != str(course_id):
            return jsonify({
                'success': False,
                'error': 'File does not belong to this course'
            }), 404

        # Build update data
        update_data = {}
        if 'display_name' in data:
            update_data['display_name'] = data['display_name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'file_category' in data:
            valid_categories = {'script', 'material', 'exercise', 'solution', 'reference', 'template', 'other'}
            if data['file_category'] in valid_categories:
                update_data['file_category'] = data['file_category']
        if 'is_public' in data:
            update_data['is_public'] = bool(data['is_public'])
            update_data['requires_enrollment'] = not bool(data['is_public'])

        if not update_data:
            return jsonify({
                'success': False,
                'error': 'No valid update fields provided'
            }), 400

        # Update file
        updated_file = CourseFileRepository.update(file_id, update_data)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_files.update',
            resource_type='course_file',
            resource_id=file_id,
            details={
                'course_id': course_id,
                'changes': list(update_data.keys())
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'file': updated_file
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to update file',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/files/<file_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_delete_course_file(course_id: str, file_id: str):
    """
    Delete a course file.

    Path Parameters:
        course_id: Course UUID
        file_id: Course file UUID

    Response:
        200: File deleted
        {
            "success": true,
            "message": "File deleted successfully"
        }

        404: File not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()

        # Get existing file
        existing_file = CourseFileRepository.find_by_id(file_id)
        if not existing_file:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        # Verify course match
        if str(existing_file['course_id']) != str(course_id):
            return jsonify({
                'success': False,
                'error': 'File does not belong to this course'
            }), 404

        # Delete physical file if exists
        if existing_file.get('storage_path'):
            import os
            try:
                if os.path.exists(existing_file['storage_path']):
                    os.remove(existing_file['storage_path'])
            except Exception as file_error:
                logger.warning(f"Could not delete physical file: {file_error}")

        # Delete database entry
        CourseFileRepository.delete(file_id)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_files.delete',
            resource_type='course_file',
            resource_id=file_id,
            details={
                'course_id': course_id,
                'file_name': existing_file['file_name']
            },
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to delete file',
            'details': str(e)
        }), 500


@api_v1.route('/admin/courses/<course_id>/files/reorder', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def admin_reorder_course_files(course_id: str):
    """
    Reorder course files.

    Path Parameters:
        course_id: Course UUID

    Request Body:
        {
            "file_ids": ["uuid1", "uuid2", "uuid3"]
        }

    Response:
        200: Files reordered
        {
            "success": true,
            "message": "Files reordered successfully"
        }

        400: Invalid request
        404: Course not found
        403: Forbidden
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        # Check if course exists
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return jsonify({
                'success': False,
                'error': 'Course not found'
            }), 404

        # Validate request
        file_ids = data.get('file_ids', [])
        if not file_ids or not isinstance(file_ids, list):
            return jsonify({
                'success': False,
                'error': 'file_ids must be a non-empty array'
            }), 400

        # Reorder files
        CourseFileRepository.update_order(course_id, file_ids)

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_files.reorder',
            resource_type='course',
            resource_id=course_id,
            details={
                'new_order': file_ids
            },
            severity='info'
        )

        return jsonify({
            'success': True,
            'message': 'Files reordered successfully'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to reorder files',
            'details': str(e)
        }), 500
