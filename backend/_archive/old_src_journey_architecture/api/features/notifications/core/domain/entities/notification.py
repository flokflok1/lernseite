"""Notification Entity"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Notification:
    """User notification entity."""
    notification_id: str
    user_id: str
    type: str
    title: str
    message: str
    read: bool = False
    created_at: Optional[datetime] = None
    
    def mark_as_read(self) -> None:
        self.read = True
