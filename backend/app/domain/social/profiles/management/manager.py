"""User Profile Management"""

from typing import Dict, Any, Optional
from app.domain.ports.core.registry import repos


class ProfileManager:
    """Manage user profiles"""

    @staticmethod
    def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        return repos.users.find_by_id(user_id)

    @staticmethod
    def update_bio(user_id: str, bio: str) -> bool:
        """Update user bio"""
        return repos.users.update_bio(user_id, bio)
