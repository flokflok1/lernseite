"""
LernsystemX Lesson Videos API - Consolidated

Lesson video generation and playback with Sora 2.

Video Operations:
- GET /lessons/:lesson_id/video - Get or check video
- POST /lessons/:lesson_id/video - Generate video with Sora 2
- GET /lessons/:lesson_id/video/status - Check generation status
- DELETE /lessons/:lesson_id/video - Delete cached video
- GET /lessons/:lesson_id/audio - Get audio track

Video Configuration:
- GET /video/avatar-styles - Available avatar styles
- GET /video/sora-status - Sora 2 API status
- GET /video/models - Available Sora models comparison

Sora 2 generates VIDEO + AUDIO together (synced!), no separate TTS needed.

All routes: /api/v1/lessons/*, /api/v1/video/*
ISO 9001:2015 compliant - Content Management Layer
"""

from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
import logging
import asyncio

from app.middleware.auth import token_required
from app.database.connection import fetch_one

# Blueprint
lesson_videos_bp = Blueprint('lesson_videos', __name__, url_prefix='')

__all__ = ['lesson_videos_bp']

logger = logging.getLogger(__name__)


# =============================================================================
# VIDEO OPERATIONS - CORE ENDPOINTS
# =============================================================================

@lesson_videos_bp.route('/lessons/<lesson_id>/video', methods=['GET'])
@token_required
def get_lesson_video(lesson_id: str):
    """
    Get cached lesson video or return generation status.

    URL Params:
        lesson_id: UUID of the lesson

    Query Params:
        format: Video format (mp4, webm) - default: mp4

    Response:
        Video file if cached, or JSON with status
    """
    try:
        from app.services.lesson_video import LessonVideoService

        # Check for cached video
        cached = LessonVideoService.get_cached_video(lesson_id)

        if cached and cached.get('status') == 'ready':
            video_path = cached.get('storage_path')

            if video_path and Path(video_path).exists():
                return send_file(
                    video_path,
                    mimetype='video/mp4',
                    as_attachment=False
                )

        # No cached video - return status
        status = LessonVideoService.get_generation_status(lesson_id)

        return jsonify({
            'success': True,
            'data': {
                'has_video': False,
                'status': status.get('status', 'not_generated'),
                'progress': status.get('progress', 0),
                'message': 'Video not yet generated. Use POST to trigger generation.'
            }
        })

    except Exception as e:
        logger.error(f"Error getting lesson video: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'VIDEO_ERROR',
                'message': str(e)
            }
        }), 500


@lesson_videos_bp.route('/lessons/<lesson_id>/video', methods=['POST'])
@token_required
def generate_lesson_video(lesson_id: str):
    """
    Generate a lesson explanation video with Sora 2.

    Sora 2 generates VIDEO + AUDIO together (synced!),
    so no separate TTS is needed.

    URL Params:
        lesson_id: UUID of the lesson

    Request Body:
        {
            "lesson_title": "Bezugskalkulation",
            "teaching_steps": [
                {
                    "speech": "Willkommen zur Bezugskalkulation...",
                    "whiteboard": [
                        {"type": "write", "content": "Listeneinkaufspreis", ...}
                    ],
                    "animation": {"type": "gesture", ...}
                },
                ...
            ],
            "avatar_style": "professional_teacher",  // optional
            "model": "sora-2",                       // optional: "sora-2" or "sora-2-pro"
            "language": "de",                        // optional: language for speech
            "force_regenerate": false                // optional
        }

    Response:
        200: {
            "success": true,
            "data": {
                "video_id": "uuid",
                "video_url": "...",              // Video includes synced audio!
                "model": "sora-2",
                "has_audio": true,
                "status": "ready" | "generating" | "fallback_mode",
                "from_cache": false,
                "duration_ms": 120000,
                "cost": 12.00
            }
        }
    """
    try:
        from app.services.lesson_video import LessonVideoService

        data = request.get_json() or {}

        lesson_title = data.get('lesson_title', 'Lektion')
        teaching_steps = data.get('teaching_steps', [])
        avatar_style = data.get('avatar_style', 'professional_teacher')
        model = data.get('model', 'sora-2')  # sora-2 or sora-2-pro
        language = data.get('language', 'de')
        force_regenerate = data.get('force_regenerate', False)

        if not teaching_steps:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_STEPS',
                    'message': 'teaching_steps are required'
                }
            }), 400

        # Validate model
        available_models = LessonVideoService.get_available_models()
        if model not in available_models:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_MODEL',
                    'message': f'Invalid model. Available: {", ".join(available_models.keys())}'
                }
            }), 400

        # Generate video (async)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                LessonVideoService.generate_lesson_video(
                    lesson_id=lesson_id,
                    lesson_title=lesson_title,
                    teaching_steps=teaching_steps,
                    avatar_style=avatar_style,
                    model=model,
                    language=language,
                    force_regenerate=force_regenerate
                )
            )
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"Error generating lesson video: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'GENERATION_ERROR',
                'message': str(e)
            }
        }), 500


@lesson_videos_bp.route('/lessons/<lesson_id>/video/status', methods=['GET'])
@token_required
def get_video_generation_status(lesson_id: str):
    """
    Get the status of video generation for a lesson.

    URL Params:
        lesson_id: UUID of the lesson

    Response:
        200: {
            "success": true,
            "data": {
                "status": "pending" | "generating" | "ready" | "failed",
                "progress": 0-100,
                "video_id": "uuid" or null,
                "error": null or "error message"
            }
        }
    """
    try:
        from app.services.lesson_video import LessonVideoService

        status = LessonVideoService.get_generation_status(lesson_id)

        return jsonify({
            'success': True,
            'data': status
        })

    except Exception as e:
        logger.error(f"Error getting video status: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'STATUS_ERROR',
                'message': str(e)
            }
        }), 500


@lesson_videos_bp.route('/lessons/<lesson_id>/video', methods=['DELETE'])
@token_required
def delete_lesson_video(lesson_id: str):
    """
    Delete cached video for a lesson.

    URL Params:
        lesson_id: UUID of the lesson

    Response:
        200: Video deleted successfully
        404: No cached video found
        500: Server error
    """
    try:
        from app.services.lesson_video import LessonVideoService

        deleted = LessonVideoService.delete_cached_video(lesson_id)

        if deleted:
            return jsonify({
                'success': True,
                'message': 'Video deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'No cached video found for this lesson'
                }
            }), 404

    except Exception as e:
        logger.error(f"Error deleting lesson video: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'DELETE_ERROR',
                'message': str(e)
            }
        }), 500


@lesson_videos_bp.route('/lessons/<lesson_id>/audio', methods=['GET'])
@token_required
def get_lesson_audio(lesson_id: str):
    """
    Get pre-generated audio track for a lesson.

    This is the TTS audio extracted from the video,
    useful for audio-only playback.

    URL Params:
        lesson_id: UUID of the lesson

    Response:
        Audio file (audio/mpeg or audio/wav)
    """
    try:
        # Look for cached audio
        query = """
            SELECT
                t.tts_id,
                m.storage_path,
                m.file_size_bytes,
                m.duration_ms
            FROM agent_tts_cache t
            JOIN agent_media_cache m ON t.media_id = m.media_id
            WHERE m.source_id = %s
              AND m.status = 'ready'
            ORDER BY m.created_at DESC
            LIMIT 1
        """

        result = fetch_one(query, (lesson_id,))

        if result and result.get('storage_path'):
            audio_path = result['storage_path']

            if Path(audio_path).exists():
                mimetype = 'audio/wav' if audio_path.endswith('.wav') else 'audio/mpeg'
                return send_file(
                    audio_path,
                    mimetype=mimetype,
                    as_attachment=False
                )

        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'No audio found for this lesson'
            }
        }), 404

    except Exception as e:
        logger.error(f"Error getting lesson audio: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AUDIO_ERROR',
                'message': str(e)
            }
        }), 500


# =============================================================================
# VIDEO CONFIGURATION - METADATA ENDPOINTS
# =============================================================================

@lesson_videos_bp.route('/video/avatar-styles', methods=['GET'])
def get_avatar_styles():
    """
    Get available avatar styles for video generation.

    Response:
        200: {
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
    from app.services.lesson_video import LessonVideoService

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


@lesson_videos_bp.route('/video/sora-status', methods=['GET'])
@token_required
def get_sora_status():
    """
    Check Sora 2 API status and get model information.

    Response:
        200: {
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
    from app.services.lesson_video import LessonVideoService

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


@lesson_videos_bp.route('/video/models', methods=['GET'])
def get_video_models():
    """
    Get available Sora video models for comparison.

    Response:
        200: {
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
    from app.services.lesson_video import LessonVideoService

    return jsonify({
        'success': True,
        'data': LessonVideoService.compare_models()
    })
