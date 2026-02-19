"""User Achievements & Badges"""

from typing import List, Dict, Any
from app.domain.ports.core.registry import repos


class AchievementsService:
    """Manage user achievements"""

    @staticmethod
    def get_achievements(user_id: str) -> List[Dict[str, Any]]:
        """Get user achievements"""
        return repos.users.get_achievements(user_id)
