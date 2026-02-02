"""
Repository for authoring_milestones table (Gamification & Achievements)
"""
from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringMilestonesRepository(BaseRepository):
    """Repository for tracking user milestones and achievements"""

    @staticmethod
    def create_milestone(
        session_id: str,
        user_id: str,
        milestone_type: str,
        achievement_title: str,
        celebration_message: str,
        badge_earned: Optional[str] = None,
        achievement_data: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Create a new milestone record.

        Args:
            session_id: UUID of authoring session
            user_id: UUID of user
            milestone_type: Type of milestone
            achievement_title: Title of achievement
            celebration_message: Celebration message
            badge_earned: Optional badge code
            achievement_data: Optional achievement statistics

        Returns:
            milestone_id if successful
        """
        query = """
            INSERT INTO ai_pipeline.authoring_milestones (
                session_id, user_id, milestone_type,
                achievement_title, celebration_message,
                badge_earned, achievement_data
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            ) RETURNING milestone_id
        """
        try:
            result = AuthoringMilestonesRepository.fetch_one(query, (
                session_id, user_id, milestone_type,
                achievement_title, celebration_message,
                badge_earned, achievement_data or {}
            ))
            return result['milestone_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating milestone: {e}")
            return None

    @staticmethod
    def get_milestone_by_id(milestone_id: str) -> Optional[Dict]:
        """Get milestone by ID"""
        query = """
            SELECT
                milestone_id, session_id, user_id,
                milestone_type, achievement_title, celebration_message,
                badge_earned, achievement_data, achieved_at
            FROM ai_pipeline.authoring_milestones
            WHERE milestone_id = %s
        """
        try:
            return AuthoringMilestonesRepository.fetch_one(query, (milestone_id,))
        except Exception as e:
            logger.error(f"Error fetching milestone: {e}")
            return None

    @staticmethod
    def get_milestones_by_user(
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get user's recent milestones.

        Args:
            user_id: UUID of user
            limit: Maximum number of milestones to return

        Returns:
            List of milestone records
        """
        query = """
            SELECT
                milestone_id, milestone_type,
                achievement_title, celebration_message,
                badge_earned, achievement_data, achieved_at
            FROM ai_pipeline.authoring_milestones
            WHERE user_id = %s
            ORDER BY achieved_at DESC
            LIMIT %s
        """
        try:
            return AuthoringMilestonesRepository.fetch_all(query, (user_id, limit))
        except Exception as e:
            logger.error(f"Error fetching user milestones: {e}")
            return []

    @staticmethod
    def get_milestones_by_session(session_id: str) -> List[Dict]:
        """Get milestones for session"""
        query = """
            SELECT
                milestone_id, milestone_type,
                achievement_title, celebration_message,
                badge_earned, achievement_data, achieved_at
            FROM ai_pipeline.authoring_milestones
            WHERE session_id = %s
            ORDER BY achieved_at ASC
        """
        try:
            return AuthoringMilestonesRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching session milestones: {e}")
            return []

    @staticmethod
    def has_milestone(
        user_id: str,
        milestone_type: str
    ) -> bool:
        """
        Check if user has achieved milestone type.

        Args:
            user_id: UUID of user
            milestone_type: Type to check

        Returns:
            True if milestone exists
        """
        query = """
            SELECT EXISTS(
                SELECT 1 FROM ai_pipeline.authoring_milestones
                WHERE user_id = %s AND milestone_type = %s
            ) as has_milestone
        """
        try:
            result = AuthoringMilestonesRepository.fetch_one(query, (user_id, milestone_type))
            return result['has_milestone'] if result else False
        except Exception as e:
            logger.error(f"Error checking milestone: {e}")
            return False

    @staticmethod
    def get_user_badges(user_id: str) -> List[str]:
        """Get list of badges earned by user"""
        query = """
            SELECT DISTINCT badge_earned
            FROM ai_pipeline.authoring_milestones
            WHERE user_id = %s AND badge_earned IS NOT NULL
            ORDER BY badge_earned
        """
        try:
            results = AuthoringMilestonesRepository.fetch_all(query, (user_id,))
            return [r['badge_earned'] for r in results]
        except Exception as e:
            logger.error(f"Error fetching user badges: {e}")
            return []

    @staticmethod
    def get_milestone_statistics(user_id: str) -> Dict:
        """Get user's milestone statistics"""
        query = """
            SELECT
                COUNT(*) as total_milestones,
                COUNT(DISTINCT milestone_type) as unique_types,
                COUNT(DISTINCT badge_earned) as badges_earned,
                MIN(achieved_at) as first_milestone_at,
                MAX(achieved_at) as last_milestone_at
            FROM ai_pipeline.authoring_milestones
            WHERE user_id = %s
        """
        try:
            result = AuthoringMilestonesRepository.fetch_one(query, (user_id,))
            return result if result else {
                'total_milestones': 0,
                'unique_types': 0,
                'badges_earned': 0,
                'first_milestone_at': None,
                'last_milestone_at': None
            }
        except Exception as e:
            logger.error(f"Error fetching milestone statistics: {e}")
            return {
                'total_milestones': 0,
                'unique_types': 0,
                'badges_earned': 0,
                'first_milestone_at': None,
                'last_milestone_at': None
            }
