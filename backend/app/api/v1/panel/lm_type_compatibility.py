"""
LernsystemX Panel API - LM Type Mode Compatibility

Configuration endpoints for learning method type to runner mode compatibility.
Panel API - Configuration ONLY, NO execution logic.
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.application.services.panel import PanelRunnerModeService
from app.domain.models.panel.runner_modes import LMTypeModeCompatibilitySet
from app.api.middleware.auth import require_auth, require_permission
from app.infrastructure.i18n.error_codes import ErrorCode
from app.api.utils.responses import success_response, error_response

bp = Blueprint('panel_lm_type_compatibility', __name__, url_prefix='/panel/lm-types')


@bp.route('/<int:method_type>/modes', methods=['GET'])
@require_auth
@require_permission('panel.lm_types.read')
def get_lm_type_modes(method_type: int):
    """
    GET /api/v1/panel/lm-types/{method_type}/modes

    Get runner mode compatibilities for a learning method type.

    Path Parameters:
        method_type: int - Learning method type ID (0-11)

    Returns:
        200: {method_type, modes: ModeCompatibility[]}
        400: Invalid method_type
    """
    result, error = PanelRunnerModeService.get_lm_type_modes(method_type)

    if error:
        return error_response(error)

    return success_response(data=result)


@bp.route('/<int:method_type>/modes', methods=['PUT'])
@require_auth
@require_permission('panel.lm_types.update')
def set_lm_type_modes(method_type: int):
    """
    PUT /api/v1/panel/lm-types/{method_type}/modes

    Set runner mode compatibilities for a learning method type.
    Replaces all existing compatibilities.

    Path Parameters:
        method_type: int - Learning method type ID (0-11)

    Request Body:
        modes: [
            {
                mode_id: int,
                is_default: bool (optional, only one can be true),
                priority: int (optional, for display order)
            }
        ]

    Returns:
        200: {method_type, modes: ModeCompatibility[]}
        400: Validation error (invalid method_type, invalid mode_ids, multiple defaults)
    """
    try:
        data = LMTypeModeCompatibilitySet(**request.get_json())
    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, details=e.errors())

    result, error = PanelRunnerModeService.set_lm_type_modes(
        method_type=method_type,
        modes=[m.dict() for m in data.modes]
    )

    if error:
        return error_response(error)

    return success_response(data=result)
