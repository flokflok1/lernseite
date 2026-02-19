"""
Social Notifications Repository

Database operations for notifications table.
Extracted from domain/social/notifications/ to comply with DDD repository rules.
"""

from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class SocialNotificationsRepository:
    """Repository for notifications table"""

    @staticmethod
    def create_notification(user_id: str, notification_type: str,
                            content: str,
                            reference_id: str = None) -> Optional[Dict[str, Any]]:
        """Create a notification."""
        query = """
            INSERT INTO notifications (user_id, notification_type, content, reference_id)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return fetch_one(
            query, (user_id, notification_type, content, reference_id)
        )

    @staticmethod
    def get_notifications(user_id: str,
                          limit: int = 20) -> List[Dict[str, Any]]:
        """Get user notifications ordered by recency."""
        query = """
            SELECT * FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return fetch_all(query, (user_id, limit))
