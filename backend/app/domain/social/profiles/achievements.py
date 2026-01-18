"""User Achievements & Badges"""

from typing import List, Dict, Any


class AchievementsService:
    """Manage user achievements"""
    
    @staticmethod
    def get_achievements(user_id: str) -> List[Dict[str, Any]]:
        """Get user achievements"""
        from app.repositories.base_repository import BaseRepository
        query = "SELECT * FROM achievements WHERE user_id = %s ORDER BY earned_at DESC"
        return BaseRepository.fetch_all(query, (user_id,))
