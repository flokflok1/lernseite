"""
User Admin Operations

Handles core admin operations: user listing, details, and group management.
Moderation operations (ban, unban, delete, verify) are in admin_part2.py.
"""

from typing import Optional, Dict, List
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query

logger = logging.getLogger(__name__)


class UserAdminRepository(BaseRepository):
    """Admin user management operations"""

    table_name = 'core.users'
    pk_column = 'user_id'

    @classmethod
    def admin_list_users(
        cls,
        page: int = 1,
        per_page: int = 50,
        group_slug: Optional[str] = None,
        search: Optional[str] = None,
        status: str = 'active',
        sort: str = 'created_at',
        order: str = 'desc'
    ) -> Dict:
        """
        List all users with pagination and filters (Admin only)

        Args:
            page: Page number (1-indexed)
            per_page: Items per page (max 100)
            group_slug: Filter by group slug (e.g., 'system-admin', 'premium-members')
            search: Search by email or name
            status: Filter by status (active, suspended, banned)
            sort: Sort field (created_at, last_login, email)
            order: Sort order (asc, desc)

        Returns:
            Dict with 'users' list and 'pagination' metadata

        Note:
            PHASE B: Replaced role parameter with group_slug.
            Users are now filtered by group membership, not single role.

        Example:
            >>> result = UserAdminRepository.admin_list_users(
            ...     page=1, per_page=50, group_slug='premium-members', search='john'
            ... )
            >>> print(result['pagination']['total'])
        """
        # Build WHERE clause
        where_conditions = []
        params = []

        if status:
            where_conditions.append("u.status = %s")
            params.append(status)

        if search:
            where_conditions.append(
                "(u.email ILIKE %s OR u.firstname ILIKE %s OR u.lastname ILIKE %s)"
            )
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Build table joins based on filters
        if group_slug:
            from_clause = """
                core.users u
                JOIN core.users_groups ug ON u.user_id = ug.user_id
                JOIN core.groups g ON ug.group_id = g.group_id
            """
            group_filter = " AND g.slug = %s"
            params.insert(0 if not where_conditions else len(params) - len([p for p in params if isinstance(p, str) and '%' in p]), group_slug)
            where_clause = where_clause + group_filter
        else:
            from_clause = "core.users u"

        # Count total
        count_query = f"""
            SELECT COUNT(DISTINCT u.user_id) as total
            FROM {from_clause}
            WHERE {where_clause}
        """
        total_result = fetch_one(count_query, tuple(params))
        total = total_result['total'] if total_result else 0

        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page
        offset = (page - 1) * per_page

        # Get users
        valid_sort_fields = {
            'created_at': 'u.created_at',
            'last_login': 'u.last_login',
            'email': 'u.email'
        }
        sort_field = valid_sort_fields.get(sort, 'u.created_at')
        sort_order = 'ASC' if order.lower() == 'asc' else 'DESC'

        users_query = f"""
            SELECT DISTINCT
                u.user_id,
                u.email,
                u.firstname,
                u.lastname,
                u.is_owner,
                u.status,
                u.created_at,
                u.last_login,
                u.email_verified
            FROM {from_clause}
            WHERE {where_clause}
            ORDER BY {sort_field} {sort_order}
            LIMIT %s OFFSET %s
        """

        users = fetch_all(users_query, tuple(params + [per_page, offset]))

        # Convert UUIDs to strings and status to is_active boolean
        for user in users:
            if 'user_id' in user and user['user_id']:
                user['user_id'] = str(user['user_id'])
            # Convert status string to is_active boolean
            if 'status' in user:
                user['is_active'] = user['status'] == 'active'

        return {
            'users': users,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        }

    @classmethod
    def admin_get_user_details(cls, user_id: str) -> Optional[Dict]:
        """
        Get comprehensive user details for admin view

        Args:
            user_id: User ID (UUID)

        Returns:
            Detailed user data including subscription, tokens, courses, login history,
            and group memberships

        Note:
            PHASE B: Removed role field. User authorization now determined by group membership.

        Example:
            >>> details = UserAdminRepository.admin_get_user_details('uuid')
            >>> print(details['subscription']['plan'])
            >>> print(details['groups'])  # List of group memberships
        """
        # Get base user info
        user = fetch_one(
            """
            SELECT
                u.user_id,
                u.email,
                u.firstname,
                u.lastname,
                u.is_owner,
                u.status,
                u.created_at,
                u.updated_at,
                u.last_login,
                u.last_login_ip,
                u.email_verified,
                u.two_factor_enabled
            FROM core.users u
            WHERE u.user_id = %s
            """,
            (user_id,)
        )

        if not user:
            return None

        # Convert UUID to string
        user['user_id'] = str(user['user_id'])

        # Convert status string to is_active boolean
        if 'status' in user:
            user['is_active'] = user['status'] == 'active'

        # Get subscription info
        subscription = fetch_one(
            """
            SELECT
                sp.plan_type as plan,
                s.status,
                s.current_period_end as expires_at,
                s.cancel_at_period_end as auto_renew
            FROM billing_storage.subscriptions s
            JOIN billing_storage.subscription_plans sp ON s.plan_id = sp.plan_id
            WHERE s.user_id = %s AND s.status = 'active'
            ORDER BY s.created_at DESC
            LIMIT 1
            """,
            (user_id,)
        )
        user['subscription'] = subscription

        # Get token info - TEMPORARILY DISABLED due to unknown schema
        user['tokens'] = None

        # Get course counts
        courses_created = fetch_one(
            "SELECT COUNT(*) as count FROM courses.courses WHERE creator_user_id = %s",
            (user_id,)
        )
        user['courses_created'] = courses_created['count'] if courses_created else 0

        courses_enrolled = fetch_one(
            "SELECT COUNT(*) as count FROM courses.course_enrollments WHERE user_id = %s",
            (user_id,)
        )
        user['courses_enrolled'] = courses_enrolled['count'] if courses_enrolled else 0

        # Get recent login history
        login_history = fetch_all(
            """
            SELECT
                created_at as login_time,
                ip_address,
                user_agent
            FROM core.audit_logs
            WHERE user_id = %s AND action = 'auth.login'
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (user_id,)
        )
        # Convert PostgreSQL types to JSON-serializable
        for log in (login_history or []):
            if 'ip_address' in log and log['ip_address']:
                log['ip_address'] = str(log['ip_address'])
            if 'login_time' in log and log['login_time']:
                log['login_time'] = log['login_time'].isoformat()
        user['login_history'] = login_history or []

        # Get ban history
        ban_history = fetch_all(
            """
            SELECT
                created_at,
                description as reason,
                metadata
            FROM core.audit_logs
            WHERE user_id = %s AND action IN ('admin.users.ban', 'admin.users.unban')
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (user_id,)
        )
        # Convert timestamps to ISO format
        for log in (ban_history or []):
            if 'created_at' in log and log['created_at']:
                log['created_at'] = log['created_at'].isoformat()
        user['ban_history'] = ban_history or []

        return user

    @classmethod
    def admin_update_groups(
        cls,
        user_id: str,
        group_slugs: List[str],
        changed_by: str,
        replace: bool = False
    ) -> bool:
        """
        Update user's group memberships (Admin only)

        Args:
            user_id: User ID to modify
            group_slugs: List of group slugs (e.g., ['system-admin', 'premium-members'])
            changed_by: Admin user ID performing the change
            replace: If True, replace all groups; if False, add to existing groups

        Returns:
            bool: True if groups updated successfully

        Note:
            PHASE B: Replaces admin_change_role() which used deleted core.roles table.
            Users can now be members of multiple groups for fine-grained access control.

        Example:
            >>> UserAdminRepository.admin_update_groups(
            ...     'user-uuid',
            ...     ['system-admin', 'content-creators'],
            ...     'admin-uuid',
            ...     replace=True
            ... )
        """
        if not group_slugs:
            return False

        # Get group IDs for slugs
        group_data = fetch_all(
            """
            SELECT group_id, slug FROM core.groups
            WHERE slug = ANY(%s)
            """,
            (group_slugs,)
        )

        if not group_data:
            return False

        group_ids = [g['group_id'] for g in group_data]

        # Replace existing groups if requested
        if replace:
            execute_query(
                "DELETE FROM core.users_groups WHERE user_id = %s",
                (user_id,)
            )

        # Add user to groups
        for group_id in group_ids:
            execute_query(
                """
                INSERT INTO core.users_groups (user_id, group_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, group_id) DO NOTHING
                """,
                (user_id, group_id)
            )

        # Update user's updated_at timestamp
        execute_query(
            "UPDATE core.users SET updated_at = NOW() WHERE user_id = %s",
            (user_id,)
        )

        return True

