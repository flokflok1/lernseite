"""
System Features - Feature Types Routes (Admin Journey)

Endpoints for listing available system feature types.

Endpoints:
  GET /admin/system-feature-types - List all feature types

Phase: 5.3.1 - System-Features Management Migration
Reference: 02a_System-Features.md, Phase 5.3
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.middleware.auth import admin_required
from src.api.system_features.core.domain.repositories.features_repository import SystemFeaturesRepository


# Blueprint
feature_types_bp = Blueprint('system_features_feature_types', __name__)


@feature_types_bp.route('/admin/system-feature-types', methods=['GET'])
@jwt_required()
@admin_required
def get_system_feature_types():
    """
    Get all available system feature types.

    Returns:
        List of all active system feature types grouped by category

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "feature_types": [
                        {
                            "feature_type_id": 1,
                            "feature_code": "socratic_dialog",
                            "name": "Sokratischer Dialog",
                            "category": "tutor",
                            "description": "KI fragt, User leitet Konzept selbst her",
                            "former_lm_id": 4,
                            "is_premium": true
                        },
                        ...
                    ],
                    "categories": ["tutor", "visualization", "it_sandbox", "collaboration", "gamification"]
                }
            }
        500: Internal server error
    """
    try:
        feature_types = SystemFeaturesRepository.get_feature_types()

        # Extract unique categories
        categories = list(set(ft['category'] for ft in feature_types))
        categories.sort()

        return jsonify({
            "success": True,
            "data": {
                "feature_types": feature_types,
                "categories": categories
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "FEATURE_TYPES_ERROR", "message": str(e)}
        }), 500


__all__ = ['feature_types_bp']
