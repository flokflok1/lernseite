"""
Sora 2 video generation module.

Handles low-level video generation API calls to OpenAI Sora 2.
"""

import uuid
from typing import Dict, Any

import requests
from requests.exceptions import RequestException, Timeout

from app.application.services.content.lesson_video.models import SORA_MODELS, DEFAULT_MODEL, SORA_API_URL
from app.application.services.content.lesson_video.helpers import get_api_key


class SoraVideoGenerator:
    """Handles Sora 2 API video generation requests."""

    @staticmethod
    def get_available_models() -> Dict[str, Any]:
        """
        Get available Sora models with specifications.

        Returns:
            Dictionary of model info keyed by model name
        """
        return SORA_MODELS

    @staticmethod
    async def generate_sora_video(
        prompt: str,
        duration_seconds: int = 15,
        resolution: str = None,
        model: str = 'sora-2'
    ) -> Dict[str, Any]:
        """
        Generate video with synced audio using OpenAI Sora 2.

        Sora 2 outputs BOTH video AND audio together!

        Args:
            prompt: Video generation prompt (includes speech text)
            duration_seconds: Video duration (5-60s for sora-2, up to 120s for pro)
            resolution: Video resolution (720p, 1080p, 4k)
            model: Sora model ('sora-2' or 'sora-2-pro')

        Returns:
            {
                'video_url': str,         # URL to video file (includes audio!)
                'video_id': str,
                'duration_seconds': int,
                'resolution': str,
                'model': str,
                'has_audio': True,        # Sora 2 always includes audio
                'generation_time_ms': int,
                'cost': float,
                'status': str
            }
        """
        # Validate model
        if model not in SORA_MODELS:
            model = DEFAULT_MODEL

        model_info = SORA_MODELS[model]
        resolution = resolution or '1080p'

        # Validate duration against model limits
        max_duration = model_info['max_duration']
        duration_seconds = min(duration_seconds, max_duration)

        api_key = get_api_key()

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'prompt': prompt,
            'duration': duration_seconds,
            'resolution': resolution,
            'output': ['video', 'audio'],  # Request both video and audio
            'style': 'photorealistic'
        }

        # Calculate estimated cost
        cost = duration_seconds * model_info['cost_per_second']

        try:
            response = requests.post(
                SORA_API_URL,
                headers=headers,
                json=payload,
                timeout=600  # 10 minutes - video generation takes time
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'video_url': data.get('video_url') or data.get('url'),
                    'video_id': data.get('id', str(uuid.uuid4())),
                    'duration_seconds': duration_seconds,
                    'resolution': resolution,
                    'model': model,
                    'has_audio': True,
                    'generation_time_ms': data.get('generation_time_ms', 0),
                    'cost': data.get('cost', cost),
                    'status': 'ready'
                }

            # API error - return with error status
            error_msg = f'Sora API error: {response.status_code}'
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except Exception:
                pass

            return {
                'video_url': None,
                'video_id': str(uuid.uuid4()),
                'duration_seconds': duration_seconds,
                'resolution': resolution,
                'model': model,
                'has_audio': True,
                'generation_time_ms': 0,
                'cost': 0,
                'status': 'api_error',
                'error': error_msg
            }

        except Timeout:
            return {
                'video_url': None,
                'video_id': str(uuid.uuid4()),
                'duration_seconds': duration_seconds,
                'resolution': resolution,
                'model': model,
                'has_audio': True,
                'generation_time_ms': 0,
                'cost': 0,
                'status': 'timeout',
                'error': 'Video generation timed out'
            }

        except RequestException as e:
            # API not available yet - return placeholder for fallback
            return {
                'video_url': None,
                'video_id': str(uuid.uuid4()),
                'duration_seconds': duration_seconds,
                'resolution': resolution,
                'model': model,
                'has_audio': True,
                'generation_time_ms': 0,
                'cost': cost,
                'status': 'api_not_available',
                'message': f'Sora 2 API request failed: {str(e)}. Using fallback rendering.'
            }
