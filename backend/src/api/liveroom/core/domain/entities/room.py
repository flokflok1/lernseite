"""Room Entity (DDD Domain Entity)"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Room:
    """LiveRoom virtual classroom entity."""
    id: int
    org_id: str
    name: str
    room_type: str
    status: str = 'active'
    course_id: Optional[str] = None
    chapter_id: Optional[str] = None
    created_by: Optional[str] = None
    description: Optional[str] = None
    max_participants: int = 50
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    enable_ai: bool = False
    enable_recording: bool = False
    ai_model: Optional[str] = None
    ai_pipeline_version: Optional[str] = None
    access_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.room_type not in ('classroom', 'seminar', 'study', 'exam', 'ai'):
            raise ValueError("Invalid room type")
        if self.status not in ('active', 'closed', 'archived'):
            raise ValueError("Invalid status")

    def is_active(self) -> bool:
        return self.status == 'active'
