"""Tutor Session Entity"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TutorSession:
    session_id: str
    user_id: str
    created_at: Optional[datetime] = None
