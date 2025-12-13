"""
LernsystemX Dashboard Service

Business logic for dashboard layout management:
- Load effective layout (user custom or role default)
- Save user layout with permission checks
- Reset layout to default
- Role-based access control

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Service layer
"""

from typing import Dict, Optional
from datetime import datetime

from app.repositories.dashboard_repository import DashboardRepository
from app.models.dashboard import (
    DashboardLayout,
    DashboardWidgetInstance,
    get_default_layout_for_role
)


class DashboardService:
    """
    Dashboard service layer

    Implements business logic for dashboard operations
    """

    # Roles that can customize their dashboard
    CUSTOMIZABLE_ROLES = [
        'premium', 'creator', 'teacher',
        'school_admin', 'company_admin',
        'admin', 'superadmin'
    ]

    # Roles that cannot customize (use fixed defaults)
    FIXED_ROLES = ['user', 'moderator', 'support']

    @classmethod
    def get_effective_layout(cls, user: Dict) -> DashboardLayout:
        """
        Get effective dashboard layout for user

        Logic:
        1. Try to load user's custom layout from DB
        2. If not found, return default layout for user's role
        3. Default layouts are defined in dashboard.py models

        Args:
            user: User dict with keys: user_id, role, organisation_id

        Returns:
            DashboardLayout: User's layout or role default

        Example:
            >>> user = {'user_id': 123, 'role': 'premium', 'organisation_id': None}
            >>> layout = DashboardService.get_effective_layout(user)
            >>> print(len(layout.widgets))
        """
        user_id = user['user_id']
        role = user.get('role', 'user')

        # Try to load custom layout
        db_layout = DashboardRepository.get_user_layout(user_id)

        if db_layout:
            # User has custom layout - convert from DB format
            layout_json = db_layout['layout_json']

            # Build DashboardLayout from DB data
            widgets = [
                DashboardWidgetInstance(**widget_data)
                for widget_data in layout_json.get('widgets', [])
            ]

            return DashboardLayout(
                userId=user_id,
                role=role,
                widgets=widgets,
                presetId=layout_json.get('presetId'),
                updatedAt=db_layout['updated_at'].isoformat() if db_layout.get('updated_at') else None,
                version=layout_json.get('version', 1),
                source=db_layout.get('source', 'user'),
                isDefault=db_layout.get('is_default', False)
            )
        else:
            # No custom layout - return role default
            return get_default_layout_for_role(user_id, role)

    @classmethod
    def save_layout(cls, user: Dict, layout: DashboardLayout) -> DashboardLayout:
        """
        Save user's dashboard layout

        Permission checks:
        - Only customizable roles can save layouts
        - Free users get 403

        Args:
            user: User dict with keys: user_id, role, organisation_id
            layout: DashboardLayout to save

        Returns:
            DashboardLayout: Saved layout

        Raises:
            PermissionError: If user role cannot customize dashboard

        Example:
            >>> user = {'user_id': 123, 'role': 'premium', 'organisation_id': None}
            >>> layout = DashboardLayout(userId=123, role='premium', widgets=[...])
            >>> saved = DashboardService.save_layout(user, layout)
        """
        user_id = user['user_id']
        role = user.get('role', 'user')

        # Permission check
        if not cls.can_customize_dashboard(role):
            raise PermissionError(
                f"Role '{role}' cannot customize dashboard. "
                f"Upgrade to Premium or higher to customize your dashboard."
            )

        # Ensure userId and role match
        if layout.userId != user_id:
            raise ValueError("Cannot save layout for different user")

        # Build layout JSON for storage
        layout_json = {
            'widgets': [widget.model_dump() for widget in layout.widgets],
            'presetId': layout.presetId,
            'version': layout.version or 1
        }

        # Save to database
        db_result = DashboardRepository.save_user_layout(
            user_id=user_id,
            role=role,
            layout_json=layout_json,
            organisation_id=user.get('organisation_id'),
            source='user'
        )

        # Convert back to DashboardLayout
        saved_layout_json = db_result['layout_json']
        widgets = [
            DashboardWidgetInstance(**widget_data)
            for widget_data in saved_layout_json.get('widgets', [])
        ]

        return DashboardLayout(
            userId=user_id,
            role=role,
            widgets=widgets,
            presetId=saved_layout_json.get('presetId'),
            updatedAt=db_result['updated_at'].isoformat() if db_result.get('updated_at') else None,
            version=saved_layout_json.get('version', 1),
            source=db_result.get('source', 'user'),
            isDefault=False
        )

    @classmethod
    def reset_layout(cls, user: Dict) -> DashboardLayout:
        """
        Reset user's layout to role default

        Deletes custom layout from database.
        Next get_effective_layout() call will return default.

        Permission checks:
        - Only customizable roles can reset layouts

        Args:
            user: User dict with keys: user_id, role, organisation_id

        Returns:
            DashboardLayout: Default layout for role

        Raises:
            PermissionError: If user role cannot customize dashboard

        Example:
            >>> user = {'user_id': 123, 'role': 'premium', 'organisation_id': None}
            >>> default_layout = DashboardService.reset_layout(user)
        """
        user_id = user['user_id']
        role = user.get('role', 'user')

        # Permission check
        if not cls.can_customize_dashboard(role):
            raise PermissionError(
                f"Role '{role}' cannot reset dashboard. "
                f"This role uses a fixed default layout."
            )

        # Delete custom layout
        DashboardRepository.delete_user_layout(user_id)

        # Return default layout
        return get_default_layout_for_role(user_id, role)

    @classmethod
    def can_customize_dashboard(cls, role: str) -> bool:
        """
        Check if role can customize dashboard

        Args:
            role: User role

        Returns:
            bool: True if role can customize

        Example:
            >>> DashboardService.can_customize_dashboard('premium')
            True
            >>> DashboardService.can_customize_dashboard('user')
            False
        """
        return role in cls.CUSTOMIZABLE_ROLES

    @classmethod
    def validate_widget_access(cls, role: str, widget_id: str) -> bool:
        """
        Validate that user role has access to widget

        Future: Check widget permissions based on role
        Currently: All widgets are accessible to all roles (filtering in frontend)

        Args:
            role: User role
            widget_id: Widget ID to check

        Returns:
            bool: True if role can access widget

        Example:
            >>> DashboardService.validate_widget_access('premium', 'plan-tokens')
            True
        """
        # Widget-level permissions can be added here in future
        # For now, frontend handles widget visibility based on role

        # Example future logic:
        # PREMIUM_ONLY_WIDGETS = ['plan-tokens', 'org-overview']
        # if widget_id in PREMIUM_ONLY_WIDGETS:
        #     return role in ['premium', 'creator', 'teacher', 'admin']

        return True

    @classmethod
    def get_layout_statistics(cls) -> Dict:
        """
        Get dashboard layout statistics (admin only)

        Returns:
            Dict with statistics about custom layouts

        Example:
            >>> stats = DashboardService.get_layout_statistics()
            >>> print(stats['total_custom_layouts'])
        """
        total_custom = DashboardRepository.count_custom_layouts()

        return {
            'total_custom_layouts': total_custom,
            'customizable_roles': cls.CUSTOMIZABLE_ROLES,
            'fixed_roles': cls.FIXED_ROLES
        }
