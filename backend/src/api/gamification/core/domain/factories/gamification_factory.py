"""
Gamification Domain - Factories

DDD Factory Pattern for creating gamification aggregates with business rules validation.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class QuestFactory:
    """Factory for creating Quest aggregates"""

    VALID_QUEST_TYPES = ['daily', 'weekly', 'achievement', 'course', 'challenge']

    @staticmethod
    def create_daily_quest(title: str, description: str, criteria: dict, reward_xp: int = 100) -> Dict[str, Any]:
        """Create a daily quest (expires in 24h)"""
        if not title or not criteria:
            raise ValueError("title and criteria are required")

        return {
            'quest_type': 'daily',
            'title': title,
            'description': description,
            'criteria': criteria,
            'reward_xp': reward_xp,
            'reward_tokens': 0,
            'expires_at': datetime.utcnow() + timedelta(days=1),
            'is_active': True
        }

    @staticmethod
    def create_weekly_quest(title: str, description: str, criteria: dict, reward_xp: int = 500) -> Dict[str, Any]:
        """Create a weekly quest (expires in 7 days)"""
        if not title or not criteria:
            raise ValueError("title and criteria are required")

        return {
            'quest_type': 'weekly',
            'title': title,
            'description': description,
            'criteria': criteria,
            'reward_xp': reward_xp,
            'reward_tokens': 50,
            'expires_at': datetime.utcnow() + timedelta(days=7),
            'is_active': True
        }


class AchievementFactory:
    """Factory for creating Achievement aggregates"""

    @staticmethod
    def create(achievement_type: str, name: str, description: str, criteria: dict,
               reward_xp: int, icon: str = 'trophy') -> Dict[str, Any]:
        """Create an achievement"""
        if achievement_type not in ['bronze', 'silver', 'gold', 'platinum']:
            raise ValueError("Invalid achievement type")
        if not name or not criteria:
            raise ValueError("name and criteria are required")
        if reward_xp < 0:
            raise ValueError("reward_xp must be non-negative")

        return {
            'achievement_type': achievement_type,
            'name': name,
            'description': description,
            'criteria': criteria,
            'reward_xp': reward_xp,
            'icon': icon,
            'is_active': True
        }
