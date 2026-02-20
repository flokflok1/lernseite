"""
User Segments Repository - Feature Flag System

Database access for user segment-based feature rollout.
"""

from typing import List
from app.infrastructure.persistence.repositories.core.base import BaseRepository


class UserSegmentsRepository(BaseRepository):
    """Repository for user segments in the feature flag system."""

    @staticmethod
    def get_user_segments(user_id: str) -> List[str]:
        """Get all segments a user belongs to."""
        query = """
            SELECT segment_name
            FROM feature_flags.user_segments
            WHERE user_id = %s
        """
        results = UserSegmentsRepository.fetch_all(query, (user_id,))
        return [r['segment_name'] for r in results] if results else []
