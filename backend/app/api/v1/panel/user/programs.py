"""User Programs API — enrolled programs, enrollment, catalog.

Endpoints:
- GET    /user/programs           — List enrolled programs
- GET    /user/programs/available — Catalog of all programs
- GET    /user/programs/<id>      — Program detail
- POST   /user/programs/<id>/enroll   — Enroll in program
- DELETE /user/programs/<id>/enroll   — Unenroll from program
"""
import logging
from flask import Blueprint, jsonify

from app.api.middleware.auth import token_required, get_current_user

logger = logging.getLogger(__name__)

programs_user_bp = Blueprint(
    'programs_user', __name__, url_prefix='/user/programs',
)


@programs_user_bp.route('', methods=['GET'])
@token_required
def list_enrolled():
    """List programs the current user is enrolled in."""
    from app.application.services.programs.program_service import ProgramService
    user = get_current_user()
    programs = ProgramService.list_user_programs(user['user_id'])
    return jsonify({'success': True, 'programs': programs}), 200


@programs_user_bp.route('/<int:program_id>', methods=['GET'])
@token_required
def get_program_detail(program_id: int):
    """Get program detail with trainer stats."""
    from app.application.services.programs.program_service import ProgramService
    user = get_current_user()
    detail = ProgramService.get_program_detail(program_id, user['user_id'])
    if not detail:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return jsonify({'success': True, **detail}), 200


@programs_user_bp.route('/available', methods=['GET'])
@token_required
def list_available():
    """List all active programs (catalog)."""
    from app.application.services.programs.program_service import ProgramService
    programs = ProgramService.list_available_programs()
    return jsonify({'success': True, 'programs': programs}), 200


@programs_user_bp.route('/<int:program_id>/enroll', methods=['POST'])
@token_required
def enroll(program_id: int):
    """Enroll current user in a program."""
    from app.application.services.programs.program_service import ProgramService
    user = get_current_user()
    ProgramService.enroll(user['user_id'], program_id)
    return jsonify({'success': True}), 200


@programs_user_bp.route('/<int:program_id>/enroll', methods=['DELETE'])
@token_required
def unenroll(program_id: int):
    """Remove current user's enrollment."""
    from app.application.services.programs.program_service import ProgramService
    user = get_current_user()
    ProgramService.unenroll(user['user_id'], program_id)
    return jsonify({'success': True}), 200
