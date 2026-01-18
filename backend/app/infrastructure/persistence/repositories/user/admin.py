"""
User Admin Operations

Handles admin-only operations: user listing, details, role changes, bans, deletion, creator verification.
"""

from typing import Optional, Dict
from datetime import datetime
import logging

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
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
        role: Optional[str] = None,
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
            role: Filter by role name
            search: Search by email or name
            status: Filter by status (active, suspended, banned)
            sort: Sort field (created_at, last_login, email)
            order: Sort order (asc, desc)

        Returns:
            Dict with 'users' list and 'pagination' metadata

        Example:
            >>> result = UserAdminRepository.admin_list_users(
            ...     page=1, per_page=50, role='premium', search='john'
            ... )
            >>> print(result['pagination']['total'])
        """
        # Build WHERE clause
        where_conditions = []
        params = []

        if status:
            where_conditions.append("u.status = %s")
            params.append(status)

        if role:
            where_conditions.append("r.role_name = %s")
            params.append(role)

        if search:
            where_conditions.append(
                "(u.email ILIKE %s OR u.firstname ILIKE %s OR u.lastname ILIKE %s)"
            )
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Count total
        count_query = f"""
            SELECT COUNT(*) as total
            FROM core.users u
            JOIN core.roles r ON u.role_id = r.role_id
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
            SELECT
                u.user_id,
                u.email,
                u.firstname,
                u.lastname,
                r.role_name as role,
                u.status,
                u.created_at,
                u.last_login,
                u.email_verified
            FROM core.users u
            JOIN core.roles r ON u.role_id = r.role_id
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
            Detailed user data including subscription, tokens, courses, login history

        Example:
            >>> details = UserAdminRepository.admin_get_user_details('uuid')
            >>> print(details['subscription']['plan'])
        """
        # Get base user info
        user = fetch_one(
            """
            SELECT
                u.user_id,
                u.email,
                u.firstname,
                u.lastname,
                r.role_name as role,
                u.status,
                u.created_at,
                u.updated_at,
                u.last_login,
                u.last_login_ip,
                u.email_verified,
                u.two_factor_enabled
            FROM core.users u
            JOIN core.roles r ON u.role_id = r.role_id
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
    def admin_change_role(
        cls,
        user_id: str,
        new_role: str,
        changed_by: str
    ) -> bool:
        """
        Change user role (Admin only)

        Args:
            user_id: User ID to modify
            new_role: New role name
            changed_by: Admin user ID performing the change

        Returns:
            bool: True if role changed successfully

        Example:
            >>> UserAdminRepository.admin_change_role(
            ...     'user-uuid', 'premium', 'admin-uuid'
            ... )
        """
        # Get role_id
        role_data = fetch_one("SELECT role_id FROM core.roles WHERE role_name = %s", (new_role,))
        if not role_data:
            return False

        # Update user role
        result = execute_query(
            """
            UPDATE core.users
            SET role_id = %s, updated_at = NOW()
            WHERE user_id = %s
            """,
            (role_data['role_id'], user_id),
            fetch_one=True
        )

        return result is not None

    @classmethod
    def admin_ban_user(
        cls,
        user_id: str,
        reason: str,
        banned_until: Optional[datetime],
        banned_by: str
    ) -> bool:
        """
        Ban a user (Admin only)

        Args:
            user_id: User ID to ban
            reason: Reason for ban
            banned_until: Ban expiry (None for permanent)
            banned_by: Admin user ID performing the ban

        Returns:
            bool: True if user banned successfully

        Example:
            >>> UserAdminRepository.admin_ban_user(
            ...     'user-uuid',
            ...     'Violation of terms',
            ...     datetime(2025, 12, 31),
            ...     'admin-uuid'
            ... )
        """
        result = execute_query(
            """
            UPDATE core.users
            SET
                status = 'banned',
                banned_until = %s,
                updated_at = NOW()
            WHERE user_id = %s
            """,
            (banned_until, user_id),
            fetch_one=True
        )

        return result is not None

    @classmethod
    def admin_unban_user(cls, user_id: str, unbanned_by: str) -> bool:
        """
        Unban a user (Admin only)

        Args:
            user_id: User ID to unban
            unbanned_by: Admin user ID performing the unban

        Returns:
            bool: True if user unbanned successfully

        Example:
            >>> UserAdminRepository.admin_unban_user('user-uuid', 'admin-uuid')
        """
        result = execute_query(
            """
            UPDATE core.users
            SET
                status = 'active',
                banned_until = NULL,
                updated_at = NOW()
            WHERE user_id = %s
            """,
            (user_id,),
            fetch_one=True
        )

        return result is not None

    @classmethod
    def admin_delete_user(
        cls,
        user_id: str,
        reason: str,
        deleted_by: str,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a user (Admin only)

        Args:
            user_id: User ID to delete
            reason: Reason for deletion
            deleted_by: Admin user ID performing the deletion
            hard_delete: If True, permanently delete; if False, soft delete

        Returns:
            bool: True if user deleted successfully

        Example:
            >>> UserAdminRepository.admin_delete_user(
            ...     'user-uuid', 'GDPR request', 'admin-uuid', hard_delete=False
            ... )
        """
        if hard_delete:
            # Hard delete - permanently remove user
            result = execute_query(
                "DELETE FROM core.users WHERE user_id = %s",
                (user_id,),
                fetch_one=False
            )
        else:
            # Soft delete - set status to deleted
            result = execute_query(
                """
                UPDATE core.users
                SET
                    status = 'deleted',
                    deleted_at = NOW(),
                    updated_at = NOW()
                WHERE user_id = %s
                """,
                (user_id,),
                fetch_one=True
            )

        return result is not None

    @classmethod
    def admin_verify_creator(
        cls,
        user_id: str,
        verified: bool,
        verified_by: str
    ) -> bool:
        """
        Verify a creator (Admin only)

        Args:
            user_id: Creator user ID
            verified: Verification status
            verified_by: Admin user ID performing the verification

        Returns:
            bool: True if creator verified successfully

        Example:
            >>> UserAdminRepository.admin_verify_creator('user-uuid', True, 'admin-uuid')
        """
        result = execute_query(
            """
            UPDATE core.users
            SET
                creator_verified = %s,
                creator_verified_at = CASE WHEN %s THEN NOW() ELSE NULL END,
                updated_at = NOW()
            WHERE user_id = %s
            """,
            (verified, verified, user_id),
            fetch_one=True
        )

        return result is not None
