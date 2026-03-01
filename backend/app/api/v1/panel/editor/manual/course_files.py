"""
Course Editor - Course Files Management

Feature-based course files management with permission-aware access.
Admin: Full access to all course files
User: Only access to files in own courses

Endpoints:
- GET    /api/v1/course-editor/manual/courses/{course_id}/files - List files
- GET    /api/v1/course-editor/manual/course-files/{file_id}/serve - Serve file
- POST   /api/v1/course-editor/manual/courses/{course_id}/files - Upload file
- GET    /api/v1/course-editor/manual/courses/{course_id}/files/{file_id} - Get file details
- PATCH  /api/v1/course-editor/manual/courses/{course_id}/files/{file_id} - Update file
- DELETE /api/v1/course-editor/manual/courses/{course_id}/files/{file_id} - Delete file
- POST   /api/v1/course-editor/manual/courses/{course_id}/files/reorder - Reorder files
"""

from flask import request, jsonify, send_file
import logging
import os
import uuid

logger = logging.getLogger(__name__)

from app.api.v1.panel.editor.manual import manual_editor_bp
from app.api.v1.panel.editor.shared.permissions import check_course_permission
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.persistence.repositories.courses.content.files import CourseFileRepository
from app.application.services.system.audit.service import AuditService
from app.api.middleware.auth import get_current_user
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response


@manual_editor_bp.route('/courses/<course_id>/files', methods=['GET'])
@check_course_permission('read')
def list_course_files(course_id: str):
    """List all files for a course."""
    try:
        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        category = request.args.get('category', None)
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))

        files = CourseFileRepository.find_by_course(
            course_id=course_id,
            category=category,
            limit=limit,
            offset=offset
        )

        total = CourseFileRepository.count_by_course(course_id, category)
        categories_summary = CourseFileRepository.get_categories_summary(course_id)

        return jsonify({
            'success': True,
            'files': files,
            'total': total,
            'categories_summary': categories_summary
        }), 200

    except Exception as e:
        logger.error(f"ERROR in list_course_files: {e}")
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': str(e)})


@manual_editor_bp.route('/course-files/<file_id>/serve', methods=['GET'])
@check_course_permission('read')
def serve_course_file(file_id: str):
    """Serve a course file for preview/download."""
    try:
        file_record = CourseFileRepository.find_by_id(file_id)
        if not file_record:
            return error_response(ErrorCode.COURSE_FILE_NOT_FOUND, 404)

        storage_path = file_record.get('storage_path')
        if not storage_path or not os.path.exists(storage_path):
            return error_response(ErrorCode.COURSE_FILE_NOT_FOUND, 404, details={'message': 'File not found on disk'})

        mime_type = file_record.get('mime_type', 'application/octet-stream')
        filename = file_record.get('display_name') or file_record.get('file_name') or 'file'

        return send_file(
            storage_path,
            mimetype=mime_type,
            as_attachment=False,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"ERROR in serve_course_file: {e}")
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': str(e)})


@manual_editor_bp.route('/courses/<course_id>/files', methods=['POST'])
@check_course_permission('write')
def upload_course_file(course_id: str):
    """Upload a file to a course."""
    try:
        current_user = get_current_user()

        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        if 'file' not in request.files:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, details={'field': 'file'})

        file = request.files['file']
        if file.filename == '':
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'field': 'file', 'message': 'No file selected'})

        allowed_extensions = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'zip'}
        file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'field': 'file', 'message': f'File type not allowed. Allowed: {", ".join(allowed_extensions)}'})

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

        display_name = request.form.get('display_name', file.filename)
        description = request.form.get('description', None)
        file_category = request.form.get('file_category', 'material')
        is_public = request.form.get('is_public', 'false').lower() == 'true'

        valid_categories = {'script', 'material', 'exercise', 'solution', 'reference', 'template', 'other'}
        if file_category not in valid_categories:
            file_category = 'other'

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        existing_file = CourseFileRepository.find_existing_duplicate(
            course_id=course_id,
            original_name=file.filename,
            size_bytes=file_size
        )

        if existing_file:
            return jsonify({
                'success': True,
                'file': existing_file,
                'already_exists': True,
                'message': f'Datei "{file.filename}" ist bereits für diesen Kurs vorhanden.'
            }), 200

        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'courses', course_id)
        os.makedirs(upload_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        storage_path = os.path.join(upload_dir, unique_filename)
        file.save(storage_path)

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

        return jsonify({'success': True, 'file': course_file}), 201

    except Exception as e:
        logger.error(f"ERROR in upload_course_file: {e}")
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': str(e)})


@manual_editor_bp.route('/courses/<course_id>/files/<file_id>', methods=['GET'])
@check_course_permission('read')
def get_course_file(course_id: str, file_id: str):
    """Get single course file details."""
    try:
        course_file = CourseFileRepository.find_by_id(file_id)

        if not course_file:
            return error_response(ErrorCode.COURSE_FILE_NOT_FOUND, 404)

        if str(course_file['course_id']) != str(course_id):
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 404, details={'message': 'File does not belong to this course'})

        return jsonify({'success': True, 'file': course_file}), 200

    except Exception as e:
        logger.error(f"ERROR in get_course_file: {e}")
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': str(e)})


@manual_editor_bp.route('/courses/<course_id>/files/<file_id>', methods=['PATCH'])
@check_course_permission('write')
def update_course_file(course_id: str, file_id: str):
    """Update course file metadata."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        existing_file = CourseFileRepository.find_by_id(file_id)
        if not existing_file:
            return error_response(ErrorCode.COURSE_FILE_NOT_FOUND, 404)

        if str(existing_file['course_id']) != str(course_id):
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 404, details={'message': 'File does not belong to this course'})

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
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'message': 'No valid update fields provided'})

        updated_file = CourseFileRepository.update(file_id, update_data)

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

        return jsonify({'success': True, 'file': updated_file}), 200

    except Exception as e:
        logger.error(f"ERROR in update_course_file: {e}")
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': str(e)})


@manual_editor_bp.route('/courses/<course_id>/files/<file_id>', methods=['DELETE'])
@check_course_permission('delete')
def delete_course_file(course_id: str, file_id: str):
    """Delete a course file."""
    try:
        current_user = get_current_user()

        existing_file = CourseFileRepository.find_by_id(file_id)
        if not existing_file:
            return error_response(ErrorCode.COURSE_FILE_NOT_FOUND, 404)

        if str(existing_file['course_id']) != str(course_id):
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 404, details={'message': 'File does not belong to this course'})

        if existing_file.get('storage_path'):
            try:
                if os.path.exists(existing_file['storage_path']):
                    os.remove(existing_file['storage_path'])
            except Exception as file_error:
                logger.warning(f"Could not delete physical file: {file_error}")

        CourseFileRepository.delete(file_id)

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

        return jsonify({'success': True, 'message': 'File deleted successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in delete_course_file: {e}")
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': str(e)})


@manual_editor_bp.route('/courses/<course_id>/files/reorder', methods=['POST'])
@check_course_permission('write')
def reorder_course_files(course_id: str):
    """Reorder course files."""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}

        course = CourseRepository.find_by_id(course_id, use_cache=False)
        if not course:
            return error_response(ErrorCode.COURSE_NOT_FOUND, 404)

        file_ids = data.get('file_ids', [])
        if not file_ids or not isinstance(file_ids, list):
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'field': 'file_ids', 'message': 'file_ids must be a non-empty array'})

        CourseFileRepository.update_order(course_id, file_ids)

        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.course_files.reorder',
            resource_type='course',
            resource_id=course_id,
            details={'new_order': file_ids},
            severity='info'
        )

        return jsonify({'success': True, 'message': 'Files reordered successfully'}), 200

    except Exception as e:
        logger.error(f"ERROR in reorder_course_files: {e}")
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500, details={'error': str(e)})
