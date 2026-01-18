"""
Feature Configuration Admin API - Enable/Disable Operations

Admin endpoints for managing feature activation status:
- Enable/disable features for all users
- Track disable reasons and timestamps
- Invalidate feature cache on status changes

All endpoints require admin authentication.
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any, Tuple
import logging
from datetime import datetime

from app.database import get_db_connection
from app.repositories.feature_configuration import FeatureConfigurationRepository
from app.services.feature_flags.cache import FeatureConfigurationCacheService
from app.infrastructure.utils.exceptions import NotFoundError
from app.middleware.auth import token_required, admin_required

logger = logging.getLogger(__name__)

bp = Blueprint(
    'admin_feature_configuration_part2',
    __name__,
    url_prefix='/admin/feature-configuration'
)


# ============================================================================
# FEATURE ENABLE/DISABLE OPERATIONS
# ============================================================================

@bp.route('/features/<feature_id>/enable', methods=['POST'])
@token_required
@admin_required
def enable_feature(feature_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Enable feature.

    Returns:
        200: Updated feature
        404: Feature not found

    Example:
        POST /api/v1/admin/feature-configuration/features/{feature_id}/enable
    """
    try:
        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.find_by_id(feature_id)

        if not feature:
            raise NotFoundError(f"Feature {feature_id} not found")

        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.update(feature_id, {
                'is_enabled': True,
                'updated_by': g.user_id,
                'updated_at': datetime.utcnow()
            })

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature.feature_code)

        logger.info(
            f"Feature enabled: {feature_id}",
            extra={'user_id': g.user_id, 'feature_id': feature_id}
        )

        return jsonify({
            'success': True,
            'data': feature.to_dict()
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'FEATURE_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error enabling feature {feature_id}: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'ENABLE_FAILED', 'message': 'Failed to enable feature'}
        }), 500


@bp.route('/features/<feature_id>/disable', methods=['POST'])
@token_required
@admin_required
def disable_feature(feature_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Disable feature.

    Request Body (optional):
        - reason: Reason for disabling

    Returns:
        200: Updated feature
        404: Feature not found

    Example:
        POST /api/v1/admin/feature-configuration/features/{feature_id}/disable
        {"reason": "Maintenance in progress"}
    """
    try:
        data = request.get_json() or {}

        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.find_by_id(feature_id)

        if not feature:
            raise NotFoundError(f"Feature {feature_id} not found")

        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.update(feature_id, {
                'is_enabled': False,
                'disabled_reason': data.get('reason'),
                'updated_by': g.user_id,
                'updated_at': datetime.utcnow()
            })

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature.feature_code)

        logger.info(
            f"Feature disabled: {feature_id}",
            extra={'user_id': g.user_id, 'feature_id': feature_id, 'reason': data.get('reason')}
        )

        return jsonify({
            'success': True,
            'data': feature.to_dict()
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': {'code': 'FEATURE_NOT_FOUND', 'message': str(e)}
        }), 404

    except Exception as e:
        logger.error(f"Error disabling feature {feature_id}: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {'code': 'DISABLE_FAILED', 'message': 'Failed to disable feature'}
        }), 500
