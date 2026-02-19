"""
User Profile Preferences

Handles user profile settings like theme preferences, bio, avatar,
portfolio, and achievements.
"""

from typing import Optional, List, Dict, Any
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, execute_query

logger = logging.getLogger(__name__)


class UserProfileRepository(BaseRepository):
    """User profile and preference management"""

    table_name = 'core.users'
    pk_column = 'user_id'

    @classmethod
    def get_theme_preference(cls, user_id: str) -> str:
        """
        Get user's theme preference

        Args:
            user_id: User ID (UUID)

        Returns:
            Theme preference ('system', 'light', or 'dark')
            Returns 'dark' as fallback if not found

        Example:
            >>> theme = UserProfileRepository.get_theme_preference('user-uuid')
            >>> print(theme)  # 'dark'
        """
        user = fetch_one(
            "SELECT theme FROM core.users WHERE user_id = %s",
            (user_id,)
        )

        if user and user.get('theme'):
            return user['theme']

        # Fallback to 'dark' if user not found or theme is NULL
        return 'dark'

    @classmethod
    def update_theme_preference(cls, user_id: str, theme: str) -> str:
        """
        Update user's theme preference

        Args:
            user_id: User ID (UUID)
            theme: New theme preference ('system', 'light', or 'dark')

        Returns:
            Updated theme preference value

        Raises:
            ValueError: If theme is not one of the valid values

        Example:
            >>> new_theme = UserProfileRepository.update_theme_preference('user-uuid', 'light')
            >>> print(new_theme)  # 'light'
        """
        # Validate theme value (defensive check, already validated by Pydantic)
        valid_themes = ['system', 'light', 'dark']
        if theme not in valid_themes:
            raise ValueError(f'Theme must be one of: {", ".join(valid_themes)}')

        # Update theme
        result = execute_query(
            """
            UPDATE core.users
            SET theme = %s, updated_at = NOW()
            WHERE user_id = %s
            RETURNING theme
            """,
            (theme, user_id),
            fetch_one=True
        )

        if not result:
            raise ValueError(f'User with ID {user_id} not found')

        return result['theme']

    @classmethod
    def update_bio(cls, user_id: str, bio: str) -> bool:
        """Update user bio."""
        result = execute_query(
            "UPDATE users SET bio = %s WHERE user_id = %s",
            (bio, user_id)
        )
        return result is not None

    @classmethod
    def update_avatar(cls, user_id: str, avatar_url: str) -> bool:
        """Update user profile picture URL."""
        result = execute_query(
            "UPDATE users SET profile_picture_url = %s WHERE user_id = %s",
            (avatar_url, user_id)
        )
        return result is not None

    @classmethod
    def get_portfolio(cls, user_id: str) -> Dict[str, Any]:
        """Get user's learning portfolio stats."""
        query = """
            SELECT
                COUNT(DISTINCT e.course_id) as courses_count,
                COUNT(DISTINCT c.certificate_id) as certificates_count
            FROM enrollments e
            LEFT JOIN certificates c ON e.enrollment_id = c.enrollment_id
            WHERE e.user_id = %s
        """
        return fetch_one(query, (user_id,)) or {}

    @classmethod
    def get_achievements(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get user achievements ordered by recency."""
        query = "SELECT * FROM achievements WHERE user_id = %s ORDER BY earned_at DESC"
        from app.infrastructure.persistence.database.connection import fetch_all
        return fetch_all(query, (user_id,))
