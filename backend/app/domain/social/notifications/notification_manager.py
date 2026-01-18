"""Notification Management"""

from typing import List, Dict, Any


class NotificationManager:
    """Manage user notifications"""
    
    @staticmethod
    def create_notification(user_id: str, notification_type: str, 
                           content: str, reference_id: str = None) -> Dict[str, Any]:
        """Create notification"""
        from app.repositories.base_repository import BaseRepository
        query = """
            INSERT INTO notifications (user_id, notification_type, content, reference_id)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return BaseRepository.fetch_one(query, (user_id, notification_type, content, reference_id))
    
    @staticmethod
    def get_notifications(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user notifications"""
        from app.repositories.base_repository import BaseRepository
        query = """
            SELECT * FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        return BaseRepository.fetch_all(query, (user_id, limit))
