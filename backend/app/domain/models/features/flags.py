"""
Pydantic Models for Feature Flags

Models for feature flag management
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FeatureFlagResponse(BaseModel):
    """Feature flag response"""
    name: str
    is_enabled: bool
    category: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FeatureFlagUpdate(BaseModel):
    """Update feature flag request"""
    is_enabled: bool


class RolloutConfigRequest(BaseModel):
    """Configure percentage rollout"""
    percentage: int = Field(..., ge=0, le=100)


class UserOverrideRequest(BaseModel):
    """User-specific override request"""
    user_id: str
    is_enabled: bool
    reason: Optional[str] = None


class OrgOverrideRequest(BaseModel):
    """Organization-specific override request"""
    organisation_id: str
    is_enabled: bool
    reason: Optional[str] = None
