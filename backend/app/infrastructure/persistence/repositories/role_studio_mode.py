"""
RoleStudioMode Repository

Handles database operations for role-studio-mode mappings.
Provides methods to retrieve and manage dynamic role configurations.

ISO 9001:2015 compliant - Standardized data access
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    delete_returning,
    execute_query
)


class RoleStudioModeRepository:
    """
    Repository for role-studio-mode mappings

    Handles all database operations for dynamic role-to-studio-mode configurations.
    Provides methods to retrieve, create, update, and delete role studio modes.
    """

    table_name = 'core.role_studio_modes'
    pk_column = 'role_code'

    @classmethod
    def find_by_code(cls, role_code: str) -> Optional[Dict]:
        """
        Find role studio mode by role code

        Args:
            role_code: The role code (e.g., 'admin', 'teacher', 'user')

        Returns:
            Role studio mode configuration as dictionary or None if not found

        Example:
            >>> admin_config = RoleStudioModeRepository.find_by_code('admin')
            >>> print(admin_config['studio_mode'])  # Output: 'admin'
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE role_code = %s
        """
        return fetch_one(query, (role_code,))

    @classmethod
    def find_by_studio_mode(
        cls,
        studio_mode: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict]:
        """
        Find all roles assigned to a specific studio mode

        Args:
            studio_mode: The studio mode (e.g., 'admin', 'moderator', 'user')
            limit: Maximum number of results
            offset: Number of records to skip

        Returns:
            List of role studio mode configurations

        Example:
            >>> admin_roles = RoleStudioModeRepository.find_by_studio_mode('admin')
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE studio_mode = %s
            ORDER BY created_at DESC
        """

        params = [studio_mode]

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return fetch_all(query, tuple(params))

    @classmethod
    def find_all_active(
        cls,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict]:
        """
        Find all active role studio modes

        Args:
            limit: Maximum number of results
            offset: Number of records to skip

        Returns:
            List of active role studio mode configurations

        Example:
            >>> active_modes = RoleStudioModeRepository.find_all_active()
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE is_active = TRUE
            ORDER BY created_at DESC
        """

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return fetch_all(query)

    @classmethod
    def find_all(
        cls,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> List[Dict]:
        """
        Find all role studio modes

        Args:
            limit: Maximum number of results
            offset: Number of records to skip
            order_by: Column to order by (default: 'created_at DESC')

        Returns:
            List of all role studio mode configurations
        """
        query = f"""
            SELECT * FROM {cls.table_name}
        """

        if order_by is None:
            order_by = 'created_at DESC'

        query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return fetch_all(query)

    @classmethod
    def find_by_filters(
        cls,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict]:
        """
        Find role studio modes by multiple filters

        Args:
            filters: Dictionary of field=value filters
                     Example: {'requires_organization': True, 'is_active': True}
            limit: Maximum number of results
            offset: Number of records to skip

        Returns:
            List of role studio mode configurations matching filters

        Example:
            >>> org_roles = RoleStudioModeRepository.find_by_filters(
            ...     {'requires_organization': True, 'is_active': True}
            ... )
        """
        if not filters:
            return cls.find_all(limit=limit, offset=offset)

        where_clauses = []
        params = []

        for field, value in filters.items():
            where_clauses.append(f"{field} = %s")
            params.append(value)

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE {where_sql}
            ORDER BY created_at DESC
        """

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return fetch_all(query, tuple(params))

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create new role studio mode

        Args:
            data: Dictionary with role configuration data
                  Required: role_code, display_name, studio_mode
                  Optional: requires_organization, permissions, is_active, description

        Returns:
            Created role studio mode configuration or None if failed

        Example:
            >>> new_role = RoleStudioModeRepository.create({
            ...     'role_code': 'content_creator',
            ...     'display_name': 'Content Creator',
            ...     'studio_mode': 'teacher',
            ...     'permissions': '{"can_create_course": true, "can_publish": false}'
            ... })
        """
        # Ensure required fields
        required_fields = ['role_code', 'display_name', 'studio_mode']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Set defaults
        if 'is_active' not in data:
            data['is_active'] = True
        if 'requires_organization' not in data:
            data['requires_organization'] = False
        if 'permissions' not in data:
            data['permissions'] = '{}'

        # Handle permissions as JSON if it's a dict
        if isinstance(data.get('permissions'), dict):
            import json
            data['permissions'] = json.dumps(data['permissions'])

        fields = list(data.keys())
        values = list(data.values())
        placeholders = ["%s"] * len(fields)

        fields_sql = ", ".join(fields)
        placeholders_sql = ", ".join(placeholders)

        query = f"""
            INSERT INTO {cls.table_name} ({fields_sql})
            VALUES ({placeholders_sql})
            RETURNING *
        """

        return insert_returning(query, tuple(values))

    @classmethod
    def update(cls, role_code: str, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update role studio mode configuration

        Args:
            role_code: The role code to update
            data: Dictionary of fields to update

        Returns:
            Updated role studio mode configuration or None if not found

        Example:
            >>> updated = RoleStudioModeRepository.update('teacher', {
            ...     'display_name': 'Instructor',
            ...     'is_active': False
            ... })
        """
        if not data:
            return cls.find_by_code(role_code)

        # Add updated_at timestamp
        data['updated_at'] = datetime.utcnow()

        # Handle permissions as JSON if it's a dict
        if isinstance(data.get('permissions'), dict):
            import json
            data['permissions'] = json.dumps(data['permissions'])

        set_clauses = []
        params = []

        for field, value in data.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        set_sql = ", ".join(set_clauses)
        params.append(role_code)

        query = f"""
            UPDATE {cls.table_name}
            SET {set_sql}
            WHERE role_code = %s
            RETURNING *
        """

        return update_returning(query, tuple(params))

    @classmethod
    def delete(cls, role_code: str) -> bool:
        """
        Delete role studio mode configuration

        Args:
            role_code: The role code to delete

        Returns:
            True if deleted successfully, False if not found

        Example:
            >>> deleted = RoleStudioModeRepository.delete('custom_role')
        """
        query = f"""
            DELETE FROM {cls.table_name}
            WHERE role_code = %s
        """

        result = delete_returning(query, (role_code,))
        return result is not None

    @classmethod
    def count(cls, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count role studio modes

        Args:
            filters: Optional filters to apply

        Returns:
            Number of matching role studio modes
        """
        query = f"SELECT COUNT(*) FROM {cls.table_name}"

        if filters:
            where_clauses = []
            params = []

            for field, value in filters.items():
                where_clauses.append(f"{field} = %s")
                params.append(value)

            where_sql = " AND ".join(where_clauses)
            query += f" WHERE {where_sql}"

            result = fetch_one(query, tuple(params))
        else:
            result = fetch_one(query)

        return result[0] if result else 0

    @classmethod
    def get_history(cls, role_code: str, limit: int = 50) -> List[Dict]:
        """
        Get change history for a role studio mode

        Args:
            role_code: The role code
            limit: Maximum number of history records

        Returns:
            List of history records showing changes
        """
        query = """
            SELECT * FROM core.role_studio_modes_history
            WHERE role_code = %s
            ORDER BY changed_at DESC
            LIMIT %s
        """

        return fetch_all(query, (role_code, limit))

    @classmethod
    def audit_log(
        cls,
        role_code: str,
        changes: Dict[str, Any],
        changed_by: str,
        change_reason: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Log a change to the audit history table

        Args:
            role_code: The role code that was changed
            changes: Dictionary of fields changed (format: {old_value, new_value})
            changed_by: User ID who made the change
            change_reason: Reason for the change (for compliance)

        Returns:
            The created history record or None if failed
        """
        # Extract old and new values from changes
        previous_display_name = changes.get('previous_display_name')
        new_display_name = changes.get('new_display_name')
        previous_studio_mode = changes.get('previous_studio_mode')
        new_studio_mode = changes.get('new_studio_mode')
        previous_permissions = changes.get('previous_permissions')
        new_permissions = changes.get('new_permissions')

        query = """
            INSERT INTO core.role_studio_modes_history
            (role_code, previous_display_name, new_display_name,
             previous_studio_mode, new_studio_mode,
             previous_permissions, new_permissions,
             changed_by, change_reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """

        params = (
            role_code,
            previous_display_name,
            new_display_name,
            previous_studio_mode,
            new_studio_mode,
            previous_permissions,
            new_permissions,
            changed_by,
            change_reason
        )

        return insert_returning(query, params)
