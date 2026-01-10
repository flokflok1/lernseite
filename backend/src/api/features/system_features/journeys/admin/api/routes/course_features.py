"""
System Features - Course Features Routes (Admin Journey)

Endpoints for managing course-level system features configuration.

Endpoints:
  GET    /admin/courses/:course_id/system-features - Get features for course
  PUT    /admin/courses/:course_id/system-features - Update features
  POST   /admin/courses/:course_id/system-features/bulk - Bulk enable/disable
  DELETE /admin/courses/:course_id/system-features/:feature_code - Remove feature

Phase: 5.3.1 - System-Features Management Migration
Reference: 02a_System-Features.md, Phase 5.3
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from app.middleware.auth import admin_required
from src.api.system_features.core.domain.repositories.features_repository import SystemFeaturesRepository


# Blueprint
course_features_bp = Blueprint('system_features_course_features', __name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class SystemFeaturesUpdate(BaseModel):
    """Request model for updating course system features"""
    scope: str = Field('course', description="Scope: course, chapter, lesson")
    scope_id: str = Field(..., description="ID of the scope target")
    features: Dict[str, bool] = Field(..., description="Feature codes mapped to enabled state")


class BulkFeaturesUpdate(BaseModel):
    """Request model for bulk feature updates"""
    feature_codes: List[str] = Field(..., description="List of feature codes")
    is_enabled: bool = Field(..., description="Enable or disable all")


# ============================================================================
# Endpoints
# ============================================================================

@course_features_bp.route('/admin/courses/<course_id>/system-features', methods=['GET'])
@jwt_required()
@admin_required
def get_course_system_features(course_id: str):
    """
    Get system features for a course (with optional scope).

    Query Parameters:
        scope: 'course' (default), 'chapter', or 'lesson'
        scope_id: ID if scope is chapter/lesson

    Args:
        course_id: UUID of the course

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "features": {
                        "socratic_dialog": true,
                        "npc_tutor": false,
                        "code_sandbox": true,
                        ...
                    },
                    "inherited": {
                        "socratic_dialog": true,
                        ...
                    },
                    "feature_details": [...],
                    "scope": "course",
                    "scope_id": "course-uuid"
                }
            }
        500: Internal server error
    """
    try:
        scope = request.args.get('scope', 'course')
        scope_id = request.args.get('scope_id', course_id)

        # Get all feature types
        all_types = SystemFeaturesRepository.get_feature_types()

        # Get course-level features
        course_features = SystemFeaturesRepository.get_course_features(course_id)

        # Build features dict (default all to False)
        features = {}
        feature_details = []

        for ft in all_types:
            code = ft['feature_code']
            # Check if enabled in course_features
            cf = next((f for f in course_features if f['feature_code'] == code), None)
            features[code] = cf['is_enabled'] if cf else False

            feature_details.append({
                **ft,
                'is_enabled': features[code],
                'config': cf['config'] if cf else {}
            })

        # For chapter/lesson scope, we'd check overrides (future enhancement)
        inherited = {} if scope == 'course' else features.copy()

        return jsonify({
            "success": True,
            "data": {
                "features": features,
                "inherited": inherited if scope != 'course' else None,
                "feature_details": feature_details,
                "scope": scope,
                "scope_id": scope_id
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_FEATURES_ERROR", "message": str(e)}
        }), 500


@course_features_bp.route('/admin/courses/<course_id>/system-features', methods=['PUT'])
@jwt_required()
@admin_required
def update_course_system_features(course_id: str):
    """
    Update system features for a course.

    Args:
        course_id: UUID of the course

    Request Body:
        {
            "scope": "course",
            "scope_id": "course-uuid",
            "features": {
                "socratic_dialog": true,
                "code_sandbox": false,
                ...
            }
        }

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "updated": ["socratic_dialog", "code_sandbox"],
                    "features": {...}
                }
            }
        400: Validation error
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_REQUEST", "message": "Request body required"}
            }), 400

        try:
            update_request = SystemFeaturesUpdate(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        updated = []

        for feature_code, is_enabled in update_request.features.items():
            # Get feature type
            feature_type = SystemFeaturesRepository.get_feature_type_by_code(feature_code)
            if not feature_type:
                continue  # Skip unknown features

            # Upsert the feature
            SystemFeaturesRepository.upsert_course_feature(
                course_id=course_id,
                feature_type_id=feature_type['feature_type_id'],
                is_enabled=is_enabled
            )
            updated.append(feature_code)

        # Get updated features
        course_features = SystemFeaturesRepository.get_course_features(course_id)
        features = {f['feature_code']: f['is_enabled'] for f in course_features}

        return jsonify({
            "success": True,
            "data": {
                "updated": updated,
                "features": features
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "UPDATE_FEATURES_ERROR", "message": str(e)}
        }), 500


@course_features_bp.route('/admin/courses/<course_id>/system-features/bulk', methods=['POST'])
@jwt_required()
@admin_required
def bulk_update_course_features(course_id: str):
    """
    Bulk enable or disable multiple features at once.

    Args:
        course_id: UUID of the course

    Request Body:
        {
            "feature_codes": ["socratic_dialog", "npc_tutor", "code_sandbox"],
            "is_enabled": true
        }

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "updated": ["socratic_dialog", "npc_tutor", "code_sandbox"],
                    "is_enabled": true
                }
            }
        400: Validation error
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": {"code": "INVALID_REQUEST", "message": "Request body required"}
            }), 400

        try:
            bulk_request = BulkFeaturesUpdate(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": {"code": "VALIDATION_ERROR", "message": str(e)}
            }), 400

        updated = []

        for feature_code in bulk_request.feature_codes:
            feature_type = SystemFeaturesRepository.get_feature_type_by_code(feature_code)
            if not feature_type:
                continue

            SystemFeaturesRepository.upsert_course_feature(
                course_id=course_id,
                feature_type_id=feature_type['feature_type_id'],
                is_enabled=bulk_request.is_enabled
            )
            updated.append(feature_code)

        return jsonify({
            "success": True,
            "data": {
                "updated": updated,
                "is_enabled": bulk_request.is_enabled
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "BULK_UPDATE_ERROR", "message": str(e)}
        }), 500


@course_features_bp.route('/admin/courses/<course_id>/system-features/<feature_code>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_course_feature(course_id: str, feature_code: str):
    """
    Remove a feature from a course (resets to default/inherited).

    Args:
        course_id: UUID of the course
        feature_code: Feature code to remove

    Response:
        200: Success
            {
                "success": true,
                "data": {
                    "deleted": "socratic_dialog",
                    "message": "Feature removed, will use inherited/default value"
                }
            }
        404: Feature not found
        500: Internal server error
    """
    try:
        feature_type = SystemFeaturesRepository.get_feature_type_by_code(feature_code)
        if not feature_type:
            return jsonify({
                "success": False,
                "error": {"code": "FEATURE_NOT_FOUND", "message": f"Feature '{feature_code}' not found"}
            }), 404

        SystemFeaturesRepository.delete_course_feature(
            course_id=course_id,
            feature_type_id=feature_type['feature_type_id']
        )

        return jsonify({
            "success": True,
            "data": {
                "deleted": feature_code,
                "message": "Feature removed, will use inherited/default value"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "DELETE_FEATURE_ERROR", "message": str(e)}
        }), 500


__all__ = ['course_features_bp']
