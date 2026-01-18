"""
Gamification Repository Package

Data access layer for gamification operations:
- User stats (XP, Level, Gold)
- User skills (Strength, Intelligence, Stamina)
- User achievements
- Quest tracking

Uses pure psycopg for PostgreSQL access.
"""

from app.infrastructure.persistence.repositories.gamification.user_stats import UserGamificationRepository

__all__ = ['UserGamificationRepository']
