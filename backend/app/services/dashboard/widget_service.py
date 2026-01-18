"""
LernsystemX Widget Service (Doku-konform)

Business logic for widget management:
- Get available widgets for role
- Add/remove widgets
- Update widget positions
- Widget settings management

ISO 9001:2015 compliant - Service layer

Uses tables: widgets, user_widgets
"""

from typing import List, Dict, Optional
from datetime import datetime

from app.infrastructure.persistence.repositories.widgets.widget_repository import WidgetRepository
from app.infrastructure.persistence.repositories.widgets.widget_instance_repository import WidgetInstanceRepository


class WidgetService:
    """
    Widget Service (Doku-konform)

    Implements business logic for widget operations
    """

    # Roles allowed to customize dashboard
    CUSTOMIZABLE_ROLES = [
        'premium', 'creator', 'teacher',
        'school_admin', 'company_admin',
        'admin', 'superadmin'
    ]

    @classmethod
    def get_available_widgets(cls, user: Dict) -> List[Dict]:
        """
        Get all widgets available for user

        Args:
            user: User dict with role

        Returns:
            List of available widget definitions
        """
        role = user.get('role', 'free')

        # Get widgets for role via PostgreSQL function
        widgets = WidgetRepository.get_widgets_for_role(role)

        return widgets

    @classmethod
    def get_user_widgets(cls, user: Dict, layout_id: Optional[str] = None) -> List[Dict]:
        """
        Get user's widget instances

        Args:
            user: User dict
            layout_id: Optional layout UUID

        Returns:
            List of widget instance dicts
        """
        user_id = user['user_id']

        # Get user's widget instances
        instances = WidgetInstanceRepository.get_user_widgets(user_id, layout_id)

        return instances

    @classmethod
    def add_widget(
        cls,
        user: Dict,
        widget_key: str,  # API uses widget_key, maps to widget_type in DB
        layout_id: Optional[str] = None,
        position_x: int = 0,
        position_y: int = 0,
        width: int = 2,
        height: int = 1,
        custom_settings: Optional[Dict] = None
    ) -> Dict:
        """
        Add widget to user's dashboard

        Args:
            user: User dict
            widget_key: Widget type identifier (e.g. 'progress', 'ki_recommendations')
            layout_id: Layout UUID
            position_x: Grid X position
            position_y: Grid Y position
            width: Grid width
            height: Grid height
            custom_settings: Custom settings

        Returns:
            Created widget instance dict

        Raises:
            PermissionError: If user cannot customize dashboard
            ValueError: If widget not found or not available
        """
        user_id = user['user_id']
        role = user.get('role', 'free')

        # Permission check
        if role not in cls.CUSTOMIZABLE_ROLES:
            raise PermissionError(
                f"Role '{role}' cannot customize dashboard. "
                "Upgrade to Premium or higher."
            )

        # Get widget definition by type
        widget = WidgetRepository.get_widget_by_type(widget_key)
        if not widget:
            raise ValueError(f"Widget '{widget_key}' not found")

        # Check if widget is available for role
        if not WidgetRepository.is_widget_available(widget_key, role):
            raise ValueError(f"Widget '{widget_key}' not available for role '{role}'")

        # Check if user already has this widget in this layout
        existing = WidgetInstanceRepository.get_widget_by_user_and_type(
            user_id, widget_key, layout_id
        )
        if existing:
            raise ValueError(f"Widget '{widget_key}' already added to this layout")

        # Add widget instance
        instance = WidgetInstanceRepository.add_widget(
            user_id=user_id,
            widget_id=widget['widget_id'],  # UUID, not integer!
            layout_id=layout_id,
            position_x=position_x,
            position_y=position_y,
            width=width,
            height=height,
            custom_settings=custom_settings
        )

        return instance

    @classmethod
    def remove_widget(cls, user: Dict, widget_instance_id: str) -> bool:
        """
        Remove widget from dashboard

        Args:
            user: User dict
            widget_instance_id: Widget instance UUID (user_widget_id)

        Returns:
            bool: True if removed

        Raises:
            PermissionError: If user cannot customize dashboard
            ValueError: If widget not found or not owned by user
        """
        role = user.get('role', 'free')

        # Permission check
        if role not in cls.CUSTOMIZABLE_ROLES:
            raise PermissionError(
                f"Role '{role}' cannot customize dashboard"
            )

        # Get widget instance
        instance = WidgetInstanceRepository.get_widget_instance(widget_instance_id)
        if not instance:
            raise ValueError("Widget instance not found")

        # Ownership check
        if instance['user_id'] != user['user_id']:
            raise PermissionError("Widget belongs to different user")

        # Remove widget
        return WidgetInstanceRepository.remove_widget(widget_instance_id)

    @classmethod
    def update_widget_position(
        cls,
        user: Dict,
        widget_instance_id: str,
        position_x: int,
        position_y: int,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Update widget position (Drag & Drop)

        Args:
            user: User dict
            widget_instance_id: Widget instance UUID (user_widget_id)
            position_x: New X position
            position_y: New Y position
            width: Optional new width
            height: Optional new height

        Returns:
            Updated widget instance dict

        Raises:
            PermissionError: If user cannot customize dashboard or not owner
        """
        role = user.get('role', 'free')

        # Permission check
        if role not in cls.CUSTOMIZABLE_ROLES:
            raise PermissionError("Cannot customize dashboard")

        # Get widget instance
        instance = WidgetInstanceRepository.get_widget_instance(widget_instance_id)
        if not instance:
            raise ValueError("Widget instance not found")

        # Ownership check
        if instance['user_id'] != user['user_id']:
            raise PermissionError("Widget belongs to different user")

        # Update position
        return WidgetInstanceRepository.update_widget_position(
            widget_instance_id,
            position_x,
            position_y,
            width,
            height
        )

    @classmethod
    def update_widget_settings(
        cls,
        user: Dict,
        widget_instance_id: str,
        custom_settings: Dict
    ) -> Optional[Dict]:
        """
        Update widget settings

        Args:
            user: User dict
            widget_instance_id: Widget instance UUID (user_widget_id)
            custom_settings: New settings dict

        Returns:
            Updated widget instance dict

        Raises:
            PermissionError: If not owner
        """
        # Get widget instance
        instance = WidgetInstanceRepository.get_widget_instance(widget_instance_id)
        if not instance:
            raise ValueError("Widget instance not found")

        # Ownership check
        if instance['user_id'] != user['user_id']:
            raise PermissionError("Widget belongs to different user")

        # Update settings
        return WidgetInstanceRepository.update_widget_settings(
            widget_instance_id,
            custom_settings
        )

    @classmethod
    def toggle_widget_visibility(
        cls,
        user: Dict,
        widget_instance_id: str
    ) -> bool:
        """
        Toggle widget visibility

        Args:
            user: User dict
            widget_instance_id: Widget instance UUID (user_widget_id)

        Returns:
            bool: New visibility state

        Raises:
            PermissionError: If not owner
        """
        # Get widget instance
        instance = WidgetInstanceRepository.get_widget_instance(widget_instance_id)
        if not instance:
            raise ValueError("Widget instance not found")

        # Ownership check
        if instance['user_id'] != user['user_id']:
            raise PermissionError("Widget belongs to different user")

        # Toggle visibility
        return WidgetInstanceRepository.toggle_widget_visibility(widget_instance_id)

    @classmethod
    def can_customize_dashboard(cls, role: str) -> bool:
        """
        Check if role can customize dashboard

        Args:
            role: User role

        Returns:
            bool: True if can customize
        """
        return role in cls.CUSTOMIZABLE_ROLES
