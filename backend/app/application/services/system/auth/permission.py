"""
Permission Service - Group-Based Access Control (GBA)

PHASE B: Group-Based Architecture for scalable permission management.
Users belong to Groups, Groups have Permissions.

All permission data is cached in Redis for performance.
"""

from typing import Optional, List, Set
import logging

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
from app.infrastructure.cache.service import CacheService

logger = logging.getLogger(__name__)


class PermissionService:
    """
    Group-based permission checking service using GBA (Group-Based Architecture).

    Permissions are assigned to Groups, not individual users.
    Users inherit permissions from their Groups.

    Data is cached in Redis for high performance.

    GBA Model:
        User → Groups (core.users_groups) → Permissions (core.group_permissions)

    Example:
        >>> user = {
        ...     'user_id': 'abc123',
        ...     'groups': ['system-admin', 'teachers'],
        ...     'permissions': ['courses.edit', 'users.manage', 'analytics.view']
        ... }
        >>> PermissionService.check_permission(user, 'courses.edit')
        True
        >>> PermissionService.check_permission(user, 'system.configure')
        False  # Not in user's permissions
    """

    # Cache TTL in seconds (5 minutes)
    CACHE_TTL = 300

    # Cache keys for performance
    CACHE_KEY_GROUP_PERMS = 'GROUP_PERMISSIONS'
    CACHE_KEY_PERM_GROUPS = 'PERMISSION_GROUPS'
    CACHE_KEY_USER_PERMS = 'USER_PERMISSIONS'

    @classmethod
    def check_permission(cls, user: dict, permission_code: str) -> bool:
        """
        Check if user has a specific permission via their groups.

        GBA LOGIC:
        1. If user has pre-computed 'permissions' array (from JWT), use it (fast)
        2. Otherwise, lookup from database based on groups

        Args:
            user: User dictionary with 'groups' or 'permissions' field
            permission_code: Permission code to check (e.g., 'courses.edit')

        Returns:
            True if user's groups include this permission, False otherwise

        Example:
            >>> user = get_current_user()  # From JWT token
            >>> if PermissionService.check_permission(user, 'courses.edit'):
            ...     # User can edit courses
            ...     return create_course()
        """
        if not user:
            return False

        # FAST PATH: Check pre-computed permissions (from JWT token)
        if 'permissions' in user:
            return permission_code in user.get('permissions', [])

        # LOOKUP PATH: Check permissions via groups
        user_groups = user.get('groups', [])
        if not user_groups:
            logger.debug(f"User {user.get('user_id', 'unknown')} has no groups")
            return False

        # Get all groups that have this permission (cached)
        groups_with_perm = cls._get_groups_with_permission(permission_code)

        # Check if user belongs to any group with this permission
        for group_info in groups_with_perm:
            if group_info['slug'] in user_groups:
                logger.debug(
                    f"User {user.get('user_id', 'unknown')} has permission "
                    f"'{permission_code}' via group '{group_info['slug']}'"
                )
                return True

        logger.debug(
            f"Permission denied: user groups {user_groups} do not have "
            f"permission '{permission_code}'"
        )
        return False

    @classmethod
    def get_user_permissions(cls, user_id: str) -> Set[str]:
        """
        Get all permissions for a user (via their groups).

        Used when building JWT token or for permission audits.

        Args:
            user_id: User ID

        Returns:
            Set of permission codes user has

        Example:
            >>> perms = PermissionService.get_user_permissions('user-123')
            >>> print(perms)
            {'courses.edit', 'users.manage', 'analytics.view'}
        """
        # Get user's groups
        user_groups = fetch_all(
            """
            SELECT g.slug, g.id
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.id
            WHERE ug.user_id = %s AND ug.deleted_at IS NULL
            """,
            (user_id,)
        ) or []

        if not user_groups:
            logger.debug(f"User {user_id} has no groups")
            return set()

        # Get all permissions for these groups
        group_ids = [g['id'] for g in user_groups]
        permissions = fetch_all(
            """
            SELECT DISTINCT p.code
            FROM core.group_permissions gp
            JOIN core.permissions p ON gp.permission_id = p.id
            WHERE gp.group_id = ANY(%s)
            """,
            (group_ids,)
        ) or []

        permission_codes = {p['code'] for p in permissions}
        logger.debug(f"User {user_id} has {len(permission_codes)} permissions")

        return permission_codes

    @classmethod
    def _get_groups_with_permission(cls, permission_code: str) -> List[dict]:
        """
        Get all groups that have a specific permission.

        Results are cached for performance.

        Args:
            permission_code: Permission code (e.g., 'courses.edit')

        Returns:
            List of group dicts with 'id', 'slug', 'name'
        """
        # Try cache first
        cache_key = CacheService.make_key(cls.CACHE_KEY_PERM_GROUPS, permission_code)

        try:
            cached_groups = CacheService.cache_get(cache_key)
            if cached_groups is not None:
                import json
                return json.loads(cached_groups)
        except Exception as e:
            logger.warning(f"Cache read error for permission {permission_code}: {e}")

        # Cache miss - query database
        try:
            results = fetch_all(
                """
                SELECT DISTINCT g.id, g.slug, g.name
                FROM core.group_permissions gp
                JOIN core.permissions p ON gp.permission_id = p.id
                JOIN core.groups g ON gp.group_id = g.id
                WHERE p.code = %s AND g.deleted_at IS NULL
                ORDER BY g.name
                """,
                (permission_code,)
            ) or []

            # Cache the result
            if results:
                try:
                    import json
                    CacheService.cache_set(cache_key, json.dumps(results), ttl=cls.CACHE_TTL)
                except Exception as e:
                    logger.warning(f"Cache write error for permission {permission_code}: {e}")

            return results

        except Exception as e:
            logger.error(f"Database error fetching groups with permission {permission_code}: {e}")
            return []

    @classmethod
    def get_group_permissions(cls, group_id: str) -> Set[str]:
        """
        Get all permissions for a group.

        Args:
            group_id: Group ID

        Returns:
            Set of permission codes for the group
        """
        # Try cache first
        cache_key = CacheService.make_key(cls.CACHE_KEY_GROUP_PERMS, group_id)

        try:
            cached_perms = CacheService.cache_get(cache_key)
            if cached_perms is not None:
                import json
                return set(json.loads(cached_perms))
        except Exception as e:
            logger.warning(f"Cache read error for group {group_id}: {e}")

        # Cache miss - query database
        try:
            results = fetch_all(
                """
                SELECT DISTINCT p.code
                FROM core.group_permissions gp
                JOIN core.permissions p ON gp.permission_id = p.id
                WHERE gp.group_id = %s
                """,
                (group_id,)
            ) or []

            permission_codes = {r['code'] for r in results}

            # Cache the result
            if results:
                try:
                    import json
                    CacheService.cache_set(cache_key, json.dumps(list(permission_codes)), ttl=cls.CACHE_TTL)
                except Exception as e:
                    logger.warning(f"Cache write error for group {group_id}: {e}")

            return permission_codes

        except Exception as e:
            logger.error(f"Database error fetching permissions for group {group_id}: {e}")
            return set()

    @classmethod
    def invalidate_group_cache(cls, group_id: Optional[str] = None):
        """
        Invalidate permission cache for a group.

        Call this after assigning/removing permissions from a group.

        Args:
            group_id: Specific group to invalidate, or None for all
        """
        if group_id:
            cache_key = CacheService.make_key(cls.CACHE_KEY_GROUP_PERMS, group_id)
            CacheService.cache_delete(cache_key)
            logger.info(f"Invalidated permission cache for group: {group_id}")
        else:
            # Invalidate all group permission caches
            CacheService.cache_delete_pattern(f'{cls.CACHE_KEY_GROUP_PERMS}:*')
            CacheService.cache_delete_pattern(f'{cls.CACHE_KEY_PERM_GROUPS}:*')
            logger.info("Invalidated all permission caches")

    @classmethod
    def invalidate_permission_cache(cls, permission_code: str):
        """
        Invalidate cache after permission changes.

        Args:
            permission_code: Permission code that changed
        """
        cache_key = CacheService.make_key(cls.CACHE_KEY_PERM_GROUPS, permission_code)
        CacheService.cache_delete(cache_key)
        logger.info(f"Invalidated permission cache for: {permission_code}")


# Convenience functions for common permission checks
def can_view_any_resource(user: dict) -> bool:
    """Check if user can view any resource regardless of ownership."""
    return PermissionService.check_permission(user, 'view_any_resource')


def can_edit_any_resource(user: dict) -> bool:
    """Check if user can edit any resource regardless of ownership."""
    return PermissionService.check_permission(user, 'edit_any_resource')


def can_delete_any_resource(user: dict) -> bool:
    """Check if user can delete any resource regardless of ownership."""
    return PermissionService.check_permission(user, 'delete_any_resource')


def can_manage_any_organisation(user: dict) -> bool:
    """Check if user can manage any organisation."""
    return PermissionService.check_permission(user, 'organisations.manage_any')


def can_view_all_analytics(user: dict) -> bool:
    """Check if user can view all analytics data."""
    return PermissionService.check_permission(user, 'analytics.view_all')
