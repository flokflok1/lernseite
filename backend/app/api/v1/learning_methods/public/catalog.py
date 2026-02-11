"""
Learning Methods Catalog API - Schema-Based Dynamic System

Public endpoint for learning method type catalog with UI schemas.

This endpoint enables zero-file-creation system: new LMs can be added
via SQL INSERT without modifying any Vue components.

Endpoints:
- GET /learning-methods/catalog - Get all 12 Content-LM types with ui_schema

Features:
- Returns complete definitions with ui_schema for dynamic form rendering
- Supports i18n via keys + English fallbacks (hybrid approach)
- Includes method metadata (name, description, group, tier, etc.)
- Caches result for performance

ISO 27001:2013 compliant - Public API endpoint
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any, Tuple
import logging

from app.infrastructure.persistence.repositories.learning_method.catalog import LearningMethodCatalogRepository
from app.infrastructure.persistence.repositories.learning_method.groups import LearningMethodGroupRepository
from app.infrastructure.cache.service import CacheService

logger = logging.getLogger(__name__)

# Blueprint
catalog_bp = Blueprint(
    'learning_methods_catalog',
    __name__,
    url_prefix='/learning-methods'
)


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================

@catalog_bp.route('/catalog', methods=['GET'])
def get_learning_methods_catalog() -> Tuple[Dict[str, Any], int]:
    """
    Get complete catalog of all Learning Methods with UI schemas.

    Public endpoint - no authentication required.
    Returns all 12 Content-LM types (lm00-lm11) with:
    - Type metadata (name, description, group, tier, icon)
    - UI schema for dynamic form rendering
    - i18n support (keys + English fallbacks)
    - Language support configuration

    Query Parameters:
        - cache: Use cached result (default: true)

    Response Format:
    {
        "success": true,
        "data": {
            "learning_methods": [
                {
                    "type_id": 1,
                    "method_type": 0,
                    "name": "Tiefgehende Erklärung",
                    "description": "KI-generierte Erklärung mit Beispielen & Analogien",
                    "group_code": "A",
                    "tier": "basic",
                    "ki_usage": "intensive",
                    "active": true,
                    "icon": "book-open",
                    "ui_schema": {
                        "lm_id": 0,
                        "lm_name": "Tiefgehende Erklärung",
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
            "total": 12,
            "groups": {
                "A": {
                    "name": "Erklärend (Explanation)",
                    "count": 5,
                    "description": "Explanatory methods for building understanding"
                },
                "B": {
                    "name": "Praxis (Practice)",
                    "count": 4,
                    "description": "Practical methods for exercise and application"
                },
                "C": {
                    "name": "Prüfung (Assessment)",
                    "count": 3,
                    "description": "Assessment methods for evaluating competency"
                }
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
        GET /api/v1/learning-methods/catalog
        -> Returns all 12 learning method types with schemas

        GET /api/v1/learning-methods/catalog?cache=false
        -> Bypass cache and get fresh data from database
    """
    try:
        # Check cache preference
        use_cache = request.args.get('cache', 'true').lower() != 'false'

        # Get catalog from repository
        catalog_data = LearningMethodCatalogRepository.get_full_catalog(use_cache=use_cache)

        if not catalog_data:
            logger.warning("No learning methods found in catalog")
            return jsonify({
                'success': True,
                'data': {
                    'learning_methods': [],
                    'total': 0,
                    'groups': {}
                },
                'timestamp': request.headers.get('X-Timestamp', '')
            }), 200

        return jsonify({
            'success': True,
            'data': catalog_data,
            'timestamp': request.headers.get('X-Timestamp', '')
        }), 200

    except Exception as e:
        logger.exception(f"Error fetching learning methods catalog: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'CATALOG_ERROR',
                'message': 'Failed to load learning methods catalog'
            }
        }), 500


@catalog_bp.route('/catalog/<int:method_type>', methods=['GET'])
def get_learning_method_by_type(method_type: int) -> Tuple[Dict[str, Any], int]:
    """
    Get single Learning Method by type ID with UI schema.

    Public endpoint - no authentication required.
    Returns complete definition of a specific LM including ui_schema.

    Path Parameters:
        - method_type: Learning method type (must be active in database)

    Returns:
        Tuple of (response_dict, status_code)

    Status Codes:
        200: Success - method returned
        404: Method not found
        400: Invalid method_type
        500: Server error

    Examples:
        GET /api/v1/learning-methods/catalog/0
        -> Returns lm00 (Tiefgehende Erklärung) with full schema

        GET /api/v1/learning-methods/catalog/5
        -> Returns lm05 (Mathe-Interaktiv) with full schema
    """
    try:
        # Validate method_type using dynamic repository method
        max_type = LearningMethodCatalogRepository.get_max_active_type()

        if not isinstance(method_type, int) or method_type < 0 or method_type > max_type:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_METHOD_TYPE',
                    'message': f'Invalid learning method type. Must be 0-{max_type}',
                    'field': 'method_type'
                }
            }), 400

        # Get method from repository
        method_data = LearningMethodCatalogRepository.get_by_type(method_type=method_type)

        if not method_data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'Learning method type {method_type} not found'
                }
            }), 404

        return jsonify({
            'success': True,
            'data': method_data,
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
        logger.exception(f"Error fetching learning method type {method_type}: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'FETCH_ERROR',
                'message': 'Failed to load learning method'
            }
        }), 500


@catalog_bp.route('/groups', methods=['GET'])
def get_learning_method_groups() -> Tuple[Dict[str, Any], int]:
    """
    Get all Learning Method Groups with tier information.

    Public endpoint - no authentication required.
    Returns all group codes (A, B, C, ...) with metadata.

    This endpoint serves as the single source of truth for:
    - Group code (A, B, C, ...)
    - Group name (Erklärend, Praxis, Prüfung, ...)
    - Group description
    - Group icon/emoji
    - Group tier level (basic, premium, enterprise)
    - Group sort order
    - Group active status

    Query Parameters:
        - cache: Use cached result (default: true)

    Response Format:
    {
        "success": true,
        "data": [
            {
                "group_code": "A",
                "name": "Erklärend",
                "description": "Explanatory methods for building understanding",
                "icon": "📖",
                "tier": "basic",
                "sort_order": 0,
                "is_active": true
            },
            {
                "group_code": "B",
                "name": "Praxis",
                "description": "Practical methods for exercise and application",
                "icon": "✏️",
                "tier": "basic",
                "sort_order": 1,
                "is_active": true
            },
            {
                "group_code": "C",
                "name": "Prüfung",
                "description": "Assessment methods for evaluating competency",
                "icon": "📝",
                "tier": "premium",
                "sort_order": 2,
                "is_active": true
            }
        ],
        "total": 3,
        "timestamp": "2026-01-21T12:34:56.789Z"
    }

    Returns:
        Tuple of (response_dict, status_code)

    Status Codes:
        200: Success - groups returned
        500: Server error

    Examples:
        GET /api/v1/learning-methods/groups
        -> Returns all 3 groups (A, B, C) with tier information

        GET /api/v1/learning-methods/groups?cache=false
        -> Bypass cache and get fresh data from database

    Note:
        This endpoint DOES NOT require authentication.
        All group data is public and cached for performance.
        Frontend uses this to determine tier levels for UI rendering.
    """
    try:
        # Check cache preference
        use_cache = request.args.get('cache', 'true').lower() != 'false'

        # Get all active groups from repository
        groups = LearningMethodGroupRepository.find_all()

        if not groups:
            logger.warning("No learning method groups found in database")
            return jsonify({
                'success': True,
                'data': [],
                'total': 0,
                'timestamp': request.headers.get('X-Timestamp', '')
            }), 200

        # Format response: convert Row objects to dicts
        groups_data = []
        for group in groups:
            # Handle both dict and Row objects
            if isinstance(group, dict):
                group_dict = group
            else:
                # Row object - convert to dict
                group_dict = dict(group) if hasattr(group, '__iter__') else group.__dict__

            groups_data.append({
                'group_code': group_dict.get('group_code'),
                'name': group_dict.get('name'),
                'description': group_dict.get('description'),
                'icon': group_dict.get('icon'),
                'tier': group_dict.get('tier'),
                'sort_order': group_dict.get('sort_order'),
                'is_active': group_dict.get('is_active', True)
            })

        return jsonify({
            'success': True,
            'data': groups_data,
            'total': len(groups_data),
            'timestamp': request.headers.get('X-Timestamp', '')
        }), 200

    except Exception as e:
        logger.exception(f"Error fetching learning method groups: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GROUPS_ERROR',
                'message': 'Failed to load learning method groups'
            }
        }), 500


__all__ = ['catalog_bp']
