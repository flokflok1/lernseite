"""
Content Translation Service
============================
Manages translation of course content (chapters, lessons, materials).
Handles KI translation jobs, manual corrections, and translation lifecycle.

Distinct from i18n_service which handles UI string translations.
This service manages translations of actual course content.
"""

from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from psycopg.rows import dict_row
from app.infrastructure.persistence.database import get_connection
from app.infrastructure.persistence.repositories.i18n_repository import I18nRepository
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

        This creates a translation job that will be picked up by the KI pipeline
        to translate course content into the target language.

        Args:
            namespace: Content namespace (e.g., 'courses', 'chapters', 'lessons')
            key_path: Unique identifier for the content (e.g., 'course_123.chapter_5.intro')
            target_language: Target language code (de, en, pl, etc.)
            content_type: Type of content ('text', 'html', 'markdown')
            context: Optional context for better translation (e.g., domain, tone)
            user_id: User who initiated the translation

        Returns:
            {
                'job_id': str,
                'status': 'pending',
                'namespace': str,
                'key_path': str,
                'target_language': str,
                'created_at': datetime,
                'estimated_completion': datetime
            }
        """
        try:
            job_id = str(uuid4())

            with get_connection() as conn:
                repo = I18nRepository(conn)

                # Create translation job record
                query = """
                    INSERT INTO translation_jobs
                    (job_id, namespace, key_path, target_language, content_type, status,
                     created_by, context, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    RETURNING job_id, status, created_at
                """

                # Use cursor directly for this operation
                with conn.cursor(row_factory=dict_row) as cursor:
                    cursor.execute(
                        query,
                        (
                            job_id,
                            namespace,
                            key_path,
                            target_language,
                            content_type,
                            'pending',
                            user_id,
                            context
                        )
                    )
                    result = cursor.fetchone()
                    conn.commit()

            logger.info(
                f"KI translation job created: {job_id}",
                extra={
                    'job_id': job_id,
                    'namespace': namespace,
                    'target_language': target_language,
                    'user_id': user_id
                }
            )

            return {
                'job_id': job_id,
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
        namespace: str,
        key_path: str,
        language_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a translation for content.

        Args:
            namespace: Content namespace
            key_path: Content identifier
            language_code: Target language code

        Returns:
            {
                'translation_id': str,
                'namespace': str,
                'key_path': str,
                'language_code': str,
                'text': str,
                'source': str,  # 'manual' | 'ki' | 'import'
                'status': str,  # 'draft' | 'active' | 'needs_review'
                'created_at': datetime,
                'updated_at': datetime
            }
            Or None if not found
        """
        try:
            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    query = """
                        SELECT
                            translation_id,
                            namespace,
                            key_path,
                            language_code,
                            text,
                            source,
                            status,
                            created_at,
                            updated_at
                        FROM translations
                        WHERE namespace = %s AND key_path = %s AND language_code = %s
                    """
                    cursor.execute(query, (namespace, key_path, language_code))
                    return cursor.fetchone()

        except Exception as e:
            logger.error(
                f"Failed to retrieve translation: {str(e)}",
                extra={'namespace': namespace, 'key_path': key_path, 'language_code': language_code}
            )
            return None

    @staticmethod
    def get_translation_by_id(translation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a translation by ID.

        Args:
            translation_id: Translation ID

        Returns:
            Translation data or None if not found
        """
        try:
            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    query = """
                        SELECT
                            translation_id,
                            namespace,
                            key_path,
                            language_code,
                            text,
                            source,
                            status,
                            created_at,
                            updated_at
                        FROM translations
                        WHERE translation_id = %s
                    """
                    cursor.execute(query, (translation_id,))
                    return cursor.fetchone()

        except Exception as e:
            logger.error(
                f"Failed to retrieve translation by ID: {str(e)}",
                extra={'translation_id': translation_id}
            )
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
        """
        Store or update a translation.

        Args:
            namespace: Content namespace
            key_path: Content identifier
            language_code: Target language code
            text: Translated text
            source: Where translation came from ('manual', 'ki', 'import')
            status: Translation status ('draft', 'active', 'needs_review')
            translated_by: User ID who created/edited the translation

        Returns:
            translation_id if successful, None on failure
        """
        try:
            translation_id = str(uuid4())

            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    query = """
                        INSERT INTO translations
                        (translation_id, namespace, key_path, language_code, text,
                         source, status, translated_by, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        ON CONFLICT (namespace, key_path, language_code)
                        DO UPDATE SET
                            text = EXCLUDED.text,
                            source = EXCLUDED.source,
                            status = EXCLUDED.status,
                            translated_by = EXCLUDED.translated_by,
                            updated_at = NOW()
                        RETURNING translation_id
                    """
                    cursor.execute(
                        query,
                        (
                            translation_id,
                            namespace,
                            key_path,
                            language_code,
                            text,
                            source,
                            status,
                            translated_by
                        )
                    )
                    result = cursor.fetchone()
                    conn.commit()

            logger.info(
                f"Translation stored: {translation_id}",
                extra={
                    'namespace': namespace,
                    'key_path': key_path,
                    'language_code': language_code,
                    'source': source
                }
            )

            return result['translation_id'] if result else translation_id

        except Exception as e:
            logger.error(
                f"Failed to store translation: {str(e)}",
                extra={
                    'namespace': namespace,
                    'key_path': key_path,
                    'language_code': language_code
                }
            )
            return None

    @staticmethod
    def update_translation(
        translation_id: str,
        text: str,
        status: str = 'active',
        updated_by: Optional[str] = None
    ) -> bool:
        """
        Update an existing translation (manual correction).

        Args:
            translation_id: ID of translation to update
            text: Corrected translation text
            status: New status
            updated_by: User ID who made the correction

        Returns:
            True if successful, False otherwise
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        UPDATE translations
                        SET text = %s,
                            status = %s,
                            source = 'manual',
                            translated_by = COALESCE(%s, translated_by),
                            updated_at = NOW()
                        WHERE translation_id = %s
                    """
                    cursor.execute(query, (text, status, updated_by, translation_id))
                    conn.commit()

            logger.info(
                f"Translation updated: {translation_id}",
                extra={'status': status, 'updated_by': updated_by}
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update translation: {str(e)}")
            return False

    @staticmethod
    def delete_translation(translation_id: str) -> bool:
        """
        Delete a translation.

        Args:
            translation_id: ID of translation to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "DELETE FROM translations WHERE translation_id = %s"
                    cursor.execute(query, (translation_id,))
                    conn.commit()

            logger.info(f"Translation deleted: {translation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete translation: {str(e)}")
            return False

    @staticmethod
    def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a KI translation job.

        Args:
            job_id: ID of the translation job

        Returns:
            Job status details or None if not found
        """
        try:
            with get_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    query = """
                        SELECT
                            job_id,
                            namespace,
                            key_path,
                            target_language,
                            status,
                            created_at,
                            completed_at,
                            result_translation_id
                        FROM translation_jobs
                        WHERE job_id = %s
                    """
                    cursor.execute(query, (job_id,))
                    return cursor.fetchone()

        except Exception as e:
            logger.error(f"Failed to get job status: {str(e)}")
            return None

__all__ = ['ContentTranslationService']
