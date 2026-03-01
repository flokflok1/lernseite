"""
Admin Learning Methods API - Schema Endpoint

Admin endpoint for fetching learning method UI schemas for dynamic form rendering.

Endpoint:
- GET /panel/learning-methods/{code}/schema - Get UI schema for learning method

This endpoint is used by the frontend DesktopLayer to dynamically load learning method
form definitions at runtime, enabling zero-downtime form updates.

ISO 27001:2013 compliant - Admin-only endpoint
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, Tuple
import logging

from app.infrastructure.persistence.repositories.learning_method.config.catalog import LearningMethodCatalogRepository
from app.api.middleware.auth import token_required, admin_required
from app.infrastructure.error_handling.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

# Blueprint
bp = Blueprint(
    'admin_learning_methods',
    __name__,
    url_prefix='/panel/learning-methods'
)


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@bp.route('/<int:code>/schema', methods=['GET'])
@token_required
@admin_required
def get_learning_method_schema(code: int) -> Tuple[Dict[str, Any], int]:
    """
    Get UI schema for a learning method by code.

    Admin-only endpoint. Returns complete form schema for dynamic form rendering.

    Path Parameters:
        - code: Learning method code (0-11 for lm00-lm11)

    Returns:
        Tuple of (response_dict, status_code)

    Response Format (200 OK):
    {
        "methodCode": 0,
        "methodName": "deep_explanation",
        "methodType": 0,
        "groupCode": "A",
        "fields": [
            {
                "name": "concept",
                "type": "text",
                "required": true,
                "label_i18n_key": "windows.lm00.conceptLabel",
                "placeholder_i18n_key": "windows.lm00.conceptPlaceholder"
            },
            {
                "name": "explanation",
                "type": "textarea",
                "required": true,
                "rows": 6,
                "label_i18n_key": "windows.lm00.explanationLabel",
                "placeholder_i18n_key": "windows.lm00.explanationPlaceholder"
            },
            ...
        ],
        "layout": "form",
        "sections": []
    }

    Status Codes:
        200: Success - schema returned
        400: Invalid method code (out of range 0-11)
        404: Learning method not found
        500: Server error

    Examples:
        GET /api/v1/panel/learning-methods/0/schema
        -> Returns UI schema for lm00 (Tiefgehende Erklärung)

        GET /api/v1/panel/learning-methods/5/schema
        -> Returns UI schema for lm05 (Mathe-Interaktiv)
    """
    try:
        # Validate code parameter (dynamically from database)
        max_type = LearningMethodCatalogRepository.get_max_active_type()

        if not isinstance(code, int) or code < 0 or code > max_type:
            logger.warning(f"Invalid learning method code requested: {code} (max: {max_type})")
            raise ValidationError(
                error_code='INVALID_METHOD_CODE',
                message=f'Invalid learning method code. Must be 0-{max_type}.',
                field='code'
            )

        # Fetch method data with schema from repository
        method_data = LearningMethodCatalogRepository.get_by_type(method_type=code)

        if not method_data:
            logger.warning(f"Learning method not found: lm{code:02d}")
            raise NotFoundError(
                error_code='LEARNING_METHOD_NOT_FOUND',
                message=f'Learning method lm{code:02d} (code {code}) not found'
            )

        # Extract UI schema from method data
        ui_schema = method_data.get('ui_schema', {})

        return jsonify(ui_schema), 200

    except ValidationError as e:
        logger.warning(f"Validation error in learning method schema: {e.message}")
        return jsonify({
            'error': {
                'code': e.error_code,
                'message': e.message,
                'field': e.field if hasattr(e, 'field') else None
            }
        }), 400

    except NotFoundError as e:
        logger.warning(f"Learning method not found: {e.message}")
        return jsonify({
            'error': {
                'code': e.error_code,
                'message': e.message
            }
        }), 404

    except Exception as e:
        logger.exception(f"Error fetching learning method schema for code {code}: {e}")
        return jsonify({
            'error': {
                'code': 'SCHEMA_FETCH_ERROR',
                'message': 'Failed to load learning method schema'
            }
        }), 500


__all__ = ['bp']
