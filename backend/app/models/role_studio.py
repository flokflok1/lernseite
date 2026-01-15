"""
Role Studio Pydantic Models

Validation models for role-studio-mode API requests and responses.
Handles serialization/deserialization and data validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class StudioModeEnum(str, Enum):
    """Valid studio modes"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    ORG_ADMIN = "org_admin"
    ORG_MEMBER = "org_member"
    TEACHER = "teacher"
    USER = "user"
    GUEST = "guest"


# ==================== REQUEST MODELS ====================

class CreateRoleStudioRequest(BaseModel):
    """Request model for creating a role studio mode"""

    role_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique role identifier (e.g., 'admin', 'teacher')"
    )

    display_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable role name for UI display"
    )

    studio_mode: StudioModeEnum = Field(
        ...,
        description="Which studio mode this role should access"
    )

    permissions: Dict[str, bool] = Field(
        default_factory=dict,
        description="Dictionary of permission flags"
    )

    requires_organization: bool = Field(
        default=False,
        description="Whether this role requires organization membership"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional description of the role"
    )

    class Config:
        schema_extra = {
            "example": {
                "role_code": "content_reviewer",
                "display_name": "Content Reviewer",
                "studio_mode": "moderator",
                "permissions": {
                    "can_moderate": True,
                    "can_view_analytics": True,
                    "can_export_data": False
                },
                "requires_organization": False,
                "description": "Reviews and approves user-generated content"
            }
        }

    @validator("role_code")
    def validate_role_code(cls, v):
        """Validate role code format"""
        if not v.replace("_", "").isalnum():
            raise ValueError("Role code must contain only alphanumeric characters and underscores")
        return v.lower()


class UpdateRoleStudioRequest(BaseModel):
    """Request model for updating a role studio mode"""

    display_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated display name"
    )

    studio_mode: Optional[StudioModeEnum] = Field(
        default=None,
        description="Updated studio mode"
    )

    permissions: Optional[Dict[str, bool]] = Field(
        default=None,
        description="Updated permissions"
    )

    requires_organization: Optional[bool] = Field(
        default=None,
        description="Updated organization requirement"
    )

    is_active: Optional[bool] = Field(
        default=None,
        description="Updated active status"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Updated description"
    )

    class Config:
        schema_extra = {
            "example": {
                "display_name": "Instructor",
                "is_active": True
            }
        }


class UpdateRolePermissionsRequest(BaseModel):
    """Request model for updating role permissions"""

    permissions: Dict[str, bool] = Field(
        ...,
        description="New permissions for the role"
    )

    change_reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Reason for the permission change (for audit trail)"
    )

    class Config:
        schema_extra = {
            "example": {
                "permissions": {
                    "can_create_course": True,
                    "can_publish": False,
                    "can_moderate": True
                },
                "change_reason": "User feedback: reduced publishing permissions"
            }
        }


class DeactivateRoleRequest(BaseModel):
    """Request model for deactivating a role"""

    change_reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Reason for deactivation"
    )

    class Config:
        schema_extra = {
            "example": {
                "change_reason": "Role no longer needed in our organization"
            }
        }


# ==================== RESPONSE MODELS ====================

class RoleStudioResponse(BaseModel):
    """Response model for a role studio mode"""

    role_code: str
    display_name: str
    studio_mode: str
    requires_organization: bool
    permissions: Dict[str, Any]
    is_active: bool
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "role_code": "admin",
                "display_name": "System Administrator",
                "studio_mode": "admin",
                "requires_organization": False,
                "permissions": {
                    "can_create_course": True,
                    "can_publish": True,
                    "can_moderate": True,
                    "can_view_analytics": True,
                    "can_export_data": True,
                    "can_manage_users": True,
                    "can_manage_roles": True,
                    "can_manage_organizations": True,
                    "can_configure_ai": True,
                    "can_manage_subscriptions": True
                },
                "is_active": True,
                "description": "System-wide administrator with complete control",
                "created_at": "2026-01-14T10:00:00Z",
                "updated_at": "2026-01-14T10:00:00Z"
            }
        }


class RoleStudioListResponse(BaseModel):
    """Response model for listing role studio modes"""

    data: list[RoleStudioResponse]
    total: int
    limit: int
    offset: int

    class Config:
        schema_extra = {
            "example": {
                "data": [
                    {
                        "role_code": "admin",
                        "display_name": "System Administrator",
                        "studio_mode": "admin",
                        "requires_organization": False,
                        "permissions": {},
                        "is_active": True,
                        "description": "System-wide administrator",
                        "created_at": "2026-01-14T10:00:00Z",
                        "updated_at": "2026-01-14T10:00:00Z"
                    },
                    {
                        "role_code": "teacher",
                        "display_name": "Teacher",
                        "studio_mode": "teacher",
                        "requires_organization": False,
                        "permissions": {},
                        "is_active": True,
                        "description": "Creates and manages courses",
                        "created_at": "2026-01-14T10:00:00Z",
                        "updated_at": "2026-01-14T10:00:00Z"
                    }
                ],
                "total": 7,
                "limit": 20,
                "offset": 0
            }
        }


class RoleStudioDetailResponse(BaseModel):
    """Detailed response with permissions and metadata"""

    role_code: str
    display_name: str
    studio_mode: str
    requires_organization: bool
    permissions: Dict[str, bool]
    is_active: bool
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    permission_count: int = Field(
        description="Total number of permissions defined for this role"
    )

    class Config:
        from_attributes = True

    @validator("permission_count", pre=True, always=True)
    def calculate_permission_count(cls, v, values):
        """Calculate permission count from permissions dict"""
        permissions = values.get("permissions", {})
        return len(permissions) if permissions else 0


class RoleChangeHistoryResponse(BaseModel):
    """Response model for role change history"""

    history_id: int
    role_code: str
    previous_display_name: Optional[str]
    new_display_name: Optional[str]
    previous_studio_mode: Optional[str]
    new_studio_mode: Optional[str]
    previous_permissions: Optional[Dict[str, Any]]
    new_permissions: Optional[Dict[str, Any]]
    changed_by: str
    change_reason: Optional[str]
    changed_at: datetime

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "history_id": 1,
                "role_code": "teacher",
                "previous_display_name": "Teacher",
                "new_display_name": "Instructor",
                "previous_studio_mode": "teacher",
                "new_studio_mode": "teacher",
                "previous_permissions": {"can_create_course": True},
                "new_permissions": {"can_create_course": True, "can_publish": True},
                "changed_by": "admin_user_id",
                "change_reason": "Expanded permissions for instructors",
                "changed_at": "2026-01-14T15:30:00Z"
            }
        }


class StudioConfigResponse(BaseModel):
    """Response model for user's studio configuration (returned from auth endpoint)"""

    role_code: str
    studio_mode: str
    display_name: str
    permissions: Dict[str, bool]
    requires_organization: bool

    class Config:
        schema_extra = {
            "example": {
                "role_code": "admin",
                "studio_mode": "admin",
                "display_name": "System Administrator",
                "permissions": {
                    "can_create_course": True,
                    "can_publish": True,
                    "can_moderate": True
                },
                "requires_organization": False
            }
        }


class PermissionsResponse(BaseModel):
    """Response model for getting role permissions"""

    role_code: str
    display_name: str
    permissions: Dict[str, bool]
    permission_count: int

    class Config:
        schema_extra = {
            "example": {
                "role_code": "admin",
                "display_name": "System Administrator",
                "permissions": {
                    "can_create_course": True,
                    "can_publish": True,
                    "can_moderate": True
                },
                "permission_count": 3
            }
        }

    @validator("permission_count", pre=True, always=True)
    def calculate_count(cls, v, values):
        """Calculate permission count"""
        permissions = values.get("permissions", {})
        return len(permissions) if permissions else 0


class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = Field(default=False)
    error: Dict[str, Any] = Field(description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid studio mode",
                    "details": {"field": "studio_mode", "value": "invalid_mode"}
                },
                "timestamp": "2026-01-14T10:00:00Z"
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response"""

    success: bool = Field(default=True)
    data: Any = Field(description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {"role_code": "admin", "display_name": "Administrator"},
                "timestamp": "2026-01-14T10:00:00Z"
            }
        }
