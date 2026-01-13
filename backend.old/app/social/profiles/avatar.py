"""Profile Picture Management"""

class AvatarService:
    """Manage profile pictures"""
    
    @staticmethod
    def update_avatar(user_id: str, avatar_url: str) -> bool:
        """Update profile picture"""
        from app.repositories.user import UserRepository
        query = "UPDATE users SET profile_picture_url = %s WHERE user_id = %s"
        result = UserRepository.execute(query, (avatar_url, user_id))
        return result > 0
