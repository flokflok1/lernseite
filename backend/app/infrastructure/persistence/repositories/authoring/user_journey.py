"""
Repository for authoring_user_journey table (Progressive Disclosure & User Guidance)
"""
from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringUserJourneyRepository(BaseRepository):
    """Repository for tracking user's journey through authoring workflow"""

    @staticmethod
    def create_journey(
        session_id: str,
        user_id: str,
        current_phase: str = 'upload',
        user_experience_level: str = 'beginner'
    ) -> Optional[str]:
        """
        Create a new journey record.

        Args:
            session_id: UUID of authoring session
            user_id: UUID of user
            current_phase: Initial phase
            user_experience_level: User's experience level

        Returns:
            journey_id if successful
        """
        query = """
            INSERT INTO ai_pipeline.authoring_user_journey (
                session_id, user_id, current_phase, user_experience_level
            ) VALUES (
                %s, %s, %s, %s
            ) RETURNING journey_id
        """
        try:
            result = AuthoringUserJourneyRepository.fetch_one(query, (
                session_id, user_id, current_phase, user_experience_level
            ))
            return result['journey_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating journey: {e}")
            return None

    @staticmethod
    def get_journey_by_session(session_id: str) -> Optional[Dict]:
        """Get journey for session"""
        query = """
            SELECT
                journey_id, session_id, user_id,
                current_phase, completed_phases,
                suggested_next_action, user_experience_level,
                tips_shown, last_tip_shown_at,
                created_at, updated_at
            FROM ai_pipeline.authoring_user_journey
            WHERE session_id = %s
        """
        try:
            return AuthoringUserJourneyRepository.fetch_one(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching journey: {e}")
            return None

    @staticmethod
    def update_phase(
        journey_id: str,
        new_phase: str,
        suggested_next_action: Optional[str] = None
    ) -> bool:
        """
        Update current phase and add to completed phases.

        Args:
            journey_id: UUID of journey
            new_phase: New phase to enter
            suggested_next_action: Next suggested action

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_user_journey
            SET current_phase = %s,
                completed_phases = CASE
                    WHEN %s = ANY(completed_phases) THEN completed_phases
                    WHEN current_phase IS DISTINCT FROM %s THEN
                        array_append(completed_phases, current_phase)
                    ELSE completed_phases
                END,
                suggested_next_action = %s,
                updated_at = NOW()
            WHERE journey_id = %s
        """
        try:
            AuthoringUserJourneyRepository.execute_update(query, (
                new_phase, new_phase, new_phase,
                suggested_next_action, journey_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error updating phase: {e}")
            return False

    @staticmethod
    def add_tip_shown(
        journey_id: str,
        tip: str
    ) -> bool:
        """Record that a tip was shown to user"""
        query = """
            UPDATE ai_pipeline.authoring_user_journey
            SET tips_shown = array_append(tips_shown, %s),
                last_tip_shown_at = NOW(),
                updated_at = NOW()
            WHERE journey_id = %s
        """
        try:
            AuthoringUserJourneyRepository.execute_update(query, (tip, journey_id))
            return True
        except Exception as e:
            logger.error(f"Error adding tip: {e}")
            return False

    @staticmethod
    def update_experience_level(
        journey_id: str,
        new_level: str
    ) -> bool:
        """Update user's experience level"""
        query = """
            UPDATE ai_pipeline.authoring_user_journey
            SET user_experience_level = %s,
                updated_at = NOW()
            WHERE journey_id = %s
        """
        try:
            AuthoringUserJourneyRepository.execute_update(query, (new_level, journey_id))
            return True
        except Exception as e:
            logger.error(f"Error updating experience level: {e}")
            return False

    @staticmethod
    def get_user_statistics(user_id: str) -> Dict:
        """Get user's journey statistics across all sessions"""
        query = """
            SELECT
                COUNT(*) as total_sessions,
                COUNT(DISTINCT current_phase) as phases_used,
                AVG(array_length(completed_phases, 1)) as avg_phases_completed,
                user_experience_level,
                COUNT(CASE WHEN current_phase = 'finalize' THEN 1 END) as completed_sessions
            FROM ai_pipeline.authoring_user_journey
            WHERE user_id = %s
            GROUP BY user_experience_level
        """
        try:
            result = AuthoringUserJourneyRepository.fetch_one(query, (user_id,))
            return result if result else {
                'total_sessions': 0,
                'phases_used': 0,
                'avg_phases_completed': 0,
                'user_experience_level': 'beginner',
                'completed_sessions': 0
            }
        except Exception as e:
            logger.error(f"Error fetching user statistics: {e}")
            return {
                'total_sessions': 0,
                'phases_used': 0,
                'avg_phases_completed': 0,
                'user_experience_level': 'beginner',
                'completed_sessions': 0
            }
