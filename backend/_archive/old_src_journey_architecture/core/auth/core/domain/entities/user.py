"""User Entity (DDD Domain Entity)

Represents a user in the system.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    User domain entity.
    
    Represents a user account with authentication, profile, and settings.
    
    Attributes:
        user_id: UUID
        email: User email address
        password_hash: Bcrypt hashed password
        firstname: User first name
        lastname: User last name
        role_id: Foreign key to roles table
        language: Preferred language (ISO 639-1 code)
        timezone: User timezone (IANA timezone)
        theme_preference: UI theme (system, light, dark)
        avatar_url: URL to user avatar image
        email_verified: Email verification status
        email_verified_at: Email verification timestamp
        two_factor_enabled: 2FA enabled flag
        two_factor_secret: TOTP secret for 2FA
        last_login: Last login timestamp
        last_login_ip: Last login IP address
        status: Account status (active, inactive, banned)
        banned_until: Ban expiration timestamp
        creator_verified: Creator verification status
        creator_verified_at: Creator verification timestamp
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp
    """
    
    user_id: str
    email: str
    password_hash: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    role_id: Optional[int] = None
    language: str = 'de'
    timezone: str = 'Europe/Berlin'
    theme_preference: str = 'dark'
    avatar_url: Optional[str] = None
    email_verified: bool = False
    email_verified_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    last_login: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    status: str = 'active'
    banned_until: Optional[datetime] = None
    creator_verified: bool = False
    creator_verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate entity constraints from DB schema."""
        # Validate theme_preference (CHECK constraint in DB)
        valid_themes = ('system', 'light', 'dark')
        if self.theme_preference not in valid_themes:
            raise ValueError(f"Invalid theme_preference: {self.theme_preference}")
        
        # Validate status
        valid_statuses = ('active', 'inactive', 'banned', 'pending', 'deactivated')
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}")
    
    def is_active(self) -> bool:
        """Check if user account is active."""
        if self.status != 'active':
            return False
        if self.banned_until and self.banned_until > datetime.utcnow():
            return False
        return True
    
    def is_verified(self) -> bool:
        """Check if user email is verified."""
        return self.email_verified
    
    def has_2fa(self) -> bool:
        """Check if user has 2FA enabled."""
        return self.two_factor_enabled and self.two_factor_secret is not None
    
    def enable_2fa(self, secret: str) -> None:
        """Enable 2FA for user."""
        self.two_factor_enabled = True
        self.two_factor_secret = secret
    
    def disable_2fa(self) -> None:
        """Disable 2FA for user."""
        self.two_factor_enabled = False
        self.two_factor_secret = None
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
    
    def update_last_login(self, ip_address: str) -> None:
        """Update last login timestamp and IP."""
        self.last_login = datetime.utcnow()
        self.last_login_ip = ip_address
    
    def ban(self, until: Optional[datetime] = None) -> None:
        """Ban user account."""
        self.status = 'banned'
        self.banned_until = until
    
    def unban(self) -> None:
        """Unban user account."""
        self.status = 'active'
        self.banned_until = None
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.status = 'deactivated'
    
    def reactivate(self) -> None:
        """Reactivate user account."""
        self.status = 'active'
