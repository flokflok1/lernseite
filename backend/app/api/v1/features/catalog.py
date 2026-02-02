"""
System Features Catalog API - Schema-Based Dynamic System

Public endpoint for system features catalog with UI schemas.

This endpoint enables system-wide feature discovery without frontend hardcoding.
New features can be added via SQL INSERT without modifying any Vue components.

Endpoints:
- GET /features/catalog - Get all 25 System-Features with ui_schema
- GET /features/catalog/<feature_code> - Get single feature by code

Features:
- Returns complete definitions with ui_schema for dynamic configuration rendering
- Supports i18n via keys + English fallbacks (hybrid approach)
- Includes feature metadata (name, description, category, requirements, etc.)
- Caches result for performance

ISO 27001:2013 compliant - Public API endpoint
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any, Tuple
import logging

from app.infrastructure.persistence.repositories.system_features_catalog import SystemFeaturesCatalogRepository
from app.infrastructure.cache.service import CacheService

logger = logging.getLogger(__name__)

# Blueprint
catalog_bp = Blueprint(
    'system_features_catalog',
    __name__,
    url_prefix='/features'
)


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@catalog_bp.route('/catalog', methods=['GET'])
def get_system_features_catalog() -> Tuple[Dict[str, Any], int]:
    """
    Get complete catalog of all System Features with UI schemas.

    Public endpoint - no authentication required.
    Returns all 25 System-Features with:
    - Feature metadata (name, description, category, requirements)
    - UI schema for dynamic configuration rendering
    - i18n support (keys + English fallbacks)
    - Language support configuration

    Query Parameters:
        - cache: Use cached result (default: true)

    Response Format:
    {
        "success": true,
        "data": {
            "features": [
                {
                    "feature_id": 1,
                    "feature_code": "whiteboard_engine",
                    "feature_name": "Interactive Whiteboard",
                    "description": "Real-time collaborative whiteboard with formula recognition",
                    "category": "interactive_tools",
                    "requires_infrastructure": true,
                    "requires_external_service": false,
                    "active": true,
                    "icon": "pen-tool",
                    "ui_schema": {
                        "feature_code": "whiteboard_engine",
                        "feature_name": "Interactive Whiteboard",
                        "form_type": "dynamic",
                        "language_support": ["de", "en", "pl"],
                        "layout": "vertical",
                        "fields": [...]
                    },
                    "created_at": "2026-01-21T...",
                    "updated_at": "2026-01-21T..."
                },
                ...
            ],
            "total": 25,
            "categories": {
                "audio": {
                    "name": "Audio",
                    "count": 2,
                    "description": "Audio processing and synthesis"
                },
                "collaboration": {
                    "name": "Collaboration",
                    "count": 3,
                    "description": "Team and group features"
                },
                ...
            }
        },
        "timestamp": "2026-01-21T12:34:56.789Z"
    }

    Returns:
        Tuple of (response_dict, status_code)

    Status Codes:
        200: Success - catalog returned
        500: Server error

    Examples:
        GET /api/v1/features/catalog
        -> Returns all 25 system features with schemas

        GET /api/v1/features/catalog?cache=false
        -> Bypass cache and get fresh data from database
    """
    try:
        # Check cache preference
        use_cache = request.args.get('cache', 'true').lower() != 'false'

        # Get catalog from repository
        catalog_data = SystemFeaturesCatalogRepository.get_full_catalog(use_cache=use_cache)

        if not catalog_data:
            logger.warning("No system features found in catalog")
            return jsonify({
                'success': True,
                'data': {
                    'features': [],
                    'total': 0,
                    'categories': {}
                },
                'timestamp': request.headers.get('X-Timestamp', '')
            }), 200

        return jsonify({
            'success': True,
            'data': catalog_data,
            'timestamp': request.headers.get('X-Timestamp', '')
        }), 200

    except Exception as e:
        logger.exception(f"Error fetching system features catalog: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'CATALOG_ERROR',
                'message': 'Failed to load system features catalog'
            }
        }), 500


@catalog_bp.route('/catalog/<feature_code>', methods=['GET'])
def get_system_feature_by_code(feature_code: str) -> Tuple[Dict[str, Any], int]:
    """
    Get single System Feature by code with UI schema.

    Public endpoint - no authentication required.
    Returns complete definition of a specific feature including ui_schema.

    Path Parameters:
        - feature_code: System feature code (e.g., whiteboard_engine, it_sandbox, npc_tutor)

    Returns:
        Tuple of (response_dict, status_code)

    Status Codes:
        200: Success - feature returned
        404: Feature not found
        400: Invalid feature_code
        500: Server error

    Examples:
        GET /api/v1/features/catalog/whiteboard_engine
        -> Returns whiteboard_engine feature with full schema

        GET /api/v1/features/catalog/npc_tutor
        -> Returns npc_tutor feature with full schema

        GET /api/v1/features/catalog/invalid_code
        -> Returns 404 Not Found
    """
    try:
        # Validate feature_code
        if not feature_code or not isinstance(feature_code, str):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_FEATURE_CODE',
                    'message': 'Invalid system feature code format',
                    'field': 'feature_code'
                }
            }), 400

        if len(feature_code) > 50:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_FEATURE_CODE',
                    'message': 'Feature code too long (max 50 characters)',
                    'field': 'feature_code'
                }
            }), 400

        # Get feature from repository
        feature_data = SystemFeaturesCatalogRepository.get_by_code(feature_code=feature_code)

        if not feature_data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'System feature {feature_code} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': feature_data,
            'timestamp': request.headers.get('X-Timestamp', '')
        }), 200

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
        logger.exception(f"Error fetching system feature {feature_code}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': 'Failed to load system feature'
            }
        }), 500


@catalog_bp.route('/catalog/category/<category>', methods=['GET'])
def get_features_by_category(category: str) -> Tuple[Dict[str, Any], int]:
    """
    Get all System Features in a specific category with UI schemas.

    Public endpoint - no authentication required.
    Returns all features grouped by category.

    Path Parameters:
        - category: Feature category (audio, collaboration, exam_systems, gamification,
                    interactive_tools, it_environments, learning_paths, meta_features, tutor, visualization)

    Returns:
        Tuple of (response_dict, status_code)

    Status Codes:
        200: Success - category features returned
        404: Category not found
        400: Invalid category
        500: Server error

    Examples:
        GET /api/v1/features/catalog/category/interactive_tools
        -> Returns all interactive_tools features

        GET /api/v1/features/catalog/category/tutor
        -> Returns all tutor features

        GET /api/v1/features/catalog/category/invalid
        -> Returns 400 Invalid category
    """
    try:
        # Validate category
        valid_categories = [
            'audio', 'collaboration', 'exam_systems', 'gamification',
            'interactive_tools', 'it_environments', 'learning_paths',
            'meta_features', 'tutor', 'visualization'
        ]

        if category not in valid_categories:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_CATEGORY',
                    'message': f'Invalid category. Must be one of: {", ".join(valid_categories)}',
                    'field': 'category',
                    'valid_categories': valid_categories
                }
            }), 400

        # Get features from repository
        features_data = SystemFeaturesCatalogRepository.get_by_category(category=category)

        if not features_data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'No features found in category {category}'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'category': category,
                'features': features_data,
                'total': len(features_data)
            },
            'timestamp': request.headers.get('X-Timestamp', '')
        }), 200

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
        logger.exception(f"Error fetching features for category {category}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': 'Failed to load features for category'
            }
        }), 500


__all__ = ['catalog_bp']
