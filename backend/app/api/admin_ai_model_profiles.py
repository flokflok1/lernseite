"""
LernsystemX Admin AI Model Profiles API

API endpoints for managing global AI model profiles.
Profiles define sets of models per category that can be applied to courses.

Endpoints:
  GET    /admin/ai-model-profiles              - List all profiles
  POST   /admin/ai-model-profiles              - Create new profile
  GET    /admin/ai-model-profiles/<key>        - Get profile by key
  PUT    /admin/ai-model-profiles/<key>        - Update profile
  DELETE /admin/ai-model-profiles/<key>        - Delete profile
  POST   /admin/ai-model-profiles/<key>/default - Set as default

Phase: KI-Studio Pro - Globale KI-Einstellungen
ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

import logging
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Optional, Union

from app.api import api_v1
from app.services.ai_model_profiles_service import AiModelProfilesService
from app.middleware.auth import admin_required

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class ProfileCreate(BaseModel):
    """Request model for creating a profile"""
    key: str = Field(..., min_length=1, max_length=50, description="Unique profile key (lowercase)")
    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    description: Optional[str] = Field(None, description="Optional description")
    # Core models
    chat_model_id: Optional[str] = Field(None, description="Chat/text model ID")
    reasoning_model_id: Optional[str] = Field(None, description="Reasoning model ID")
    image_model_id: Optional[str] = Field(None, description="Image generation model ID")
    audio_model_id: Optional[str] = Field(None, description="Audio/TTS model ID")
    realtime_model_id: Optional[str] = Field(None, description="Realtime model ID")
    embedding_model_id: Optional[str] = Field(None, description="Embedding model ID")
    # Extended models
    legacy_model_id: Optional[str] = Field(None, description="Legacy model ID")
    moderation_model_id: Optional[str] = Field(None, description="Moderation model ID")
    video_model_id: Optional[str] = Field(None, description="Video model ID")
    vision_model_id: Optional[str] = Field(None, description="Vision model ID")
    transcription_model_id: Optional[str] = Field(None, description="Transcription model ID")
    translation_model_id: Optional[str] = Field(None, description="Translation model ID")
    is_default: bool = Field(False, description="Set as default profile")


class ProfileUpdate(BaseModel):
    """Request model for updating a profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    # Core models - accept str or int, convert to str
    chat_model_id: Optional[Union[str, int]] = None
    reasoning_model_id: Optional[Union[str, int]] = None
    image_model_id: Optional[Union[str, int]] = None
    audio_model_id: Optional[Union[str, int]] = None
    realtime_model_id: Optional[Union[str, int]] = None
    embedding_model_id: Optional[Union[str, int]] = None
    # Extended models
    legacy_model_id: Optional[Union[str, int]] = None
    moderation_model_id: Optional[Union[str, int]] = None
    video_model_id: Optional[Union[str, int]] = None
    vision_model_id: Optional[Union[str, int]] = None
    transcription_model_id: Optional[Union[str, int]] = None
    translation_model_id: Optional[Union[str, int]] = None
    is_default: Optional[bool] = None

    @field_validator('chat_model_id', 'reasoning_model_id', 'image_model_id', 'audio_model_id',
                     'realtime_model_id', 'embedding_model_id', 'legacy_model_id', 'moderation_model_id',
                     'video_model_id', 'vision_model_id', 'transcription_model_id', 'translation_model_id',
                     mode='before')
    @classmethod
    def convert_to_str(cls, v):
        if v is None:
            return None
        return str(v)


# ============================================================================
# Endpoints
# ============================================================================

@api_v1.route('/admin/ai-model-profiles', methods=['GET'])
@jwt_required()
@admin_required
def list_ai_model_profiles():
    """
    List all active AI model profiles.

    Query Parameters:
        summary (bool): If true, return only key/name/description/is_default

    Returns:
        List of profiles

    Example Response:
        {
            "success": true,
            "data": {
                "profiles": [
                    {
                        "key": "standard",
                        "name": "Standard",
                        "description": "...",
                        "chat_model_id": "gpt-4o-mini",
                        ...
                    }
                ],
                "count": 4
            }
        }
    """
    try:
        summary_only = request.args.get('summary', 'false').lower() == 'true'

        if summary_only:
            profiles = AiModelProfilesService.get_profile_summary()
        else:
            profiles = AiModelProfilesService.get_all_profiles()

        return jsonify({
            "success": True,
            "data": {
                "profiles": profiles,
                "count": len(profiles)
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "LIST_PROFILES_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/ai-model-profiles', methods=['POST'])
@jwt_required()
@admin_required
def create_ai_model_profile():
    """
    Create a new AI model profile.

    Request Body:
        {
            "key": "custom",
            "name": "Custom Profile",
            "description": "My custom profile",
            "chat_model_id": "gpt-4o",
            "reasoning_model_id": "o3",
            ...
        }

    Returns:
        Created profile

    Example Response:
        {
            "success": true,
            "data": {
                "profile": {...},
                "message": "Profile created"
            }
        }
    """
    try:
        data = request.get_json() or {}
        create_data = ProfileCreate(**data)

        profile = AiModelProfilesService.create_profile(
            key=create_data.key,
            name=create_data.name,
            description=create_data.description,
            chat_model_id=create_data.chat_model_id,
            reasoning_model_id=create_data.reasoning_model_id,
            image_model_id=create_data.image_model_id,
            audio_model_id=create_data.audio_model_id,
            realtime_model_id=create_data.realtime_model_id,
            embedding_model_id=create_data.embedding_model_id,
            is_default=create_data.is_default
        )

        return jsonify({
            "success": True,
            "data": {
                "profile": profile,
                "message": "Profile created"
            }
        }), 201
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "VALIDATION_ERROR", "message": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "CREATE_PROFILE_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/ai-model-profiles/<key>', methods=['GET'])
@jwt_required()
@admin_required
def get_ai_model_profile(key: str):
    """
    Get a profile by key.

    Path Parameters:
        key: Profile key

    Query Parameters:
        include_model_info (bool): Include full model info for each model ID

    Returns:
        Profile with optional model info

    Example Response:
        {
            "success": true,
            "data": {
                "profile": {
                    "key": "standard",
                    "name": "Standard",
                    "chat_model_id": "gpt-4o-mini",
                    "chat_model_info": {
                        "model_id": "gpt-4o-mini",
                        "display_name": "GPT-4o Mini",
                        "category": "chat",
                        ...
                    }
                }
            }
        }
    """
    try:
        include_model_info = request.args.get('include_model_info', 'false').lower() == 'true'

        if include_model_info:
            profile = AiModelProfilesService.get_profile_with_model_info(key)
        else:
            profile = AiModelProfilesService.get_profile(key)

        if not profile:
            return jsonify({
                "success": False,
                "error": {"code": "NOT_FOUND", "message": f"Profile '{key}' not found"}
            }), 404

        return jsonify({
            "success": True,
            "data": {"profile": profile}
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_PROFILE_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/ai-model-profiles/<key>', methods=['PUT'])
@jwt_required()
@admin_required
def update_ai_model_profile(key: str):
    """
    Update a profile.

    Path Parameters:
        key: Profile key

    Request Body:
        {
            "name": "Updated Name",
            "chat_model_id": "gpt-4o",
            ...
        }

    Returns:
        Updated profile

    Example Response:
        {
            "success": true,
            "data": {
                "profile": {...},
                "message": "Profile updated"
            }
        }
    """
    try:
        data = request.get_json() or {}
        logger.info(f"Update profile {key} with data: {data}")
        update_data = ProfileUpdate(**data)

        profile = AiModelProfilesService.update_profile(
            key=key,
            name=update_data.name,
            description=update_data.description,
            chat_model_id=update_data.chat_model_id,
            reasoning_model_id=update_data.reasoning_model_id,
            image_model_id=update_data.image_model_id,
            audio_model_id=update_data.audio_model_id,
            realtime_model_id=update_data.realtime_model_id,
            embedding_model_id=update_data.embedding_model_id,
            legacy_model_id=update_data.legacy_model_id,
            moderation_model_id=update_data.moderation_model_id,
            video_model_id=update_data.video_model_id,
            vision_model_id=update_data.vision_model_id,
            transcription_model_id=update_data.transcription_model_id,
            translation_model_id=update_data.translation_model_id,
            is_default=update_data.is_default
        )

        return jsonify({
            "success": True,
            "data": {
                "profile": profile,
                "message": "Profile updated"
            }
        }), 200
    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e}")
        return jsonify({
            "success": False,
            "error": {"code": "VALIDATION_ERROR", "message": str(e)}
        }), 400
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return jsonify({
            "success": False,
            "error": {"code": "VALIDATION_ERROR", "message": str(e)}
        }), 400
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({
            "success": False,
            "error": {"code": "UPDATE_PROFILE_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/ai-model-profiles/<key>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_ai_model_profile(key: str):
    """
    Delete a profile.

    Path Parameters:
        key: Profile key

    Returns:
        Success message

    Example Response:
        {
            "success": true,
            "data": {
                "message": "Profile deleted",
                "deleted": true
            }
        }
    """
    try:
        deleted = AiModelProfilesService.delete_profile(key)

        return jsonify({
            "success": True,
            "data": {
                "message": "Profile deleted",
                "deleted": deleted
            }
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "DELETE_ERROR", "message": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "DELETE_PROFILE_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/ai-model-profiles/<key>/default', methods=['POST'])
@jwt_required()
@admin_required
def set_default_ai_model_profile(key: str):
    """
    Set a profile as the default.

    Path Parameters:
        key: Profile key to set as default

    Returns:
        Updated profile

    Example Response:
        {
            "success": true,
            "data": {
                "profile": {...},
                "message": "Profile set as default"
            }
        }
    """
    try:
        profile = AiModelProfilesService.set_default_profile(key)

        return jsonify({
            "success": True,
            "data": {
                "profile": profile,
                "message": "Profile set as default"
            }
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": {"code": "SET_DEFAULT_ERROR", "message": str(e)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "SET_DEFAULT_PROFILE_ERROR", "message": str(e)}
        }), 500


@api_v1.route('/admin/ai-model-profiles/models-by-category', methods=['GET'])
@jwt_required()
@admin_required
def get_models_by_category():
    """
    Get available models grouped by category.

    Returns:
        Models grouped by category for profile editing UI

    Example Response:
        {
            "success": true,
            "data": {
                "categories": {
                    "chat": [
                        {"model_id": "gpt-4o", "display_name": "GPT-4o", ...}
                    ],
                    "reasoning": [...],
                    ...
                }
            }
        }
    """
    try:
        categories = AiModelProfilesService.get_available_models_by_category()

        return jsonify({
            "success": True,
            "data": {"categories": categories}
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "GET_MODELS_ERROR", "message": str(e)}
        }), 500
