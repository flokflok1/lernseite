"""
Learning Method Types Endpoint (DDD)

Get all available learning method types (12 Content-LMs, 3 Groups A-C).
"""

from flask import jsonify
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.ki.learning_method_mapping import get_all_methods_as_dict, get_group_info

from .blueprints import lm_types_bp

logger = logging.getLogger(__name__)


@lm_types_bp.route('/learning-method-types', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
@limiter.limit("60 per minute")
def get_learning_method_types() -> Tuple[Dict[str, Any], int]:
    """
    Get all active learning method types (12 Content-LMs, 3 Groups A-C).

    Returns:
        JSON response with types, groups, and total count

    Response:
        {
            "success": true,
            "types": [
                {
                    "lm_id": 0,
                    "name": "Tiefgehende Erklärung",
                    "group": "A",
                    "method_type": "explanatory",
                    "ki_usage": "intensive",
                    "prompt_key": "deep_explanation",
                    "description": "..."
                },
                ...
            ],
            "total": 12,
            "groups": {
                "A": {"name": "Erklärende Methoden", "count": 5},
                "B": {"name": "Praxis/Übung", "count": 4},
                "C": {"name": "Prüfungsorientiert", "count": 3}
            }
        }

    Business Rules:
    - 12 Content-Lernmethoden (LM00-LM11)
    - 3 Gruppen (A, B, C)
    - method_type 0-11
    """
    try:
        # Get all method types from mapping
        types = get_all_methods_as_dict()

        # Get group info
        groups = get_group_info()

        return jsonify({
            'success': True,
            'types': types,
            'total': len(types),
            'groups': groups
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning method types: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning method types',
            'message': str(e)
        }), 500
