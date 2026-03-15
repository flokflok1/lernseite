"""
Archive Folder API Routes — CRUD for folder hierarchy.

DDD Layer: API (Flask routes only, no business logic)
Blueprint: exam_folders_admin at /admin/exam-archive/folders
"""
import logging

from flask import Blueprint, request, jsonify, g
from app.api.middleware.auth import admin_required
from app.application.services.exams.folder_service import FolderService
from app.infrastructure.persistence.repositories.exams.programs import ExamProgramRepository

logger = logging.getLogger(__name__)

folders_bp = Blueprint(
    'exam_folders_admin',
    __name__,
    url_prefix='/admin/exam-archive/folders',
)


@folders_bp.route('/programs', methods=['GET'])
@admin_required
def list_programs():
    """GET — Programs with folder stats."""
    programs = FolderService.list_programs_with_root_folders()
    return jsonify(programs), 200


@folders_bp.route('/tree/<int:program_id>', methods=['GET'])
@admin_required
def get_tree(program_id: int):
    """GET — Full sidebar tree for a program."""
    tree = FolderService.get_sidebar_tree(program_id)
    return jsonify(tree), 200


@folders_bp.route('/contents/<folder_id>', methods=['GET'])
@admin_required
def get_contents(folder_id: str):
    """GET — Folder contents (children + files + breadcrumb)."""
    contents = FolderService.get_folder_contents(folder_id)
    if not contents:
        return jsonify({'error': 'Folder not found'}), 404
    return jsonify(contents), 200


@folders_bp.route('/contents/program/<int:program_id>', methods=['GET'])
@admin_required
def get_program_root(program_id: int):
    """GET — Root-level contents for a program."""
    contents = FolderService.get_program_root_contents(program_id)
    return jsonify(contents), 200


@folders_bp.route('/', methods=['POST'])
@admin_required
def create_folder():
    """POST — Create a new folder."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    program_id = data.get('program_id')
    parent_folder_id = data.get('parent_folder_id')

    if not program_id and not parent_folder_id:
        return jsonify({'error': 'program_id or parent_folder_id required'}), 400

    try:
        user_id = getattr(g, 'user_id', None)
        folder = FolderService.create_folder(
            program_id=program_id,
            name=name,
            parent_folder_id=parent_folder_id,
            icon=data.get('icon'),
            user_id=str(user_id) if user_id else None,
        )
        return jsonify(folder), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@folders_bp.route('/<folder_id>', methods=['PATCH'])
@admin_required
def update_folder(folder_id: str):
    """PATCH — Update folder (name, icon, metadata)."""
    data = request.get_json()
    allowed = {'name', 'icon', 'metadata'}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400

    result = FolderService.update_folder(folder_id, **updates)
    if not result:
        return jsonify({'error': 'Folder not found'}), 404
    return jsonify(result), 200


@folders_bp.route('/<folder_id>/move', methods=['POST'])
@admin_required
def move_folder(folder_id: str):
    """POST — Move folder to new parent."""
    data = request.get_json()
    try:
        result = FolderService.move_folder(folder_id, data.get('new_parent_id'))
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@folders_bp.route('/<folder_id>', methods=['DELETE'])
@admin_required
def delete_folder(folder_id: str):
    """DELETE — Delete folder and all descendants."""
    deleted = FolderService.delete_folder(folder_id)
    if not deleted:
        return jsonify({'error': 'Folder not found'}), 404
    return jsonify({'deleted': True}), 200


@folders_bp.route('/move-file', methods=['POST'])
@admin_required
def move_file():
    """POST — Move exam into folder."""
    data = request.get_json()
    exam_id = data.get('exam_id')
    folder_id = data.get('folder_id')
    if not exam_id:
        return jsonify({'error': 'exam_id required'}), 400
    FolderService.move_file_to_folder(exam_id, folder_id)
    return jsonify({'moved': True}), 200


# ── Program CRUD ─────────────────────────────────────────

@folders_bp.route('/programs', methods=['POST'])
@admin_required
def create_program():
    """POST — Create a new exam program."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    import re
    program_key = re.sub(r'[^a-z0-9_]', '_', name.lower().strip())

    result = ExamProgramRepository.create({
        'program_key': program_key,
        'display_name': {'de': name, 'en': name},
        'program_type': data.get('program_type', 'custom'),
        'provider': data.get('provider'),
        'icon': data.get('icon', '📁'),
        'sort_order': data.get('sort_order', 99),
    })
    if not result:
        return jsonify({'error': 'Failed to create program'}), 500
    return jsonify(result), 201


@folders_bp.route('/programs/<int:program_id>', methods=['PATCH'])
@admin_required
def update_program(program_id: int):
    """PATCH — Update program (display_name, icon, provider)."""
    data = request.get_json()
    result = ExamProgramRepository.update(program_id, data)
    if not result:
        return jsonify({'error': 'Program not found'}), 404
    return jsonify(result), 200


@folders_bp.route('/programs/<int:program_id>', methods=['DELETE'])
@admin_required
def delete_program(program_id: int):
    """DELETE — Delete a program and all its folders."""
    deleted = ExamProgramRepository.delete_by_id(program_id)
    if not deleted:
        return jsonify({'error': 'Program not found'}), 404
    return jsonify({'deleted': True}), 200
