"""
LernsystemX Lesson Video Generation Service

Generates and caches high-quality lesson explanation videos using:
- Sora 2 / Sora 2 Pro for video WITH synced audio (all-in-one!)
- Video caching for repeated playback

Sora 2 generates both video AND synchronized audio together,
so no separate TTS needed!

Each lesson gets a pre-generated video that can be replayed without
regenerating. Videos are stored in agent_media_cache and agent_video_cache.

Usage:
    from app.services.lesson_video_service import LessonVideoService

    # Generate a lesson video with sora-2 (default) or sora-2-pro
    video = await LessonVideoService.generate_lesson_video(
        lesson_id="uuid",
        lesson_title="Bezugskalkulation",
        teaching_steps=[...],
        avatar_style="professional_teacher",
        model="sora-2"  # or "sora-2-pro" for higher quality
    )

    # Get cached video
    video = LessonVideoService.get_cached_video(lesson_id)
"""

import os
import uuid
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout

from app.services.ai_adapter import AIAdapter, AIProviderError, AITimeoutError


class VideoGenerationError(Exception):
    """Raised when video generation fails"""
    pass


class LessonVideoService:
    """
    Service for generating and caching lesson explanation videos.

    Uses Sora 2 for video + audio generation (synced together).
    Videos are cached and can be replayed without regeneration.
    """

    # OpenAI Sora 2 API endpoint
    SORA_API_URL = 'https://api.openai.com/v1/videos/generations'

    # Available Sora models
    SORA_MODELS = {
        'sora-2': {
            'name': 'Sora 2',
            'description': 'Flagship video generation with synced audio',
            'performance': 'higher',
            'speed': 'slow',
            'input': ['text', 'image'],
            'output': ['video', 'audio'],
            'cost_per_second': 0.10,  # Estimated
            'max_duration': 60
        },
        'sora-2-pro': {
            'name': 'Sora 2 Pro',
            'description': 'Premium quality video generation with synced audio',
            'performance': 'highest',
            'speed': 'slower',
            'input': ['text', 'image'],
            'output': ['video', 'audio'],
            'cost_per_second': 0.20,  # Estimated - higher quality
            'max_duration': 120
        }
    }

    # Default model
    DEFAULT_MODEL = 'sora-2'

    # Video generation settings
    DEFAULT_RESOLUTION = '1080p'
    DEFAULT_FRAMERATE = 30

    # Avatar styles for Sora video prompts
    AVATAR_STYLES = {
        'professional_teacher': {
            'name': 'Professioneller Lehrer',
            'description': 'A professional male teacher in his 40s with glasses, wearing a blue dress shirt and brown vest, standing in front of a classic green chalkboard in a well-lit classroom',
            'voice_style': 'warm, clear German male voice, professional but friendly tone',
            'gestures': 'uses natural hand gestures while explaining, occasionally points to the chalkboard',
            'expression': 'friendly and encouraging, maintains eye contact'
        },
        'female_instructor': {
            'name': 'Dozentin',
            'description': 'A professional female instructor in her 30s with a warm smile, wearing smart casual attire, standing in a modern classroom with a whiteboard',
            'voice_style': 'clear, confident German female voice, engaging and encouraging',
            'gestures': 'animated hand movements while explaining concepts, writes on whiteboard',
            'expression': 'enthusiastic and approachable'
        },
        'casual_tutor': {
            'name': 'Lockerer Tutor',
            'description': 'A young casual tutor in their 20s, wearing a polo shirt, in a cozy study room with bookshelves',
            'voice_style': 'relaxed, friendly German voice, conversational tone like talking to a friend',
            'gestures': 'relaxed and conversational, uses casual hand gestures',
            'expression': 'friendly peer, nodding encouragingly'
        },
        'animated_expert': {
            'name': 'Animierter Experte',
            'description': 'A Pixar-style 3D animated character, friendly expert with expressive features, in a colorful educational environment',
            'voice_style': 'energetic, clear German voice with enthusiasm',
            'gestures': 'expressive animated movements, points and gestures dynamically',
            'expression': 'highly expressive, engaging cartoon-style emotions'
        }
    }

    @staticmethod
    def _get_api_key() -> str:
        """Get OpenAI API key from database or environment"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            try:
                from app.repositories.ai_provider_repository import AIProviderRepository
                api_key = AIProviderRepository.get_decrypted_api_key('openai')
            except Exception:
                pass

        if not api_key:
            raise AIProviderError('OpenAI API key not configured')

        return api_key

    @staticmethod
    def _generate_content_hash(
        lesson_id: str,
        teaching_steps: List[Dict],
        avatar_style: str,
        model: str
    ) -> str:
        """Generate a unique hash for the lesson content"""
        content = json.dumps({
            'lesson_id': lesson_id,
            'steps': teaching_steps,
            'avatar': avatar_style,
            'model': model
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    @classmethod
    def get_available_models(cls) -> Dict[str, Any]:
        """
        Get available Sora models with their specifications.

        Returns:
            Dictionary of model info
        """
        return cls.SORA_MODELS

    @classmethod
    def generate_video_prompt(
        cls,
        lesson_title: str,
        speech_text: str,
        whiteboard_content: str,
        avatar_style: str = 'professional_teacher',
        language: str = 'de'
    ) -> str:
        """
        Generate a Sora 2 video prompt for a teaching step.

        Sora 2 generates BOTH video AND synced audio, so we include
        voice instructions in the prompt.

        Args:
            lesson_title: Title of the lesson
            speech_text: What the teacher should say (will be spoken!)
            whiteboard_content: What should be written on the board
            avatar_style: Style of the avatar teacher
            language: Language for speech (default: German)

        Returns:
            Sora 2 prompt string
        """
        style = cls.AVATAR_STYLES.get(avatar_style, cls.AVATAR_STYLES['professional_teacher'])

        # Language-specific instructions
        lang_instruction = 'German' if language == 'de' else language.capitalize()

        prompt = f"""
Generate a professional educational video with synchronized audio:

=== VISUAL SCENE ===
SETTING: {style['description']}
TEACHER ACTIONS: {style['gestures']}
FACIAL EXPRESSION: {style['expression']}

CHALKBOARD/WHITEBOARD CONTENT:
{whiteboard_content if whiteboard_content else '(Empty board, teacher explains verbally)'}

TOPIC: {lesson_title}

=== AUDIO/SPEECH ===
The teacher speaks the following text in {lang_instruction}:
"{speech_text}"

VOICE STYLE: {style['voice_style']}

=== PRODUCTION QUALITY ===
- Style: High-quality, photorealistic (or Pixar-style if animated avatar)
- Camera: Medium shot with slight natural movement
- Lighting: Warm, well-lit classroom environment
- Audio: Clear speech, no background noise, professional recording quality
- Lip-sync: Perfect synchronization between speech and mouth movements

The video should look like a professional online learning platform (similar to Studyflix or Khan Academy).
"""
        return prompt.strip()

    @classmethod
    async def generate_sora_video(
        cls,
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
        if model not in cls.SORA_MODELS:
            model = cls.DEFAULT_MODEL

        model_info = cls.SORA_MODELS[model]
        resolution = resolution or cls.DEFAULT_RESOLUTION

        # Validate duration
        max_duration = model_info['max_duration']
        duration_seconds = min(duration_seconds, max_duration)

        api_key = cls._get_api_key()

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
                cls.SORA_API_URL,
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

    @classmethod
    def get_cached_video(cls, lesson_id: str, model: str = None) -> Optional[Dict[str, Any]]:
        """
        Get cached video for a lesson if it exists.

        Args:
            lesson_id: UUID of the lesson
            model: Optional model filter (sora-2 or sora-2-pro)

        Returns:
            Cached video info or None if not cached
        """
        try:
            from app.repositories.base_repository import BaseRepository

            query = """
                SELECT
                    v.video_id,
                    v.video_type,
                    v.resolution,
                    v.thumbnail_path,
                    v.render_time_ms,
                    v.generation_cost,
                    v.avatar_id as avatar_style,
                    m.storage_path,
                    m.file_size_bytes,
                    m.duration_ms,
                    m.status,
                    m.access_count,
                    m.generation_model as model,
                    m.created_at
                FROM agent_video_cache v
                JOIN agent_media_cache m ON v.media_id = m.media_id
                WHERE m.source_id = %s
                  AND m.status = 'ready'
            """

            params = [lesson_id]

            if model:
                query += " AND m.generation_model = %s"
                params.append(model)

            query += " ORDER BY m.created_at DESC LIMIT 1"

            result = BaseRepository.fetch_one(query, tuple(params))

            if result:
                # Update access count
                update_query = """
                    UPDATE agent_media_cache
                    SET access_count = access_count + 1,
                        last_accessed_at = NOW()
                    WHERE media_id = (
                        SELECT media_id FROM agent_video_cache WHERE video_id = %s
                    )
                """
                BaseRepository.execute(update_query, (result['video_id'],))

                return dict(result)

            return None

        except Exception as e:
            print(f'Error getting cached video: {e}')
            return None

    @classmethod
    def cache_video(
        cls,
        lesson_id: str,
        video_path: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Cache a generated video for a lesson.

        Args:
            lesson_id: UUID of the lesson
            video_path: Path to the video file (includes audio)
            metadata: Video metadata (duration, resolution, model, etc.)

        Returns:
            video_id of the cached video
        """
        try:
            from app.repositories.base_repository import BaseRepository

            media_id = str(uuid.uuid4())
            video_id = str(uuid.uuid4())
            content_hash = metadata.get('content_hash', hashlib.sha256(lesson_id.encode()).hexdigest())
            model = metadata.get('model', cls.DEFAULT_MODEL)

            # Insert into agent_media_cache
            media_query = """
                INSERT INTO agent_media_cache (
                    media_id, content_hash, media_type, source_type, source_id,
                    storage_path, file_size_bytes, duration_ms, generation_model,
                    generation_cost, status, quality_tier, never_expire
                ) VALUES (
                    %s, %s, 'video_explanation', 'lesson', %s,
                    %s, %s, %s, %s, %s, 'ready', 3, true
                )
            """

            BaseRepository.execute(media_query, (
                media_id,
                content_hash,
                lesson_id,
                video_path,
                metadata.get('file_size', 0),
                metadata.get('duration_ms', 0),
                model,
                metadata.get('cost', 0)
            ))

            # Insert into agent_video_cache
            video_query = """
                INSERT INTO agent_video_cache (
                    video_id, media_id, video_type, source_text,
                    avatar_id, avatar_provider, resolution, framerate,
                    render_time_ms, generation_cost
                ) VALUES (
                    %s, %s, 'explanation', %s,
                    %s, 'openai_sora', %s, %s, %s, %s
                )
            """

            BaseRepository.execute(video_query, (
                video_id,
                media_id,
                metadata.get('source_text', ''),
                metadata.get('avatar_style', 'professional_teacher'),
                metadata.get('resolution', '1080p'),
                metadata.get('framerate', 30),
                metadata.get('render_time_ms', 0),
                metadata.get('cost', 0)
            ))

            return video_id

        except Exception as e:
            raise VideoGenerationError(f'Failed to cache video: {str(e)}')

    @classmethod
    async def generate_lesson_video(
        cls,
        lesson_id: str,
        lesson_title: str,
        teaching_steps: List[Dict[str, Any]],
        avatar_style: str = 'professional_teacher',
        model: str = 'sora-2',
        force_regenerate: bool = False,
        language: str = 'de'
    ) -> Dict[str, Any]:
        """
        Generate a complete lesson video with Sora 2.

        Sora 2 generates video WITH synced audio, so everything
        comes out as one file - no separate TTS needed!

        Args:
            lesson_id: UUID of the lesson
            lesson_title: Title of the lesson
            teaching_steps: List of teaching step dictionaries with:
                - speech: Text the teacher speaks
                - whiteboard: List of whiteboard actions
                - animation: Teacher animation type
            avatar_style: Style of the teacher avatar
            model: Sora model ('sora-2' or 'sora-2-pro')
            force_regenerate: If True, regenerate even if cached
            language: Language for speech (default: 'de' for German)

        Returns:
            {
                'video_id': str,
                'video_url': str,       # Video includes audio!
                'duration_ms': int,
                'model': str,
                'from_cache': bool,
                'cost': float,
                'status': str
            }
        """
        # Validate model
        if model not in cls.SORA_MODELS:
            model = cls.DEFAULT_MODEL

        # Check cache first
        if not force_regenerate:
            cached = cls.get_cached_video(lesson_id, model)
            if cached:
                return {
                    'video_id': cached['video_id'],
                    'video_url': cached['storage_path'],
                    'duration_ms': cached['duration_ms'],
                    'model': cached.get('model', model),
                    'avatar_style': cached.get('avatar_style', avatar_style),
                    'from_cache': True,
                    'cost': 0,
                    'status': 'ready',
                    'has_audio': True
                }

        # Combine all speech texts for the full video
        all_speech_texts = []
        all_whiteboard_content = []

        for step in teaching_steps:
            speech_text = step.get('speech', '')
            if speech_text:
                all_speech_texts.append(speech_text)

            for action in step.get('whiteboard', []):
                if action.get('type') in ['write', 'highlight']:
                    content = action.get('content', '')
                    if content:
                        all_whiteboard_content.append(content)

        # Create combined prompt for the entire lesson
        combined_speech = ' '.join(all_speech_texts)
        combined_whiteboard = '\n'.join(all_whiteboard_content)

        # Estimate duration based on speech length (roughly 150 words per minute)
        word_count = len(combined_speech.split())
        estimated_duration = max(15, min(60, int((word_count / 150) * 60)))

        # For sora-2-pro, we can go longer
        if model == 'sora-2-pro':
            estimated_duration = max(15, min(120, int((word_count / 150) * 60)))

        # Generate the video prompt
        video_prompt = cls.generate_video_prompt(
            lesson_title=lesson_title,
            speech_text=combined_speech,
            whiteboard_content=combined_whiteboard,
            avatar_style=avatar_style,
            language=language
        )

        # Generate video with Sora (includes synced audio!)
        video_result = await cls.generate_sora_video(
            prompt=video_prompt,
            duration_seconds=estimated_duration,
            model=model
        )

        # Generate content hash for caching
        content_hash = cls._generate_content_hash(lesson_id, teaching_steps, avatar_style, model)

        result = {
            'lesson_id': lesson_id,
            'lesson_title': lesson_title,
            'video_id': video_result['video_id'],
            'video_url': video_result.get('video_url'),
            'duration_ms': video_result['duration_seconds'] * 1000,
            'model': model,
            'model_info': cls.SORA_MODELS[model],
            'avatar_style': avatar_style,
            'content_hash': content_hash,
            'has_audio': True,  # Sora 2 always includes synced audio
            'from_cache': False,
            'cost': video_result['cost'],
            'status': video_result['status']
        }

        # Handle different statuses
        if video_result['status'] == 'ready' and video_result.get('video_url'):
            # Success! Cache the video
            # In production: download video, save to storage, then cache
            result['message'] = 'Video generated successfully with synchronized audio'

        elif video_result['status'] == 'api_not_available':
            result['message'] = video_result.get('message', 'Sora 2 API not available. Using fallback rendering.')
            result['fallback'] = True

        elif video_result['status'] == 'api_error':
            result['message'] = video_result.get('error', 'API error occurred')
            result['error'] = video_result.get('error')

        elif video_result['status'] == 'timeout':
            result['message'] = 'Video generation timed out. Please try again.'
            result['error'] = 'timeout'

        return result

    @classmethod
    def get_generation_status(cls, lesson_id: str) -> Dict[str, Any]:
        """
        Get the status of video generation for a lesson.

        Args:
            lesson_id: UUID of the lesson

        Returns:
            {
                'status': 'pending' | 'generating' | 'ready' | 'failed',
                'progress': 0-100,
                'video_id': str or None,
                'model': str or None,
                'error': str or None
            }
        """
        cached = cls.get_cached_video(lesson_id)

        if cached:
            return {
                'status': cached.get('status', 'ready'),
                'progress': 100,
                'video_id': cached['video_id'],
                'model': cached.get('model'),
                'has_audio': True,
                'error': None
            }

        # Check if generation is in progress (would check job queue in production)
        return {
            'status': 'pending',
            'progress': 0,
            'video_id': None,
            'model': None,
            'has_audio': None,
            'error': None
        }

    @classmethod
    def delete_cached_video(cls, lesson_id: str, model: str = None) -> bool:
        """
        Delete cached video for a lesson.

        Args:
            lesson_id: UUID of the lesson
            model: Optional - delete only for specific model

        Returns:
            True if deleted, False if not found
        """
        try:
            from app.repositories.base_repository import BaseRepository

            query = """
                DELETE FROM agent_media_cache
                WHERE source_id = %s
                  AND source_type = 'lesson'
                  AND media_type = 'video_explanation'
            """
            params = [lesson_id]

            if model:
                query += " AND generation_model = %s"
                params.append(model)

            result = BaseRepository.execute(query, tuple(params))
            return result > 0

        except Exception as e:
            print(f'Error deleting cached video: {e}')
            return False

    @classmethod
    def compare_models(cls) -> Dict[str, Any]:
        """
        Compare available Sora models.

        Returns:
            Comparison information for UI selection
        """
        return {
            'models': cls.SORA_MODELS,
            'default': cls.DEFAULT_MODEL,
            'recommendation': {
                'for_quick_preview': 'sora-2',
                'for_production': 'sora-2-pro',
                'description': 'sora-2 is faster and cheaper, sora-2-pro has higher quality'
            }
        }
