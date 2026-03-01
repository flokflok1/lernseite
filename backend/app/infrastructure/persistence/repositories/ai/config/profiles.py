"""
LernsystemX AI Model Profiles Repository

Database operations for global AI model profiles.
Profiles define sets of models per category (chat, reasoning, image, audio, etc.).

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Repository layer
"""

from typing import Dict, Optional, List
from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class AiModelProfilesRepository(BaseRepository):
    """
    Repository for ai_model_profiles table.

    Manages global AI model profiles that can be applied to courses.
    Only one profile can be marked as default (is_default = true).
    """

    table_name = 'ai_pipeline.ai_model_profiles'
    pk_column = 'id'

    @classmethod
    def find_by_key(cls, key: str) -> Optional[Dict]:
        """
        Get profile by unique key.

        Args:
            key: Profile key (e.g., 'standard', 'quality', 'budget')

        Returns:
            Profile dict or None

        Example:
            >>> profile = AiModelProfilesRepository.find_by_key('standard')
            >>> print(profile['chat_model_id'])  # 'gpt-4o-mini'
        """
        query = """
            SELECT *
            FROM ai_pipeline.ai_model_profiles
            WHERE key = %s
        """
        return fetch_one(query, (key,))

    @classmethod
    def find_default(cls) -> Optional[Dict]:
        """
        Get the default profile (is_default = true).

        Returns:
            Default profile dict or None

        Example:
            >>> default = AiModelProfilesRepository.find_default()
            >>> print(default['name'])  # 'Standard'
        """
        query = """
            SELECT *
            FROM ai_pipeline.ai_model_profiles
            WHERE is_default = TRUE AND is_active = TRUE
            LIMIT 1
        """
        return fetch_one(query)

    @classmethod
    def find_all_active(cls) -> List[Dict]:
        """
        Get all active profiles.

        Returns:
            List of active profile dicts, default first

        Example:
            >>> profiles = AiModelProfilesRepository.find_all_active()
        """
        query = """
            SELECT *
            FROM ai_pipeline.ai_model_profiles
            WHERE is_active = TRUE
            ORDER BY is_default DESC, name ASC
        """
        return fetch_all(query)

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
    ) -> Dict:
        """
        Create a new profile.

        Args:
            key: Unique key
            name: Display name
            description: Optional description
            chat_model_id: Chat/text model ID
            reasoning_model_id: Reasoning model ID
            image_model_id: Image model ID
            audio_model_id: Audio/TTS model ID
            realtime_model_id: Realtime model ID
            embedding_model_id: Embedding model ID
            is_default: Set as default profile

        Returns:
            Created profile dict

        Example:
            >>> profile = AiModelProfilesRepository.create_profile(
            ...     key='custom',
            ...     name='Custom',
            ...     chat_model_id='gpt-4o'
            ... )
        """
        # If setting as default, unset other defaults first
        if is_default:
            cls._unset_all_defaults()

        return cls.create({
            'key': key,
            'name': name,
            'description': description,
            'chat_model_id': chat_model_id,
            'reasoning_model_id': reasoning_model_id,
            'image_model_id': image_model_id,
            'audio_model_id': audio_model_id,
            'realtime_model_id': realtime_model_id,
            'embedding_model_id': embedding_model_id,
            'is_default': is_default,
            'is_active': True
        })

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
        is_default: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict]:
        """
        Update an existing profile.

        Args:
            key: Profile key to update
            (other args): Fields to update (None = don't change)

        Returns:
            Updated profile dict or None if not found

        Example:
            >>> profile = AiModelProfilesRepository.update_profile(
            ...     key='standard',
            ...     chat_model_id='gpt-4o'
            ... )
        """
        existing = cls.find_by_key(key)
        if not existing:
            return None

        # If setting as default, unset other defaults first
        if is_default is True:
            cls._unset_all_defaults()

        # Build update dict with non-None values
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if description is not None:
            update_data['description'] = description
        if chat_model_id is not None:
            update_data['chat_model_id'] = chat_model_id
        if reasoning_model_id is not None:
            update_data['reasoning_model_id'] = reasoning_model_id
        if image_model_id is not None:
            update_data['image_model_id'] = image_model_id
        if audio_model_id is not None:
            update_data['audio_model_id'] = audio_model_id
        if realtime_model_id is not None:
            update_data['realtime_model_id'] = realtime_model_id
        if embedding_model_id is not None:
            update_data['embedding_model_id'] = embedding_model_id
        if legacy_model_id is not None:
            update_data['legacy_model_id'] = legacy_model_id
        if moderation_model_id is not None:
            update_data['moderation_model_id'] = moderation_model_id
        if video_model_id is not None:
            update_data['video_model_id'] = video_model_id
        if vision_model_id is not None:
            update_data['vision_model_id'] = vision_model_id
        if transcription_model_id is not None:
            update_data['transcription_model_id'] = transcription_model_id
        if translation_model_id is not None:
            update_data['translation_model_id'] = translation_model_id
        if is_default is not None:
            update_data['is_default'] = is_default
        if is_active is not None:
            update_data['is_active'] = is_active

        if not update_data:
            return existing

        return cls.update_by(update_data, key=key)

    @classmethod
    def delete_profile(cls, key: str) -> bool:
        """
        Delete a profile by key.

        Args:
            key: Profile key to delete

        Returns:
            True if deleted, False if not found

        Example:
            >>> AiModelProfilesRepository.delete_profile('custom')
            True
        """
        result = cls.delete_by(key=key)
        return result is not None

    @classmethod
    def set_default(cls, key: str) -> Optional[Dict]:
        """
        Set a profile as the default.

        Args:
            key: Profile key to set as default

        Returns:
            Updated profile dict or None if not found

        Example:
            >>> AiModelProfilesRepository.set_default('quality')
        """
        existing = cls.find_by_key(key)
        if not existing:
            return None

        # Unset all other defaults
        cls._unset_all_defaults()

        # Set this one as default
        return cls.update_by({'is_default': True}, key=key)

    @classmethod
    def _unset_all_defaults(cls) -> None:
        """
        Unset is_default on all profiles.
        Internal method called before setting a new default.
        """
        query = """
            UPDATE ai_pipeline.ai_model_profiles
            SET is_default = FALSE, updated_at = NOW()
            WHERE is_default = TRUE
        """
        execute_query(query)

    @classmethod
    def get_profile_summary(cls) -> List[Dict]:
        """
        Get summary of all profiles for dropdown/list display.

        Returns:
            List of {key, name, description, is_default} dicts

        Example:
            >>> summaries = AiModelProfilesRepository.get_profile_summary()
        """
        query = """
            SELECT key, name, description, is_default
            FROM ai_pipeline.ai_model_profiles
            WHERE is_active = TRUE
            ORDER BY is_default DESC, name ASC
        """
        return fetch_all(query)

    @classmethod
    def count_active(cls) -> int:
        """
        Count active profiles.

        Returns:
            Number of active profiles
        """
        return cls.count(is_active=True)
