"""
Gamification Repository

Handles database operations for gamification system (XP, levels, RPG stats).
"""
import psycopg
from typing import Optional, Dict, Any


class GamificationRepository:
    """Repository for gamification data (XP, levels, RPG stats)."""

    def __init__(self, connection: psycopg.Connection):
        """
        Initialize repository.

        Args:
            connection: Database connection
        """
        self.connection = connection

    def get_user_gamification_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete gamification data for a user.

        Args:
            user_id: User UUID

        Returns:
            Dict with gamification data or None if not found
        """
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    total_xp,
                    current_level,
                    xp_to_next_level,
                    strength,
                    intelligence,
                    stamina,
                    gold,
                    skill_points
                FROM gamification.user_xp
                WHERE user_id = %s
            """, (user_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                'xp': row[0],
                'level': row[1],
                'xpToNext': row[2],
                'baseStats': {
                    'strength': row[3],
                    'intelligence': row[4],
                    'stamina': row[5]
                },
                'gold': row[6],
                'skillPoints': row[7]
            }

    def get_or_create_user_gamification(self, user_id: str) -> Dict[str, Any]:
        """
        Get user gamification data, create default entry if doesn't exist.

        Args:
            user_id: User UUID

        Returns:
            Dict with gamification data
        """
        # Try to get existing data
        data = self.get_user_gamification_data(user_id)
        if data:
            return data

        # Create default entry
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO gamification.user_xp (
                    user_id,
                    total_xp,
                    current_level,
                    xp_to_next_level,
                    strength,
                    intelligence,
                    stamina,
                    gold,
                    skill_points
                ) VALUES (%s, 0, 1, 100, 0, 0, 0, 0, 0)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id,))
            self.connection.commit()

        # Return default data
        return {
            'xp': 0,
            'level': 1,
            'xpToNext': 100,
            'baseStats': {
                'strength': 0,
                'intelligence': 0,
                'stamina': 0
            },
            'gold': 0,
            'skillPoints': 0
        }

    def update_user_stats(
        self,
        user_id: str,
        strength: Optional[int] = None,
        intelligence: Optional[int] = None,
        stamina: Optional[int] = None,
        gold: Optional[int] = None,
        skill_points: Optional[int] = None
    ) -> bool:
        """
        Update user RPG stats.

        Args:
            user_id: User UUID
            strength: New strength value (optional)
            intelligence: New intelligence value (optional)
            stamina: New stamina value (optional)
            gold: New gold value (optional)
            skill_points: New skill points value (optional)

        Returns:
            True if updated successfully
        """
        updates = []
        params = []

        if strength is not None:
            updates.append("strength = %s")
            params.append(strength)
        if intelligence is not None:
            updates.append("intelligence = %s")
            params.append(intelligence)
        if stamina is not None:
            updates.append("stamina = %s")
            params.append(stamina)
        if gold is not None:
            updates.append("gold = %s")
            params.append(gold)
        if skill_points is not None:
            updates.append("skill_points = %s")
            params.append(skill_points)

        if not updates:
            return False

        params.append(user_id)

        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE gamification.user_xp
                SET {', '.join(updates)}
                WHERE user_id = %s
            """, params)
            self.connection.commit()

        return True


__all__ = ['GamificationRepository']
