"""
LernsystemX Admin Roles Models

Pydantic models for RBAC 2.0 (Custom Roles & Feature Assignments).

Phase 5.3 - Owner-Admin & Dynamic Roles System
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RoleTemplate(str, Enum):
    """Predefined role templates"""
    PARENT = 'parent'
    ENTERPRISE_ADMIN = 'enterprise_admin'
    AUDITOR = 'auditor'
    LIBRARIAN = 'librarian'
    COURSE_MANAGER = 'course_manager'


# ============================================================================
# Request Models
# ============================================================================

class CreateRoleRequest(BaseModel):
    """Request to create a custom role"""
    role_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique role name (lowercase, no spaces)",
        pattern=r'^[a-z][a-z0-9_]*$'
    )
    display_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Display name for the role"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Role description"
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
        description="Color for role badge (hex format)"
    )
    icon: Optional[str] = Field(
        '👤',
        max_length=10,
        description="Icon/emoji for role"
    )
    feature_ids: List[int] = Field(
        default_factory=list,
        description="List of feature IDs to assign to this role"
    )
    permission_ids: List[int] = Field(
        default_factory=list,
        description="List of permission IDs to assign to this role"
    )

    @field_validator('role_name')
    @classmethod
    def validate_role_name(cls, v):
        """Ensure role name doesn't conflict with system roles"""
        system_roles = [
            'free', 'premium', 'creator', 'teacher',
            'school_admin', 'company_admin', 'support',
            'moderator', 'admin'
        ]
        if v in system_roles:
            raise ValueError(
                f'Role name "{v}" is reserved for system roles'
            )
        return v

    @field_validator('hierarchy_level')
    @classmethod
    def validate_hierarchy(cls, v):
        """Ensure hierarchy level is not 9 (reserved for admin)"""
        if v >= 9:
            raise ValueError(
                'Hierarchy level 9 is reserved for admin role'
            )
        return v


class UpdateRoleRequest(BaseModel):
    """Request to update a custom role"""
    display_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Display name for the role"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Role description"
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
        description="Color for role badge"
    )
    icon: Optional[str] = Field(
        None,
        max_length=10,
        description="Icon/emoji for role"
    )

    @field_validator('hierarchy_level')
    @classmethod
    def validate_hierarchy(cls, v):
        """Ensure hierarchy level is not 9 (reserved for admin)"""
        if v is not None and v >= 9:
            raise ValueError(
                'Hierarchy level 9 is reserved for admin role'
            )
        return v


class AssignFeaturesRequest(BaseModel):
    """Request to assign features to a role"""
    feature_ids: List[int] = Field(
        ...,
        description="List of feature IDs to assign"
    )
    replace: bool = Field(
        default=False,
        description="Replace all existing features (true) or add to existing (false)"
    )


class AssignPermissionsRequest(BaseModel):
    """Request to assign permissions to a role"""
    permission_ids: List[int] = Field(
        ...,
        description="List of permission IDs to assign"
    )
    replace: bool = Field(
        default=False,
        description="Replace all existing permissions (true) or add to existing (false)"
    )


class CreateFromTemplateRequest(BaseModel):
    """Request to create a role from a template"""
    template: RoleTemplate = Field(
        ...,
        description="Template to use"
    )
    role_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique role name (lowercase, no spaces)",
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

    @field_validator('role_name')
    @classmethod
    def validate_role_name(cls, v):
        """Ensure role name doesn't conflict with system roles"""
        system_roles = [
            'free', 'premium', 'creator', 'teacher',
            'school_admin', 'company_admin', 'support',
            'moderator', 'admin'
        ]
        if v in system_roles:
            raise ValueError(
                f'Role name "{v}" is reserved for system roles'
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
    enabled_for_role: Optional[bool] = None  # If included in role context


class PermissionResponse(BaseModel):
    """Permission response"""
    permission_id: int
    permission_key: str
    display_name: Optional[str]
    description: Optional[str]
    module: Optional[str]
    category: Optional[str]


class RoleResponse(BaseModel):
    """Role response with details"""
    role_id: int
    role_name: str
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


class RoleDetailResponse(RoleResponse):
    """Detailed role response with features and permissions"""
    features: List[FeatureResponse]
    permissions: List[PermissionResponse]
    user_count: Optional[int] = None  # Number of users with this role


class RoleTemplateResponse(BaseModel):
    """Role template response"""
    template: RoleTemplate
    display_name: str
    description: str
    recommended_hierarchy: int
    default_features: List[str]  # Feature codes
    default_color: str
    default_icon: str


class DeleteRoleResponse(BaseModel):
    """Response after deleting a role"""
    success: bool
    message: str
    affected_users: int
    reassigned_to_role: Optional[str] = None


# ============================================================================
# Filter/Query Models
# ============================================================================

class RoleFilterParams(BaseModel):
    """Query parameters for filtering roles"""
    is_custom: Optional[bool] = Field(
        None,
        description="Filter by custom roles (true) or system roles (false)"
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
        description="Search in role name or display name"
    )
    include_features: bool = Field(
        default=False,
        description="Include feature assignments in response"
    )
    include_permissions: bool = Field(
        default=False,
        description="Include permission assignments in response"
    )
