"""
Shared helper functions for organisations API

Contains permission checking and common utilities used across modules.
"""

from typing import Optional


def can_manage_organisation(user: dict, org_id: int) -> bool:
    """
    Check if user can manage organisation

    Args:
        user: Current user dictionary
        org_id: Organisation ID

    Returns:
        True if user can manage this organisation
    """
    # Admins can manage all organisations
    if user['role'] in ['admin', 'superadmin']:
        return True

    # Organisation admins can only manage their own organisation
    if user.get('organization_id') == org_id:
        # Check if user has org_admin role
        org_user_query = """
            SELECT org_role FROM organisation_users
            WHERE org_id = %s AND user_id = %s AND status = 'active'
        """
        from app.database.connection import fetch_one
        org_user = fetch_one(org_user_query, (org_id, user['user_id']))

        if org_user and org_user['org_role'] == 'org_admin':
            return True

    return False


def check_org_membership(user: dict, org_id: int, required_roles: Optional[list] = None) -> bool:
    """
    Check if user is a member of organisation with optional role check

    Args:
        user: Current user dictionary
        org_id: Organisation ID
        required_roles: Optional list of required org roles (e.g., ['org_admin', 'teacher'])

    Returns:
        True if user is member (and has required role if specified)
    """
    # Admins always have access
    if user['role'] in ['admin', 'superadmin']:
        return True

    # Check basic membership
    if user.get('organization_id') != org_id:
        return False

    # If no specific role required, membership is enough
    if not required_roles:
        return True

    # Check org role
    from app.database.connection import fetch_one
    org_user_query = """
        SELECT org_role FROM organisation_users
        WHERE org_id = %s AND user_id = %s AND status = 'active'
    """
    org_user = fetch_one(org_user_query, (org_id, user['user_id']))

    if org_user and org_user['org_role'] in required_roles:
        return True

    return False
