"""User Profile Management"""

from typing import Dict, Any, Optional
from app.infrastructure.persistence.repositories.user import UserRepository


class ProfileManager:
    """Manage user profiles"""
    
    @staticmethod
    def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        return UserRepository.find_by_id(user_id)
    
    @staticmethod
    def update_bio(user_id: str, bio: str) -> bool:
        """Update user bio"""
        query = "UPDATE users SET bio = %s WHERE user_id = %s"
        result = UserRepository.execute(query, (bio, user_id))
        return result > 0
