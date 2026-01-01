"""
LernsystemX Admin Course System Features API

API endpoints for managing course-specific System Features.
Features can be enabled/disabled per course, chapter, or lesson (with inheritance).

Feature Categories:
- tutor: Sokratischer Dialog (LM04), NPC-Tutor (LM07)
- visualization: Mindmap-Generator (LM05)
- it_sandbox: Code Sandbox (LM09), Network Sim (LM10), IT-Scenario (LM11), Error Analysis (LM16)
- collaboration: Peer Instruction (LM26), Team-Case (LM27), Peer Review (LM28), etc.
- gamification: Adaptive Difficulty, Spaced Repetition, XP & Quests

Endpoints:
  GET    /admin/courses/:course_id/system-features           - Get features for scope
  PUT    /admin/courses/:course_id/system-features           - Update features
  GET    /admin/system-feature-types                         - List all feature types
  POST   /admin/courses/:course_id/system-features/bulk      - Bulk enable/disable

Phase: KI-Studio Pro - System-Features
Reference: 02a_System-Features.md, Migration 069
"""

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from app.api import api_v1
from app.repositories.base_repository import BaseRepository
from app.middleware.auth import admin_required


# ============================================================================
# Pydantic Models
# ============================================================================

class FeatureUpdate(BaseModel):
    """Single feature update"""
    feature_code: str = Field(..., description="Feature code (e.g., 'socratic_dialog')")
    is_enabled: bool = Field(..., description="Enable or disable")
    config: Optional[Dict[str, Any]] = Field(None, description="Feature-specific config")


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
# Repository Functions (inline for simplicity)
# ============================================================================

class SystemFeaturesRepository:
    """Repository for system feature operations"""

    @staticmethod
    def get_feature_types() -> List[Dict]:
        """Get all system feature types"""
        query = """
            SELECT
                feature_type_id,
                feature_code,
                name,
                category,
                description,
                former_lm_id,
                is_premium,
                is_active
            FROM system_feature_types
            WHERE is_active = TRUE
            ORDER BY category, feature_code
        """
        return BaseRepository.fetch_all(query) or []

    @staticmethod
    def get_course_features(course_id: str) -> List[Dict]:
        """Get all features enabled for a course"""
        query = """
            SELECT
                cf.course_feature_id,
                cf.course_id,
                cf.feature_type_id,
                cf.is_enabled,
                cf.config,
                sft.feature_code,
                sft.name,
                sft.category
            FROM course_features cf
            JOIN system_feature_types sft ON cf.feature_type_id = sft.feature_type_id
            WHERE cf.course_id = %s
        """
        return BaseRepository.fetch_all(query, (course_id,)) or []

    @staticmethod
    def get_feature_type_by_code(feature_code: str) -> Optional[Dict]:
        """Get feature type by code"""
        query = """
            SELECT feature_type_id, feature_code, name, category, is_premium
            FROM system_feature_types
            WHERE feature_code = %s AND is_active = TRUE
        """
        return BaseRepository.fetch_one(query, (feature_code,))

    @staticmethod
    def upsert_course_feature(course_id: str, feature_type_id: int, is_enabled: bool, config: Dict = None) -> Dict:
        """Insert or update a course feature"""
        query = """
            INSERT INTO course_features (course_id, feature_type_id, is_enabled, config)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (course_id, feature_type_id)
            DO UPDATE SET
                is_enabled = EXCLUDED.is_enabled,
                config = COALESCE(EXCLUDED.config, course_features.config),
                updated_at = NOW()
            RETURNING course_feature_id, course_id, feature_type_id, is_enabled, config
        """
        import json
        config_json = json.dumps(config or {})
        return BaseRepository.fetch_one(query, (course_id, feature_type_id, is_enabled, config_json))

    @staticmethod
    def delete_course_feature(course_id: str, feature_type_id: int) -> bool:
        """Remove a course feature"""
        query = """
            DELETE FROM course_features
            WHERE course_id = %s AND feature_type_id = %s
        """
        BaseRepository.execute(query, (course_id, feature_type_id))
        return True


# ============================================================================
# Endpoints
# ============================================================================

@api_v1.route('/admin/system-feature-types', methods=['GET'])
@jwt_required()
@admin_required
def get_system_feature_types():
    """
    Get all available system feature types.

    Returns:
        List of all active system feature types grouped by category

    Example Response:
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


@api_v1.route('/admin/courses/<course_id>/system-features', methods=['GET'])
@jwt_required()
@admin_required
def get_course_system_features(course_id: str):
    """
    Get system features for a course (with optional scope).

    Query Parameters:
        scope: 'course' (default), 'chapter', or 'lesson'
        scope_id: ID if scope is chapter/lesson

    Returns:
        Features enabled for the course with inherited values

    Example Response:
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
                "feature_details": [...]
            }
        }
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


@api_v1.route('/admin/courses/<course_id>/system-features', methods=['PUT'])
@jwt_required()
@admin_required
def update_course_system_features(course_id: str):
    """
    Update system features for a course.

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

    Returns:
        Updated features

    Example Response:
        {
            "success": true,
            "data": {
                "updated": ["socratic_dialog", "code_sandbox"],
                "features": {...}
            }
        }
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


@api_v1.route('/admin/courses/<course_id>/system-features/bulk', methods=['POST'])
@jwt_required()
@admin_required
def bulk_update_course_features(course_id: str):
    """
    Bulk enable or disable multiple features at once.

    Request Body:
        {
            "feature_codes": ["socratic_dialog", "npc_tutor", "code_sandbox"],
            "is_enabled": true
        }

    Returns:
        List of updated features
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


@api_v1.route('/admin/courses/<course_id>/system-features/<feature_code>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_course_feature(course_id: str, feature_code: str):
    """
    Remove a feature from a course (resets to default/inherited).

    Returns:
        Success status
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
