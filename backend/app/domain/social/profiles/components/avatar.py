"""Profile Picture Management"""

from app.domain.ports.core.registry import repos


class AvatarService:
    """Manage profile pictures"""

    @staticmethod
    def update_avatar(user_id: str, avatar_url: str) -> bool:
        """Update profile picture"""
        query = "UPDATE users SET profile_picture_url = %s WHERE user_id = %s"
        result = repos.users.execute(query, (avatar_url, user_id))
        return result > 0
