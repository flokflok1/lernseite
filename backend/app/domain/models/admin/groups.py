"""
LernsystemX Admin Groups Models

Pydantic models for GBA 2.0 (Custom Groups & Feature Assignments).

Phase 5.3 - Owner-Admin & Dynamic Groups System
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GroupTemplate(str, Enum):
    """Predefined group templates"""
    PARENT = 'parent'
    ENTERPRISE_ADMIN = 'enterprise_admin'
    AUDITOR = 'auditor'
    LIBRARIAN = 'librarian'
    COURSE_MANAGER = 'course_manager'


# ============================================================================
# Request Models
# ============================================================================

class CreateGroupRequest(BaseModel):
    """Request to create a custom group"""
    group_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique group name (lowercase, no spaces)",
        pattern=r'^[a-z][a-z0-9_]*$'
    )
    display_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Display name for the group"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Group description"
    )
    hierarchy_level: int = Field(
        ...,
        ge=1,
        le=8,
        description="Hierarchy level (1-8, level 9 reserved for admin)"
    )
    color: Optional[str] = Field(
        '#6b7280',
        pattern=r'^#[0-9a-fA-F]{6}$',
        description="Color for group badge (hex format)"
    )
    icon: Optional[str] = Field(
        '👤',
        max_length=10,
        description="Icon/emoji for group"
    )
    feature_ids: List[int] = Field(
        default_factory=list,
        description="List of feature IDs to assign to this group"
    )
    permission_ids: List[int] = Field(
        default_factory=list,
        description="List of permission IDs to assign to this group"
    )

    @field_validator('group_name')
    @classmethod
    def validate_group_name(cls, v):
        """Ensure group name doesn't conflict with system groups"""
        system_groups = [
            'free', 'premium', 'creator', 'teacher',
            'school_admin', 'company_admin', 'support',
            'moderator', 'admin'
        ]
        if v in system_groups:
            raise ValueError(
                f'Group name "{v}" is reserved for system groups'
            )
        return v

    @field_validator('hierarchy_level')
    @classmethod
    def validate_hierarchy(cls, v):
        """Ensure hierarchy level is not 9 (reserved for admin)"""
        if v >= 9:
            raise ValueError(
                'Hierarchy level 9 is reserved for admin group'
            )
        return v


class UpdateGroupRequest(BaseModel):
    """Request to update a custom group"""
    display_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Display name for the group"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Group description"
    )
    hierarchy_level: Optional[int] = Field(
        None,
        ge=1,
        le=8,
        description="Hierarchy level (1-8)"
    )
    color: Optional[str] = Field(
        None,
        pattern=r'^#[0-9a-fA-F]{6}$',
        description="Color for group badge"
    )
    icon: Optional[str] = Field(
        None,
        max_length=10,
        description="Icon/emoji for group"
    )

    @field_validator('hierarchy_level')
    @classmethod
    def validate_hierarchy(cls, v):
        """Ensure hierarchy level is not 9 (reserved for admin)"""
        if v is not None and v >= 9:
            raise ValueError(
                'Hierarchy level 9 is reserved for admin group'
            )
        return v


class AssignFeaturesRequest(BaseModel):
    """Request to assign features to a group"""
    feature_ids: List[int] = Field(
        ...,
        description="List of feature IDs to assign"
    )
    replace: bool = Field(
        default=False,
        description="Replace all existing features (true) or add to existing (false)"
    )


class AssignPermissionsRequest(BaseModel):
    """Request to assign permissions to a group"""
    permission_ids: List[int] = Field(
        ...,
        description="List of permission IDs to assign"
    )
    replace: bool = Field(
        default=False,
        description="Replace all existing permissions (true) or add to existing (false)"
    )


class CreateFromTemplateRequest(BaseModel):
    """Request to create a group from a template"""
    template: GroupTemplate = Field(
        ...,
        description="Template to use"
    )
    group_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique group name (lowercase, no spaces)",
        pattern=r'^[a-z][a-z0-9_]*$'
    )
    display_name: Optional[str] = Field(
        None,
        description="Override display name (uses template default if not provided)"
    )
    customize_features: Optional[List[int]] = Field(
        None,
        description="Override feature IDs (uses template defaults if not provided)"
    )

    @field_validator('group_name')
    @classmethod
    def validate_group_name(cls, v):
        """Ensure group name doesn't conflict with system groups"""
        system_groups = [
            'free', 'premium', 'creator', 'teacher',
            'school_admin', 'company_admin', 'support',
            'moderator', 'admin'
        ]
        if v in system_groups:
            raise ValueError(
                f'Group name "{v}" is reserved for system groups'
            )
        return v


# ============================================================================
# Response Models
# ============================================================================

class FeatureResponse(BaseModel):
    """System feature response"""
    feature_id: int
    feature_code: str
    feature_name: str
    category: str
    active: bool
    enabled_for_group: Optional[bool] = None  # If included in group context


class PermissionResponse(BaseModel):
    """Permission response"""
    permission_id: int
    permission_key: str
    display_name: Optional[str]
    description: Optional[str]
    module: Optional[str]
    category: Optional[str]


class GroupResponse(BaseModel):
    """Group response with details"""
    group_id: int
    group_name: str
    display_name: str
    description: Optional[str]
    hierarchy_level: int
    color: str
    icon: str
    is_system: bool
    is_custom: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None  # UUID as string
    feature_count: Optional[int] = None
    permission_count: Optional[int] = None


class GroupDetailResponse(GroupResponse):
    """Detailed group response with features and permissions"""
    features: List[FeatureResponse]
    permissions: List[PermissionResponse]
    user_count: Optional[int] = None  # Number of users in this group


class GroupTemplateResponse(BaseModel):
    """Group template response"""
    template: GroupTemplate
    display_name: str
    description: str
    recommended_hierarchy: int
    default_features: List[str]  # Feature codes
    default_color: str
    default_icon: str


class DeleteGroupResponse(BaseModel):
    """Response after deleting a group"""
    success: bool
    message: str
    affected_users: int
    reassigned_to_group: Optional[str] = None


# ============================================================================
# Filter/Query Models
# ============================================================================

class GroupFilterParams(BaseModel):
    """Query parameters for filtering groups"""
    is_custom: Optional[bool] = Field(
        None,
        description="Filter by custom groups (true) or system groups (false)"
    )
    hierarchy_min: Optional[int] = Field(
        None,
        ge=1,
        le=9,
        description="Minimum hierarchy level"
    )
    hierarchy_max: Optional[int] = Field(
        None,
        ge=1,
        le=9,
        description="Maximum hierarchy level"
    )
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Search in group name or display name"
    )
    include_features: bool = Field(
        default=False,
        description="Include feature assignments in response"
    )
    include_permissions: bool = Field(
        default=False,
        description="Include permission assignments in response"
    )
