"""
LernsystemX Course AI Settings Service

Business logic for course-specific AI model configuration:
- Get/set AI models per course (all 6 categories)
- Apply global profiles to courses
- Resolve effective models (course → profile → system default)

Model Categories:
- chat_model_id: Chat/text generation
- reasoning_model_id: Prüfungen/Reasoning (o3, o1)
- image_model_id: Image generation
- audio_model_id: TTS/STT
- realtime_model_id: Realtime audio
- embedding_model_id: Embeddings

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Service layer
"""

from typing import Dict, Optional, List, Any
from flask import current_app

from app.infrastructure.persistence.repositories.courses.ai_settings import CourseAiSettingsRepository
from app.infrastructure.persistence.repositories.ai.profiles import AiModelProfilesRepository
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.cache.service import CacheService


class CourseAiSettingsService:
    """
    Service layer for course AI settings.

    Implements business logic for AI model configuration per course.
    Provides fallback chain: Course Setting → Profile → System Default.
    """

    # Model type constants (matching repository)
    MODEL_TYPES = CourseAiSettingsRepository.MODEL_TYPES

    @classmethod
    def get_settings(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Get AI settings for a course with profile info.

        Args:
            course_id: Course UUID

        Returns:
            Settings dict with profile info or None

        Example:
            >>> settings = CourseAiSettingsService.get_settings('abc-123')
        """
        return CourseAiSettingsRepository.find_with_profile(course_id)

    @classmethod
    def get_or_create_settings(cls, course_id: str) -> Dict[str, Any]:
        """
        Get AI settings or create with default profile.

        Args:
            course_id: Course UUID

        Returns:
            Settings dict (existing or newly created with default profile)

        Example:
            >>> settings = CourseAiSettingsService.get_or_create_settings('abc-123')
        """
        existing = cls.get_settings(course_id)
        if existing:
            return existing

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise ValueError(f"Course not found: {course_id}")

        # Get default profile and apply it
        default_profile = AiModelProfilesRepository.find_default()
        if default_profile:
            return cls.apply_profile(course_id, default_profile['key'])

        # No default profile - create empty settings
        return CourseAiSettingsRepository.upsert(course_id=course_id)

    @classmethod
    def update_settings(
        cls,
        course_id: str,
        chat_model_id: Optional[str] = None,
        reasoning_model_id: Optional[str] = None,
        image_model_id: Optional[str] = None,
        audio_model_id: Optional[str] = None,
        realtime_model_id: Optional[str] = None,
        embedding_model_id: Optional[str] = None,
        additional_settings: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Update AI settings for a course.

        When individual models are updated, profile_key is preserved
        but the course now has custom overrides.

        Args:
            course_id: Course UUID
            *_model_id: Model IDs for each category (None = don't change)
            additional_settings: JSONB for extensions

        Returns:
            Updated settings

        Example:
            >>> settings = CourseAiSettingsService.update_settings(
            ...     course_id='abc-123',
            ...     chat_model_id='gpt-4o'
            ... )
        """
        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise ValueError(f"Course not found: {course_id}")

        # Get existing settings to preserve profile_key
        existing = CourseAiSettingsRepository.find_by_course_id(course_id)
        profile_key = existing.get('profile_key') if existing else None

        # Invalidate cache
        cls._invalidate_cache(course_id)

        return CourseAiSettingsRepository.upsert(
            course_id=course_id,
            profile_key=profile_key,
            chat_model_id=chat_model_id,
            reasoning_model_id=reasoning_model_id,
            image_model_id=image_model_id,
            audio_model_id=audio_model_id,
            realtime_model_id=realtime_model_id,
            embedding_model_id=embedding_model_id,
            additional_settings=additional_settings
        )

    @classmethod
    def apply_profile(cls, course_id: str, profile_key: str) -> Dict[str, Any]:
        """
        Apply a global profile to a course.

        Copies all model IDs from the profile to course settings.
        Sets profile_key for reference.

        Args:
            course_id: Course UUID
            profile_key: Profile key to apply

        Returns:
            Updated settings

        Raises:
            ValueError: If profile not found

        Example:
            >>> settings = CourseAiSettingsService.apply_profile('abc-123', 'quality')
        """
        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise ValueError(f"Course not found: {course_id}")

        # Get profile
        profile = AiModelProfilesRepository.find_by_key(profile_key)
        if not profile:
            raise ValueError(f"Profile not found: {profile_key}")

        # Invalidate cache
        cls._invalidate_cache(course_id)

        # Apply profile
        return CourseAiSettingsRepository.apply_profile(course_id, profile_key, profile)

    @classmethod
    def reset_to_defaults(cls, course_id: str) -> bool:
        """
        Reset course to use system defaults (delete settings).

        Args:
            course_id: Course UUID

        Returns:
            True if settings were deleted

        Example:
            >>> CourseAiSettingsService.reset_to_defaults('abc-123')
        """
        cls._invalidate_cache(course_id)
        return CourseAiSettingsRepository.delete_by_course_id(course_id)

    @classmethod
    def get_effective_settings(cls, course_id: str) -> Dict[str, Any]:
        """
        Get all effective models for a course.

        Resolves the fallback chain:
        1. Course-specific model ID
        2. Profile model ID (if profile_key set)
        3. Default profile model ID
        4. System default

        Args:
            course_id: Course UUID

        Returns:
            Dict with all model types and their effective values

        Example:
            >>> models = CourseAiSettingsService.get_effective_settings('abc-123')
        """
        settings = CourseAiSettingsRepository.find_by_course_id(course_id)
        default_profile = AiModelProfilesRepository.find_default()
        system_defaults = cls._get_system_defaults()

        # Get profile if set
        profile = None
        if settings and settings.get('profile_key'):
            profile = AiModelProfilesRepository.find_by_key(settings['profile_key'])

        result = {
            'course_id': course_id,
            'profile_key': settings.get('profile_key') if settings else None,
            'profile_name': None,
            'is_custom': settings is not None
        }

        # Get profile name
        if profile:
            result['profile_name'] = profile.get('name')
        elif default_profile:
            result['profile_name'] = f"{default_profile.get('name')} (Default)"

        # Resolve each model type
        for model_type in cls.MODEL_TYPES:
            # Priority: Course → Profile → Default Profile → System Default
            value = None

            if settings and settings.get(model_type):
                value = settings[model_type]
            elif profile and profile.get(model_type):
                value = profile[model_type]
            elif default_profile and default_profile.get(model_type):
                value = default_profile[model_type]
            else:
                value = system_defaults.get(model_type)

            result[model_type] = value

        return result

    @classmethod
    def get_effective_model(cls, course_id: str, model_type: str) -> str:
        """
        Get the effective model for a single category.

        Args:
            course_id: Course UUID
            model_type: One of the MODEL_TYPES

        Returns:
            Model identifier string

        Example:
            >>> model = CourseAiSettingsService.get_effective_model('abc-123', 'chat_model_id')
        """
        effective = cls.get_effective_settings(course_id)
        return effective.get(model_type, cls._get_system_defaults().get(model_type))

    @classmethod
    def get_available_profiles(cls) -> List[Dict[str, Any]]:
        """
        Get all available profiles for selection.

        Returns:
            List of profile summaries (key, name, description, is_default)

        Example:
            >>> profiles = CourseAiSettingsService.get_available_profiles()
        """
        return AiModelProfilesRepository.get_profile_summary()

    @classmethod
    def list_all_settings(
        cls,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List all courses with custom AI settings.

        Args:
            limit: Maximum results
            offset: Skip count

        Returns:
            Dict with items, total, pagination info

        Example:
            >>> result = CourseAiSettingsService.list_all_settings()
        """
        items = CourseAiSettingsRepository.find_all_with_course_info(limit, offset)
        total = CourseAiSettingsRepository.count_courses_with_settings()

        return {
            'items': items,
            'total': total,
            'limit': limit,
            'offset': offset
        }

    @classmethod
    def _get_system_defaults(cls) -> Dict[str, str]:
        """
        Get system default models from config.

        Returns:
            Dict with default model for each type
        """
        try:
            return {
                'chat_model_id': current_app.config.get('DEFAULT_CHAT_MODEL', 'gpt-4o-mini'),
                'reasoning_model_id': current_app.config.get('DEFAULT_REASONING_MODEL', 'gpt-4o'),
                'image_model_id': current_app.config.get('DEFAULT_IMAGE_MODEL', 'dall-e-3'),
                'audio_model_id': current_app.config.get('DEFAULT_AUDIO_MODEL', 'tts-1'),
                'realtime_model_id': current_app.config.get('DEFAULT_REALTIME_MODEL', 'gpt-4o-realtime-preview'),
                'embedding_model_id': current_app.config.get('DEFAULT_EMBEDDING_MODEL', 'text-embedding-3-small')
            }
        except RuntimeError:
            # Outside of application context
            return {
                'chat_model_id': 'gpt-4o-mini',
                'reasoning_model_id': 'gpt-4o',
                'image_model_id': 'dall-e-3',
                'audio_model_id': 'tts-1',
                'realtime_model_id': 'gpt-4o-realtime-preview',
                'embedding_model_id': 'text-embedding-3-small'
            }

    @classmethod
    def _invalidate_cache(cls, course_id: str) -> None:
        """
        Invalidate cached settings for a course.

        Args:
            course_id: Course UUID
        """
        for model_type in cls.MODEL_TYPES:
            cache_key = CacheService.make_key('COURSE_AI', course_id, model_type)
            CacheService.delete(cache_key)
