"""Profile Picture Management"""

from app.domain.ports.core.registry import repos


class AvatarService:
    """Manage profile pictures"""

    @staticmethod
    def update_avatar(user_id: str, avatar_url: str) -> bool:
        """Update profile picture"""
        return repos.users.update_avatar(user_id, avatar_url)
