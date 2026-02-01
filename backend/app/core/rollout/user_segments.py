"""
User Segment-Based Rollout

Enable features for specific user segments (beta users, premium, etc.)
"""

from typing import List, Optional, Dict, Any
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class UserSegmentsRepository(BaseRepository):
    """Repository for user segments"""
    
    @staticmethod
    def get_user_segments(user_id: str) -> List[str]:
        """Get all segments a user belongs to"""
        query = """
            SELECT segment_name 
            FROM feature_flags.user_segments
            WHERE user_id = %s
        """
        results = UserSegmentsRepository.fetch_all(query, (user_id,))
        return [r['segment_name'] for r in results] if results else []


class UserSegments:
    """User segment management for feature rollout"""
    
    # Predefined segments
    SEGMENTS = {
        'beta_users': 'Users opted into beta program',
        'premium_users': 'Premium/paid subscribers',
        'internal': 'Internal team members',
        'educators': 'Teachers and educators',
        'enterprise': 'Enterprise organisation members',
        'early_adopters': 'Early adopters',
        'power_users': 'High-engagement users'
    }
    
    @staticmethod
    def is_in_segment(user_id: str, segment_name: str) -> bool:
        """Check if user is in a specific segment"""
        user_segments = UserSegmentsRepository.get_user_segments(user_id)
        return segment_name in user_segments
    
    @staticmethod
    def is_in_any_segment(user_id: str, segments: List[str]) -> bool:
        """Check if user is in any of the given segments"""
        user_segments = UserSegmentsRepository.get_user_segments(user_id)
        return any(seg in user_segments for seg in segments)
