"""
Feedback Attachment Entity (DDD Domain Entity)

Represents file attachments for user feedback (e.g., screenshots).
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FeedbackAttachment:
    """
    Feedback Attachment domain entity.

    Tracks file attachments with AI screenshot detection.

    Attributes:
        attachment_id: UUID
        feedback_id: Parent feedback UUID
        file_name: Original file name
        file_type: MIME type
        file_size: File size in bytes
        file_path: Storage path
        is_screenshot: Whether file is detected as screenshot
        ai_screenshot_description: AI-generated description of screenshot
        created_at: Upload timestamp
    """

    attachment_id: str
    feedback_id: str
    file_name: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    is_screenshot: bool = False
    ai_screenshot_description: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate feedback attachment entity."""
        if not self.attachment_id or not self.attachment_id.strip():
            raise ValueError("Attachment ID cannot be empty")

        if not self.feedback_id or not self.feedback_id.strip():
            raise ValueError("Feedback ID cannot be empty")

        if not self.file_name or not self.file_name.strip():
            raise ValueError("File name cannot be empty")

        if not self.file_path or not self.file_path.strip():
            raise ValueError("File path cannot be empty")

        if self.file_size is not None and self.file_size < 0:
            raise ValueError("File size cannot be negative")

    def is_image(self) -> bool:
        """Check if attachment is an image."""
        if not self.file_type:
            return False

        image_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
        return self.file_type.lower() in image_types

    def is_pdf(self) -> bool:
        """Check if attachment is a PDF."""
        return self.file_type == 'application/pdf' if self.file_type else False

    def is_video(self) -> bool:
        """Check if attachment is a video."""
        if not self.file_type:
            return False

        return self.file_type.startswith('video/')

    def get_file_size_mb(self) -> Optional[float]:
        """
        Get file size in megabytes.

        Returns:
            File size in MB or None if size not available
        """
        if self.file_size is None:
            return None

        return self.file_size / (1024 * 1024)

    def get_file_extension(self) -> Optional[str]:
        """Get file extension from filename."""
        if '.' not in self.file_name:
            return None

        return self.file_name.rsplit('.', 1)[1].lower()

    def has_ai_description(self) -> bool:
        """Check if AI screenshot description is available."""
        return self.ai_screenshot_description is not None

    def mark_as_screenshot(self, ai_description: Optional[str] = None) -> None:
        """Mark attachment as screenshot with optional AI description."""
        self.is_screenshot = True
        if ai_description:
            self.ai_screenshot_description = ai_description
