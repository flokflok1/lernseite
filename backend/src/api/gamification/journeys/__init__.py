"""Gamification Domain - All Journeys"""

from .admin import quest_management_bp
from .user import xp_quests_user_bp, daily_recall_user_bp, adaptive_difficulty_user_bp

ALL_JOURNEY_BLUEPRINTS = [
    # Admin Journey (3 endpoints)
    quest_management_bp,

    # User Journey (10 endpoints)
    xp_quests_user_bp,  # 5 endpoints (profile, quests, start, complete, achievements)
    daily_recall_user_bp,  # 3 endpoints (due, review, stats)
    adaptive_difficulty_user_bp,  # 2 endpoints (get, update)
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'quest_management_bp',
    'xp_quests_user_bp',
    'daily_recall_user_bp',
    'adaptive_difficulty_user_bp',
]
