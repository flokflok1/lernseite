"""
LernsystemX Courses API - Core Read Operations

User-facing course browsing and retrieval.

Read Operations:
- GET /courses - List/search public courses
- GET /courses/:id - Get course details
- GET /courses/:id/chapters - Get course chapters
- GET /courses/:id/chapters/:chapterId - Get chapter details with lessons

All routes: /api/v1/courses/*
ISO 9001:2015 compliant - Course Management Layer
"""

from flask import Blueprint, request, jsonify
import logging

from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.persistence.repositories.courses.content.chapters import ChapterRepository
from app.infrastructure.persistence.repositories.courses.content.lessons import LessonRepository
from app.infrastructure.persistence.repositories.enrollments.core import EnrollmentRepository
from app.api.middleware.auth import get_current_user
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

logger = logging.getLogger(__name__)

core_bp = Blueprint('courses_core', __name__, url_prefix='/courses')

__all__ = ['core_bp']


# =============================================================================
# COURSE CRUD - READ OPERATIONS
# =============================================================================

@core_bp.route('', methods=['GET'])
def list_courses():
    """
    List and search public published courses.

    Query Parameters:
        search (str): Search term for title/description
        category (str): Filter by category
        level (str): Filter by level (beginner, intermediate, advanced, expert)
        language (str): Filter by language (de, en, etc.)
        min_price (float): Minimum price
        max_price (float): Maximum price
        tags (str): Comma-separated tags
        course_type (str): Filter by type (academy, creator)
        include_drafts (bool): Include draft courses (admin only)
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)

    Response:
        200: List of courses with pagination
        500: Server error
    """
    try:
        # Get query parameters
        search_term = request.args.get('search')
        category = request.args.get('category')
        level = request.args.get('level')
        language = request.args.get('language')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        tags_str = request.args.get('tags')
        course_type = request.args.get('course_type')
        include_drafts_param = request.args.get('include_drafts', 'false').lower() == 'true'
        page = max(int(request.args.get('page', 1)), 1)
        per_page = min(int(request.args.get('per_page', 20)), 100)

        # Parse tags
        tags = tags_str.split(',') if tags_str else None

        # Only allow include_drafts for moderator+ (RBAC 2.0: dynamic from DB)
        include_drafts = False
        if include_drafts_param:
            try:
                user = get_current_user()
                from app.application.services.system.auth.permission import PermissionService
                if user and PermissionService.check_threshold(user, 'courses.view_drafts'):
                    include_drafts = True
            except:
                pass

        # Calculate offset
        offset = (page - 1) * per_page

        # Search courses
        result = CourseRepository.search_public_courses(
            search_term=search_term,
            category=category,
            level=level,
            language=language,
            min_price=min_price,
            max_price=max_price,
            tags=tags,
            course_type=course_type,
            include_drafts=include_drafts,
            limit=per_page,
            offset=offset
        )

        total_pages = (result['total'] + per_page - 1) // per_page

        return jsonify({
            'success': True,
            'courses': result['items'],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': result['total'],
                'total_pages': total_pages
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing courses: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@core_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id: str):
    """
    Get course details.

    For public published courses: Anyone can view
    For unpublished courses: Only creator, org members, or admins

    Response:
        200: Course details
        401: Authentication required
        403: Access denied
        404: Course not found
    """
    try:
        course = CourseRepository.find_by_id(course_id)

        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404, details={'message': 'The requested course does not exist'})

        # Check access permissions
        user = get_current_user()

        # Public published courses are accessible to everyone
        if course.get('published'):
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # For non-public/draft courses, check permissions
        if not user:
            return error_response(ErrorCode.AUTH_TOKEN_MISSING, 401, details={'message': 'This course requires authentication to view'})

        # Course creator can always view
        if str(user['user_id']) == str(course.get('creator_user_id')):
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # Organisation members can view org courses
        if course.get('organisation_id') and user.get('organisation_id') == course['organisation_id']:
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # Admins can view any course (RBAC 2.0: dynamic from DB)
        from app.application.services.system.auth.permission import PermissionService
        if PermissionService.check_threshold(user, 'courses.view_any'):
            return jsonify({
                'success': True,
                'course': course
            }), 200

        # Check if user is enrolled
        if EnrollmentRepository.is_user_enrolled(user['user_id'], course_id):
            return jsonify({
                'success': True,
                'course': course
            }), 200

        return error_response(ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS, 403, details={'message': 'You do not have permission to view this course'})

    except Exception as e:
        logger.error(f"Error getting course: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@core_bp.route('/<course_id>/chapters', methods=['GET'])
def get_course_chapters(course_id: str):
    """
    Get all chapters for a course.

    Response:
        200: List of chapters
        404: Course not found
    """
    try:
        course = CourseRepository.find_by_id(course_id)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        chapters = ChapterRepository.find_by_course(course_id)

        return jsonify({
            'success': True,
            'chapters': chapters
        }), 200

    except Exception as e:
        logger.error(f"Error getting course chapters: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})


@core_bp.route('/<course_id>/chapters/<chapter_id>', methods=['GET'])
def get_chapter_detail(course_id: str, chapter_id: str):
    """
    Get chapter details with its lessons.

    Response:
        200: Chapter with lessons
        404: Chapter not found
    """
    try:
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return error_response(ErrorCode.CHAPTER_NOT_FOUND, 404)

        lessons = LessonRepository.find_by_chapter(chapter_id)
        chapter['lessons'] = lessons

        return jsonify({
            'success': True,
            'chapter': chapter
        }), 200

    except Exception as e:
        logger.error(f"Error getting chapter detail: {e}")
        return error_response(ErrorCode.OPERATION_FAILED, 500, details={'details': str(e)})
