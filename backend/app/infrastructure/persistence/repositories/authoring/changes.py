"""
Repository for authoring_changes table (Edit Mode Change Tracking)
"""
from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringChangesRepository(BaseRepository):
    """Repository for tracking changes in authoring sessions (Edit Mode)"""

    @staticmethod
    def create_change(
        session_id: str,
        change_type: str,
        entity_type: str,
        entity_id: Optional[str],
        temp_id: Optional[str],
        before_data: Optional[Dict],
        after_data: Optional[Dict],
        diff: Optional[Dict],
        user_action: str,
        changed_by: str,
        sequence_number: int
    ) -> Optional[str]:
        """
        Record a change in an authoring session.

        Args:
            session_id: UUID of authoring session
            change_type: Type of change (chapter_added, lesson_edited, etc.)
            entity_type: Type of entity (course, chapter, lesson, method)
            entity_id: UUID of entity (NULL for new entities)
            temp_id: Temporary ID in draft_structure
            before_data: State before change (NULL for additions)
            after_data: State after change (NULL for deletions)
            diff: Structured diff for UI display
            user_action: Human-readable description
            changed_by: User who made the change
            sequence_number: Sequential order for undo/redo

        Returns:
            change_id if successful, None otherwise
        """
        query = """
            INSERT INTO ai_pipeline.authoring_changes (
                session_id, change_type, entity_type, entity_id, temp_id,
                before_data, after_data, diff, user_action, changed_by, sequence_number
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING change_id
        """
        try:
            result = AuthoringChangesRepository.fetch_one(query, (
                session_id, change_type, entity_type, entity_id, temp_id,
                before_data, after_data, diff, user_action, changed_by, sequence_number
            ))
            return result['change_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating change: {e}")
            return None

    @staticmethod
    def get_changes_by_session(
        session_id: str,
        include_reverted: bool = False
    ) -> List[Dict]:
        """
        Get all changes for a session.

        Args:
            session_id: UUID of authoring session
            include_reverted: Include reverted changes

        Returns:
            List of change records
        """
        query = """
            SELECT
                change_id, session_id, change_type, entity_type,
                entity_id, temp_id, before_data, after_data, diff,
                user_action, changed_by, sequence_number,
                is_reverted, created_at
            FROM ai_pipeline.authoring_changes
            WHERE session_id = %s
        """
        if not include_reverted:
            query += " AND is_reverted = FALSE"

        query += " ORDER BY sequence_number ASC"

        try:
            return AuthoringChangesRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching changes: {e}")
            return []

    @staticmethod
    def get_changes_by_entity(
        entity_type: str,
        entity_id: str
    ) -> List[Dict]:
        """
        Get all changes for a specific entity.

        Args:
            entity_type: Type of entity
            entity_id: UUID of entity

        Returns:
            List of change records
        """
        query = """
            SELECT
                change_id, session_id, change_type, entity_type,
                entity_id, temp_id, before_data, after_data, diff,
                user_action, changed_by, sequence_number,
                is_reverted, created_at
            FROM ai_pipeline.authoring_changes
            WHERE entity_type = %s AND entity_id = %s
            ORDER BY created_at DESC
        """
        try:
            return AuthoringChangesRepository.fetch_all(query, (entity_type, entity_id))
        except Exception as e:
            logger.error(f"Error fetching entity changes: {e}")
            return []

    @staticmethod
    def get_change_by_id(change_id: str) -> Optional[Dict]:
        """Get single change by ID"""
        query = """
            SELECT
                change_id, session_id, change_type, entity_type,
                entity_id, temp_id, before_data, after_data, diff,
                user_action, changed_by, sequence_number,
                is_reverted, created_at
            FROM ai_pipeline.authoring_changes
            WHERE change_id = %s
        """
        try:
            return AuthoringChangesRepository.fetch_one(query, (change_id,))
        except Exception as e:
            logger.error(f"Error fetching change: {e}")
            return None

    @staticmethod
    def revert_change(change_id: str) -> bool:
        """
        Mark a change as reverted (for undo).

        Args:
            change_id: UUID of change to revert

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_changes
            SET is_reverted = TRUE
            WHERE change_id = %s
        """
        try:
            AuthoringChangesRepository.execute_update(query, (change_id,))
            return True
        except Exception as e:
            logger.error(f"Error reverting change: {e}")
            return False

    @staticmethod
    def get_next_sequence_number(session_id: str) -> int:
        """
        Get next sequence number for session.

        Args:
            session_id: UUID of authoring session

        Returns:
            Next sequence number
        """
        query = """
            SELECT COALESCE(MAX(sequence_number), 0) + 1 as next_seq
            FROM ai_pipeline.authoring_changes
            WHERE session_id = %s
        """
        try:
            result = AuthoringChangesRepository.fetch_one(query, (session_id,))
            return result['next_seq'] if result else 1
        except Exception as e:
            logger.error(f"Error getting next sequence: {e}")
            return 1

    @staticmethod
    def get_change_statistics(session_id: str) -> Dict:
        """
        Get statistics about changes in session.

        Args:
            session_id: UUID of authoring session

        Returns:
            Statistics dict
        """
        query = """
            SELECT
                COUNT(*) as total_changes,
                COUNT(CASE WHEN change_type LIKE '%_added' THEN 1 END) as additions,
                COUNT(CASE WHEN change_type LIKE '%_edited' THEN 1 END) as edits,
                COUNT(CASE WHEN change_type LIKE '%_deleted' THEN 1 END) as deletions,
                COUNT(CASE WHEN is_reverted = TRUE THEN 1 END) as reverted
            FROM ai_pipeline.authoring_changes
            WHERE session_id = %s
        """
        try:
            result = AuthoringChangesRepository.fetch_one(query, (session_id,))
            return result if result else {
                'total_changes': 0,
                'additions': 0,
                'edits': 0,
                'deletions': 0,
                'reverted': 0
            }
        except Exception as e:
            logger.error(f"Error fetching change statistics: {e}")
            return {
                'total_changes': 0,
                'additions': 0,
                'edits': 0,
                'deletions': 0,
                'reverted': 0
            }

    @staticmethod
    def get_changes_by_type(
        session_id: str,
        change_type: str
    ) -> List[Dict]:
        """
        Get changes of specific type.

        Args:
            session_id: UUID of authoring session
            change_type: Type of change

        Returns:
            List of matching changes
        """
        query = """
            SELECT
                change_id, entity_type, entity_id, temp_id,
                before_data, after_data, diff, user_action,
                sequence_number, created_at
            FROM ai_pipeline.authoring_changes
            WHERE session_id = %s AND change_type = %s
            AND is_reverted = FALSE
            ORDER BY sequence_number ASC
        """
        try:
            return AuthoringChangesRepository.fetch_all(query, (session_id, change_type))
        except Exception as e:
            logger.error(f"Error fetching changes by type: {e}")
            return []
