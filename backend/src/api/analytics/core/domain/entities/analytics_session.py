"""
Analytics Session Entity (DDD Domain Entity)

Represents a user session for analytics tracking.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnalyticsSession:
    """
    Analytics Session domain entity.

    Tracks user sessions with device info, location, and activity.

    Attributes:
        session_id: UUID
        user_id: User UUID (optional for anonymous)
        organization_id: Organization UUID (optional)
        session_token: Session token
        ip_address_hash: Hashed IP address (privacy)
        user_agent: Browser user agent string
        device_type: Device type (desktop, mobile, tablet, unknown)
        browser: Browser name
        os: Operating system
        country: Country code (2 letters)
        city: City name
        started_at: Session start timestamp
        last_activity_at: Last activity timestamp
        ended_at: Session end timestamp (NULL if active)
        duration_seconds: Session duration in seconds
        page_views: Number of page views in session
    """

    session_id: str
    session_token: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    ip_address_hash: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: str = 'unknown'
    browser: Optional[str] = None
    os: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    started_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    page_views: int = 0

    def __post_init__(self):
        """Validate analytics session entity."""
        if not self.session_id or not self.session_id.strip():
            raise ValueError("Session ID cannot be empty")
        if self.device_type not in ('desktop', 'mobile', 'tablet', 'unknown'):
            raise ValueError("Invalid device type")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("Duration cannot be negative")
        if self.page_views < 0:
            raise ValueError("Page views cannot be negative")

    def record_page_view(self) -> None:
        """Record a page view in this session."""
        self.page_views += 1
        self.last_activity_at = datetime.utcnow()

    def end_session(self) -> None:
        """
        End this session and calculate duration.

        Raises:
            ValueError: If session already ended
        """
        if self.ended_at:
            raise ValueError("Session already ended")

        self.ended_at = datetime.utcnow()

        if self.started_at:
            duration = (self.ended_at - self.started_at).total_seconds()
            self.duration_seconds = int(duration)

    def is_active(self) -> bool:
        """Check if session is still active."""
        return self.ended_at is None

    def is_mobile(self) -> bool:
        """Check if session is from mobile device."""
        return self.device_type == 'mobile'

    def is_desktop(self) -> bool:
        """Check if session is from desktop."""
        return self.device_type == 'desktop'

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()

    def get_duration_minutes(self) -> Optional[float]:
        """
        Get session duration in minutes.

        Returns:
            Duration in minutes or None if not ended
        """
        if not self.duration_seconds:
            return None
        return self.duration_seconds / 60.0
