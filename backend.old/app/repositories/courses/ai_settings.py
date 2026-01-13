"""
LernsystemX Course AI Settings Repository

Database operations for course-specific AI model configuration.
Each course can override default models via profile or individual model IDs.

Model Categories:
- chat_model_id: Chat/text generation
- reasoning_model_id: Prüfungen/Reasoning (o3, o1, etc.)
- image_model_id: Image generation
- audio_model_id: TTS/STT
- realtime_model_id: Realtime audio
- embedding_model_id: Embeddings

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Repository layer
"""

from typing import Dict, Optional, List
from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all


class CourseAiSettingsRepository(BaseRepository):
    """
    Repository for course_ai_settings table.

    Manages course-specific AI model configurations.
    NULL values mean use system defaults from the default profile.
    """

    table_name = 'courses.course_ai_settings'
    pk_column = 'id'

    # Valid model type columns
    MODEL_TYPES = [
        'chat_model_id',
        'reasoning_model_id',
        'image_model_id',
        'audio_model_id',
        'realtime_model_id',
        'embedding_model_id'
    ]

    @classmethod
    def find_by_course_id(cls, course_id: str) -> Optional[Dict]:
        """
        Get AI settings for a specific course.

        Args:
            course_id: Course UUID

        Returns:
            Settings dict or None if no custom settings

        Example:
            >>> settings = CourseAiSettingsRepository.find_by_course_id('abc-123')
            >>> print(settings['chat_model_id'])  # 'gpt-4o' or None
        """
        query = """
            SELECT *
            FROM courses.course_ai_settings
            WHERE course_id = %s
        """
        return fetch_one(query, (course_id,))

    @classmethod
    def find_with_course_info(cls, course_id: str) -> Optional[Dict]:
        """
        Get AI settings with course title.

        Args:
            course_id: Course UUID

        Returns:
            Settings with course info or None

        Example:
            >>> settings = CourseAiSettingsRepository.find_with_course_info('abc-123')
            >>> print(settings['course_title'], settings['chat_model_id'])
        """
        query = """
            SELECT
                cas.*,
                c.title as course_title
            FROM courses.course_ai_settings cas
            JOIN courses.courses c ON c.course_id = cas.course_id
            WHERE cas.course_id = %s
        """
        return fetch_one(query, (course_id,))

    @classmethod
    def find_with_profile(cls, course_id: str) -> Optional[Dict]:
        """
        Get AI settings with profile information.

        Args:
            course_id: Course UUID

        Returns:
            Settings with profile info joined

        Example:
            >>> settings = CourseAiSettingsRepository.find_with_profile('abc-123')
            >>> print(settings['profile_name'])
        """
        query = """
            SELECT
                cas.*,
                c.title as course_title,
                amp.name as profile_name,
                amp.description as profile_description
            FROM courses.course_ai_settings cas
            JOIN courses.courses c ON c.course_id = cas.course_id
            LEFT JOIN ai_pipeline.ai_model_profiles amp ON amp.key = cas.profile_key
            WHERE cas.course_id = %s
        """
        return fetch_one(query, (course_id,))

    @classmethod
    def upsert(
        cls,
        course_id: str,
        profile_key: Optional[str] = None,
        chat_model_id: Optional[str] = None,
        reasoning_model_id: Optional[str] = None,
        image_model_id: Optional[str] = None,
        audio_model_id: Optional[str] = None,
        realtime_model_id: Optional[str] = None,
        embedding_model_id: Optional[str] = None,
        additional_settings: Optional[Dict] = None
    ) -> Dict:
        """
        Create or update AI settings for a course.

        Args:
            course_id: Course UUID
            profile_key: Reference to ai_model_profiles.key
            chat_model_id: Chat/text model ID (None = use profile/default)
            reasoning_model_id: Reasoning model ID
            image_model_id: Image model ID
            audio_model_id: Audio/TTS model ID
            realtime_model_id: Realtime model ID
            embedding_model_id: Embedding model ID
            additional_settings: JSONB for future extensions

        Returns:
            Created or updated settings

        Example:
            >>> settings = CourseAiSettingsRepository.upsert(
            ...     course_id='abc-123',
            ...     profile_key='quality',
            ...     chat_model_id='gpt-4o'
            ... )
        """
        query = """
            INSERT INTO course_ai_settings (
                course_id, profile_key,
                chat_model_id, reasoning_model_id, image_model_id,
                audio_model_id, realtime_model_id, embedding_model_id,
                additional_settings
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (course_id) DO UPDATE SET
                profile_key = EXCLUDED.profile_key,
                chat_model_id = EXCLUDED.chat_model_id,
                reasoning_model_id = EXCLUDED.reasoning_model_id,
                image_model_id = EXCLUDED.image_model_id,
                audio_model_id = EXCLUDED.audio_model_id,
                realtime_model_id = EXCLUDED.realtime_model_id,
                embedding_model_id = EXCLUDED.embedding_model_id,
                additional_settings = EXCLUDED.additional_settings,
                updated_at = NOW()
            RETURNING *
        """
        import json
        additional_json = json.dumps(additional_settings) if additional_settings else '{}'

        return fetch_one(query, (
            course_id,
            profile_key,
            chat_model_id,
            reasoning_model_id,
            image_model_id,
            audio_model_id,
            realtime_model_id,
            embedding_model_id,
            additional_json
        ))

    @classmethod
    def apply_profile(cls, course_id: str, profile_key: str, profile: Dict) -> Dict:
        """
        Apply a profile to a course (copy all model IDs from profile).

        Args:
            course_id: Course UUID
            profile_key: Profile key being applied
            profile: Profile dict with model IDs

        Returns:
            Updated course settings

        Example:
            >>> profile = AiModelProfilesRepository.find_by_key('quality')
            >>> settings = CourseAiSettingsRepository.apply_profile('abc-123', 'quality', profile)
        """
        return cls.upsert(
            course_id=course_id,
            profile_key=profile_key,
            chat_model_id=profile.get('chat_model_id'),
            reasoning_model_id=profile.get('reasoning_model_id'),
            image_model_id=profile.get('image_model_id'),
            audio_model_id=profile.get('audio_model_id'),
            realtime_model_id=profile.get('realtime_model_id'),
            embedding_model_id=profile.get('embedding_model_id')
        )

    @classmethod
    def delete_by_course_id(cls, course_id: str) -> bool:
        """
        Delete AI settings for a course (reset to defaults).

        Args:
            course_id: Course UUID

        Returns:
            True if deleted, False if not found

        Example:
            >>> CourseAiSettingsRepository.delete_by_course_id('abc-123')
            True
        """
        result = cls.delete_by(course_id=course_id)
        return result is not None

    @classmethod
    def find_all_with_course_info(
        cls,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get all course AI settings with course info.

        Args:
            limit: Maximum results
            offset: Skip count

        Returns:
            List of settings with course info

        Example:
            >>> all_settings = CourseAiSettingsRepository.find_all_with_course_info()
        """
        query = """
            SELECT
                cas.*,
                c.title as course_title,
                c.status as course_status,
                amp.name as profile_name
            FROM courses.course_ai_settings cas
            JOIN courses.courses c ON c.course_id = cas.course_id
            LEFT JOIN ai_pipeline.ai_model_profiles amp ON amp.key = cas.profile_key
            ORDER BY c.title
            LIMIT %s OFFSET %s
        """
        return fetch_all(query, (limit, offset))

    @classmethod
    def get_effective_model(
        cls,
        course_id: str,
        model_type: str,
        default: str
    ) -> str:
        """
        Get effective model for a course (course setting or default).

        Args:
            course_id: Course UUID
            model_type: One of the MODEL_TYPES columns
            default: Default model if no course setting

        Returns:
            Model identifier string

        Example:
            >>> model = CourseAiSettingsRepository.get_effective_model(
            ...     'abc-123', 'chat_model_id', 'gpt-4o'
            ... )
        """
        if model_type not in cls.MODEL_TYPES:
            raise ValueError(f"Invalid model_type: {model_type}. Must be one of {cls.MODEL_TYPES}")

        settings = cls.find_by_course_id(course_id)
        if settings and settings.get(model_type):
            return settings[model_type]
        return default

    @classmethod
    def count_courses_with_settings(cls) -> int:
        """
        Count courses that have custom AI settings.

        Returns:
            Count of courses with custom settings
        """
        query = """
            SELECT COUNT(*) as count
            FROM course_ai_settings
        """
        result = fetch_one(query)
        return result['count'] if result else 0

    @classmethod
    def count_by_profile(cls, profile_key: str) -> int:
        """
        Count courses using a specific profile.

        Args:
            profile_key: Profile key

        Returns:
            Count of courses using this profile
        """
        query = """
            SELECT COUNT(*) as count
            FROM courses.course_ai_settings
            WHERE profile_key = %s
        """
        result = fetch_one(query, (profile_key,))
        return result['count'] if result else 0
