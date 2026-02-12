"""
LernsystemX Panel API - System Features

Configuration endpoints for system features (read + minimal edit).
Panel API - Configuration ONLY, NO execution logic.
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.application.services.panel import PanelRunnerModeService
from app.domain.models.panel.system_features import SystemFeatureUpdate
from app.api.middleware.auth import token_required, permission_required
from app.infrastructure.i18n.error_codes import ErrorCode
from app.api.utils.responses import success_response, error_response

bp = Blueprint('panel_system_features', __name__, url_prefix='/panel/system-features')


@bp.route('', methods=['GET'])
@token_required
@permission_required('panel.system_features.read')
def list_system_features():
    """
    GET /api/v1/panel/system-features

    List all system features.

    Query Parameters:
        category: str - Filter by category
        include_inactive: bool - Include inactive features (default: false)

    Returns:
        200: {data: SystemFeature[], total: int, categories: string[]}
    """
    category = request.args.get('category')
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

    features, total, categories = PanelRunnerModeService.list_system_features(
        category=category,
        include_inactive=include_inactive
    )

    return success_response(
        data=features,
        meta={
            'total': total,
            'categories': categories
        }
    )


@bp.route('/<int:feature_id>', methods=['GET'])
@token_required
@permission_required('panel.system_features.read')
def get_system_feature(feature_id: int):
    """
    GET /api/v1/panel/system-features/{feature_id}

    Get system feature by ID.

    Returns:
        200: SystemFeature
        404: Not found
    """
    feature, error = PanelRunnerModeService.get_system_feature(feature_id)

    if error:
        return error_response(error)

    return success_response(data=feature)


@bp.route('/<int:feature_id>', methods=['PATCH'])
@token_required
@permission_required('panel.system_features.update')
def update_system_feature(feature_id: int):
    """
    PATCH /api/v1/panel/system-features/{feature_id}

    Update system feature (limited fields).

    Allowed fields:
        - active: bool
        - config: object
        - feature_name: str
        - description: str
        - icon: str

    Note: feature_code and category are immutable.

    Returns:
        200: Updated SystemFeature
        404: Not found
    """
    try:
        data = SystemFeatureUpdate(**request.get_json())
    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, details=e.errors())

    feature, error = PanelRunnerModeService.update_system_feature(
        feature_id=feature_id,
        data=data.dict(exclude_unset=True)
    )

    if error:
        return error_response(error)

    return success_response(data=feature)
