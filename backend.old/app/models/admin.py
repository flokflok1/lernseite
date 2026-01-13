"""
LernsystemX Admin Models

Pydantic models for admin operations validation and serialization.

Phase B24 - Admin System
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Valid user roles"""
    FREE = 'free'
    PREMIUM = 'premium'
    CREATOR = 'creator'
    TEACHER = 'teacher'
    SCHOOL = 'school'
    COMPANY = 'company'
    SUPPORT = 'support'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class UserStatus(str, Enum):
    """Valid user statuses"""
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    BANNED = 'banned'
    DELETED = 'deleted'


# ============================================================================
# Request Models
# ============================================================================

class RoleChangeRequest(BaseModel):
    """Request to change user role"""
    role: UserRole = Field(..., description="New role for the user")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for role change")


class BanUserRequest(BaseModel):
    """Request to ban a user"""
    reason: str = Field(..., min_length=10, max_length=1000, description="Reason for ban")
    duration_days: Optional[int] = Field(None, ge=1, le=365, description="Ban duration in days (if not permanent)")
    permanent: bool = Field(default=False, description="Permanent ban")
    notify_user: bool = Field(default=True, description="Send email notification to user")

    @validator('duration_days')
    def validate_duration(cls, v, values):
        """Ensure duration_days is None if permanent is True"""
        if values.get('permanent') and v is not None:
            raise ValueError('Cannot set duration_days for permanent bans')
        if not values.get('permanent') and v is None:
            raise ValueError('duration_days required for non-permanent bans')
        return v


class GrantTokensRequest(BaseModel):
    """Request to grant tokens to a user"""
    amount: int = Field(..., ge=1, le=1000000, description="Number of tokens to grant")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for granting tokens")


class ModerateContentRequest(BaseModel):
    """Request to moderate content"""
    action: str = Field(..., description="Action to take (approve, reject, ban)")
    reason: str = Field(..., min_length=10, max_length=1000, description="Reason for moderation action")
    notify_creator: bool = Field(default=True, description="Notify content creator")

    @validator('action')
    def validate_action(cls, v):
        """Validate moderation action"""
        valid_actions = ['approve', 'reject', 'ban', 'feature', 'unfeature']
        if v not in valid_actions:
            raise ValueError(f'Invalid action. Must be one of: {", ".join(valid_actions)}')
        return v


# ============================================================================
# Response Models
# ============================================================================

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class UserListItem(BaseModel):
    """User item in list view"""
    user_id: str
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    role: str
    status: str
    created_at: datetime
    last_login: Optional[datetime]
    email_verified: bool
    organization_id: Optional[str]


class UserListResponse(BaseModel):
    """Response for user list endpoint"""
    success: bool = True
    users: List[UserListItem]
    pagination: PaginationMeta


class SubscriptionInfo(BaseModel):
    """User subscription information"""
    plan: str
    status: str
    expires_at: Optional[datetime]
    auto_renew: bool = False


class TokenInfo(BaseModel):
    """User token information"""
    balance: int
    total_used: int
    total_granted: int
    total_purchased: int


class UserDetailResponse(BaseModel):
    """Detailed user information"""
    user_id: str
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    last_login_ip: Optional[str]
    email_verified: bool
    two_factor_enabled: bool
    organization_id: Optional[str]
    subscription: Optional[SubscriptionInfo]
    tokens: Optional[TokenInfo]
    courses_created: int = 0
    courses_enrolled: int = 0
    login_history: List[Dict[str, Any]] = []
    ban_history: List[Dict[str, Any]] = []


class AdminActionResponse(BaseModel):
    """Generic admin action response"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# Audit Log Models
# ============================================================================

class AuditLogEntry(BaseModel):
    """Audit log entry"""
    log_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    severity: str
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Response for audit log list"""
    success: bool = True
    logs: List[AuditLogEntry]
    pagination: PaginationMeta


# ============================================================================
# System Stats Models
# ============================================================================

class SystemStats(BaseModel):
    """System-wide statistics"""
    total_users: int
    active_users_7_days: int
    active_users_30_days: int
    total_organisations: int
    total_courses: int
    published_courses: int
    premium_subscriptions: int
    total_tokens_available: int
    total_tokens_used: int
    tokens_used_30_days: int


class DashboardStats(BaseModel):
    """Admin dashboard statistics"""
    system: SystemStats
    recent_signups: int
    recent_logins: int
    pending_moderation: int
    open_support_tickets: int


# ============================================================================
# Phase 2.1 - Admin Dashboard Stats Models
# ============================================================================

class UserStatsResponse(BaseModel):
    """User statistics for admin dashboard"""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Currently active users (last 7 days)")
    banned_users: int = Field(..., description="Number of banned users")
    new_users_30d: int = Field(..., description="New users in last 30 days")


class CourseStatsResponse(BaseModel):
    """Course statistics for admin dashboard"""
    total_courses: int = Field(..., description="Total number of courses")
    published: int = Field(..., description="Published courses")
    pending_review: int = Field(..., description="Courses pending review")
    rejected: int = Field(..., description="Rejected courses")


class SystemStatsResponse(BaseModel):
    """System statistics for admin dashboard"""
    uptime: float = Field(..., description="System uptime in seconds")
    db_latency: float = Field(..., description="Database latency in ms")
    request_count_24h: int = Field(..., description="API requests in last 24 hours")
    error_rate: float = Field(..., description="Error rate percentage (0-100)")
