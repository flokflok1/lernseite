"""UserSession Entity (DDD Domain Entity)

Represents a user authentication session.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserSession:
    """
    User session domain entity.
    
    Tracks user authentication sessions with JWT tokens.
    
    Attributes:
        session_id: UUID
        user_id: User UUID reference
        jti: JWT ID (unique identifier for token)
        refresh_token_hash: Hashed refresh token
        ip_address: Client IP address
        user_agent: Browser user agent string
        device_info: Device information (JSONB)
        expires_at: Session expiration timestamp
        revoked: Session revocation status
        revoked_at: Revocation timestamp
        created_at: Session creation timestamp
    """
    
    session_id: str
    user_id: str
    jti: str
    refresh_token_hash: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[dict] = None
    expires_at: datetime = None
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if session is valid (not expired, not revoked)."""
        if self.revoked:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def revoke(self) -> None:
        """Revoke this session."""
        self.revoked = True
        self.revoked_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if not self.expires_at:
            return False
        return self.expires_at < datetime.utcnow()
