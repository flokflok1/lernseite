"""
LernsystemX Setup - Group Management

Provides flexible group creation and management during setup wizard.
Allows creating custom groups with hierarchy levels up to 1000.

ISO 27001:2013 compliant - Flexible authorization groups
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid

from app.infrastructure.persistence.database.connection import execute_query, fetch_one, fetch_all


class GroupSetup:
    """
    Setup and manage authorization groups

    Implements flexible group hierarchy with levels 1-1000.
    """

    # Predefined hierarchy levels
    HIERARCHY_LEVELS = {
        'owner': 1000,              # Super Admin (highest)
        'system_admin': 950,        # System Admin
        'org_admin': 800,           # Organization Admin
        'content_management': 600,  # Content Management
        'teacher': 400,             # Teachers
        'support': 350,             # Support Team
        'premium': 250,             # Premium Members
        'regular_user': 100,        # Regular Users
        'guest': 50,                # Guest Access
    }

    @classmethod
    def create_group(
        cls,
        name: str,
        slug: str,
        description: str,
        hierarchy_level: int,
        group_type: str = 'custom',
        organisation_id: Optional[str] = None,
        is_system_group: bool = False,
        is_protected: bool = False
    ) -> Dict:
        """
        Create a new group with hierarchical authorization.

        Args:
            name: Group name (e.g., 'Organization Owner')
            slug: URL-safe identifier (e.g., 'org-owner')
            description: Group description
            hierarchy_level: Authorization level (1-1000). Higher = more authority.
                            1000 = Owner (highest), 1 = Guest (lowest)
            group_type: Type of group (custom, department, team, org_admin, system_admin)
            organisation_id: Optional org ID for org-specific groups
            is_system_group: True if this is a system group
            is_protected: True if group cannot be deleted

        Returns:
            Dictionary with created group data

        Raises:
            ValueError: If validation fails

        Example:
            >>> group = GroupSetup.create_group(
            ...     name='Organization Owner',
            ...     slug='org-owner',
            ...     description='Organization owner with full authority',
            ...     hierarchy_level=1000,
            ...     group_type='org_admin',
            ...     is_system_group=True,
            ...     is_protected=True
            ... )
            >>> print(f"Created group: {group['id']}")
        """
        # Validate hierarchy level
        if not (1 <= hierarchy_level <= 1000):
            raise ValueError(f"Hierarchy level must be between 1 and 1000, got {hierarchy_level}")

        # Validate slug format
        if not cls._validate_slug(slug):
            raise ValueError("Slug must be lowercase alphanumeric with hyphens only")

        # Validate group type
        valid_types = ['department', 'class', 'team', 'org_admin', 'org_members',
                      'system_admin', 'moderators', 'support', 'custom']
        if group_type not in valid_types:
            raise ValueError(f"Invalid group_type. Must be one of: {', '.join(valid_types)}")

        # Check if slug already exists
        existing = fetch_one(
            """
            SELECT id FROM core.groups
            WHERE slug = %s
              AND (organisation_id IS NULL OR organisation_id = %s)
            """,
            (slug, organisation_id)
        )
        if existing:
            raise ValueError(f"Group with slug '{slug}' already exists")

        # Create group
        group_id = str(uuid.uuid4())

        result = execute_query(
            """
            INSERT INTO core.groups (
                id, name, slug, description, hierarchy_level, group_type,
                organisation_id, is_system_group, is_protected, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id, name, slug, hierarchy_level, group_type, is_system_group
            """,
            (group_id, name, slug, description, hierarchy_level, group_type,
             organisation_id, is_system_group, is_protected),
            fetch_one=True
        )

        if not result:
            raise ValueError("Failed to create group")

        return {
            'id': result['id'],
            'name': result['name'],
            'slug': result['slug'],
            'description': description,
            'hierarchy_level': result['hierarchy_level'],
            'group_type': result['group_type'],
            'is_system_group': result['is_system_group'],
            'is_protected': is_protected,
            'created_at': datetime.utcnow().isoformat()
        }

    @classmethod
    def assign_group_to_user(
        cls,
        user_id: str,
        group_id: str,
        admin_user_id: Optional[str] = None,
        member_role: str = 'member'
    ) -> Dict:
        """
        Assign a user to a group (with optional admin authorization check).

        Args:
            user_id: Target user ID
            group_id: Group ID to assign
            admin_user_id: Admin performing the assignment (for audit logging)
            member_role: Role within group (member, moderator, owner)

        Returns:
            Dictionary with assignment data

        Raises:
            ValueError: If validation fails or admin lacks authority

        Example:
            >>> assignment = GroupSetup.assign_group_to_user(
            ...     user_id='user-123',
            ...     group_id='group-456',
            ...     admin_user_id='admin-789'
            ... )
        """
        # Validate member role
        valid_roles = ['member', 'moderator', 'owner']
        if member_role not in valid_roles:
            raise ValueError(f"Invalid member_role. Must be one of: {', '.join(valid_roles)}")

        # Get group hierarchy level
        group = fetch_one(
            "SELECT id, hierarchy_level, name FROM core.groups WHERE id = %s",
            (group_id,)
        )
        if not group:
            raise ValueError(f"Group {group_id} not found")

        # If admin specified, validate they have authority
        if admin_user_id:
            admin_valid, reason = cls._validate_admin_hierarchy(
                admin_user_id,
                group['hierarchy_level']
            )
            if not admin_valid:
                raise ValueError(f"Admin lacks authority: {reason}")

        # Create assignment
        result = execute_query(
            """
            INSERT INTO core.users_groups (
                user_id, group_id, member_role, is_active, joined_at, created_at
            )
            VALUES (%s, %s, %s, TRUE, NOW(), NOW())
            ON CONFLICT (user_id, group_id) DO UPDATE
            SET is_active = TRUE, member_role = %s
            RETURNING user_id, group_id, member_role, joined_at
            """,
            (user_id, group_id, member_role, member_role),
            fetch_one=True
        )

        # Audit log
        if admin_user_id:
            cls._audit_assignment(
                user_id, group_id, admin_user_id,
                f"Assigned to group {group['name']} (level {group['hierarchy_level']})"
            )

        return {
            'user_id': result['user_id'],
            'group_id': result['group_id'],
            'member_role': result['member_role'],
            'joined_at': result['joined_at'].isoformat() if result['joined_at'] else None
        }

    @classmethod
    def assign_permission_to_group(
        cls,
        group_id: str,
        permission_code: str,
        admin_user_id: Optional[str] = None
    ) -> Dict:
        """
        Assign a permission to a group.

        Args:
            group_id: Group ID
            permission_code: Permission code (e.g., 'content.courses:write')
            admin_user_id: Admin performing assignment (for audit)

        Returns:
            Dictionary with assignment data

        Example:
            >>> perm = GroupSetup.assign_permission_to_group(
            ...     group_id='group-123',
            ...     permission_code='admin.users:write'
            ... )
        """
        # Get permission ID
        permission = fetch_one(
            "SELECT id, code, display_name FROM core.permissions WHERE code = %s",
            (permission_code,)
        )
        if not permission:
            raise ValueError(f"Permission {permission_code} not found")

        # Assign permission
        result = execute_query(
            """
            INSERT INTO core.group_permissions (group_id, permission_id, created_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (group_id, permission_id) DO NOTHING
            RETURNING group_id, permission_id
            """,
            (group_id, permission['id']),
            fetch_one=True
        )

        if result:
            # Audit log
            if admin_user_id:
                cls._audit_permission_assignment(
                    group_id, permission_code, admin_user_id,
                    f"Granted permission {permission_code}"
                )

            return {
                'group_id': result['group_id'],
                'permission_id': result['permission_id'],
                'permission_code': permission_code,
                'assigned_at': datetime.utcnow().isoformat()
            }

        return {'status': 'already_assigned'}

    @classmethod
    def get_all_groups(cls, organisation_id: Optional[str] = None) -> List[Dict]:
        """
        Get all groups (optionally filtered by organization).

        Args:
            organisation_id: Optional org ID to filter

        Returns:
            List of group dictionaries
        """
        if organisation_id:
            groups = fetch_all(
                """
                SELECT id, name, slug, description, hierarchy_level, group_type,
                       is_system_group, is_protected, created_at
                FROM core.groups
                WHERE organisation_id = %s OR (organisation_id IS NULL AND is_system_group = TRUE)
                ORDER BY hierarchy_level DESC, name ASC
                """,
                (organisation_id,)
            )
        else:
            groups = fetch_all(
                """
                SELECT id, name, slug, description, hierarchy_level, group_type,
                       is_system_group, is_protected, created_at
                FROM core.groups
                ORDER BY hierarchy_level DESC, name ASC
                """
            )

        return [
            {
                'id': g['id'],
                'name': g['name'],
                'slug': g['slug'],
                'description': g['description'],
                'hierarchy_level': g['hierarchy_level'],
                'group_type': g['group_type'],
                'is_system_group': g['is_system_group'],
                'is_protected': g['is_protected'],
                'created_at': g['created_at'].isoformat() if g['created_at'] else None
            }
            for g in groups
        ]

    @classmethod
    def get_group_permissions(cls, group_id: str) -> List[Dict]:
        """
        Get all permissions assigned to a group.

        Args:
            group_id: Group ID

        Returns:
            List of permission dictionaries
        """
        permissions = fetch_all(
            """
            SELECT p.id, p.code, p.display_name, p.category, gp.created_at
            FROM core.group_permissions gp
            JOIN core.permissions p ON gp.permission_id = p.id
            WHERE gp.group_id = %s
            ORDER BY p.code ASC
            """,
            (group_id,)
        )

        return [
            {
                'id': p['id'],
                'code': p['code'],
                'display_name': p['display_name'],
                'category': p['category'],
                'assigned_at': p['created_at'].isoformat() if p['created_at'] else None
            }
            for p in permissions
        ]

    @staticmethod
    def _validate_slug(slug: str) -> bool:
        """Validate slug format (lowercase alphanumeric with hyphens)."""
        import re
        return bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', slug))

    @staticmethod
    def _validate_admin_hierarchy(admin_user_id: str, target_hierarchy: int) -> Tuple[bool, str]:
        """Check if admin has authority to manage target hierarchy level."""
        result = execute_query(
            """
            SELECT validate_hierarchy_assignment(%s, %s) as (is_valid BOOLEAN, reason VARCHAR)
            """,
            (admin_user_id, target_hierarchy),
            fetch_one=True
        )

        if result:
            return result['is_valid'], result['reason']
        return False, "Unknown error"

    @staticmethod
    def _audit_assignment(user_id: str, group_id: str, admin_id: str, action: str) -> None:
        """Log group assignment to audit log."""
        execute_query(
            """
            SELECT audit_hierarchy_assignment(%s, %s,
                (SELECT hierarchy_level FROM core.groups WHERE id = %s),
                %s, %s)
            """,
            (user_id, group_id, group_id, admin_id, action)
        )

    @staticmethod
    def _audit_permission_assignment(group_id: str, permission_code: str, admin_id: str, action: str) -> None:
        """Log permission assignment to audit log."""
        execute_query(
            """
            INSERT INTO audit_logs (event_type, user_id, action, severity, metadata, created_at)
            VALUES ('permission_assignment', %s, %s, 'low',
                    %s::jsonb, NOW())
            """,
            (admin_id, action, f'{{"group_id": "{group_id}", "permission_code": "{permission_code}"}}')
        )


# Convenience functions
def create_group(**kwargs) -> Dict:
    """Quick group creation function."""
    return GroupSetup.create_group(**kwargs)


def assign_group_to_user(**kwargs) -> Dict:
    """Quick group assignment function."""
    return GroupSetup.assign_group_to_user(**kwargs)


def assign_permission_to_group(**kwargs) -> Dict:
    """Quick permission assignment function."""
    return GroupSetup.assign_permission_to_group(**kwargs)
