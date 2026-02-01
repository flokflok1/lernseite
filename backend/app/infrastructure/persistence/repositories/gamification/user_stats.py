"""
User Gamification Stats Repository

Data access layer for gamification:
- User XP, Level, Gold, Skill Points
- User Skills (Strength, Intelligence, Stamina)
- Quests (from courses)
- Achievements

Uses pure psycopg for PostgreSQL access with connection pooling.
"""

from typing import Dict, Any, Optional, List
from psycopg.rows import dict_row

from app.core.bootstrap import extensions


class UserGamificationRepository:
    """
    User Gamification Repository for RPG-style gamification data

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def get_user_stats(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user gamification stats (XP, Level, Gold, Skill Points)

        Args:
            user_id: User identifier (UUID)

        Returns:
            Stats dictionary or None if not found
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        user_id,
                        total_xp,
                        current_level,
                        xp_to_next_level,
                        created_at,
                        updated_at
                    FROM gamification.user_xp
                    WHERE user_id = %s
                """, (user_id,))

                return cur.fetchone()

    @classmethod
    def get_user_skills(cls, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user skills (Strength, Intelligence, Stamina, etc.)

        Args:
            user_id: User identifier (UUID)

        Returns:
            List of skill dictionaries
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        skill_id,
                        user_id,
                        skill_name,
                        skill_category,
                        proficiency_level,
                        verified,
                        earned_at
                    FROM gamification.user_skills
                    WHERE user_id = %s
                    ORDER BY earned_at DESC
                """, (user_id,))

                return cur.fetchall()

    @classmethod
    def get_user_achievements(cls, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user achievements

        Args:
            user_id: User identifier (UUID)

        Returns:
            List of achievement dictionaries
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        achievement_id,
                        user_id,
                        achievement_type,
                        title,
                        description,
                        icon,
                        points,
                        earned_at
                    FROM gamification.user_achievements
                    WHERE user_id = %s
                    ORDER BY earned_at DESC
                """, (user_id,))

                return cur.fetchall()

    @classmethod
    def create_default_stats(cls, user_id: str) -> Dict[str, Any]:
        """
        Create default gamification stats for new user

        Args:
            user_id: User identifier (UUID)

        Returns:
            Created stats dictionary
        """
        with extensions.db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Insert default XP record
                cur.execute("""
                    INSERT INTO gamification.user_xp (
                        user_id, total_xp, current_level, xp_to_next_level
                    ) VALUES (%s, 0, 1, 100)
                    ON CONFLICT (user_id) DO NOTHING
                    RETURNING *
                """, (user_id,))

                result = cur.fetchone()
                conn.commit()

                return result or cls.get_user_stats(user_id)

    @classmethod
    def get_user_gamification_data(cls, user_id: str) -> Dict[str, Any]:
        """
        Get complete gamification data for user (stats + skills + achievements)

        Args:
            user_id: User identifier (UUID)

        Returns:
            Complete gamification data dictionary
        """
        # Get stats
        stats = cls.get_user_stats(user_id)

        # If no stats exist, create default
        if not stats:
            stats = cls.create_default_stats(user_id)

        # Get skills
        skills = cls.get_user_skills(user_id)

        # Get achievements
        achievements = cls.get_user_achievements(user_id)

        # Calculate base stats from skills (Strength, Intelligence, Stamina)
        base_stats = {
            'strength': 0,
            'intelligence': 0,
            'stamina': 0
        }

        # Count skills by category to determine base stats
        for skill in skills:
            category = skill.get('skill_category', '').lower()
            if 'strength' in category or 'code' in category:
                base_stats['strength'] += 1
            elif 'intelligence' in category or 'logic' in category:
                base_stats['intelligence'] += 1
            elif 'stamina' in category or 'endurance' in category:
                base_stats['stamina'] += 1

        return {
            'level': stats.get('current_level', 1),
            'xp': stats.get('total_xp', 0),
            'xpToNext': stats.get('xp_to_next_level', 100),
            'gold': 0,  # TODO: Add gold column to DB
            'skillPoints': 0,  # TODO: Calculate from level
            'baseStats': base_stats,
            'skills': skills,
            'achievements': achievements
        }
