"""
Roles & Permissions Service
============================
Service for managing roles, permissions and user assignments.
Supports custom roles and user-specific permission overrides.
"""

from typing import Optional, List, Dict, Any
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query
import logging

logger = logging.getLogger(__name__)


class RolesService:
    """Service for role and permission management."""

    # =========================================================================
    # Roles CRUD
    # =========================================================================

    @staticmethod
    def get_all_roles(include_system: bool = True) -> List[Dict[str, Any]]:
        """Get all roles with their permission counts."""
        try:
            query = """
                SELECT
                    r.role_id,
                    r.role_name,
                    r.display_name,
                    r.description,
                    r.hierarchy_level,
                    r.is_builtin,
                    r.is_administrator,
                    r.color,
                    r.icon,
                    r.created_at,
                    COUNT(DISTINCT rp.permission_id) as permission_count,
                    COUNT(DISTINCT u.user_id) as user_count
                FROM roles r
                LEFT JOIN role_permissions rp ON r.role_id = rp.role_id
                LEFT JOIN users u ON r.role_id = u.role_id
                WHERE (%s = TRUE OR r.is_builtin = FALSE)
                GROUP BY r.role_id
                ORDER BY r.hierarchy_level DESC, r.role_name
            """
            return fetch_all(query, (include_system,)) or []
        except Exception as e:
            logger.error(f"Error fetching roles: {e}")
            return []

    @staticmethod
    def get_role(role_id: int) -> Optional[Dict[str, Any]]:
        """Get single role with full details."""
        try:
            query = """
                SELECT
                    r.role_id,
                    r.role_name,
                    r.display_name,
                    r.description,
                    r.hierarchy_level,
                    r.is_builtin,
                    r.is_administrator,
                    r.color,
                    r.icon,
                    r.created_by,
                    r.created_at
                FROM roles r
                WHERE r.role_id = %s
            """
            role = fetch_one(query, (role_id,))
            if role:
                role['permissions'] = RolesService.get_role_permissions(role_id)
            return role
        except Exception as e:
            logger.error(f"Error fetching role {role_id}: {e}")
            return None

    @staticmethod
    def create_role(
        role_name: str,
        display_name: str,
        description: Optional[str],
        hierarchy_level: int,
        color: str,
        icon: str,
        created_by: str
    ) -> Optional[int]:
        """Create a new custom role."""
        try:
            query = """
                INSERT INTO roles
                    (role_name, display_name, description, hierarchy_level,
                     is_builtin, is_administrator, color, icon, created_by)
                VALUES (%s, %s, %s, %s, FALSE, FALSE, %s, %s, %s)
                RETURNING role_id
            """
            result = fetch_one(query, (
                role_name, display_name, description, hierarchy_level,
                color, icon, created_by
            ))
            return result['role_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return None

    @staticmethod
    def update_role(
        role_id: int,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        hierarchy_level: Optional[int] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None
    ) -> bool:
        """Update role (only custom roles can be fully edited)."""
        try:
            # Build dynamic update query
            updates = []
            params = []

            if display_name is not None:
                updates.append("display_name = %s")
                params.append(display_name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if hierarchy_level is not None:
                updates.append("hierarchy_level = %s")
                params.append(hierarchy_level)
            if color is not None:
                updates.append("color = %s")
                params.append(color)
            if icon is not None:
                updates.append("icon = %s")
                params.append(icon)

            if not updates:
                return True

            params.append(role_id)
            query = f"""
                UPDATE roles SET {', '.join(updates)}
                WHERE role_id = %s AND is_builtin = FALSE
            """
            execute_query(query, tuple(params))
            return True
        except Exception as e:
            logger.error(f"Error updating role {role_id}: {e}")
            return False

    @staticmethod
    def delete_role(role_id: int) -> bool:
        """Delete a custom role (moves users to 'free' role)."""
        try:
            # First move users to free role
            execute_query(
                """
                UPDATE users SET role_id = (SELECT role_id FROM roles WHERE role_name = 'free')
                WHERE role_id = %s
                """,
                (role_id,)
            )
            # Delete role (only custom roles)
            execute_query(
                "DELETE FROM roles WHERE role_id = %s AND is_builtin = FALSE",
                (role_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting role {role_id}: {e}")
            return False

    # =========================================================================
    # Permissions
    # =========================================================================

    @staticmethod
    def get_all_permissions(category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all available permissions grouped by category."""
        try:
            query = """
                SELECT
                    permission_id,
                    permission_key,
                    display_name,
                    description,
                    module,
                    category,
                    is_system,
                    sort_order
                FROM permissions
                WHERE (%s IS NULL OR category = %s)
                ORDER BY category, sort_order, permission_key
            """
            return fetch_all(query, (category, category)) or []
        except Exception as e:
            logger.error(f"Error fetching permissions: {e}")
            return []

    @staticmethod
    def get_permissions_grouped() -> Dict[str, List[Dict[str, Any]]]:
        """Get permissions grouped by category."""
        permissions = RolesService.get_all_permissions()
        grouped = {}
        for perm in permissions:
            cat = perm.get('category', 'Sonstige')
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(perm)
        return grouped

    # =========================================================================
    # Role-Permission Assignments
    # =========================================================================

    @staticmethod
    def get_role_permissions(role_id: int) -> List[Dict[str, Any]]:
        """Get all permissions for a role."""
        try:
            query = """
                SELECT
                    p.permission_id,
                    p.permission_key,
                    p.display_name,
                    p.module,
                    p.category
                FROM permissions p
                JOIN role_permissions rp ON p.permission_id = rp.permission_id
                WHERE rp.role_id = %s
                ORDER BY p.category, p.sort_order
            """
            return fetch_all(query, (role_id,)) or []
        except Exception as e:
            logger.error(f"Error fetching role permissions: {e}")
            return []

    @staticmethod
    def set_role_permissions(role_id: int, permission_ids: List[int]) -> bool:
        """Set permissions for a role (replaces existing)."""
        try:
            # Remove existing permissions
            execute_query(
                "DELETE FROM role_permissions WHERE role_id = %s",
                (role_id,)
            )
            # Add new permissions
            for perm_id in permission_ids:
                execute_query(
                    "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (role_id, perm_id)
                )
            return True
        except Exception as e:
            logger.error(f"Error setting role permissions: {e}")
            return False

    @staticmethod
    def add_role_permission(role_id: int, permission_id: int) -> bool:
        """Add single permission to role."""
        try:
            execute_query(
                "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (role_id, permission_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error adding role permission: {e}")
            return False

    @staticmethod
    def remove_role_permission(role_id: int, permission_id: int) -> bool:
        """Remove single permission from role."""
        try:
            execute_query(
                "DELETE FROM role_permissions WHERE role_id = %s AND permission_id = %s",
                (role_id, permission_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error removing role permission: {e}")
            return False

    # =========================================================================
    # User-Permission Overrides
    # =========================================================================

    @staticmethod
    def get_user_permission_overrides(user_id: str) -> List[Dict[str, Any]]:
        """Get user-specific permission overrides."""
        try:
            query = """
                SELECT
                    up.permission_id,
                    p.permission_key,
                    p.display_name,
                    p.category,
                    up.granted,
                    up.granted_by,
                    u.username as granted_by_username,
                    up.granted_at,
                    up.expires_at,
                    up.reason
                FROM user_permissions up
                JOIN permissions p ON up.permission_id = p.permission_id
                LEFT JOIN users u ON up.granted_by = u.user_id
                WHERE up.user_id = %s
                ORDER BY p.category, p.sort_order
            """
            return fetch_all(query, (user_id,)) or []
        except Exception as e:
            logger.error(f"Error fetching user overrides: {e}")
            return []

    @staticmethod
    def set_user_permission_override(
        user_id: str,
        permission_id: int,
        granted: bool,
        granted_by: str,
        expires_at: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """Set or update user permission override."""
        try:
            query = """
                INSERT INTO user_permissions
                    (user_id, permission_id, granted, granted_by, expires_at, reason)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, permission_id) DO UPDATE SET
                    granted = EXCLUDED.granted,
                    granted_by = EXCLUDED.granted_by,
                    granted_at = NOW(),
                    expires_at = EXCLUDED.expires_at,
                    reason = EXCLUDED.reason
            """
            execute_query(query, (
                user_id, permission_id, granted, granted_by, expires_at, reason
            ))
            return True
        except Exception as e:
            logger.error(f"Error setting user override: {e}")
            return False

    @staticmethod
    def remove_user_permission_override(user_id: str, permission_id: int) -> bool:
        """Remove user permission override."""
        try:
            execute_query(
                "DELETE FROM user_permissions WHERE user_id = %s AND permission_id = %s",
                (user_id, permission_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error removing user override: {e}")
            return False

    # =========================================================================
    # User Role Management
    # =========================================================================

    @staticmethod
    def get_users_by_role(role_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get users with a specific role."""
        try:
            query = """
                SELECT
                    u.user_id,
                    u.username,
                    u.email,
                    u.first_name,
                    u.last_name,
                    u.is_active,
                    u.created_at,
                    u.last_login
                FROM users u
                WHERE u.role_id = %s
                ORDER BY u.username
                LIMIT %s
            """
            return fetch_all(query, (role_id, limit)) or []
        except Exception as e:
            logger.error(f"Error fetching users by role: {e}")
            return []

    @staticmethod
    def assign_role_to_user(user_id: str, role_id: int) -> bool:
        """Assign a role to a user."""
        try:
            execute_query(
                "UPDATE users SET role_id = %s WHERE user_id = %s",
                (role_id, user_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error assigning role to user: {e}")
            return False

    @staticmethod
    def get_user_effective_permissions(user_id: str) -> List[Dict[str, Any]]:
        """Get all effective permissions for a user (role + overrides)."""
        try:
            query = "SELECT * FROM get_user_permissions(%s)"
            return fetch_all(query, (user_id,)) or []
        except Exception as e:
            logger.error(f"Error fetching user permissions: {e}")
            return []

    @staticmethod
    def check_user_permission(user_id: str, permission_key: str) -> bool:
        """Check if user has a specific permission."""
        try:
            query = "SELECT user_has_permission(%s, %s) as has_perm"
            result = fetch_one(query, (user_id, permission_key))
            return result.get('has_perm', False) if result else False
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
