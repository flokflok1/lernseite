"""
LernsystemX Dashboard Models

Pydantic models for dashboard layout operations:
- Dashboard layout retrieval
- Dashboard layout saving
- Widget configuration
- Role-based defaults

ISO 9001:2015 compliant - Dashboard configuration standards
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class DashboardWidgetInstance(BaseModel):
    """
    Individual widget instance in dashboard layout

    Matches frontend type from widgets.ts
    """
    instanceId: str = Field(..., description="Unique instance ID (userId-widgetId)")
    widgetId: str = Field(..., description="Widget definition ID")
    order: int = Field(..., ge=0, description="Display order (lower = earlier)")
    visible: bool = Field(default=True, description="Widget visibility")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Widget-specific configuration")

    # Grid position (optional for advanced layouts)
    position: Optional[Dict[str, int]] = Field(
        default=None,
        description="Grid position {row, col, width, height}"
    )

    model_config = ConfigDict(from_attributes=True)


class DashboardLayout(BaseModel):
    """
    Complete dashboard layout configuration

    Matches frontend DashboardLayout interface
    """
    userId: int = Field(..., description="User ID this layout belongs to")
    role: str = Field(..., description="User role (for filtering)")
    widgets: List[DashboardWidgetInstance] = Field(
        default_factory=list,
        description="List of widget instances"
    )
    presetId: Optional[str] = Field(default=None, description="Preset ID if using preset")
    updatedAt: Optional[str] = Field(default=None, description="Last updated timestamp (ISO)")
    version: Optional[int] = Field(default=1, description="Layout version for migration")

    # Internal fields (not sent to frontend)
    source: Optional[str] = Field(default='user', description="Layout source (system/role/organisation/user)")
    isDefault: Optional[bool] = Field(default=False, description="Whether this is a default layout")

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate user role"""
        valid_roles = [
            'user', 'premium', 'creator', 'teacher',
            'school_admin', 'company_admin', 'moderator',
            'support', 'admin', 'superadmin'
        ]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        """Validate layout source"""
        if v is None:
            return v
        valid_sources = ['system', 'role', 'organisation', 'user']
        if v not in valid_sources:
            raise ValueError(f'Source must be one of: {", ".join(valid_sources)}')
        return v

    model_config = ConfigDict(from_attributes=True)


class DashboardLayoutSaveRequest(BaseModel):
    """
    Request model for saving dashboard layout

    Only widgets are required - userId and role come from JWT
    """
    widgets: List[DashboardWidgetInstance] = Field(..., description="Widget instances to save")
    presetId: Optional[str] = Field(default=None, description="Preset ID if using preset")

    model_config = ConfigDict(from_attributes=True)


class DashboardLayoutResponse(BaseModel):
    """
    API response for dashboard layout operations

    Wraps layout in standard API response format
    """
    success: bool = Field(..., description="Operation success status")
    layout: DashboardLayout = Field(..., description="Dashboard layout data")
    message: Optional[str] = Field(default=None, description="Optional message")

    model_config = ConfigDict(from_attributes=True)


class DashboardLayoutResetResponse(BaseModel):
    """
    API response for layout reset operation
    """
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Reset confirmation message")
    layout: DashboardLayout = Field(..., description="Default layout after reset")

    model_config = ConfigDict(from_attributes=True)


# Default widget configurations per role
DEFAULT_LAYOUTS = {
    'user': {
        'widgets': [
            {'instanceId': 'user-welcome', 'widgetId': 'welcome', 'order': 0, 'visible': True},
            {'instanceId': 'user-profile', 'widgetId': 'profile-summary', 'order': 1, 'visible': True},
            {'instanceId': 'user-courses', 'widgetId': 'enrolled-courses', 'order': 2, 'visible': True},
            {'instanceId': 'user-progress', 'widgetId': 'courses-progress', 'order': 3, 'visible': True},
        ],
        'presetId': 'free-default',
        'source': 'role'
    },
    'premium': {
        'widgets': [
            {'instanceId': 'premium-welcome', 'widgetId': 'welcome', 'order': 0, 'visible': True},
            {'instanceId': 'premium-profile', 'widgetId': 'profile-summary', 'order': 1, 'visible': True},
            {'instanceId': 'premium-tokens', 'widgetId': 'plan-tokens', 'order': 2, 'visible': True},
            {'instanceId': 'premium-courses', 'widgetId': 'enrolled-courses', 'order': 3, 'visible': True},
            {'instanceId': 'premium-progress', 'widgetId': 'courses-progress', 'order': 4, 'visible': True},
            {'instanceId': 'premium-activity', 'widgetId': 'activity', 'order': 5, 'visible': True},
        ],
        'presetId': 'premium-default',
        'source': 'role'
    },
    'creator': {
        'widgets': [
            {'instanceId': 'creator-welcome', 'widgetId': 'welcome', 'order': 0, 'visible': True},
            {'instanceId': 'creator-profile', 'widgetId': 'profile-summary', 'order': 1, 'visible': True},
            {'instanceId': 'creator-tokens', 'widgetId': 'plan-tokens', 'order': 2, 'visible': True},
            {'instanceId': 'creator-courses', 'widgetId': 'enrolled-courses', 'order': 3, 'visible': True},
            {'instanceId': 'creator-progress', 'widgetId': 'courses-progress', 'order': 4, 'visible': True},
            {'instanceId': 'creator-activity', 'widgetId': 'activity', 'order': 5, 'visible': True},
        ],
        'presetId': 'creator-default',
        'source': 'role'
    },
    'teacher': {
        'widgets': [
            {'instanceId': 'teacher-welcome', 'widgetId': 'welcome', 'order': 0, 'visible': True},
            {'instanceId': 'teacher-profile', 'widgetId': 'profile-summary', 'order': 1, 'visible': True},
            {'instanceId': 'teacher-tokens', 'widgetId': 'plan-tokens', 'order': 2, 'visible': True},
            {'instanceId': 'teacher-courses', 'widgetId': 'enrolled-courses', 'order': 3, 'visible': True},
            {'instanceId': 'teacher-progress', 'widgetId': 'courses-progress', 'order': 4, 'visible': True},
        ],
        'presetId': 'teacher-default',
        'source': 'role'
    },
    'school_admin': {
        'widgets': [
            {'instanceId': 'school-welcome', 'widgetId': 'welcome', 'order': 0, 'visible': True},
            {'instanceId': 'school-org', 'widgetId': 'org-overview', 'order': 1, 'visible': True},
            {'instanceId': 'school-profile', 'widgetId': 'profile-summary', 'order': 2, 'visible': True},
            {'instanceId': 'school-courses', 'widgetId': 'enrolled-courses', 'order': 3, 'visible': True},
        ],
        'presetId': 'school-admin-default',
        'source': 'role'
    },
    'company_admin': {
        'widgets': [
            {'instanceId': 'company-welcome', 'widgetId': 'welcome', 'order': 0, 'visible': True},
            {'instanceId': 'company-org', 'widgetId': 'org-overview', 'order': 1, 'visible': True},
            {'instanceId': 'company-profile', 'widgetId': 'profile-summary', 'order': 2, 'visible': True},
            {'instanceId': 'company-courses', 'widgetId': 'enrolled-courses', 'order': 3, 'visible': True},
        ],
        'presetId': 'company-admin-default',
        'source': 'role'
    },
    'admin': {
        'widgets': [
            {'instanceId': 'admin-welcome', 'widgetId': 'welcome', 'order': 0, 'visible': True},
            {'instanceId': 'admin-profile', 'widgetId': 'profile-summary', 'order': 1, 'visible': True},
            {'instanceId': 'admin-tokens', 'widgetId': 'plan-tokens', 'order': 2, 'visible': True},
            {'instanceId': 'admin-courses', 'widgetId': 'enrolled-courses', 'order': 3, 'visible': True},
            {'instanceId': 'admin-activity', 'widgetId': 'activity', 'order': 4, 'visible': True},
        ],
        'presetId': 'admin-default',
        'source': 'role'
    },
}


def get_default_layout_for_role(user_id: int, role: str) -> DashboardLayout:
    """
    Get default dashboard layout for a given role

    Args:
        user_id: User ID
        role: User role

    Returns:
        DashboardLayout: Default layout for role

    Example:
        >>> layout = get_default_layout_for_role(123, 'premium')
        >>> len(layout.widgets)
        6
    """
    # Get default configuration for role, fallback to 'user' if not found
    default_config = DEFAULT_LAYOUTS.get(role, DEFAULT_LAYOUTS['user'])

    # Build widget instances
    widgets = [
        DashboardWidgetInstance(**widget_config)
        for widget_config in default_config['widgets']
    ]

    return DashboardLayout(
        userId=user_id,
        role=role,
        widgets=widgets,
        presetId=default_config.get('presetId'),
        source=default_config.get('source', 'role'),
        isDefault=True,
        version=1
    )
