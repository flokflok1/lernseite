"""
LernsystemX Panel API - Runner Modes

Configuration endpoints for runner modes.
Panel API - Configuration ONLY, NO execution logic.
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError

from app.application.services.content.runner.mode_service import PanelRunnerModeService
from app.domain.models.runner.modes import (
    RunnerModeCreate,
    RunnerModeUpdate,
    FeatureMappingSet,
    LMTypeModeCompatibilitySet
)
from app.api.middleware.auth import token_required, permission_required
from app.infrastructure.i18n.error_codes import ErrorCode
from app.api.responses.responses import success_response, error_response

bp = Blueprint('panel_runner_modes', __name__, url_prefix='/panel/runner-modes')


# =============================================================================
# Runner Modes CRUD
# =============================================================================

@bp.route('', methods=['GET'])
@token_required
@permission_required('panel.runner_modes.read')
def list_modes():
    """
    GET /api/v1/panel/runner-modes

    List all runner modes.

    Query Parameters:
        include_inactive: bool - Include inactive modes (default: false)

    Returns:
        200: {data: RunnerMode[], total: int}
    """
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    modes, total = PanelRunnerModeService.list_modes(include_inactive=include_inactive)

    return success_response(
        data=modes,
        meta={'total': total}
    )


@bp.route('/<int:mode_id>', methods=['GET'])
@token_required
@permission_required('panel.runner_modes.read')
def get_mode(mode_id: int):
    """
    GET /api/v1/panel/runner-modes/{mode_id}

    Get runner mode by ID.

    Returns:
        200: RunnerMode
        404: Not found
    """
    mode, error = PanelRunnerModeService.get_mode(mode_id)

    if error:
        return error_response(error)

    return success_response(data=mode)


@bp.route('/code/<string:mode_code>', methods=['GET'])
@token_required
@permission_required('panel.runner_modes.read')
def get_mode_by_code(mode_code: str):
    """
    GET /api/v1/panel/runner-modes/code/{mode_code}

    Get runner mode by code.

    Returns:
        200: RunnerMode
        404: Not found
    """
    mode, error = PanelRunnerModeService.get_mode_by_code(mode_code)

    if error:
        return error_response(error)

    return success_response(data=mode)


@bp.route('', methods=['POST'])
@token_required
@permission_required('panel.runner_modes.create')
def create_mode():
    """
    POST /api/v1/panel/runner-modes

    Create new runner mode.

    Request Body:
        mode_code: str - Unique mode code (lowercase, alphanumeric + underscore)
        name: str - Display name
        description: str - Optional description
        time_limited: bool - Whether mode has time limit
        graded: bool - Whether mode is graded
        allows_hints: bool - Whether hints are allowed
        allows_skip: bool - Whether skipping is allowed
        allows_review: bool - Whether review after completion is allowed
        display_order: int - Display order

    Returns:
        201: Created RunnerMode
        400: Validation error
        409: Mode code already exists
    """
    try:
        data = RunnerModeCreate(**request.get_json())
    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, details=e.errors())

    mode, error = PanelRunnerModeService.create_mode(data.dict())

    if error:
        return error_response(error)

    return success_response(data=mode, status_code=201)


@bp.route('/<int:mode_id>', methods=['PATCH'])
@token_required
@permission_required('panel.runner_modes.update')
def update_mode(mode_id: int):
    """
    PATCH /api/v1/panel/runner-modes/{mode_id}

    Update runner mode.

    Returns:
        200: Updated RunnerMode
        404: Not found
    """
    try:
        data = RunnerModeUpdate(**request.get_json())
    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, details=e.errors())

    mode, error = PanelRunnerModeService.update_mode(mode_id, data.dict(exclude_unset=True))

    if error:
        return error_response(error)

    return success_response(data=mode)


@bp.route('/<int:mode_id>', methods=['DELETE'])
@token_required
@permission_required('panel.runner_modes.delete')
def delete_mode(mode_id: int):
    """
    DELETE /api/v1/panel/runner-modes/{mode_id}

    Soft delete runner mode (sets active = false).

    Returns:
        204: No content
        404: Not found
    """
    success, error = PanelRunnerModeService.delete_mode(mode_id)

    if error:
        return error_response(error)

    return '', 204


# =============================================================================
# Feature Mappings
# =============================================================================

@bp.route('/<int:mode_id>/features', methods=['GET'])
@token_required
@permission_required('panel.runner_modes.read')
def get_mode_features(mode_id: int):
    """
    GET /api/v1/panel/runner-modes/{mode_id}/features

    Get feature mappings for a runner mode.

    Returns:
        200: {mode_id, mode_code, features: FeatureMapping[]}
        404: Mode not found
    """
    result, error = PanelRunnerModeService.get_mode_features(mode_id)

    if error:
        return error_response(error)

    return success_response(data=result)


@bp.route('/<int:mode_id>/features', methods=['PUT'])
@token_required
@permission_required('panel.runner_modes.update')
def set_mode_features(mode_id: int):
    """
    PUT /api/v1/panel/runner-modes/{mode_id}/features

    Set feature mappings for a runner mode.
    Replaces all existing mappings.

    Request Body:
        features: [
            {
                feature_id: int,
                relationship: 'required' | 'optional' | 'excluded',
                config: object (optional)
            }
        ]

    Returns:
        200: {mode_id, mode_code, features: FeatureMapping[]}
        404: Mode not found
        400: Validation error (invalid feature IDs)
    """
    try:
        data = FeatureMappingSet(**request.get_json())
    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, details=e.errors())

    result, error = PanelRunnerModeService.set_mode_features(
        mode_id=mode_id,
        features=[f.dict() for f in data.features]
    )

    if error:
        return error_response(error)

    return success_response(data=result)
