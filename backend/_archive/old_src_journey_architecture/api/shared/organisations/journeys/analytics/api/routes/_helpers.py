"""
Organisations Domain - Shared Route Helpers (Analytics Journey)

Common imports and utilities for analytics routes.
"""

# Flask imports
from flask import request, jsonify
from datetime import datetime, timedelta
from typing import Tuple

# Pydantic validation
from pydantic import ValidationError

# DDD Organisations Domain
from src.api.organisations.core.infrastructure.repositories.organisation_repository import OrganisationRepository

# Legacy imports (app structure) - TODO: migrate
from app.models.organisation import OrganisationStatsResponse
from app.models.analytics import (
    TimeSeriesResponse,
    TimeSeriesDataPoint,
    OrgTopCoursesResponse,
    OrgTopCourseAnalytics,
    OrgTopModulesResponse,
    OrgTopModuleAnalytics
)
from app.repositories.analytics import AnalyticsRepository
from app.repositories.subscription import SubscriptionRepository
from app.middleware.auth import (
    token_required,
    get_current_user
)
from app.security.permissions import require_permission, Permissions


def parse_date_range(range_param: str) -> Tuple[datetime, datetime]:
    """
    Parse range parameter to from_date and to_date

    Args:
        range_param: Time range string ('7d', '30d', '90d')

    Returns:
        Tuple of (from_date, to_date)
    """
    range_map = {
        '7d': 7,
        '30d': 30,
        '90d': 90
    }

    days = range_map.get(range_param, 7)
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=days)

    return from_date, to_date


def check_org_access(user: dict, org_id: int) -> None:
    """
    Check if user has access to organisation analytics

    Args:
        user: Current user
        org_id: Organisation ID

    Raises:
        PermissionError: If user doesn't have access
    """
    # System admin and superadmin can access all orgs
    if user.get('role') in ['admin', 'superadmin']:
        return

    # Org members can only access their own org
    user_org_id = user.get('organization_id')
    if user_org_id != org_id:
        raise PermissionError(f"Access denied to organisation {org_id}")


def check_org_membership(user: dict, org_id: int, required_roles: list = None) -> bool:
    """
    Check if user is member of organisation with required role

    Args:
        user: Current user dict
        org_id: Organisation ID
        required_roles: List of required org roles (optional)

    Returns:
        True if user is member with required role, False otherwise
    """
    # Admins can access all organisations
    if user.get('role') in ['admin', 'superadmin']:
        return True

    # Check if user is member of this organisation
    if user.get('organization_id') != org_id:
        return False

    # If roles required, check org_role
    if required_roles:
        return user.get('org_role') in required_roles

    return True


__all__ = [
    # Flask
    'request',
    'jsonify',
    'datetime',
    'timedelta',
    # Pydantic
    'ValidationError',
    # Repositories
    'OrganisationRepository',
    'AnalyticsRepository',
    'SubscriptionRepository',
    # Models
    'OrganisationStatsResponse',
    'TimeSeriesResponse',
    'TimeSeriesDataPoint',
    'OrgTopCoursesResponse',
    'OrgTopCourseAnalytics',
    'OrgTopModulesResponse',
    'OrgTopModuleAnalytics',
    # Middleware
    'token_required',
    'get_current_user',
    'require_permission',
    'Permissions',
    # Helpers
    'parse_date_range',
    'check_org_access',
    'check_org_membership',
]
