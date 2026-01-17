"""
Course Editor - Theory Sheet Management

Feature-based theory sheet management with permission-aware access.
Admin: Full access to all theory sheets
User: Only access to theory sheets in own courses

Theory sheets for chapters and lessons:
- Chapter theories: One summary per chapter + optional additional sheets
- Lesson theories: Multiple sheets with ordering

Endpoints:
- GET    /api/v1/course-editor/manual/chapters/{chapter_id}/theory - List chapter theories
- POST   /api/v1/course-editor/manual/chapters/{chapter_id}/theory - Create chapter theory
- GET    /api/v1/course-editor/manual/lessons/{lesson_id}/theory - List lesson theories
- POST   /api/v1/course-editor/manual/lessons/{lesson_id}/theory - Create lesson theory
- PATCH  /api/v1/course-editor/manual/theory-sheets/{theory_id} - Update theory sheet
- DELETE /api/v1/course-editor/manual/theory-sheets/{theory_id} - Delete theory sheet
- GET    /api/v1/course-editor/manual/theory-sheets/{theory_id} - Get theory sheet detail
"""

import logging
from pydantic import ValidationError

from flask import jsonify, request

from app.api.v1.course_editor.manual_editor import manual_editor_bp
from app.api.v1.course_editor.shared.permissions import check_course_permission
from app.middleware.auth import get_current_user
from app.models.theory_sheet import (
    TheorySheetCreate,
    TheorySheetResponse,
    TheorySheetUpdate,
)
from app.repositories.courses.chapters import ChapterRepository
from app.repositories.courses.lessons import LessonRepository
from app.repositories.theory_sheet import TheorySheetRepository
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


# ============================================================================
# Chapter Theory Sheets
# ============================================================================

@manual_editor_bp.route('/chapters/<chapter_id>/theory', methods=['GET'])
@check_course_permission('read')
def list_chapter_theories(chapter_id: str):
    """
    List all theory sheets for a chapter.

    Query Parameters:
        - limit: Max results (default 100, max 1000)
        - offset: Skip N records (default 0)

    Returns:
        200: {success: True, data: Theory[], total: int}
        404: Chapter not found

    Example:
        GET /admin/chapters/uuid-1/theory?limit=100&offset=0
        Response:
            {
                "success": true,
                "data": [{...}, {...}],
                "total": 15
            }
    """
    try:
        # Verify chapter exists
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CHAPTER_NOT_FOUND',
                    'message': 'error.chapter_not_found'
                }
            }), 404

        # Get theory sheets
        theories = TheorySheetRepository.list_by_chapter(chapter_id)
        total = TheorySheetRepository.count_by_chapter(chapter_id)

        return jsonify({
            'success': True,
            'data': theories,
            'total': total
        }), 200

    except Exception as e:
        logger.error(f"ERROR in list_chapter_theories: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_load_chapter_theories'
            }
        }), 500


@manual_editor_bp.route('/chapters/<chapter_id>/theory', methods=['POST'])
@check_course_permission('write')
def create_chapter_theory(chapter_id: str):
    """
    Create new theory sheet for chapter.

    Request Body:
        - title: Theory title (required)
        - content: Theory content (required, markdown/rich text)
        - is_summary: Is this the chapter summary? (default: False)

    Returns:
        201: {success: True, data: Theory}
        400: Validation error
        404: Chapter not found

    Example:
        POST /admin/chapters/uuid-1/theory
        Body: {"title": "Summary", "content": "...", "is_summary": true}
        Response: {success: True, data: {...}}
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        # Verify chapter exists
        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CHAPTER_NOT_FOUND',
                    'message': 'error.chapter_not_found'
                }
            }), 404

        # Validate request
        try:
            theory_data = TheorySheetCreate(
                parent_id=chapter_id,
                parent_type='chapter',
                **data
            )
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'error.theory_sheet_validation_failed'
                }
            }), 400

        # Create theory sheet
        theory = TheorySheetRepository.create_chapter_theory(
            chapter_id=chapter_id,
            title=theory_data.title,
            content=theory_data.content,
            is_summary=theory_data.is_summary or False
        )

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.theory_sheets.create',
            resource_type='theory_sheet',
            resource_id=str(theory['theory_id']),
            details={
                'chapter_id': chapter_id,
                'title': theory_data.title,
                'is_summary': theory_data.is_summary,
                'chapter_title': chapter['title']
            },
            severity='info'
        )

        return jsonify({'success': True, 'data': theory}), 201

    except Exception as e:
        logger.error(f"ERROR in create_chapter_theory: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_create_chapter_theory'
            }
        }), 500


# ============================================================================
# Lesson Theory Sheets
# ============================================================================

@manual_editor_bp.route('/lessons/<lesson_id>/theory', methods=['GET'])
@check_course_permission('read')
def list_lesson_theories(lesson_id: str):
    """
    List all theory sheets for a lesson.

    Query Parameters:
        - limit: Max results (default 100, max 1000)
        - offset: Skip N records (default 0)

    Returns:
        200: {success: True, data: Theory[], total: int}
        404: Lesson not found

    Example:
        GET /admin/lessons/uuid-1/theory?limit=100&offset=0
        Response:
            {
                "success": true,
                "data": [{...}, {...}],
                "total": 15
            }
    """
    try:
        # Verify lesson exists
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'LESSON_NOT_FOUND',
                    'message': 'error.lesson_not_found'
                }
            }), 404

        # Get theory sheets
        theories = TheorySheetRepository.list_by_lesson(lesson_id)
        total = TheorySheetRepository.count_by_lesson(lesson_id)

        return jsonify({
            'success': True,
            'data': theories,
            'total': total
        }), 200

    except Exception as e:
        logger.error(f"ERROR in list_lesson_theories: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_load_lesson_theories'
            }
        }), 500


@manual_editor_bp.route('/lessons/<lesson_id>/theory', methods=['POST'])
@check_course_permission('write')
def create_lesson_theory(lesson_id: str):
    """
    Create new theory sheet for lesson.

    Request Body:
        - title: Theory title (required)
        - content: Theory content (required, markdown/rich text)
        - order_index: Display order (optional, default 0)

    Returns:
        201: {success: True, data: Theory}
        400: Validation error
        404: Lesson not found

    Example:
        POST /admin/lessons/uuid-1/theory
        Body: {"title": "Overview", "content": "...", "order_index": 0}
        Response: {success: True, data: {...}}
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        # Verify lesson exists
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'LESSON_NOT_FOUND',
                    'message': 'error.lesson_not_found'
                }
            }), 404

        # Validate request
        try:
            theory_data = TheorySheetCreate(
                parent_id=lesson_id,
                parent_type='lesson',
                **data
            )
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'error.theory_sheet_validation_failed'
                }
            }), 400

        # Create theory sheet
        theory = TheorySheetRepository.create_lesson_theory(
            lesson_id=lesson_id,
            title=theory_data.title,
            content=theory_data.content,
            order_index=theory_data.order_index or 0
        )

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.theory_sheets.create',
            resource_type='theory_sheet',
            resource_id=str(theory['theory_id']),
            details={
                'lesson_id': lesson_id,
                'title': theory_data.title,
                'order_index': theory_data.order_index,
                'lesson_title': lesson['title']
            },
            severity='info'
        )

        return jsonify({'success': True, 'data': theory}), 201

    except Exception as e:
        logger.error(f"ERROR in create_lesson_theory: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_create_lesson_theory'
            }
        }), 500


# ============================================================================
# Theory Sheet Operations
# ============================================================================

@manual_editor_bp.route('/theory-sheets/<theory_id>', methods=['GET'])
@check_course_permission('read')
def get_theory_sheet(theory_id: str):
    """
    Get theory sheet by ID.

    Path Parameters:
        - theory_id: Theory sheet ID

    Returns:
        200: {success: True, data: Theory}
        404: Theory sheet not found

    Example:
        GET /admin/theory-sheets/uuid-1
        Response:
            {
                "success": true,
                "data": {
                    "theory_id": "uuid-1",
                    "title": "Overview",
                    "content": "..."
                }
            }
    """
    try:
        theory = TheorySheetRepository.get_by_id(theory_id)
        if not theory:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'THEORY_SHEET_NOT_FOUND',
                    'message': 'error.theory_sheet_not_found'
                }
            }), 404

        return jsonify({'success': True, 'data': theory}), 200

    except Exception as e:
        logger.error(f"ERROR in get_theory_sheet: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_load_theory_sheet'
            }
        }), 500


@manual_editor_bp.route('/theory-sheets/<theory_id>', methods=['PATCH'])
@check_course_permission('write')
def update_theory_sheet(theory_id: str):
    """
    Update theory sheet.

    Path Parameters:
        - theory_id: Theory sheet ID

    Request Body:
        - title: New title (optional)
        - content: New content (optional)
        - order_index: New display order (optional, lesson theories only)

    Returns:
        200: {success: True, data: Theory}
        400: Validation error
        404: Theory sheet not found

    Example:
        PATCH /admin/theory-sheets/uuid-1
        Body: {"title": "Updated Title", "content": "..."}
        Response: {success: True, data: {...}}
    """
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        # Get theory sheet to determine parent type
        theory = TheorySheetRepository.get_by_id(theory_id)
        if not theory:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'THEORY_SHEET_NOT_FOUND',
                    'message': 'error.theory_sheet_not_found'
                }
            }), 404

        parent_type = theory['parent_type']

        # Validate request
        try:
            update_data = TheorySheetUpdate(**data)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'error.theory_sheet_validation_failed'
                }
            }), 400

        # Update theory sheet
        updated_theory = TheorySheetRepository.update_theory(
            theory_id=theory_id,
            parent_type=parent_type,
            title=update_data.title,
            content=update_data.content,
            order_index=update_data.order_index
        )

        if not updated_theory:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'THEORY_SHEET_NOT_FOUND',
                    'message': 'error.theory_sheet_not_found'
                }
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.theory_sheets.update',
            resource_type='theory_sheet',
            resource_id=theory_id,
            details={
                'parent_id': theory['parent_id'],
                'parent_type': parent_type,
                'title': updated_theory['title']
            },
            severity='info'
        )

        return jsonify({'success': True, 'data': updated_theory}), 200

    except Exception as e:
        logger.error(f"ERROR in update_theory_sheet: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_update_theory_sheet'
            }
        }), 500


@manual_editor_bp.route('/theory-sheets/<theory_id>', methods=['DELETE'])
@check_course_permission('delete')
def delete_theory_sheet(theory_id: str):
    """
    Delete theory sheet.

    Path Parameters:
        - theory_id: Theory sheet ID

    Returns:
        204: No content (success)
        404: Theory sheet not found

    Example:
        DELETE /admin/theory-sheets/uuid-1
        Response: 204 No Content
    """
    try:
        current_user = get_current_user()

        # Get theory sheet to determine parent type and details
        theory = TheorySheetRepository.get_by_id(theory_id)
        if not theory:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'THEORY_SHEET_NOT_FOUND',
                    'message': 'error.theory_sheet_not_found'
                }
            }), 404

        parent_type = theory['parent_type']

        # Delete theory sheet
        deleted = TheorySheetRepository.delete_by_id(theory_id, parent_type)
        if not deleted:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'THEORY_SHEET_NOT_FOUND',
                    'message': 'error.theory_sheet_not_found'
                }
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.theory_sheets.delete',
            resource_type='theory_sheet',
            resource_id=theory_id,
            details={
                'parent_id': theory['parent_id'],
                'parent_type': parent_type,
                'title': theory['title']
            },
            severity='info'
        )

        return '', 204

    except Exception as e:
        logger.error(f"ERROR in delete_theory_sheet: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'error.failed_to_delete_theory_sheet'
            }
        }), 500
