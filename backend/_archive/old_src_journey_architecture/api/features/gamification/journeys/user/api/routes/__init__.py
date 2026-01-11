"""Gamification Domain - User Journey API Routes"""
from .xp_quests import xp_quests_user_bp
from .daily_recall import daily_recall_user_bp
from .adaptive_difficulty import adaptive_difficulty_user_bp

__all__ = ['xp_quests_user_bp', 'daily_recall_user_bp', 'adaptive_difficulty_user_bp']
