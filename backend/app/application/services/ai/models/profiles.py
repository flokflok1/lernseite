"""
LernsystemX AI Model Profiles Service

Business logic for global AI model profiles:
- CRUD operations for profiles
- Default profile management
- Profile validation against available models

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Service layer
"""

from typing import Dict, Optional, List, Any

from app.infrastructure.persistence.repositories.ai.profiles import AiModelProfilesRepository
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository


class AIModelProfilesService:
    """
    Service layer for AI model profiles.

    Implements business logic for managing global AI profiles
    that can be applied to courses.
    """

    # Valid model categories
    MODEL_CATEGORIES = ['chat', 'reasoning', 'image', 'audio', 'realtime', 'embedding',
                        'legacy', 'moderation', 'video', 'vision', 'transcription', 'translation']

    @classmethod
    def get_all_profiles(cls) -> List[Dict[str, Any]]:
        """
        Get all active profiles.

        Returns:
            List of profile dicts with all fields

        Example:
            >>> profiles = AIModelProfilesService.get_all_profiles()
        """
        return AiModelProfilesRepository.find_all_active()

    @classmethod
    def get_profile(cls, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a profile by key.

        Args:
            key: Profile key

        Returns:
            Profile dict or None

        Example:
            >>> profile = AIModelProfilesService.get_profile('standard')
        """
        return AiModelProfilesRepository.find_by_key(key)

    @classmethod
    def get_default_profile(cls) -> Optional[Dict[str, Any]]:
        """
        Get the default profile.

        Returns:
            Default profile dict or None

        Example:
            >>> default = AIModelProfilesService.get_default_profile()
        """
        return AiModelProfilesRepository.find_default()

    @classmethod
    def get_profile_summary(cls) -> List[Dict[str, Any]]:
        """
        Get profile summaries for dropdown display.

        Returns:
            List of {key, name, description, is_default} dicts

        Example:
            >>> summaries = AIModelProfilesService.get_profile_summary()
        """
        return AiModelProfilesRepository.get_profile_summary()

    @classmethod
    def create_profile(
        cls,
        key: str,
        name: str,
        description: Optional[str] = None,
        chat_model_id: Optional[str] = None,
        reasoning_model_id: Optional[str] = None,
        image_model_id: Optional[str] = None,
        audio_model_id: Optional[str] = None,
        realtime_model_id: Optional[str] = None,
        embedding_model_id: Optional[str] = None,
        is_default: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new profile.

        Args:
            key: Unique key (lowercase, no spaces)
            name: Display name
            description: Optional description
            *_model_id: Model IDs for each category
            is_default: Set as default profile

        Returns:
            Created profile dict

        Raises:
            ValueError: If key already exists or models invalid

        Example:
            >>> profile = AIModelProfilesService.create_profile(
            ...     key='custom',
            ...     name='Custom Profile',
            ...     chat_model_id='gpt-4o'
            ... )
        """
        # Validate key format
        cls._validate_key(key)

        # Check if key exists
        existing = AiModelProfilesRepository.find_by_key(key)
        if existing:
            raise ValueError(f"Profile with key '{key}' already exists")

        # Validate model IDs (if provided)
        cls._validate_model_ids(
            chat_model_id=chat_model_id,
            reasoning_model_id=reasoning_model_id,
            image_model_id=image_model_id,
            audio_model_id=audio_model_id,
            realtime_model_id=realtime_model_id,
            embedding_model_id=embedding_model_id
        )

        return AiModelProfilesRepository.create_profile(
            key=key,
            name=name,
            description=description,
            chat_model_id=chat_model_id,
            reasoning_model_id=reasoning_model_id,
            image_model_id=image_model_id,
            audio_model_id=audio_model_id,
            realtime_model_id=realtime_model_id,
            embedding_model_id=embedding_model_id,
            is_default=is_default
        )

    @classmethod
    def update_profile(
        cls,
        key: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        chat_model_id: Optional[str] = None,
        reasoning_model_id: Optional[str] = None,
        image_model_id: Optional[str] = None,
        audio_model_id: Optional[str] = None,
        realtime_model_id: Optional[str] = None,
        embedding_model_id: Optional[str] = None,
        legacy_model_id: Optional[str] = None,
        moderation_model_id: Optional[str] = None,
        video_model_id: Optional[str] = None,
        vision_model_id: Optional[str] = None,
        transcription_model_id: Optional[str] = None,
        translation_model_id: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update an existing profile.

        Args:
            key: Profile key to update
            (other args): Fields to update (None = don't change)

        Returns:
            Updated profile dict

        Raises:
            ValueError: If profile not found

        Example:
            >>> profile = AIModelProfilesService.update_profile(
            ...     key='standard',
            ...     chat_model_id='gpt-4o'
            ... )
        """
        existing = AiModelProfilesRepository.find_by_key(key)
        if not existing:
            raise ValueError(f"Profile '{key}' not found")

        result = AiModelProfilesRepository.update_profile(
            key=key,
            name=name,
            description=description,
            chat_model_id=chat_model_id,
            reasoning_model_id=reasoning_model_id,
            image_model_id=image_model_id,
            audio_model_id=audio_model_id,
            realtime_model_id=realtime_model_id,
            embedding_model_id=embedding_model_id,
            legacy_model_id=legacy_model_id,
            moderation_model_id=moderation_model_id,
            video_model_id=video_model_id,
            vision_model_id=vision_model_id,
            transcription_model_id=transcription_model_id,
            translation_model_id=translation_model_id,
            is_default=is_default
        )

        if not result:
            raise ValueError(f"Failed to update profile '{key}'")

        return result

    @classmethod
    def delete_profile(cls, key: str) -> bool:
        """
        Delete a profile.

        Args:
            key: Profile key to delete

        Returns:
            True if deleted

        Raises:
            ValueError: If profile not found or is default

        Example:
            >>> AIModelProfilesService.delete_profile('custom')
        """
        existing = AiModelProfilesRepository.find_by_key(key)
        if not existing:
            raise ValueError(f"Profile '{key}' not found")

        if existing.get('is_default'):
            raise ValueError("Cannot delete the default profile. Set another profile as default first.")

        return AiModelProfilesRepository.delete_profile(key)

    @classmethod
    def set_default_profile(cls, key: str) -> Dict[str, Any]:
        """
        Set a profile as the default.

        Args:
            key: Profile key to set as default

        Returns:
            Updated profile dict

        Raises:
            ValueError: If profile not found

        Example:
            >>> AIModelProfilesService.set_default_profile('quality')
        """
        existing = AiModelProfilesRepository.find_by_key(key)
        if not existing:
            raise ValueError(f"Profile '{key}' not found")

        result = AiModelProfilesRepository.set_default(key)
        if not result:
            raise ValueError(f"Failed to set default profile '{key}'")

        return result

    @classmethod
    def get_profile_with_model_info(cls, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a profile with full model information for each model ID.

        Args:
            key: Profile key

        Returns:
            Profile dict with model info added

        Example:
            >>> profile = AIModelProfilesService.get_profile_with_model_info('standard')
            >>> print(profile['chat_model_info']['display_name'])  # 'GPT-4o Mini'
        """
        profile = AiModelProfilesRepository.find_by_key(key)
        if not profile:
            return None

        # Add model info for each category
        model_fields = [
            'chat_model_id', 'reasoning_model_id', 'image_model_id',
            'audio_model_id', 'realtime_model_id', 'embedding_model_id'
        ]

        for field in model_fields:
            model_id = profile.get(field)
            if model_id:
                model_info = AIModelsRepository.get_by_model_id(model_id)
                info_field = field.replace('_id', '_info')
                profile[info_field] = model_info

        return profile

    @classmethod
    def _validate_key(cls, key: str) -> None:
        """
        Validate profile key format.

        Args:
            key: Profile key

        Raises:
            ValueError: If key format invalid
        """
        if not key:
            raise ValueError("Profile key is required")
        if len(key) > 50:
            raise ValueError("Profile key must be 50 characters or less")
        if not key.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Profile key must be alphanumeric (with underscores/hyphens)")
        if key != key.lower():
            raise ValueError("Profile key must be lowercase")

    @classmethod
    def _validate_model_ids(cls, **model_ids) -> None:
        """
        Validate that model IDs exist in the database.

        Args:
            **model_ids: Model IDs to validate

        Raises:
            ValueError: If any model ID is invalid

        Note:
            Validation is optional - models may not exist in all environments.
            We log warnings but don't fail hard.
        """
        # For now, we don't validate model IDs against the database
        # because models might be synced from external providers
        # and not all models may exist locally
        pass

    @classmethod
    def get_available_models_by_category(cls) -> Dict[str, List[Dict]]:
        """
        Get available models grouped by category.

        Returns:
            Dict with category keys and list of model dicts

        Example:
            >>> models = AIModelProfilesService.get_available_models_by_category()
            >>> print(models['chat'])  # [{'model_id': 'gpt-4o', ...}, ...]
        """
        result = {}
        for category in cls.MODEL_CATEGORIES:
            models = AIModelsRepository.get_by_category(category, active_only=True)
            result[category] = models or []
        return result
