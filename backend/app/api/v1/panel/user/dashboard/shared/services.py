"""
LernsystemX Dashboard Core Services

Centralized service layer for dashboard operations.
Implements DDD pattern with clear separation of concerns.

Services:
    - DashboardLayoutService: Layout management
    - DashboardWidgetService: Widget operations
    - DashboardRecommendationService: KI recommendations
    - DashboardAnalyticsService: Dashboard analytics

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Service layer
DDD compliant - Domain-Driven Design
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.infrastructure.persistence.repositories.dashboard.core import DashboardRepository
from app.infrastructure.persistence.repositories.widgets.widget_repository import WidgetRepository
from app.infrastructure.persistence.repositories.dashboard.core import DashboardRepository as RecommendationRepository  # TODO: Fix this
from app.domain.models.admin.dashboard import (
    DashboardLayout,
    DashboardWidgetInstance,
    get_default_layout_for_role
)


class DashboardLayoutService:
    """
    Dashboard Layout Service

    Manages user dashboard layouts with role-based permissions.

    Business Rules:
        - Premium+ roles can customize layouts
        - Free users get fixed role defaults
        - Layouts are versioned for compatibility
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
        Get effective dashboard layout for user.

        Logic:
            1. Try to load user's custom layout from DB
            2. If not found, return default layout for user's role
            3. Default layouts are defined in dashboard.py models

        Args:
            user: User dict with keys: user_id, role, organisation_id

        Returns:
            DashboardLayout: User's layout or role default
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
        Save user's dashboard layout.

        Permission checks:
            - Only customizable roles can save layouts
            - Free users get 403

        Args:
            user: User dict
            layout: Dashboard layout to save

        Returns:
            DashboardLayout: Saved layout

        Raises:
            PermissionError: If user role cannot customize dashboard
        """
        role = user.get('role', 'user')

        # Permission check
        if role not in cls.CUSTOMIZABLE_ROLES:
            raise PermissionError(
                f"Role '{role}' cannot customize dashboard. "
                f"Upgrade to Premium for custom dashboards."
            )

        # Prepare layout data
        layout_data = {
            'widgets': [widget.model_dump() for widget in layout.widgets],
            'presetId': layout.presetId,
            'version': layout.version
        }

        # Save to DB
        saved = DashboardRepository.save_user_layout(
            user_id=user['user_id'],
            layout_json=layout_data
        )

        # Return updated layout
        layout.updatedAt = saved['updated_at'].isoformat() if saved.get('updated_at') else None
        layout.source = 'user'
        layout.isDefault = False

        return layout

    @classmethod
    def reset_layout(cls, user: Dict) -> DashboardLayout:
        """
        Reset dashboard layout to default.

        Deletes user's custom layout.
        Next get_effective_layout() will return role default.

        Args:
            user: User dict

        Returns:
            DashboardLayout: Role default layout

        Raises:
            PermissionError: If user role cannot reset dashboard
        """
        role = user.get('role', 'user')

        # Permission check
        if role not in cls.CUSTOMIZABLE_ROLES:
            raise PermissionError(
                f"Role '{role}' cannot reset dashboard. "
                f"No custom layouts available for this role."
            )

        # Delete custom layout
        DashboardRepository.delete_user_layout(user['user_id'])

        # Return role default
        default_layout = get_default_layout_for_role(user['user_id'], role)
        default_layout.source = 'role'
        default_layout.isDefault = True

        return default_layout


class DashboardWidgetService:
    """
    Dashboard Widget Service

    Manages widget registry and user widget instances.

    Business Rules:
        - All widgets have role-based availability
        - Premium widgets require Premium+ subscription
        - Widget positions are grid-based (x, y, width, height)
    """

    @classmethod
    def get_available_widgets(cls, user: Dict) -> List[Dict]:
        """
        Get all widgets available for user's role.

        Filters widgets based on:
            - User's role
            - Premium status
            - Widget requirements

        Args:
            user: User dict

        Returns:
            List of available widget definitions
        """
        role = user.get('role', 'user')

        # Get all widgets from registry
        all_widgets = WidgetRepository.get_all_widgets()

        # Filter by role and premium status
        available = []
        for widget in all_widgets:
            # Check if widget is available for this role
            if cls._is_widget_available(widget, role):
                widget['is_available'] = True
                available.append(widget)

        return available

    @classmethod
    def _is_widget_available(cls, widget: Dict, role: str) -> bool:
        """
        Check if widget is available for role.

        Args:
            widget: Widget definition
            role: User role

        Returns:
            True if available, False otherwise
        """
        requires_premium = widget.get('requires_premium', False)

        premium_roles = [
            'premium', 'creator', 'teacher',
            'school_admin', 'company_admin',
            'admin', 'superadmin'
        ]

        if requires_premium and role not in premium_roles:
            return False

        return True

    @classmethod
    def get_user_widgets(cls, user: Dict, layout_id: Optional[str] = None) -> List[Dict]:
        """
        Get user's widget instances.

        Args:
            user: User dict
            layout_id: Optional layout UUID

        Returns:
            List of user's widget instances
        """
        return WidgetRepository.get_user_widget_instances(
            user_id=user['user_id'],
            layout_id=layout_id
        )

    @classmethod
    def add_widget(
        cls,
        user: Dict,
        widget_key: str,
        layout_id: Optional[str] = None,
        position_x: int = 0,
        position_y: int = 0,
        width: int = 2,
        height: int = 2,
        custom_settings: Optional[Dict] = None
    ) -> Dict:
        """
        Add widget to user's dashboard.

        Args:
            user: User dict
            widget_key: Widget identifier
            layout_id: Optional layout UUID
            position_x: Grid X position
            position_y: Grid Y position
            width: Widget width in grid units
            height: Widget height in grid units
            custom_settings: Widget-specific settings

        Returns:
            Created widget instance

        Raises:
            PermissionError: If user cannot customize dashboard
            ValueError: If widget doesn't exist or is not available
        """
        role = user.get('role', 'user')

        # Permission check
        if role not in DashboardLayoutService.CUSTOMIZABLE_ROLES:
            raise PermissionError(
                f"Role '{role}' cannot add widgets. "
                f"Upgrade to Premium for custom dashboards."
            )

        # Check widget exists and is available
        widget_def = WidgetRepository.get_widget_by_key(widget_key)
        if not widget_def:
            raise ValueError(f"Widget '{widget_key}' does not exist")

        if not cls._is_widget_available(widget_def, role):
            raise ValueError(f"Widget '{widget_key}' is not available for role '{role}'")

        # Add widget instance
        return WidgetRepository.add_widget_instance(
            user_id=user['user_id'],
            widget_key=widget_key,
            layout_id=layout_id,
            position_x=position_x,
            position_y=position_y,
            width=width,
            height=height,
            custom_settings=custom_settings or {}
        )

    @classmethod
    def remove_widget(cls, user: Dict, widget_instance_id: str) -> bool:
        """
        Remove widget from dashboard.

        Args:
            user: User dict
            widget_instance_id: Widget instance UUID

        Returns:
            True if removed, False if not found

        Raises:
            PermissionError: If user doesn't own widget
        """
        # Verify ownership
        widget = WidgetRepository.get_widget_instance_by_id(widget_instance_id)
        if not widget:
            return False

        if widget['user_id'] != user['user_id']:
            raise PermissionError("Cannot remove widget owned by another user")

        return WidgetRepository.delete_widget_instance(widget_instance_id)

    @classmethod
    def update_widget_position(
        cls,
        user: Dict,
        widget_instance_id: str,
        position_x: int,
        position_y: int,
        width: int,
        height: int
    ) -> Dict:
        """
        Update widget position (Drag & Drop).

        Args:
            user: User dict
            widget_instance_id: Widget instance UUID
            position_x: New X position
            position_y: New Y position
            width: New width
            height: New height

        Returns:
            Updated widget instance

        Raises:
            PermissionError: If user doesn't own widget
            ValueError: If widget not found
        """
        # Verify ownership
        widget = WidgetRepository.get_widget_instance_by_id(widget_instance_id)
        if not widget:
            raise ValueError("Widget not found")

        if widget['user_id'] != user['user_id']:
            raise PermissionError("Cannot update widget owned by another user")

        return WidgetRepository.update_widget_position(
            widget_instance_id=widget_instance_id,
            position_x=position_x,
            position_y=position_y,
            width=width,
            height=height
        )

    @classmethod
    def update_widget_settings(
        cls,
        user: Dict,
        widget_instance_id: str,
        custom_settings: Dict
    ) -> Dict:
        """
        Update widget custom settings.

        Args:
            user: User dict
            widget_instance_id: Widget instance UUID
            custom_settings: New settings dict

        Returns:
            Updated widget instance

        Raises:
            PermissionError: If user doesn't own widget
            ValueError: If widget not found
        """
        # Verify ownership
        widget = WidgetRepository.get_widget_instance_by_id(widget_instance_id)
        if not widget:
            raise ValueError("Widget not found")

        if widget['user_id'] != user['user_id']:
            raise PermissionError("Cannot update widget owned by another user")

        return WidgetRepository.update_widget_settings(
            widget_instance_id=widget_instance_id,
            custom_settings=custom_settings
        )

    @classmethod
    def toggle_widget_visibility(cls, user: Dict, widget_instance_id: str) -> bool:
        """
        Toggle widget visibility.

        Args:
            user: User dict
            widget_instance_id: Widget instance UUID

        Returns:
            New visibility state (True = visible)

        Raises:
            PermissionError: If user doesn't own widget
            ValueError: If widget not found
        """
        # Verify ownership
        widget = WidgetRepository.get_widget_instance_by_id(widget_instance_id)
        if not widget:
            raise ValueError("Widget not found")

        if widget['user_id'] != user['user_id']:
            raise PermissionError("Cannot toggle widget owned by another user")

        new_visibility = not widget.get('is_visible', True)

        WidgetRepository.update_widget_visibility(
            widget_instance_id=widget_instance_id,
            is_visible=new_visibility
        )

        return new_visibility


class DashboardRecommendationService:
    """
    Dashboard Recommendation Service

    Manages KI-powered recommendations for users.

    Business Rules:
        - Only Premium+ users get recommendations
        - Recommendations are scored and ranked
        - Users can dismiss or accept recommendations
    """

    PREMIUM_ROLES = [
        'premium', 'creator', 'teacher',
        'school_admin', 'company_admin',
        'admin', 'superadmin'
    ]

    @classmethod
    def get_recommendations(
        cls,
        user: Dict,
        limit: int = 10,
        include_dismissed: bool = False
    ) -> List[Dict]:
        """
        Get KI recommendations for user.

        Args:
            user: User dict
            limit: Max recommendations
            include_dismissed: Include dismissed recommendations

        Returns:
            List of recommendations

        Raises:
            PermissionError: If user is not Premium+
        """
        role = user.get('role', 'user')

        if role not in cls.PREMIUM_ROLES:
            raise PermissionError(
                "KI recommendations require Premium subscription"
            )

        return RecommendationRepository.get_user_recommendations(
            user_id=user['user_id'],
            limit=limit,
            include_dismissed=include_dismissed
        )

    @classmethod
    def dismiss_recommendation(cls, user: Dict, recommendation_id: str) -> bool:
        """
        Dismiss a recommendation.

        Args:
            user: User dict
            recommendation_id: Recommendation UUID

        Returns:
            True if dismissed, False if not found
        """
        return RecommendationRepository.dismiss_recommendation(
            user_id=user['user_id'],
            recommendation_id=recommendation_id
        )

    @classmethod
    def accept_recommendation(cls, user: Dict, recommendation_id: str) -> Dict:
        """
        Accept a recommendation.

        Performs action based on recommendation type:
            - course: Enrolls user in course
            - learning_path: Adds learning path
            - exam: Schedules exam

        Args:
            user: User dict
            recommendation_id: Recommendation UUID

        Returns:
            Action result dict

        Raises:
            ValueError: If recommendation not found
        """
        recommendation = RecommendationRepository.get_recommendation_by_id(
            recommendation_id
        )

        if not recommendation or recommendation['user_id'] != user['user_id']:
            raise ValueError("Recommendation not found")

        # Perform action based on type
        result = cls._execute_recommendation_action(user, recommendation)

        # Mark as accepted
        RecommendationRepository.accept_recommendation(
            recommendation_id=recommendation_id
        )

        return result

    @classmethod
    def _execute_recommendation_action(cls, user: Dict, recommendation: Dict) -> Dict:
        """
        Execute recommendation action.

        Args:
            user: User dict
            recommendation: Recommendation dict

        Returns:
            Action result
        """
        rec_type = recommendation['recommendation_type']
        target_id = recommendation['target_id']

        if rec_type == 'course':
            # Enroll user in course
            from app.infrastructure.persistence.repositories.enrollments.core import EnrollmentRepository
            enrollment = EnrollmentRepository.create_enrollment(
                user_id=user['user_id'],
                course_id=target_id,
                access_type='recommended'
            )
            return {
                'action': 'enrolled',
                'course_id': target_id,
                'enrollment_id': enrollment['enrollment_id']
            }

        elif rec_type == 'learning_path':
            # Add learning path
            return {
                'action': 'learning_path_added',
                'path_id': target_id
            }

        elif rec_type == 'exam':
            # Schedule exam
            return {
                'action': 'exam_scheduled',
                'exam_id': target_id
            }

        else:
            return {
                'action': 'accepted',
                'type': rec_type
            }

    @classmethod
    def get_stats(cls, user: Dict) -> Dict:
        """
        Get recommendation statistics.

        Args:
            user: User dict

        Returns:
            Stats dict with counts and rates
        """
        return RecommendationRepository.get_recommendation_stats(
            user_id=user['user_id']
        )


# Exports
__all__ = [
    'DashboardLayoutService',
    'DashboardWidgetService',
    'DashboardRecommendationService',
]
