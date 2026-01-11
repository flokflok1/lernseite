"""
Gamification Domain

Domain for gamification systems (XP/Quests, Daily Recall, Adaptive Difficulty).

Features:
1. XP & Quest System - Experience points, levels, quests, achievements
2. Daily Recall - Spaced repetition system using SM2 algorithm
3. Adaptive Difficulty - ELO-based difficulty rating

Journeys:
- Admin Journey: Quest & Achievement management (3 endpoints)
- User Journey: XP/Quests, Daily Recall, Adaptive Difficulty (10 endpoints)

Total: 13 Endpoints

Phase: 5.3.3 - Gamification Domain Implementation
"""

from .journeys import ALL_JOURNEY_BLUEPRINTS

__all__ = ['ALL_JOURNEY_BLUEPRINTS']
