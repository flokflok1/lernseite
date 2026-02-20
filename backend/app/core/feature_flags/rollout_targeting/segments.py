"""
User Segment-Based Rollout

Enable features for specific user segments (beta users, premium, etc.)
"""

from typing import List
from app.infrastructure.persistence.repositories.feature_flags.segments import UserSegmentsRepository


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
