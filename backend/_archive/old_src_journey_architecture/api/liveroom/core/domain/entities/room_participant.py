"""RoomParticipant Entity"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

@dataclass
class RoomParticipant:
    """LiveRoom participant entity."""
    id: int
    room_id: int
    user_id: str
    role: str = 'student'
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    active: bool = True
    participation_score: Decimal = Decimal('0.00')

    def __post_init__(self):
        if self.role not in ('host', 'teacher', 'student', 'guest'):
            raise ValueError("Invalid role")
