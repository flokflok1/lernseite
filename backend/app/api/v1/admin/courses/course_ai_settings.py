"""
LernsystemX Admin Course AI Settings API

API endpoints for managing course-specific AI model configuration.
Each course can reference a global profile and/or override individual models.

Model Categories (6):
- chat_model_id: Chat/text generation
- reasoning_model_id: Prüfungen/Reasoning (o3, o1)
- image_model_id: Image generation
- audio_model_id: TTS/STT
- realtime_model_id: Realtime audio
- embedding_model_id: Embeddings

Endpoints:
  GET    /admin/course-ai-settings/:course_id         - Get settings for course
  PUT    /admin/course-ai-settings/:course_id         - Update settings
  DELETE /admin/course-ai-settings/:course_id         - Reset to defaults
  GET    /admin/course-ai-settings/profiles           - List available profiles
  POST   /admin/course-ai-settings/:course_id/apply-profile - Apply profile
  GET    /admin/course-ai-settings                    - List all custom settings

Phase: KI-Studio Pro - Kurs-spezifische KI-Einstellungen
ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.api.v1 import api_v1
from app.application.services.course_ai_settings_service import CourseAiSettingsService
from app.api.middleware.auth import admin_required
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response


# ============================================================================
# Pydantic Models
# ============================================================================

class CourseAiSettingsUpdate(BaseModel):
    """Request model for updating course AI settings (6 model categories)"""
    chat_model_id: Optional[str] = Field(None, description="Model for chat/text generation")
    reasoning_model_id: Optional[str] = Field(None, description="Model for reasoning/exams (o3, o1)")
    image_model_id: Optional[str] = Field(None, description="Model for image generation")
    audio_model_id: Optional[str] = Field(None, description="Model for TTS/STT")
    realtime_model_id: Optional[str] = Field(None, description="Model for realtime audio")
    embedding_model_id: Optional[str] = Field(None, description="Model for embeddings")
    additional_settings: Optional[Dict[str, Any]] = Field(None, description="Additional JSONB settings")


class ApplyProfileRequest(BaseModel):
    """Request model for applying a global profile"""
    profile_key: str = Field(..., description="Profile key from ai_model_profiles table")


# ============================================================================
# Endpoints
# ============================================================================

@api_v1.route('/admin/course-ai-settings/profiles', methods=['GET'])
@jwt_required()
@admin_required
def get_available_profiles():
    """
    Get available global model profiles.

    Returns:
        List of available profiles for course assignment

    Example Response:
        {
            "success": true,
            "data": {
                "profiles": [
                    {
                        "key": "standard",
                        "name": "Standard",
                        "description": "Ausgewogene Qualität und Kosten",
                        "is_default": true
                    },
                    ...
                ]
            }
        }
    """
    try:
        profiles = CourseAiSettingsService.get_available_profiles()
        return jsonify({
            "success": True,
            "data": {"profiles": profiles}
        }), 200
    except Exception as e:
        return error_response(ErrorCode.AI_CONFIGURATION_ERROR, 500, details={'error': str(e)})


@api_v1.route('/admin/course-ai-settings', methods=['GET'])
@jwt_required()
@admin_required
def list_all_course_ai_settings():
    """
    List all courses with custom AI settings.

    Query Parameters:
        limit: Maximum results (default 100)
        offset: Skip count (default 0)

    Returns:
        Paginated list of courses with custom settings

    Example Response:
        {
            "success": true,
            "data": {
                "items": [
                    {
                        "course_id": "abc-123",
                        "course_title": "Fachinformatiker",
                        "profile_key": "quality",
                        "profile_name": "Qualität",
                        "chat_model_id": "gpt-4o",
                        ...
                    }
                ],
                "total": 15,
                "limit": 100,
                "offset": 0
            }
        }
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)

        result = CourseAiSettingsService.list_all_settings(limit=limit, offset=offset)
        return jsonify({
            "success": True,
            "data": result
        }), 200
    except Exception as e:
        return error_response(ErrorCode.AI_CONFIGURATION_ERROR, 500, details={'error': str(e)})


@api_v1.route('/admin/course-ai-settings/<course_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_course_ai_settings(course_id: str):
    """
    Get AI settings for a specific course.

    Path Parameters:
        course_id: Course UUID

    Returns:
        Course AI settings and effective models (with fallback resolution)

    Example Response:
        {
            "success": true,
            "data": {
                "settings": {
                    "course_id": "abc-123",
                    "profile_key": "quality",
                    "profile_name": "Qualität",
                    "chat_model_id": "gpt-4o",
                    "reasoning_model_id": null,
                    ...
                },
                "effective": {
                    "course_id": "abc-123",
                    "profile_key": "quality",
                    "profile_name": "Qualität",
                    "chat_model_id": "gpt-4o",
                    "reasoning_model_id": "o3",
                    "image_model_id": "gpt-image-1",
                    "audio_model_id": "tts-1-hd",
                    "realtime_model_id": "gpt-4o-realtime-preview",
                    "embedding_model_id": "text-embedding-3-large",
                    "is_custom": true
                }
            }
        }
    """
    try:
        settings = CourseAiSettingsService.get_settings(course_id)
        effective = CourseAiSettingsService.get_effective_settings(course_id)

        return jsonify({
            "success": True,
            "data": {
                "settings": settings,
                "effective": effective
            }
        }), 200
    except ValueError as e:
        return error_response(ErrorCode.COURSE_NOT_FOUND, 404, details={'error': str(e)})
    except Exception as e:
        return error_response(ErrorCode.AI_CONFIGURATION_ERROR, 500, details={'error': str(e)})


@api_v1.route('/admin/course-ai-settings/<course_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_course_ai_settings(course_id: str):
    """
    Update AI settings for a course.

    Sets individual model overrides. Profile is preserved but
    these values take precedence over profile defaults.

    Path Parameters:
        course_id: Course UUID

    Request Body:
        {
            "chat_model_id": "gpt-4o",
            "reasoning_model_id": "o3",
            "image_model_id": "gpt-image-1",
            "audio_model_id": "tts-1-hd",
            "realtime_model_id": "gpt-4o-realtime-preview",
            "embedding_model_id": "text-embedding-3-large"
        }

    Returns:
        Updated settings and effective models

    Example Response:
        {
            "success": true,
            "data": {
                "settings": {...},
                "effective": {...},
                "message": "Settings updated"
            }
        }
    """
    try:
        data = request.get_json() or {}
        update = CourseAiSettingsUpdate(**data)

        settings = CourseAiSettingsService.update_settings(
            course_id=course_id,
            chat_model_id=update.chat_model_id,
            reasoning_model_id=update.reasoning_model_id,
            image_model_id=update.image_model_id,
            audio_model_id=update.audio_model_id,
            realtime_model_id=update.realtime_model_id,
            embedding_model_id=update.embedding_model_id,
            additional_settings=update.additional_settings
        )

        effective = CourseAiSettingsService.get_effective_settings(course_id)

        return jsonify({
            "success": True,
            "data": {
                "settings": settings,
                "effective": effective,
                "message": "Settings updated"
            }
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "VALIDATION_ERROR", "message": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "UPDATE_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/course-ai-settings/<course_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def reset_course_ai_settings(course_id: str):
    """
    Reset course AI settings to system defaults.

    Deletes all custom settings, making the course use
    the default profile's models.

    Path Parameters:
        course_id: Course UUID

    Returns:
        Success message

    Example Response:
        {
            "success": true,
            "data": {
                "message": "Settings reset to defaults",
                "deleted": true
            }
        }
    """
    try:
        deleted = CourseAiSettingsService.reset_to_defaults(course_id)

        return jsonify({
            "success": True,
            "data": {
                "message": "Settings reset to defaults",
                "deleted": deleted
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "RESET_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/course-ai-settings/<course_id>/apply-profile', methods=['POST'])
@jwt_required()
@admin_required
def apply_profile_to_course(course_id: str):
    """
    Apply a global profile to a course.

    Copies all model IDs from the profile to course settings.
    Sets profile_key for reference.

    Path Parameters:
        course_id: Course UUID

    Request Body:
        {
            "profile_key": "quality"
        }

    Returns:
        Updated settings with applied profile

    Example Response:
        {
            "success": true,
            "data": {
                "settings": {
                    "course_id": "abc-123",
                    "profile_key": "quality",
                    "chat_model_id": "gpt-4o",
                    ...
                },
                "effective": {...},
                "profile_applied": "quality",
                "message": "Profile 'Qualität' applied"
            }
        }
    """
    try:
        data = request.get_json() or {}
        req = ApplyProfileRequest(**data)

        settings = CourseAiSettingsService.apply_profile(
            course_id=course_id,
            profile_key=req.profile_key
        )

        effective = CourseAiSettingsService.get_effective_settings(course_id)

        # Get profile name for message
        profile_name = settings.get('profile_name') or req.profile_key

        return jsonify({
            "success": True,
            "data": {
                "settings": settings,
                "effective": effective,
                "profile_applied": req.profile_key,
                "message": f"Profile '{profile_name}' applied"
            }
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "INVALID_PROFILE", "message": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "APPLY_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/course-ai-settings/<course_id>/effective', methods=['GET'])
@jwt_required()
@admin_required
def get_effective_course_settings(course_id: str):
    """
    Get effective models for a course (with full fallback resolution).

    Resolves the fallback chain:
    1. Course-specific model ID
    2. Profile model ID (if profile_key set)
    3. Default profile model ID
    4. System default

    Path Parameters:
        course_id: Course UUID

    Returns:
        Effective models for all 6 categories

    Example Response:
        {
            "success": true,
            "data": {
                "course_id": "abc-123",
                "profile_key": "quality",
                "profile_name": "Qualität",
                "chat_model_id": "gpt-4o",
                "reasoning_model_id": "o3",
                "image_model_id": "gpt-image-1",
                "audio_model_id": "tts-1-hd",
                "realtime_model_id": "gpt-4o-realtime-preview",
                "embedding_model_id": "text-embedding-3-large",
                "is_custom": true
            }
        }
    """
    try:
        effective = CourseAiSettingsService.get_effective_settings(course_id)

        return jsonify({
            "success": True,
            "data": effective
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_EFFECTIVE_ERROR", "message": str(e)}
        }), 500
