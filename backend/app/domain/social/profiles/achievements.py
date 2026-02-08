"""User Achievements & Badges"""

from typing import List, Dict, Any
from app.domain.ports.registry import repos


class AchievementsService:
    """Manage user achievements"""

    @staticmethod
    def get_achievements(user_id: str) -> List[Dict[str, Any]]:
        """Get user achievements"""
        query = "SELECT * FROM achievements WHERE user_id = %s ORDER BY earned_at DESC"
        return repos.query_runner.fetch_all(query, (user_id,))
