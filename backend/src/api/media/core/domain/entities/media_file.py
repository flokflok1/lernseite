"""Media File Entity"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class MediaFile:
    file_id: str
    user_id: str
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    mime_type: Optional[str] = None
    duration: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def is_audio(self) -> bool:
        return self.file_type.startswith('audio/')
    
    def is_video(self) -> bool:
        return self.file_type.startswith('video/')
