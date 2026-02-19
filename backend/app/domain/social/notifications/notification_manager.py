"""Notification Management"""

from typing import List, Dict, Any
from app.domain.ports.core.registry import repos


class NotificationManager:
    """Manage user notifications"""

    @staticmethod
    def create_notification(user_id: str, notification_type: str,
                           content: str, reference_id: str = None) -> Dict[str, Any]:
        """Create notification"""
        return repos.social_notifications.create_notification(
            user_id, notification_type, content, reference_id
        )

    @staticmethod
    def get_notifications(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user notifications"""
        return repos.social_notifications.get_notifications(user_id, limit)
