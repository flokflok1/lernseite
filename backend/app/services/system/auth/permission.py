"""
Permission Service - Dynamic Hierarchy-Based Access Control

RBAC 2.0: Flexible permission system with database-configurable thresholds.
Replaces hardcoded role checks with dynamic hierarchy level checks.

Admin panel can adjust thresholds in real-time without code changes.
"""

from typing import Optional
import logging

from app.database.connection import fetch_one
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class PermissionService:
    """
    Dynamic permission checking service using hierarchy levels.

    Permissions are configured in core.permission_thresholds table and
    cached in Redis for performance.

    Example:
        >>> user = {'hierarchy_level': 8, 'role': 'admin'}
        >>> PermissionService.check_threshold(user, 'courses.edit_any')
        True
        >>> PermissionService.check_threshold(user, 'system.configure')
        False  # Requires hierarchy_level >= 9
    """

    # Cache TTL in seconds (5 minutes)
    CACHE_TTL = 300

    # Default fallback if permission not found in database
    DEFAULT_THRESHOLD = 8  # admin+

    @classmethod
    def check_threshold(cls, user: dict, permission_key: str) -> bool:
        """
        Check if user's hierarchy level meets the threshold for a permission.

        Args:
            user: User dictionary with 'hierarchy_level' field
            permission_key: Permission key (e.g., 'courses.edit_any', 'simulations.view_any')

        Returns:
            True if user has sufficient hierarchy level, False otherwise

        Example:
            >>> user = get_current_user()
            >>> if PermissionService.check_threshold(user, 'courses.edit_any'):
            ...     # User can edit any course
            ...     pass
        """
        hierarchy_level = user.get('hierarchy_level', 0)

        # Get required threshold (cached)
        required_level = cls._get_threshold(permission_key)

        # Check if user meets threshold
        has_permission = hierarchy_level >= required_level

        if not has_permission:
            logger.debug(
                f"Permission denied: user hierarchy {hierarchy_level} < "
                f"required {required_level} for {permission_key}"
            )

        return has_permission

    @classmethod
    def _get_threshold(cls, permission_key: str) -> int:
        """
        Get minimum hierarchy level required for permission.

        Checks cache first, then database. Falls back to DEFAULT_THRESHOLD
        if permission not found.

        Args:
            permission_key: Permission key to lookup

        Returns:
            Minimum hierarchy level required (1-10)
        """
        # Try cache first
        cache_key = CacheService.make_key('PERMISSION_THRESHOLD', permission_key)

        try:
            cached_threshold = CacheService.cache_get(cache_key)
            if cached_threshold is not None:
                return int(cached_threshold)
        except Exception as e:
            logger.warning(f"Cache read error for {permission_key}: {e}")

        # Cache miss - query database
        try:
            result = fetch_one(
                """
                SELECT min_hierarchy_level
                FROM core.permission_thresholds
                WHERE permission_key = %s AND is_active = true
                """,
                (permission_key,)
            )

            if result:
                threshold = result['min_hierarchy_level']

                # Cache the result
                try:
                    CacheService.cache_set(cache_key, threshold, ttl=cls.CACHE_TTL)
                except Exception as e:
                    logger.warning(f"Cache write error for {permission_key}: {e}")

                return threshold
            else:
                # Permission not found - use default and log warning
                logger.warning(
                    f"Permission threshold '{permission_key}' not found in database. "
                    f"Using default threshold {cls.DEFAULT_THRESHOLD}"
                )

                # Cache the default to avoid repeated DB queries
                try:
                    CacheService.cache_set(cache_key, cls.DEFAULT_THRESHOLD, ttl=60)
                except Exception:
                    pass

                return cls.DEFAULT_THRESHOLD

        except Exception as e:
            logger.error(f"Database error fetching threshold for {permission_key}: {e}")
            return cls.DEFAULT_THRESHOLD

    @classmethod
    def invalidate_threshold_cache(cls, permission_key: Optional[str] = None):
        """
        Invalidate permission threshold cache.

        Call this after updating thresholds in admin panel.

        Args:
            permission_key: Specific permission to invalidate, or None for all

        Example:
            >>> # After updating threshold in admin panel:
            >>> PermissionService.invalidate_threshold_cache('courses.edit_any')
        """
        if permission_key:
            cache_key = CacheService.make_key('PERMISSION_THRESHOLD', permission_key)
            CacheService.cache_delete(cache_key)
            logger.info(f"Invalidated cache for permission: {permission_key}")
        else:
            # Invalidate all permission thresholds
            # Note: This is expensive - prefer specific invalidation
            CacheService.cache_delete_pattern('PERMISSION_THRESHOLD:*')
            logger.info("Invalidated all permission threshold caches")

    @classmethod
    def get_all_thresholds(cls) -> list:
        """
        Get all permission thresholds from database.

        Used by admin panel to display current configuration.

        Returns:
            List of threshold dictionaries with keys:
            - threshold_id
            - permission_key
            - min_hierarchy_level
            - description
            - is_active
        """
        from app.database.connection import fetch_all

        results = fetch_all(
            """
            SELECT
                threshold_id,
                permission_key,
                min_hierarchy_level,
                description,
                is_active,
                created_at,
                updated_at
            FROM core.permission_thresholds
            ORDER BY permission_key
            """
        )

        return results or []

    @classmethod
    def update_threshold(cls, permission_key: str, new_level: int, user_id: Optional[str] = None) -> bool:
        """
        Update permission threshold (admin only).

        Args:
            permission_key: Permission to update
            new_level: New minimum hierarchy level (1-10)
            user_id: User making the change (for audit log)

        Returns:
            True if updated successfully, False otherwise

        Raises:
            ValueError: If new_level not in range 1-10
        """
        if not (1 <= new_level <= 10):
            raise ValueError(f"Hierarchy level must be between 1 and 10, got {new_level}")

        from app.database.connection import execute_query

        try:
            # Update threshold
            execute_query(
                """
                UPDATE core.permission_thresholds
                SET min_hierarchy_level = %s,
                    updated_at = NOW()
                WHERE permission_key = %s
                """,
                (new_level, permission_key)
            )

            # Invalidate cache
            cls.invalidate_threshold_cache(permission_key)

            logger.info(
                f"Updated permission threshold: {permission_key} -> {new_level} "
                f"(by user {user_id or 'system'})"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to update threshold {permission_key}: {e}")
            return False


# Convenience functions for common permission checks
def can_view_any_resource(user: dict) -> bool:
    """Check if user can view any resource regardless of ownership."""
    return PermissionService.check_threshold(user, 'view_any_resource')


def can_edit_any_resource(user: dict) -> bool:
    """Check if user can edit any resource regardless of ownership."""
    return PermissionService.check_threshold(user, 'edit_any_resource')


def can_delete_any_resource(user: dict) -> bool:
    """Check if user can delete any resource regardless of ownership."""
    return PermissionService.check_threshold(user, 'delete_any_resource')


def can_manage_any_organisation(user: dict) -> bool:
    """Check if user can manage any organisation."""
    return PermissionService.check_threshold(user, 'organisations.manage_any')


def can_view_all_analytics(user: dict) -> bool:
    """Check if user can view all analytics data."""
    return PermissionService.check_threshold(user, 'analytics.view_all')
