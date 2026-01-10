"""
Organisations Domain - Shared Route Helpers (Admin Journey)

Common imports and utilities for admin organisation routes.
"""

# Flask imports
from flask import request, jsonify, g

# Pydantic validation
from pydantic import ValidationError

# DDD Organisations Domain (NEW - src structure)
from src.api.organisations.core.infrastructure.repositories.organisation_repository import OrganisationRepository
from src.api.organisations.core.application.services.organisation_service import OrganisationService

# Legacy imports (app structure) - TODO: migrate
from app.models.organisation import (
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationResponse,
    OrganisationListResponse,
    OrganisationAssignUserRequest,
    OrganisationUserResponse
)
from app.middleware.auth import (
    token_required,
    admin_required,
    get_current_user
)


def can_manage_organisation(current_user: dict, org_id: int) -> bool:
    """
    Check if user can manage organisation

    Args:
        current_user: Current user dict
        org_id: Organisation ID

    Returns:
        True if user can manage, False otherwise
    """
    # Admins can manage all organisations
    if current_user.get('role') in ['admin', 'superadmin']:
        return True

    # org_admin can manage their own organisation
    if current_user.get('org_role') == 'org_admin' and current_user.get('organization_id') == org_id:
        return True

    return False


def check_org_membership(current_user: dict, org_id: int, required_roles: list = None) -> bool:
    """
    Check if user is member of organisation with required role

    Args:
        current_user: Current user dict
        org_id: Organisation ID
        required_roles: List of required org roles (optional)

    Returns:
        True if user is member with required role, False otherwise
    """
    # Admins can access all organisations
    if current_user.get('role') in ['admin', 'superadmin']:
        return True

    # Check if user is member of this organisation
    if current_user.get('organization_id') != org_id:
        return False

    # If roles required, check org_role
    if required_roles:
        return current_user.get('org_role') in required_roles

    return True


__all__ = [
    # Flask
    'request',
    'jsonify',
    'g',
    # Pydantic
    'ValidationError',
    # DDD Services/Repos
    'OrganisationRepository',
    'OrganisationService',
    # Models (Legacy)
    'OrganisationCreate',
    'OrganisationUpdate',
    'OrganisationResponse',
    'OrganisationListResponse',
    'OrganisationAssignUserRequest',
    'OrganisationUserResponse',
    # Middleware (Legacy)
    'token_required',
    'admin_required',
    'get_current_user',
    # Helpers
    'can_manage_organisation',
    'check_org_membership',
]
