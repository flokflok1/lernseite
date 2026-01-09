"""
Lesson Video Configuration Endpoints

Provides endpoints for:
- GET /api/v1/video/avatar-styles - Available avatar styles
- GET /api/v1/video/sora-status - Sora 2 API status
- GET /api/v1/video/models - Available Sora models comparison

Configuration and metadata endpoints for video generation system.
"""

from flask import Blueprint, jsonify
from app.middleware.auth import token_required
import logging

logger = logging.getLogger(__name__)


# Blueprint for video configuration
video_config_bp = Blueprint(
    'lesson_video_config',
    __name__
)


@video_config_bp.route('/video/avatar-styles', methods=['GET'])
def get_avatar_styles():
    """
    Get available avatar styles for video generation.

    Response:
    {
        "success": true,
        "data": {
            "styles": {
                "professional_teacher": {
                    "name": "Professional Teacher",
                    "description": "A professional male teacher...",
                    "thumbnail": "/assets/avatars/professional_teacher.png"
                },
                ...
            },
            "default": "professional_teacher"
        }
    }
    """
    from app.services.lesson_video_service import LessonVideoService

    styles = {}
    for style_key, style_info in LessonVideoService.AVATAR_STYLES.items():
        styles[style_key] = {
            'name': style_key.replace('_', ' ').title(),
            'description': style_info['description'],
            'thumbnail': f'/assets/avatars/{style_key}.png'
        }

    return jsonify({
        'success': True,
        'data': {
            'styles': styles,
            'default': 'professional_teacher'
        }
    })


@video_config_bp.route('/video/sora-status', methods=['GET'])
@token_required
def get_sora_status():
    """
    Check Sora 2 API status and get model information.

    Response:
    {
        "success": true,
        "data": {
            "sora_available": true,
            "models": {
                "sora-2": { ... },
                "sora-2-pro": { ... }
            },
            "default_model": "sora-2",
            "features": {
                "video": true,
                "audio": true,
                "synced_audio": true
            }
        }
    }
    """
    from app.services.lesson_video_service import LessonVideoService

    models = LessonVideoService.get_available_models()
    comparison = LessonVideoService.compare_models()

    # TODO: Actually check API availability
    # For now, assume it's available since Sora 2 is released
    sora_available = True

    return jsonify({
        'success': True,
        'data': {
            'sora_available': sora_available,
            'models': models,
            'default_model': comparison['default'],
            'recommendation': comparison['recommendation'],
            'features': {
                'video': True,
                'audio': True,
                'synced_audio': True,  # Sora 2 generates synced audio!
                'input_types': ['text', 'image'],
                'output_types': ['video', 'audio']
            },
            'message': 'Sora 2 generates video WITH synchronized audio - no separate TTS needed!'
        }
    })


@video_config_bp.route('/video/models', methods=['GET'])
def get_video_models():
    """
    Get available Sora video models for comparison.

    Response:
    {
        "success": true,
        "data": {
            "models": {
                "sora-2": {
                    "name": "Sora 2",
                    "description": "Flagship video generation with synced audio",
                    "performance": "higher",
                    "speed": "slow",
                    "cost_per_second": 0.10,
                    "max_duration": 60
                },
                "sora-2-pro": {
                    "name": "Sora 2 Pro",
                    "description": "Premium quality...",
                    "performance": "highest",
                    "speed": "slower",
                    "cost_per_second": 0.20,
                    "max_duration": 120
                }
            },
            "default": "sora-2",
            "recommendation": { ... }
        }
    }
    """
    from app.services.lesson_video_service import LessonVideoService

    return jsonify({
        'success': True,
        'data': LessonVideoService.compare_models()
    })
