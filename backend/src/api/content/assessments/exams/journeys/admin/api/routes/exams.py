"""
Admin Exam Routes (Journey-Based API)

Admin journey for exam management.
ALL data loaded dynamically from database - NO hardcoded values.

Endpoints:
- GET /api/v1/admin/courses/<course_id>/exams - List course exams
- GET /api/v1/admin/chapters/<chapter_id>/exams - List chapter exams
- GET /api/v1/admin/exams/<id> - Get exam details
- POST /api/v1/admin/courses/<course_id>/exams - Create exam
- PUT /api/v1/admin/exams/<id> - Update exam
- PATCH /api/v1/admin/exams/<id>/settings - Update exam settings
- POST /api/v1/admin/exams/<id>/publish - Publish exam
- POST /api/v1/admin/exams/<id>/unpublish - Unpublish exam
- DELETE /api/v1/admin/exams/<id> - Delete exam
- GET /api/v1/admin/exams/types - Get available exam types (from DB)
"""

from flask import Blueprint, request, jsonify
from decimal import Decimal
from src.core.auth.permissions import require_auth, require_role
from src.api.content.assessments.exams.application.services.exam_service import ExamService
from src.core.utils.validators import Validators, ValidationError


# Create blueprint
admin_exams_bp = Blueprint('admin_exams', __name__)


@admin_exams_bp.route('/api/v1/admin/courses/<course_id>/exams', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_course_exams(course_id: str):
    """List exams for a course."""
    try:
        Validators.validate_uuid(course_id)
        published_only = request.args.get('published_only', 'false').lower() == 'true'

        exams = ExamService.list_exams(
            course_id=course_id,
            published_only=published_only
        )

        exams_data = [
            {
                'exam_id': e.exam_id,
                'course_id': e.course_id,
                'chapter_id': e.chapter_id,
                'exam_type': e.exam_type,
                'title': e.title,
                'duration_minutes': e.duration_minutes,
                'passing_score': float(e.passing_score),
                'published': e.published,
                'created_at': e.created_at.isoformat() if e.created_at else None
            }
            for e in exams
        ]

        return jsonify({
            'success': True,
            'data': exams_data,
            'meta': {'course_id': course_id, 'count': len(exams_data)}
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_EXAMS_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/chapters/<chapter_id>/exams', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def list_chapter_exams(chapter_id: str):
    """List exams for a chapter."""
    try:
        Validators.validate_uuid(chapter_id)
        published_only = request.args.get('published_only', 'false').lower() == 'true'

        exams = ExamService.list_exams(
            chapter_id=chapter_id,
            published_only=published_only
        )

        exams_data = [
            {
                'exam_id': e.exam_id,
                'course_id': e.course_id,
                'chapter_id': e.chapter_id,
                'exam_type': e.exam_type,
                'title': e.title,
                'duration_minutes': e.duration_minutes,
                'passing_score': float(e.passing_score),
                'published': e.published,
                'created_at': e.created_at.isoformat() if e.created_at else None
            }
            for e in exams
        ]

        return jsonify({
            'success': True,
            'data': exams_data,
            'meta': {'chapter_id': chapter_id, 'count': len(exams_data)}
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'LIST_EXAMS_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/exams/<exam_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_exam(exam_id: str):
    """Get exam by ID with full details."""
    try:
        Validators.validate_uuid(exam_id)
        exam = ExamService.get_exam_by_id(exam_id)

        if not exam:
            return jsonify({'success': False, 'error': {'code': 'EXAM_NOT_FOUND', 'message': f'Exam {exam_id} not found'}}), 404

        exam_data = {
            'exam_id': exam.exam_id,
            'course_id': exam.course_id,
            'chapter_id': exam.chapter_id,
            'created_by': exam.created_by,
            'exam_type': exam.exam_type,
            'title': exam.title,
            'description': exam.description,
            'instructions': exam.instructions,
            'duration_minutes': exam.duration_minutes,
            'passing_score': float(exam.passing_score),
            'total_points': float(exam.total_points) if exam.total_points else None,
            'randomize_questions': exam.randomize_questions,
            'show_results_immediately': exam.show_results_immediately,
            'allow_review': exam.allow_review,
            'max_attempts': exam.max_attempts,
            'settings': exam.settings,
            'published': exam.published,
            'created_at': exam.created_at.isoformat() if exam.created_at else None,
            'updated_at': exam.updated_at.isoformat() if exam.updated_at else None
        }

        return jsonify({'success': True, 'data': exam_data}), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_EXAM_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/courses/<course_id>/exams', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def create_exam(course_id: str):
    """Create new exam in course."""
    try:
        Validators.validate_uuid(course_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['title', 'exam_type', 'duration_minutes', 'passing_score'])

        user_id = request.user_id
        user_role = request.user_role

        exam = ExamService.create_exam(
            course_id=course_id,
            exam_type=data['exam_type'],
            title=data['title'],
            duration_minutes=data['duration_minutes'],
            passing_score=Decimal(str(data['passing_score'])),
            user_id=user_id,
            user_role=user_role,
            chapter_id=data.get('chapter_id'),
            description=data.get('description'),
            instructions=data.get('instructions'),
            total_points=Decimal(str(data['total_points'])) if data.get('total_points') else None,
            randomize_questions=data.get('randomize_questions', False),
            show_results_immediately=data.get('show_results_immediately', True),
            allow_review=data.get('allow_review', True),
            max_attempts=data.get('max_attempts'),
            settings=data.get('settings', {})
        )

        exam_data = {
            'exam_id': exam.exam_id,
            'course_id': exam.course_id,
            'chapter_id': exam.chapter_id,
            'exam_type': exam.exam_type,
            'title': exam.title,
            'duration_minutes': exam.duration_minutes,
            'passing_score': float(exam.passing_score),
            'published': exam.published,
            'created_at': exam.created_at.isoformat() if exam.created_at else None
        }

        return jsonify({'success': True, 'data': exam_data}), 201

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_DATA', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'CREATE_EXAM_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/exams/<exam_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'creator'])
def update_exam(exam_id: str):
    """Update exam metadata."""
    try:
        Validators.validate_uuid(exam_id)
        data = request.get_json()

        # Convert Decimal fields
        if 'passing_score' in data:
            data['passing_score'] = Decimal(str(data['passing_score']))
        if 'total_points' in data and data['total_points'] is not None:
            data['total_points'] = Decimal(str(data['total_points']))

        user_id = request.user_id
        user_role = request.user_role

        exam = ExamService.update_exam(
            exam_id=exam_id,
            user_id=user_id,
            user_role=user_role,
            updates=data
        )

        exam_data = {
            'exam_id': exam.exam_id,
            'title': exam.title,
            'duration_minutes': exam.duration_minutes,
            'passing_score': float(exam.passing_score),
            'published': exam.published,
            'updated_at': exam.updated_at.isoformat() if exam.updated_at else None
        }

        return jsonify({'success': True, 'data': exam_data}), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'EXAM_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_EXAM_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/exams/<exam_id>/settings', methods=['PATCH'])
@require_auth
@require_role(['admin', 'creator'])
def update_exam_settings(exam_id: str):
    """Update exam settings (JSONB)."""
    try:
        Validators.validate_uuid(exam_id)
        data = request.get_json()
        Validators.validate_json_keys(data, ['settings'])

        user_id = request.user_id
        user_role = request.user_role

        exam = ExamService.update_exam_settings(
            exam_id=exam_id,
            settings=data['settings'],
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'exam_id': exam.exam_id, 'settings': exam.settings},
            'message': 'Exam settings updated successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'EXAM_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UPDATE_SETTINGS_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/exams/<exam_id>/publish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def publish_exam(exam_id: str):
    """Publish exam."""
    try:
        Validators.validate_uuid(exam_id)
        user_id = request.user_id
        user_role = request.user_role

        exam = ExamService.publish_exam(
            exam_id=exam_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'exam_id': exam.exam_id, 'title': exam.title, 'published': exam.published},
            'message': 'Exam published successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'EXAM_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'PUBLISH_EXAM_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/exams/<exam_id>/unpublish', methods=['POST'])
@require_auth
@require_role(['admin', 'creator'])
def unpublish_exam(exam_id: str):
    """Unpublish exam."""
    try:
        Validators.validate_uuid(exam_id)
        user_id = request.user_id
        user_role = request.user_role

        exam = ExamService.unpublish_exam(
            exam_id=exam_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({
            'success': True,
            'data': {'exam_id': exam.exam_id, 'title': exam.title, 'published': exam.published},
            'message': 'Exam unpublished successfully'
        }), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'EXAM_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'UNPUBLISH_EXAM_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/exams/<exam_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_exam(exam_id: str):
    """Delete exam (hard delete - cascade to questions and attempts)."""
    try:
        Validators.validate_uuid(exam_id)
        user_id = request.user_id
        user_role = request.user_role

        ExamService.delete_exam(
            exam_id=exam_id,
            user_id=user_id,
            user_role=user_role
        )

        return jsonify({'success': True, 'message': 'Exam deleted successfully'}), 200

    except PermissionError as e:
        return jsonify({'success': False, 'error': {'code': 'PERMISSION_DENIED', 'message': str(e)}}), 403
    except ValueError as e:
        return jsonify({'success': False, 'error': {'code': 'EXAM_NOT_FOUND', 'message': str(e)}}), 404
    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'INVALID_UUID', 'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'DELETE_EXAM_ERROR', 'message': str(e)}}), 500


@admin_exams_bp.route('/api/v1/admin/exams/types', methods=['GET'])
@require_auth
@require_role(['admin', 'creator', 'moderator'])
def get_exam_types():
    """
    Get available exam types from database.

    Returns valid exam types loaded dynamically from DB constraint.
    NO hardcoded exam type lists.
    """
    try:
        exam_types = ExamService.get_available_exam_types()

        return jsonify({
            'success': True,
            'data': exam_types,
            'meta': {'count': len(exam_types)}
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'GET_EXAM_TYPES_ERROR', 'message': str(e)}}), 500
