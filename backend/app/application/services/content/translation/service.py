"""
Content Translation Service
============================
Manages translation of course content (chapters, lessons, materials).
Handles KI translation jobs, manual corrections, and translation lifecycle.

Distinct from i18n_service which handles UI string translations.
This service manages translations of actual course content.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from app.infrastructure.persistence.repositories.content_translation.core import ContentTranslationRepository
import logging

logger = logging.getLogger(__name__)


class ContentTranslationService:
    """
    Service for managing content translations (courses, chapters, lessons).

    Handles:
    - Initiating KI translation jobs
    - Storing and retrieving translations
    - Manual translation corrections
    - Translation quality tracking
    """

    @staticmethod
    def initiate_ki_translation(
        namespace: str,
        key_path: str,
        target_language: str,
        content_type: str = 'text',
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate a KI translation job for content.

        Args:
            namespace: Content namespace (e.g., 'courses', 'chapters', 'lessons')
            key_path: Unique identifier for the content
            target_language: Target language code (de, en, pl, etc.)
            content_type: Type of content ('text', 'html', 'markdown')
            context: Optional context for better translation
            user_id: User who initiated the translation

        Returns:
            Job details dict with job_id, status, created_at, etc.
        """
        try:
            result = ContentTranslationRepository.create_job(
                namespace=namespace,
                key_path=key_path,
                target_language=target_language,
                content_type=content_type,
                user_id=user_id,
                context=context
            )

            logger.info(
                f"KI translation job created: {result['job_id'] if result else 'unknown'}",
                extra={
                    'namespace': namespace,
                    'target_language': target_language,
                    'user_id': user_id
                }
            )

            return {
                'job_id': result['job_id'] if result else None,
                'status': 'pending',
                'namespace': namespace,
                'key_path': key_path,
                'target_language': target_language,
                'created_at': result['created_at'] if result else datetime.utcnow(),
                'estimated_completion': None
            }

        except Exception as e:
            logger.error(
                f"Failed to initiate KI translation: {str(e)}",
                extra={'namespace': namespace, 'key_path': key_path}
            )
            raise

    @staticmethod
    def get_translation(
        namespace: str, key_path: str, language_code: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a translation for content."""
        try:
            return ContentTranslationRepository.find_translation(
                namespace, key_path, language_code
            )
        except Exception as e:
            logger.error(
                f"Failed to retrieve translation: {str(e)}",
                extra={'namespace': namespace, 'key_path': key_path, 'language_code': language_code}
            )
            return None

    @staticmethod
    def get_translation_by_id(translation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a translation by ID."""
        try:
            return ContentTranslationRepository.find_translation_by_id(translation_id)
        except Exception as e:
            logger.error(f"Failed to retrieve translation by ID: {str(e)}")
            return None

    @staticmethod
    def store_translation(
        namespace: str,
        key_path: str,
        language_code: str,
        text: str,
        source: str = 'manual',
        status: str = 'active',
        translated_by: Optional[str] = None
    ) -> Optional[str]:
        """Store or update a translation. Returns translation_id."""
        try:
            result = ContentTranslationRepository.upsert_translation(
                namespace=namespace,
                key_path=key_path,
                language_code=language_code,
                text=text,
                source=source,
                status=status,
                translated_by=translated_by
            )

            logger.info(
                f"Translation stored: {result}",
                extra={
                    'namespace': namespace,
                    'key_path': key_path,
                    'language_code': language_code,
                    'source': source
                }
            )
            return result

        except Exception as e:
            logger.error(
                f"Failed to store translation: {str(e)}",
                extra={'namespace': namespace, 'key_path': key_path}
            )
            return None

    @staticmethod
    def update_translation(
        translation_id: str,
        text: str,
        status: str = 'active',
        updated_by: Optional[str] = None
    ) -> bool:
        """Update an existing translation (manual correction)."""
        try:
            ContentTranslationRepository.update_translation_text(
                translation_id, text, status, updated_by
            )
            logger.info(f"Translation updated: {translation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update translation: {str(e)}")
            return False

    @staticmethod
    def delete_translation(translation_id: str) -> bool:
        """Delete a translation."""
        try:
            ContentTranslationRepository.delete_translation(translation_id)
            logger.info(f"Translation deleted: {translation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete translation: {str(e)}")
            return False

    @staticmethod
    def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a KI translation job."""
        try:
            return ContentTranslationRepository.get_job_status(job_id)
        except Exception as e:
            logger.error(f"Failed to get job status: {str(e)}")
            return None

__all__ = ['ContentTranslationService']
