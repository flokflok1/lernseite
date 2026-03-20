"""Admin Programs API — CRUD for programs and program types.

Endpoints:
- GET    /admin/programs           — List all programs with parts
- POST   /admin/programs           — Create program
- PUT    /admin/programs/<id>      — Update program
- DELETE /admin/programs/<id>      — Soft-delete program
- GET    /admin/program-types      — List types
- POST   /admin/program-types      — Create type
- PUT    /admin/program-types/<key> — Update type
- DELETE /admin/program-types/<key> — Delete type
"""
import logging
from flask import Blueprint, jsonify, request

from app.api.middleware.auth import admin_required

logger = logging.getLogger(__name__)

programs_admin_bp = Blueprint(
    'programs_admin', __name__, url_prefix='/admin/programs',
)

program_types_bp = Blueprint(
    'program_types_admin', __name__, url_prefix='/admin/program-types',
)


# --- Programs ---

@programs_admin_bp.route('', methods=['GET'])
@admin_required
def list_programs():
    """List all programs with their parts."""
    from app.application.services.programs.program_admin_service import ProgramAdminService
    programs = ProgramAdminService.list_programs()
    return jsonify({'success': True, 'programs': programs}), 200


@programs_admin_bp.route('', methods=['POST'])
@admin_required
def create_program():
    """Create a new program."""
    from app.application.services.programs.program_admin_service import ProgramAdminService
    data = request.get_json() or {}
    if not data.get('program_key') or not data.get('display_name'):
        return jsonify({'success': False, 'error': 'program_key and display_name required'}), 400
    program = ProgramAdminService.create_program(data)
    return jsonify({'success': True, 'program': program}), 201


@programs_admin_bp.route('/<int:program_id>', methods=['PUT'])
@admin_required
def update_program(program_id: int):
    """Update an existing program."""
    from app.application.services.programs.program_admin_service import ProgramAdminService
    data = request.get_json() or {}
    program = ProgramAdminService.update_program(program_id, data)
    return jsonify({'success': True, 'program': program}), 200


@programs_admin_bp.route('/<int:program_id>', methods=['DELETE'])
@admin_required
def delete_program(program_id: int):
    """Soft-delete a program."""
    from app.application.services.programs.program_admin_service import ProgramAdminService
    ProgramAdminService.trash_program(program_id)
    return jsonify({'success': True}), 200


# --- Program Types ---

@program_types_bp.route('', methods=['GET'])
@admin_required
def list_types():
    """List all program types."""
    from app.application.services.programs.program_admin_service import ProgramAdminService
    types = ProgramAdminService.list_types()
    return jsonify({'success': True, 'types': types}), 200


@program_types_bp.route('', methods=['POST'])
@admin_required
def create_type():
    """Create a new program type."""
    from app.application.services.programs.program_admin_service import ProgramAdminService
    data = request.get_json() or {}
    if not data.get('type_key') or not data.get('display_name'):
        return jsonify({'success': False, 'error': 'type_key and display_name required'}), 400
    t = ProgramAdminService.create_type(data)
    return jsonify({'success': True, 'type': t}), 201


@program_types_bp.route('/<type_key>', methods=['PUT'])
@admin_required
def update_type(type_key: str):
    """Update a program type."""
    from app.application.services.programs.program_admin_service import ProgramAdminService
    data = request.get_json() or {}
    t = ProgramAdminService.update_type(type_key, data)
    return jsonify({'success': True, 'type': t}), 200


@program_types_bp.route('/<type_key>', methods=['DELETE'])
@admin_required
def delete_type(type_key: str):
    """Delete a program type."""
    from app.application.services.programs.program_admin_service import ProgramAdminService
    ProgramAdminService.delete_type(type_key)
    return jsonify({'success': True}), 200
