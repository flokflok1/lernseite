"""
LernsystemX Agent API - Media Endpoints

Media cache and serving endpoints:
- GET    /api/v1/agents/:course_id/media/stats - Get media cache statistics
- GET    /api/v1/media/tts/:media_id           - Serve cached TTS audio

ISO 9001:2015 compliant - Agent Media Layer
Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

import os
from flask import Blueprint, jsonify, send_file

from app.services.media_cache_service import MediaCacheService
from app.repositories.agent import AgentRepository
from app.middleware.auth import token_required

from app.api.system_features.agents._helpers import error_response

# Blueprint for media endpoints (agents-related)
agents_media_bp = Blueprint('agents_media', __name__, url_prefix='/agents')

# Blueprint for general media serving (non-agent prefix)
media_bp = Blueprint('media', __name__, url_prefix='/media')


@agents_media_bp.route('/<course_id>/media/stats', methods=['GET'])
@token_required
def get_agent_media_stats(course_id: str):
    """
    Get media cache statistics for a course agent

    Response:
        200: {
            tts_cached: int,
            tts_accesses: int,
            videos_cached: int,
            transcripts_cached: int,
            total_storage_mb: float,
            estimated_savings_eur: float
        }
    """
    try:
        agent = AgentRepository.get_agent_by_course(course_id)
        if not agent:
            return jsonify({
                'success': True,
                'data': {
                    'tts_cached': 0,
                    'videos_cached': 0,
                    'transcripts_cached': 0,
                    'total_storage_mb': 0,
                    'estimated_savings_eur': 0
                }
            }), 200

        stats = MediaCacheService.get_cache_stats(agent['agent_id'])

        return jsonify({
            'success': True,
            'data': stats
        }), 200

    except Exception as e:
        return error_response('Failed to get media stats', details=str(e))


@media_bp.route('/tts/<media_id>', methods=['GET'])
@token_required
def serve_tts_audio(media_id: str):
    """
    Serve cached TTS audio file

    Response:
        200: Audio file (audio/mpeg)
        404: Media not found
    """
    try:
        # Get media path from database
        from app.services.media_cache_service import MediaCacheRepository

        query = """
            SELECT storage_path, mime_type
            FROM agent_media_cache
            WHERE media_id = %s AND status = 'ready'
        """
        result = MediaCacheRepository.fetch_one(query, (media_id,))

        if not result or not os.path.exists(result['storage_path']):
            return error_response('Media not found', code=404)

        return send_file(
            result['storage_path'],
            mimetype=result.get('mime_type', 'audio/mpeg'),
            as_attachment=False
        )

    except Exception as e:
        return error_response('Failed to serve media', details=str(e))
