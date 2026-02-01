"""
Setup Wizard - Groups Management API Routes

Provides API endpoints for creating and managing authorization groups
during the setup wizard with flexible hierarchy levels (1-1000).

Endpoints:
- GET /setup/groups - List all groups
- POST /setup/groups - Create new group
- POST /setup/groups/:id/permissions - Assign permission to group
- POST /setup/groups/:id/assign-user - Assign user to group
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Tuple
from app.setup.group_setup import GroupSetup
from app.setup.admin_setup import AdminSetup


bp = Blueprint('setup_groups', __name__, url_prefix='/setup/groups')


def _get_response(data: any, status_code: int = 200) -> Tuple[Dict, int]:
    """Standardize API response format."""
    return jsonify({'success': status_code < 400, 'data': data}), status_code


# ============================================================================
# 1. LIST GROUPS
# ============================================================================

@bp.route('', methods=['GET'])
def list_groups():
    """
    GET /setup/groups

    List all available groups with hierarchy levels.

    Query Parameters:
        - organisation_id: Optional org ID to filter

    Returns:
        200: List of groups sorted by hierarchy level (descending)

    Example:
        GET /setup/groups
        {
            "success": true,
            "data": [
                {
                    "id": "uuid",
                    "name": "System Admin",
                    "slug": "system-admin",
                    "hierarchy_level": 950,
                    "group_type": "system_admin",
                    "is_system_group": true,
                    "is_protected": true
                },
                ...
            ]
        }
    """
    try:
        organisation_id = request.args.get('organisation_id')
        groups = GroupSetup.get_all_groups(organisation_id=organisation_id)

        return _get_response({
            'groups': groups,
            'total': len(groups),
            'hierarchy_info': {
                'min_level': 1,
                'max_level': 1000,
                'available_levels': list(range(1, 1001)),
                'predefined_levels': {
                    'owner': 1000,
                    'system_admin': 950,
                    'org_admin': 800,
                    'content_management': 600,
                    'teacher': 400,
                    'support': 350,
                    'premium': 250,
                    'regular_user': 100,
                    'guest': 50
                }
            }
        }, 200)

    except Exception as e:
        return _get_response({'error': str(e)}, 400)


# ============================================================================
# 2. CREATE GROUP
# ============================================================================

@bp.route('', methods=['POST'])
def create_group():
    """
    POST /setup/groups

    Create a new authorization group with hierarchical level.

    Request Body:
        {
            "name": "Organization Owner",          # Required
            "slug": "org-owner",                   # Required
            "description": "Organization owner",   # Optional
            "hierarchy_level": 1000,               # Required (1-1000)
            "group_type": "org_admin",             # Optional (default: 'custom')
            "organisation_id": "org-uuid",         # Optional
            "is_system_group": false,              # Optional (default: false)
            "is_protected": false                  # Optional (default: false)
        }

    Returns:
        201: Created group with all details
        400: Validation error (hierarchy out of range, invalid slug, etc.)

    Example:
        POST /setup/groups
        Content-Type: application/json

        {
            "name": "Organization Owner",
            "slug": "org-owner",
            "description": "Full authority within organisation",
            "hierarchy_level": 1000,
            "group_type": "org_admin",
            "is_protected": true
        }

        Response:
        {
            "success": true,
            "data": {
                "id": "group-uuid",
                "name": "Organization Owner",
                "slug": "org-owner",
                "hierarchy_level": 1000,
                "group_type": "org_admin",
                "is_protected": true,
                "created_at": "2026-01-25T10:30:00Z"
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return _get_response({'error': 'Request body required'}, 400)

        # Validate required fields
        required = ['name', 'slug', 'hierarchy_level']
        missing = [f for f in required if f not in data]
        if missing:
            return _get_response({
                'error': f"Missing required fields: {', '.join(missing)}"
            }, 400)

        # Create group
        group = GroupSetup.create_group(
            name=data['name'],
            slug=data['slug'],
            description=data.get('description', ''),
            hierarchy_level=data['hierarchy_level'],
            group_type=data.get('group_type', 'custom'),
            organisation_id=data.get('organisation_id'),
            is_system_group=data.get('is_system_group', False),
            is_protected=data.get('is_protected', False)
        )

        return _get_response(group, 201)

    except ValueError as e:
        return _get_response({'error': str(e)}, 400)
    except Exception as e:
        return _get_response({'error': f"Server error: {str(e)}"}, 500)


# ============================================================================
# 3. ASSIGN PERMISSION TO GROUP
# ============================================================================

@bp.route('/<group_id>/permissions', methods=['POST'])
def assign_permission(group_id: str):
    """
    POST /setup/groups/:group_id/permissions

    Assign permission to a group.

    Path Parameters:
        - group_id: Group ID

    Request Body:
        {
            "permission_code": "content.courses:write",  # Required
            "admin_user_id": "admin-uuid"                # Optional (for audit)
        }

    Returns:
        201: Permission assigned
        400: Invalid permission or group

    Example:
        POST /setup/groups/group-uuid/permissions
        {
            "permission_code": "admin.users:write"
        }
    """
    try:
        data = request.get_json()

        if not data or 'permission_code' not in data:
            return _get_response({'error': 'permission_code required'}, 400)

        permission = GroupSetup.assign_permission_to_group(
            group_id=group_id,
            permission_code=data['permission_code'],
            admin_user_id=data.get('admin_user_id')
        )

        return _get_response(permission, 201)

    except ValueError as e:
        return _get_response({'error': str(e)}, 400)
    except Exception as e:
        return _get_response({'error': f"Server error: {str(e)}"}, 500)


# ============================================================================
# 4. GET GROUP PERMISSIONS
# ============================================================================

@bp.route('/<group_id>/permissions', methods=['GET'])
def get_group_permissions(group_id: str):
    """
    GET /setup/groups/:group_id/permissions

    Get all permissions assigned to a group.

    Path Parameters:
        - group_id: Group ID

    Returns:
        200: List of permissions

    Example:
        GET /setup/groups/group-uuid/permissions
        {
            "success": true,
            "data": {
                "permissions": [
                    {
                        "id": "perm-uuid",
                        "code": "admin.users:write",
                        "display_name": "Write Users",
                        "category": "admin",
                        "assigned_at": "2026-01-25T10:30:00Z"
                    },
                    ...
                ]
            }
        }
    """
    try:
        permissions = GroupSetup.get_group_permissions(group_id)
        return _get_response({'permissions': permissions}, 200)

    except Exception as e:
        return _get_response({'error': str(e)}, 500)


# ============================================================================
# 5. ASSIGN USER TO GROUP
# ============================================================================

@bp.route('/<group_id>/assign-user', methods=['POST'])
def assign_user(group_id: str):
    """
    POST /setup/groups/:group_id/assign-user

    Assign a user to a group.

    Path Parameters:
        - group_id: Group ID

    Request Body:
        {
            "user_id": "user-uuid",         # Required
            "member_role": "member",        # Optional (member, moderator, owner)
            "admin_user_id": "admin-uuid"   # Optional (for admin validation)
        }

    Returns:
        201: User assigned to group
        400: Invalid user or group

    Example:
        POST /setup/groups/group-uuid/assign-user
        {
            "user_id": "user-uuid",
            "member_role": "owner"
        }
    """
    try:
        data = request.get_json()

        if not data or 'user_id' not in data:
            return _get_response({'error': 'user_id required'}, 400)

        assignment = GroupSetup.assign_group_to_user(
            user_id=data['user_id'],
            group_id=group_id,
            admin_user_id=data.get('admin_user_id'),
            member_role=data.get('member_role', 'member')
        )

        return _get_response(assignment, 201)

    except ValueError as e:
        return _get_response({'error': str(e)}, 400)
    except Exception as e:
        return _get_response({'error': f"Server error: {str(e)}"}, 500)


# ============================================================================
# 6. SETUP ADMIN WITH CUSTOM GROUP
# ============================================================================

@bp.route('/setup-admin', methods=['POST'])
def setup_admin_with_group():
    """
    POST /setup/groups/setup-admin

    Create admin user and assign to specified group (FLEXIBLE).

    Request Body:
        {
            "email": "admin@example.com",
            "password": "SecurePass123!",
            "first_name": "Admin",
            "last_name": "User",
            "admin_group_slug": "owner",          # Can be any group slug!
            "organisation_id": "org-uuid",        # Optional
            "enable_2fa": false                   # Optional
        }

    Returns:
        201: Admin created and assigned to group

    Example:
        POST /setup/groups/setup-admin
        {
            "email": "owner@example.com",
            "password": "SecurePass123!",
            "first_name": "Owner",
            "last_name": "User",
            "admin_group_slug": "owner",          # NEW: Flexible group!
            "enable_2fa": true
        }

        Response:
        {
            "success": true,
            "data": {
                "user_id": "user-uuid",
                "email": "owner@example.com",
                "admin_group": "Owner",            # Shows which group
                "admin_group_slug": "owner",
                "hierarchy_level": 1000,           # Shows hierarchy
                "is_owner": true,
                "two_factor_enabled": true,
                "recovery_codes": ["code1", ...]
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return _get_response({'error': 'Request body required'}, 400)

        # Validate required fields
        required = ['email', 'password', 'first_name', 'last_name']
        missing = [f for f in required if f not in data]
        if missing:
            return _get_response({
                'error': f"Missing required fields: {', '.join(missing)}"
            }, 400)

        # Create admin with flexible group (NOT HARDCODED!)
        admin = AdminSetup.create_admin(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            admin_group_slug=data.get('admin_group_slug', 'system-admin'),  # FLEXIBLE!
            organisation_id=data.get('organisation_id'),
            enable_2fa=data.get('enable_2fa', False)
        )

        return _get_response(admin, 201)

    except ValueError as e:
        return _get_response({'error': str(e)}, 400)
    except Exception as e:
        return _get_response({'error': f"Server error: {str(e)}"}, 500)
