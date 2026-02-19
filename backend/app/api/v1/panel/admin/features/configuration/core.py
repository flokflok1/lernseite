"""
Feature Configuration Admin API - Core CRUD Operations

Admin endpoints for managing feature flags and configurations:
- Feature creation and management
- Role and tier mappings
- Feature activation/deactivation
- Permission overrides

All endpoints require admin authentication.
"""

from flask import Blueprint, jsonify, request, g
from typing import Dict, Any, Tuple, Optional
import logging
from datetime import datetime

from app.infrastructure.persistence.database import get_db_connection
from app.infrastructure.persistence.repositories.features.configuration import FeatureConfigurationRepository
from app.application.services.system.feature_flags.service import FeatureConfigurationService
from app.application.services.system.feature_flags.cache import FeatureConfigurationCacheService
from app.infrastructure.error_handling.exceptions import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
    ConflictError
)
from app.api.middleware.auth import token_required, admin_required

logger = logging.getLogger(__name__)

bp = Blueprint(
    'admin_feature_configuration',
    __name__,
    url_prefix='/admin/feature-configuration'
)


# ============================================================================
# FEATURE CRUD OPERATIONS
# ============================================================================

@bp.route('/features', methods=['GET'])
@token_required
@admin_required
def list_features() -> Tuple[Dict[str, Any], int]:
    """
    List all feature configurations.

    Query Parameters:
        - limit: Max results (default 50, max 500)
        - offset: Skip N results (default 0)
        - enabled: Filter by enabled status (true/false)
        - category: Filter by category

    Returns:
        200: List of features
        401: Unauthorized
        403: Forbidden (not admin)

    Example:
        GET /api/v1/admin/feature-configuration/features?limit=20&offset=0
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))

        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)

            filters = {}

            # Apply optional filters
            if request.args.get('enabled') is not None:
                filters['is_enabled'] = request.args.get('enabled').lower() == 'true'

            if request.args.get('category'):
                filters['category'] = request.args.get('category')

            features = repo.find_all(filters=filters, limit=limit, offset=offset)
            total = repo.count(filters=filters)

        return jsonify({
            'success': True,
            'data': [f.to_dict() for f in features],
            'meta': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200

    except Exception as e:
        logger.error(f"Error listing features: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_FEATURES_FAILED',
                'message': 'Failed to list features'
            }
        }), 500


@bp.route('/features/<feature_id>', methods=['GET'])
@token_required
@admin_required
def get_feature(feature_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get single feature configuration.

    Returns:
        200: Feature data
        404: Feature not found
        401: Unauthorized
        403: Forbidden

    Example:
        GET /api/v1/admin/feature-configuration/features/{feature_id}
    """
    try:
        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.find_by_id(feature_id)

        if not feature:
            raise NotFoundError(f"Feature {feature_id} not found")

        return jsonify({
            'success': True,
            'data': feature.to_dict()
        }), 200

    except NotFoundError as e:
        logger.warning(f"Feature not found: {feature_id}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FEATURE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except Exception as e:
        logger.error(f"Error getting feature {feature_id}: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_FEATURE_FAILED',
                'message': 'Failed to get feature'
            }
        }), 500


@bp.route('/features', methods=['POST'])
@token_required
@admin_required
def create_feature() -> Tuple[Dict[str, Any], int]:
    """
    Create new feature configuration.

    Request Body:
        - feature_name: Feature name (required)
        - feature_code: Unique feature code (required)
        - description: Feature description
        - category: Feature category (required)
        - is_enabled: Enable feature (default false)
        - tier_required: Min subscription tier
        - max_daily_quota: Daily quota limit
        - max_monthly_quota: Monthly quota limit

    Returns:
        201: Created feature
        400: Validation error
        409: Feature already exists

    Example:
        POST /api/v1/admin/feature-configuration/features
        {
            "feature_name": "AI Editor",
            "feature_code": "ai_editor",
            "description": "AI-powered content editing",
            "category": "ai",
            "is_enabled": false,
            "tier_required": "premium"
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required = ['feature_name', 'feature_code', 'category']
        missing = [f for f in required if f not in data]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")

        # Check if feature already exists
        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            existing = repo.find_by_code(data['feature_code'])

        if existing:
            raise ConflictError(f"Feature with code '{data['feature_code']}' already exists")

        # Add metadata
        data['created_by'] = g.user_id
        data['created_at'] = datetime.utcnow()

        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.create(data)

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature.feature_code)

        logger.info(
            f"Feature created: {data['feature_code']}",
            extra={'user_id': g.user_id, 'feature_code': data['feature_code']}
        )

        return jsonify({
            'success': True,
            'data': feature.to_dict()
        }), 201

    except ValidationError as e:
        logger.warning(f"Validation error creating feature: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except ConflictError as e:
        logger.warning(f"Feature conflict: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {
                'code': 'FEATURE_EXISTS',
                'message': str(e)
            }
        }), 409

    except Exception as e:
        logger.error(f"Error creating feature: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_FEATURE_FAILED',
                'message': 'Failed to create feature'
            }
        }), 500


@bp.route('/features/<feature_id>', methods=['PATCH', 'PUT'])
@token_required
@admin_required
def update_feature(feature_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Update feature configuration.

    Request Body:
        - feature_name: Feature name
        - description: Feature description
        - is_enabled: Enable/disable feature
        - tier_required: Min subscription tier
        - max_daily_quota: Daily quota limit
        - max_monthly_quota: Monthly quota limit

    Returns:
        200: Updated feature
        404: Feature not found
        400: Validation error

    Example:
        PATCH /api/v1/admin/feature-configuration/features/{feature_id}
        {
            "is_enabled": true,
            "tier_required": "premium"
        }
    """
    try:
        data = request.get_json()

        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.find_by_id(feature_id)

        if not feature:
            raise NotFoundError(f"Feature {feature_id} not found")

        # Add metadata
        data['updated_by'] = g.user_id
        data['updated_at'] = datetime.utcnow()

        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.update(feature_id, data)

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature.feature_code)

        logger.info(
            f"Feature updated: {feature_id}",
            extra={'user_id': g.user_id, 'feature_id': feature_id}
        )

        return jsonify({
            'success': True,
            'data': feature.to_dict()
        }), 200

    except NotFoundError as e:
        logger.warning(f"Feature not found: {feature_id}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FEATURE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except Exception as e:
        logger.error(f"Error updating feature {feature_id}: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_FEATURE_FAILED',
                'message': 'Failed to update feature'
            }
        }), 500


@bp.route('/features/<feature_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_feature(feature_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Delete feature configuration (soft delete).

    Returns:
        204: No content
        404: Feature not found

    Example:
        DELETE /api/v1/admin/feature-configuration/features/{feature_id}
    """
    try:
        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            feature = repo.find_by_id(feature_id)

        if not feature:
            raise NotFoundError(f"Feature {feature_id} not found")

        with get_db_connection() as conn:
            repo = FeatureConfigurationRepository(conn)
            repo.soft_delete(feature_id)

        # Invalidate cache
        FeatureConfigurationCacheService.invalidate_feature(feature.feature_code)

        logger.info(
            f"Feature deleted: {feature_id}",
            extra={'user_id': g.user_id, 'feature_id': feature_id}
        )

        return '', 204

    except NotFoundError as e:
        logger.warning(f"Feature not found: {feature_id}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FEATURE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except Exception as e:
        logger.error(f"Error deleting feature {feature_id}: {e}", extra={'user_id': g.user_id})
        return jsonify({
            'success': False,
            'error': {
                'code': 'DELETE_FEATURE_FAILED',
                'message': 'Failed to delete feature'
            }
        }), 500
