"""AI Job Entity"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AIJob:
    job_id: str
    user_id: str
    job_type: str
    status: str = 'pending'
    created_at: Optional[datetime] = None
