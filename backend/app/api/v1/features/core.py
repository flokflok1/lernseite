"""
Feature-Based Authorization API Endpoints

Public endpoints for feature access control:
- GET /features/available - Get features available to current user
- GET /features/check/<feature_code> - Check if user can access a feature
- GET /features/<feature_code>/metadata - Get feature metadata (public)

All endpoints except /metadata require authentication.
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, Tuple
import logging
from pydantic import ValidationError

from app.middleware.auth import token_required, get_current_user
from app.services.system.features.service import FeatureService

logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class NotFoundError(Exception):
    """Resource not found error."""
    pass


class UnauthorizedError(Exception):
    """Authorization required error."""
    pass

# Create blueprint (will be registered under /api/v1)
features_bp = Blueprint('features', __name__, url_prefix='/features')


# ============================================================================
# PUBLIC ENDPOINTS (No Authentication Required)
# ============================================================================

@features_bp.route('/<feature_code>/metadata', methods=['GET'])
def get_feature_metadata(feature_code: str) -> Tuple[Dict[str, Any], int]:
    """
    Get metadata for a specific feature (public).

    Public endpoint - no authentication required.

    Args:
        feature_code: Feature code (e.g., 'ai_editor', 'code_sandbox')

    Returns:
        200: Feature metadata
        404: Feature not found

    Example:
        GET /api/v1/features/ai_editor/metadata

        Response:
        {
            "success": true,
            "data": {
                "feature_code": "ai_editor",
                "feature_name": "AI-Studio",
                "description": "AI-powered content creation and analysis",
                "category": "ai",
                "requires_infrastructure": true,
                "icon": "sparkles"
            }
        }
    """
    try:
        # Validate feature code
        if not feature_code or not isinstance(feature_code, str):
            raise ValueError("Invalid feature code")

        # Get feature metadata
        metadata = FeatureService.get_feature_metadata(feature_code)

        if not metadata:
            raise NotFoundError(f"Feature '{feature_code}' not found")

        return jsonify({
            'success': True,
            'data': metadata
        }), 200

    except NotFoundError as e:
        logger.warning(f"Feature not found: {feature_code}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FEATURE_NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except ValueError as e:
        logger.warning(f"Validation error for feature {feature_code}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        logger.error(f"Error fetching feature metadata for {feature_code}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'METADATA_FETCH_FAILED',
                'message': 'Failed to fetch feature metadata'
            }
        }), 500


# ============================================================================
# AUTHENTICATED ENDPOINTS (Authentication Required)
# ============================================================================

@features_bp.route('/available', methods=['GET'])
@token_required
def get_available_features() -> Tuple[Dict[str, Any], int]:
    """
    Get all features available to the current user.

    Requires authentication.

    Returns:
        200: List of available features
        401: Unauthorized

    Example:
        GET /api/v1/features/available
        Authorization: Bearer <token>

        Response:
        {
            "success": true,
            "data": [
                {
                    "feature_code": "ai_editor",
                    "feature_name": "AI-Studio",
                    "access_level": "execute",
                    "category": "ai"
                },
                {
                    "feature_code": "code_sandbox",
                    "feature_name": "Code Sandbox",
                    "access_level": "execute",
                    "category": "it_environments"
                }
            ],
            "meta": {
                "total": 15,
                "timestamp": "2026-01-14T10:30:00Z"
            }
        }
    """
    try:
        # Get current user from token
        current_user = get_current_user()

        if not current_user:
            raise UnauthorizedError("User not found in token")

        user_id = current_user.get('user_id') or current_user.get('id')

        # Get available features for user
        features = FeatureService.get_available_features(user_id)

        return jsonify({
            'success': True,
            'data': features,
            'meta': {
                'total': len(features),
                'timestamp': None  # Added by middleware if needed
            }
        }), 200

    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': str(e)
            }
        }), 401

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        logger.error(f"Error fetching available features: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FEATURES_FETCH_FAILED',
                'message': 'Failed to fetch available features'
            }
        }), 500


@features_bp.route('/check/<feature_code>', methods=['GET'])
@token_required
def check_feature_access(feature_code: str) -> Tuple[Dict[str, Any], int]:
    """
    Check if the current user can access a specific feature.

    Requires authentication.

    Args:
        feature_code: Feature code to check

    Query Parameters:
        None

    Returns:
        200: Access check result
        401: Unauthorized
        400: Invalid feature code

    Example:
        GET /api/v1/features/check/ai_editor
        Authorization: Bearer <token>

        Response:
        {
            "success": true,
            "data": {
                "feature_code": "ai_editor",
                "has_access": true,
                "access_level": "execute"
            }
        }
    """
    try:
        # Get current user from token
        current_user = get_current_user()

        if not current_user:
            raise UnauthorizedError("User not found in token")

        user_id = current_user.get('user_id') or current_user.get('id')

        # Validate feature code
        if not feature_code or not isinstance(feature_code, str):
            raise ValueError("Invalid feature code")

        # Check if user can access feature
        has_access = FeatureService.can_access_feature(
            user_id,
            feature_code,
            require_active=True
        )

        # Get access level if user has access
        access_level = None
        if has_access:
            features = FeatureService.get_available_features(user_id)
            for f in features:
                if f.get('feature_code') == feature_code:
                    access_level = f.get('access_level', 'view')
                    break

        return jsonify({
            'success': True,
            'data': {
                'feature_code': feature_code,
                'has_access': has_access,
                'access_level': access_level
            }
        }), 200

    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': str(e)
            }
        }), 401

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        logger.error(f"Error checking feature access for {feature_code}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'ACCESS_CHECK_FAILED',
                'message': 'Failed to check feature access'
            }
        }), 500


@features_bp.route('/context/<context_type>', methods=['GET'])
@token_required
def get_context_features(context_type: str) -> Tuple[Dict[str, Any], int]:
    """
    Get features filtered by user context.

    Contexts:
    - 'user': Learning and personal features
    - 'admin': Administration and management features
    - 'community': Public and social features

    Requires authentication.

    Args:
        context_type: Context type (user, admin, community)

    Returns:
        200: Context-filtered features
        400: Invalid context
        401: Unauthorized

    Example:
        GET /api/v1/features/context/admin
        Authorization: Bearer <token>
    """
    try:
        # Get current user from token
        current_user = get_current_user()

        if not current_user:
            raise UnauthorizedError("User not found in token")

        user_id = current_user.get('user_id') or current_user.get('id')

        # Validate context type
        valid_contexts = ['user', 'admin', 'community']
        if context_type not in valid_contexts:
            raise ValueError(
                f"Invalid context. Must be one of: {', '.join(valid_contexts)}"
            )

        # Get context-filtered features
        features = FeatureService.get_user_context_features(
            user_id,
            context=context_type
        )

        return jsonify({
            'success': True,
            'data': features,
            'meta': {
                'context': context_type,
                'total': len(features)
            }
        }), 200

    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access attempt: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': str(e)
            }
        }), 401

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_CONTEXT',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        logger.error(f"Error fetching context features for {context_type}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'CONTEXT_FEATURES_FAILED',
                'message': 'Failed to fetch context features'
            }
        }), 500


# ============================================================================
# HEALTH CHECK (No Authentication)
# ============================================================================

@features_bp.route('/health', methods=['GET'])
def health_check() -> Tuple[Dict[str, Any], int]:
    """
    Health check endpoint for feature service.

    Returns:
        200: Service is healthy
    """
    return jsonify({
        'success': True,
        'data': {
            'status': 'healthy',
            'service': 'features-api'
        }
    }), 200
