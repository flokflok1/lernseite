"""
LernsystemX Roles Repository

Repository for RBAC 2.0 - Custom Roles & Feature Assignments.

Phase 5.3 - Owner-Admin & Dynamic Roles System
"""

from typing import Optional, List, Dict, Any
from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    delete_returning,
    execute_query
)


class RolesRepository(BaseRepository):
    """Repository for roles management"""

    table_name = 'core.roles'
    pk_column = 'role_id'

    @classmethod
    def find_by_name(cls, role_name: str) -> Optional[Dict]:
        """
        Find role by name

        Args:
            role_name: Role name to search for

        Returns:
            Role as dictionary or None
        """
        query = """
            SELECT * FROM core.roles
            WHERE role_name = %s
        """
        return fetch_one(query, (role_name,))

    @classmethod
    def find_all_with_stats(
        cls,
        is_builtin: Optional[bool] = None,
        hierarchy_min: Optional[int] = None,
        hierarchy_max: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Dict]:
        """
        Find all roles with feature/permission counts

        Args:
            is_builtin: Filter by builtin roles (None = all)
            hierarchy_min: Minimum hierarchy level
            hierarchy_max: Maximum hierarchy level
            search: Search in role_name or display_name

        Returns:
            List of roles with statistics
        """
        conditions = []
        params = []

        if is_builtin is not None:
            conditions.append("r.is_builtin = %s")
            params.append(is_builtin)

        if hierarchy_min is not None:
            conditions.append("r.hierarchy_level >= %s")
            params.append(hierarchy_min)

        if hierarchy_max is not None:
            conditions.append("r.hierarchy_level <= %s")
            params.append(hierarchy_max)

        if search:
            conditions.append("(r.role_name ILIKE %s OR r.display_name ILIKE %s)")
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT
                r.*,
                COUNT(DISTINCT rfa.feature_id) as feature_count,
                COUNT(DISTINCT rp.permission_id) as permission_count,
                COUNT(DISTINCT u.user_id) as user_count
            FROM core.roles r
            LEFT JOIN core.role_feature_assignments rfa ON r.role_id = rfa.role_id AND rfa.enabled = TRUE
            LEFT JOIN core.role_permissions rp ON r.role_id = rp.role_id
            LEFT JOIN core.users u ON r.role_id = u.role_id
            {where_clause}
            GROUP BY r.role_id
            ORDER BY r.hierarchy_level DESC, r.role_name
        """

        return fetch_all(query, tuple(params) if params else None)

    @classmethod
    def find_by_id_with_details(cls, role_id: int) -> Optional[Dict]:
        """
        Find role by ID with full details (features, permissions, user count)

        Args:
            role_id: Role ID

        Returns:
            Role with details or None
        """
        query = """
            SELECT
                r.*,
                COUNT(DISTINCT rfa.feature_id) as feature_count,
                COUNT(DISTINCT rp.permission_id) as permission_count,
                COUNT(DISTINCT u.user_id) as user_count
            FROM core.roles r
            LEFT JOIN core.role_feature_assignments rfa ON r.role_id = rfa.role_id AND rfa.enabled = TRUE
            LEFT JOIN core.role_permissions rp ON r.role_id = rp.role_id
            LEFT JOIN core.users u ON r.role_id = u.role_id
            WHERE r.role_id = %s
            GROUP BY r.role_id
        """
        return fetch_one(query, (role_id,))

    @classmethod
    def get_role_features(cls, role_id: int) -> List[Dict]:
        """
        Get all features assigned to a role

        Args:
            role_id: Role ID

        Returns:
            List of features with assignment status
        """
        query = """
            SELECT
                f.feature_id,
                f.feature_code,
                f.feature_name,
                f.category,
                f.active,
                COALESCE(rfa.enabled, FALSE) as enabled_for_role
            FROM support_systems.system_features f
            LEFT JOIN core.role_feature_assignments rfa
                ON f.feature_id = rfa.feature_id
                AND rfa.role_id = %s
            ORDER BY f.category, f.feature_name
        """
        return fetch_all(query, (role_id,))

    @classmethod
    def get_role_permissions(cls, role_id: int) -> List[Dict]:
        """
        Get all permissions assigned to a role

        Args:
            role_id: Role ID

        Returns:
            List of permissions
        """
        query = """
            SELECT
                p.permission_id,
                p.permission_key,
                p.display_name,
                p.description,
                p.module,
                p.category
            FROM core.permissions p
            JOIN core.role_permissions rp ON p.permission_id = rp.permission_id
            WHERE rp.role_id = %s
            ORDER BY p.category, p.permission_key
        """
        return fetch_all(query, (role_id,))

    @classmethod
    def create_role(
        cls,
        role_name: str,
        display_name: str,
        description: Optional[str],
        hierarchy_level: int,
        color: str,
        icon: str,
        created_by: str  # UUID
    ) -> Dict:
        """
        Create a new custom role

        Args:
            role_name: Unique role name
            display_name: Display name
            description: Role description
            hierarchy_level: Hierarchy level (1-8)
            color: Color hex code
            icon: Icon emoji
            created_by: Creator user UUID

        Returns:
            Created role
        """
        query = """
            INSERT INTO core.roles (
                role_name,
                display_name,
                description,
                hierarchy_level,
                color,
                icon,
                is_builtin,
                is_administrator,
                created_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s, FALSE, FALSE, %s
            )
            RETURNING *
        """
        return insert_returning(
            query,
            (role_name, display_name, description, hierarchy_level, color, icon, created_by)
        )

    @classmethod
    def update_role(
        cls,
        role_id: int,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        hierarchy_level: Optional[int] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update a custom role

        Args:
            role_id: Role ID
            display_name: New display name
            description: New description
            hierarchy_level: New hierarchy level
            color: New color
            icon: New icon

        Returns:
            Updated role or None
        """
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
            return cls.find_by_id(role_id)

        updates.append("updated_at = NOW()")

        params.append(role_id)

        query = f"""
            UPDATE core.roles
            SET {', '.join(updates)}
            WHERE role_id = %s AND is_builtin = FALSE
            RETURNING *
        """

        return update_returning(query, tuple(params))

    @classmethod
    def delete_role(cls, role_id: int) -> bool:
        """
        Delete a custom role (only if is_builtin = FALSE)

        Args:
            role_id: Role ID

        Returns:
            True if deleted, False otherwise
        """
        query = """
            DELETE FROM core.roles
            WHERE role_id = %s AND is_builtin = FALSE
            RETURNING role_id
        """
        result = delete_returning(query, (role_id,))
        return result is not None

    @classmethod
    def assign_features(
        cls,
        role_id: int,
        feature_ids: List[int],
        created_by: str,  # UUID
        replace: bool = False
    ) -> int:
        """
        Assign features to a role

        Args:
            role_id: Role ID
            feature_ids: List of feature IDs to assign
            created_by: User UUID who is assigning
            replace: If True, remove existing assignments first

        Returns:
            Number of features assigned
        """
        if replace:
            # Remove existing assignments
            delete_query = """
                DELETE FROM core.role_feature_assignments
                WHERE role_id = %s
            """
            execute_query(delete_query, (role_id,))

        if not feature_ids:
            return 0

        # Insert new assignments
        values = []
        params = []
        for feature_id in feature_ids:
            values.append("(%s, %s, TRUE, %s)")
            params.extend([role_id, feature_id, created_by])

        insert_query = f"""
            INSERT INTO core.role_feature_assignments (
                role_id, feature_id, enabled, created_by
            ) VALUES {', '.join(values)}
            ON CONFLICT (role_id, feature_id)
            DO UPDATE SET enabled = TRUE
        """

        execute_query(insert_query, tuple(params))
        return len(feature_ids)

    @classmethod
    def assign_permissions(
        cls,
        role_id: int,
        permission_ids: List[int],
        replace: bool = False
    ) -> int:
        """
        Assign permissions to a role

        Args:
            role_id: Role ID
            permission_ids: List of permission IDs to assign
            replace: If True, remove existing assignments first

        Returns:
            Number of permissions assigned
        """
        if replace:
            # Remove existing assignments
            delete_query = """
                DELETE FROM core.role_permissions
                WHERE role_id = %s
            """
            execute_query(delete_query, (role_id,))

        if not permission_ids:
            return 0

        # Insert new assignments
        values = []
        params = []
        for permission_id in permission_ids:
            values.append("(%s, %s)")
            params.extend([role_id, permission_id])

        insert_query = f"""
            INSERT INTO core.role_permissions (role_id, permission_id)
            VALUES {', '.join(values)}
            ON CONFLICT (role_id, permission_id) DO NOTHING
        """

        execute_query(insert_query, tuple(params))
        return len(permission_ids)

    @classmethod
    def get_user_count_by_role(cls, role_id: int) -> int:
        """
        Get number of users with this role

        Args:
            role_id: Role ID

        Returns:
            User count
        """
        query = """
            SELECT COUNT(*) as count
            FROM core.users
            WHERE role_id = %s
        """
        result = fetch_one(query, (role_id,))
        return result['count'] if result else 0

    @classmethod
    def reassign_users(
        cls,
        from_role_id: int,
        to_role_id: int
    ) -> int:
        """
        Reassign users from one role to another

        Args:
            from_role_id: Source role ID
            to_role_id: Target role ID

        Returns:
            Number of users reassigned
        """
        query = """
            UPDATE core.users
            SET role_id = %s, updated_at = NOW()
            WHERE role_id = %s
        """
        result = execute_query(query, (to_role_id, from_role_id))
        return result if isinstance(result, int) else 0

    @classmethod
    def get_all_available_permissions(cls) -> List[Dict]:
        """
        Get all available permissions that can be assigned to roles.

        Returns permissions from security.permissions table or hardcoded list.

        Returns:
            List of permission dictionaries with keys: permission_key, description, category
        """
        # For now, return permissions from Permissions class
        # In the future, this could be a database table
        from app.infrastructure.security.permissions import Permissions

        permissions = []

        # Get all permission constants from Permissions class
        for attr_name in dir(Permissions):
            if not attr_name.startswith('_') and attr_name.isupper():
                permission_value = getattr(Permissions, attr_name)
                permissions.append({
                    'permission_key': permission_value,
                    'description': f'Permission: {attr_name.replace("_", " ").title()}',
                    'category': permission_value.split(':')[0] if ':' in permission_value else 'general'
                })

        return permissions

    @classmethod
    def get_all_system_features(cls) -> List[Dict]:
        """
        Get all system features from support_systems.system_features table.

        Returns all 25 System-Features that can be assigned to roles.

        Returns:
            List of feature dictionaries
        """
        query = """
            SELECT
                feature_code,
                feature_name,
                description,
                category,
                icon,
                requires_infrastructure,
                requires_external_service
            FROM support_systems.system_features
            WHERE active = true
            ORDER BY category, feature_name
        """
        return fetch_all(query)
