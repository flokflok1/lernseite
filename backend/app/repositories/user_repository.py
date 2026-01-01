"""
LernsystemX User Repository

Handles all user-related database operations including:
- User CRUD operations
- Authentication (login, password verification)
- Password hashing with bcrypt
- Email verification
- Role management

ISO 27001 compliant - Secure user data handling
"""

from typing import Optional, Dict, List
from datetime import datetime

import bcrypt

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all, execute_query


class UserRepository(BaseRepository):
    """
    User repository with authentication support

    Extends BaseRepository with user-specific operations.
    """

    table_name = 'users'
    pk_column = 'user_id'

    @classmethod
    def find_by_id(cls, user_id: str) -> Optional[Dict]:
        """
        Find user by ID with role name included

        Args:
            user_id: User ID (UUID)

        Returns:
            User data with role name (without password_hash) or None

        Example:
            >>> user = UserRepository.find_by_id('8828daa5-213d-46b9-981a-a1c6f3233afd')
            >>> print(user['role'])  # 'admin' (not role_id)
        """
        user = fetch_one(
            """
            SELECT u.*, r.role_name as role
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.user_id = %s
            """,
            (user_id,)
        )

        if user:
            user.pop('password_hash', None)
            # Convert UUID to string for Pydantic
            if 'user_id' in user and user['user_id']:
                user['user_id'] = str(user['user_id'])

        return user

    @classmethod
    def create_user(
        cls,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = 'free',
        organization_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Create new user with hashed password

        Args:
            email: User email (unique)
            password: Plain text password (will be hashed)
            first_name: User first name
            last_name: User last name
            role: User role name (default: 'free')
            organization_id: Organization ID (optional)

        Returns:
            Created user as dictionary (without password_hash)

        Raises:
            ValueError: If email already exists or role not found

        Example:
            >>> user = UserRepository.create_user(
            ...     email='user@example.com',
            ...     password='SecurePass123!',
            ...     first_name='John',
            ...     last_name='Doe',
            ...     role='premium'
            ... )
        """
        # Check if email already exists
        existing_user = fetch_one("SELECT user_id FROM users WHERE email = %s", (email,))
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Get role_id from role name
        role_data = fetch_one("SELECT role_id FROM roles WHERE role_name = %s", (role,))
        if not role_data:
            raise ValueError(f"Role '{role}' not found")
        role_id = role_data['role_id']

        # Hash password
        password_hash = cls._hash_password(password)

        # Create user with correct column names
        user = execute_query(
            """
            INSERT INTO users (email, password_hash, firstname, lastname, role_id, status, email_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (email, password_hash, first_name, last_name, role_id, 'active', False),
            fetch_one=True
        )

        # Remove password_hash from return value
        if user and 'password_hash' in user:
            user.pop('password_hash')

        return user

    @classmethod
    def authenticate(cls, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with email and password

        Args:
            email: User email
            password: Plain text password

        Returns:
            User data (without password_hash) if authentication successful,
            None otherwise

        Example:
            >>> user = UserRepository.authenticate(
            ...     'user@example.com',
            ...     'SecurePass123!'
            ... )
            >>> if user:
            ...     print(f"Welcome {user['firstname']}!")
            ... else:
            ...     print("Invalid credentials")
        """
        user = fetch_one(
            """
            SELECT u.*, r.role_name as role
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.email = %s
            """,
            (email,)
        )

        if not user:
            # User not found - perform dummy hash to prevent timing attacks
            bcrypt.hashpw(b'dummy', bcrypt.gensalt())
            return None

        # Check if user is active
        if user.get('status') != 'active':
            return None

        # Verify password
        if not cls._verify_password(password, user['password_hash']):
            return None

        # Update last login
        execute_query(
            "UPDATE users SET last_login = %s WHERE user_id = %s",
            (datetime.utcnow(), user['user_id'])
        )

        # Remove password_hash from return value
        user.pop('password_hash', None)

        return user

    @classmethod
    def find_by_email(cls, email: str) -> Optional[Dict]:
        """
        Find user by email

        Args:
            email: User email

        Returns:
            User data (without password_hash) or None

        Example:
            >>> user = UserRepository.find_by_email('user@example.com')
        """
        user = fetch_one("SELECT * FROM users WHERE email = %s", (email,))

        if user:
            user.pop('password_hash', None)

        return user

    @classmethod
    def update_password(cls, user_id: int, new_password: str) -> bool:
        """
        Update user password

        Args:
            user_id: User ID
            new_password: New plain text password (will be hashed)

        Returns:
            bool: True if password updated successfully

        Example:
            >>> success = UserRepository.update_password(123, 'NewSecurePass456!')
        """
        password_hash = cls._hash_password(new_password)

        result = cls.update(user_id, {'password_hash': password_hash})

        return result is not None

    @classmethod
    def verify_email(cls, user_id: int) -> bool:
        """
        Mark user email as verified

        Args:
            user_id: User ID

        Returns:
            bool: True if email verified successfully

        Example:
            >>> UserRepository.verify_email(123)
        """
        result = cls.update(user_id, {'email_verified': True})
        return result is not None

    @classmethod
    def deactivate_user(cls, user_id: int) -> bool:
        """
        Deactivate user account

        Args:
            user_id: User ID

        Returns:
            bool: True if user deactivated successfully

        Example:
            >>> UserRepository.deactivate_user(123)
        """
        execute_query(
            "UPDATE users SET status = %s WHERE user_id = %s",
            ('inactive', user_id)
        )
        return True

    @classmethod
    def activate_user(cls, user_id: int) -> bool:
        """
        Activate user account

        Args:
            user_id: User ID

        Returns:
            bool: True if user activated successfully

        Example:
            >>> UserRepository.activate_user(123)
        """
        execute_query(
            "UPDATE users SET status = %s WHERE user_id = %s",
            ('active', user_id)
        )
        return True

    @classmethod
    def find_by_role(cls, role: str, active_only: bool = True) -> List[Dict]:
        """
        Find all users with specific role

        Args:
            role: User role name
            active_only: Only return active users (default: True)

        Returns:
            List of users

        Example:
            >>> admins = UserRepository.find_by_role('admin')
            >>> premium_users = UserRepository.find_by_role('premium', active_only=False)
        """
        # Get role_id from role name
        role_data = fetch_one("SELECT role_id FROM roles WHERE role_name = %s", (role,))
        if not role_data:
            return []

        if active_only:
            users = fetch_all(
                "SELECT * FROM users WHERE role_id = %s AND status = %s",
                (role_data['role_id'], 'active')
            )
        else:
            users = fetch_all(
                "SELECT * FROM users WHERE role_id = %s",
                (role_data['role_id'],)
            )

        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)

        return users

    @classmethod
    def find_by_organisation(cls, organisation_id: int, active_only: bool = True) -> List[Dict]:
        """
        Find all users in an organisation

        Args:
            organisation_id: Organisation ID
            active_only: Only return active users (default: True)

        Returns:
            List of users

        Example:
            >>> org_users = UserRepository.find_by_organisation(5)
        """
        # Note: users table does NOT have organization_id column
        # This requires querying via organisation_members table
        if active_only:
            users = fetch_all(
                """
                SELECT u.* FROM users u
                JOIN organisation_members om ON u.user_id = om.user_id
                WHERE om.organisation_id = %s AND u.status = %s
                """,
                (organisation_id, 'active')
            )
        else:
            users = fetch_all(
                """
                SELECT u.* FROM users u
                JOIN organisation_members om ON u.user_id = om.user_id
                WHERE om.organisation_id = %s
                """,
                (organisation_id,)
            )

        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)

        return users

    @classmethod
    def search_users(
        cls,
        query: str,
        limit: int = 10,
        role: Optional[str] = None
    ) -> List[Dict]:
        """
        Search users by email, first name, or last name

        Args:
            query: Search query
            limit: Maximum number of results
            role: Filter by role name (optional)

        Returns:
            List of matching users

        Example:
            >>> users = UserRepository.search_users('john', limit=5)
            >>> admins = UserRepository.search_users('john', role='admin')
        """
        search_pattern = f"%{query}%"

        sql = """
            SELECT * FROM users
            WHERE (
                email ILIKE %s
                OR firstname ILIKE %s
                OR lastname ILIKE %s
            )
            AND status = 'active'
        """
        params = [search_pattern, search_pattern, search_pattern]

        if role:
            # Get role_id from role name
            role_data = fetch_one("SELECT role_id FROM roles WHERE role_name = %s", (role,))
            if role_data:
                sql += " AND role_id = %s"
                params.append(role_data['role_id'])

        sql += f" LIMIT {limit}"

        users = fetch_all(sql, tuple(params))

        # Remove password_hash from all users
        for user in users:
            user.pop('password_hash', None)

        return users

    @classmethod
    def get_user_stats(cls) -> Dict:
        """
        Get user statistics

        Returns:
            Dictionary with user counts by role and status

        Example:
            >>> stats = UserRepository.get_user_stats()
            >>> print(f"Total users: {stats['total']}")
            >>> print(f"Premium users: {stats['by_role']['premium']}")
        """
        # Total users
        total_result = fetch_one("SELECT COUNT(*) as count FROM users")
        total = total_result['count'] if total_result else 0

        # Active users
        active_result = fetch_one("SELECT COUNT(*) as count FROM users WHERE status = 'active'")
        active = active_result['count'] if active_result else 0

        # Users by role (with role names)
        by_role_query = """
            SELECT r.role_name, COUNT(u.user_id) as count
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.status = 'active'
            GROUP BY r.role_name
        """
        by_role = fetch_all(by_role_query)
        by_role_dict = {row['role_name']: row['count'] for row in by_role}

        # Email verified
        verified_result = fetch_one(
            "SELECT COUNT(*) as count FROM users WHERE email_verified = true AND status = 'active'"
        )
        verified = verified_result['count'] if verified_result else 0

        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'verified': verified,
            'by_role': by_role_dict
        }

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password

        Example (internal use only):
            >>> hashed = UserRepository._hash_password('SecurePass123!')
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)  # Cost factor 12
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash

        Args:
            password: Plain text password
            password_hash: Hashed password from database

        Returns:
            bool: True if password matches, False otherwise

        Example (internal use only):
            >>> is_valid = UserRepository._verify_password('password', hashed)
        """
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False

    # ============================================================================
    # ADMIN METHODS (Phase B24 - Admin System)
    # ============================================================================

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
            >>> result = UserRepository.admin_list_users(
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
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
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
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
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
            >>> details = UserRepository.admin_get_user_details('uuid')
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
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
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
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.plan_id
            WHERE s.user_id = %s AND s.status = 'active'
            ORDER BY s.created_at DESC
            LIMIT 1
            """,
            (user_id,)
        )
        user['subscription'] = subscription

        # Get token info - TEMPORARILY DISABLED due to unknown schema
        # token_info = fetch_one(
        #     """
        #     SELECT
        #         (total_tokens - used_tokens) as balance,
        #         total_tokens as total_granted,
        #         0 as total_purchased,
        #         used_tokens as total_used
        #     FROM token_wallets
        #     WHERE user_id = %s
        #     """,
        #     (user_id,)
        # )
        user['tokens'] = None  # Temporarily disabled

        # Get course counts
        courses_created = fetch_one(
            "SELECT COUNT(*) as count FROM courses WHERE creator_user_id = %s",
            (user_id,)
        )
        user['courses_created'] = courses_created['count'] if courses_created else 0

        courses_enrolled = fetch_one(
            "SELECT COUNT(*) as count FROM course_enrollments WHERE user_id = %s",
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
            FROM audit_logs
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
            FROM audit_logs
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
            >>> UserRepository.admin_change_role(
            ...     'user-uuid', 'premium', 'admin-uuid'
            ... )
        """
        # Get role_id
        role_data = fetch_one("SELECT role_id FROM roles WHERE role_name = %s", (new_role,))
        if not role_data:
            return False

        # Update user role
        result = execute_query(
            """
            UPDATE users
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
            >>> UserRepository.admin_ban_user(
            ...     'user-uuid',
            ...     'Violation of terms',
            ...     datetime(2025, 12, 31),
            ...     'admin-uuid'
            ... )
        """
        result = execute_query(
            """
            UPDATE users
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
            >>> UserRepository.admin_unban_user('user-uuid', 'admin-uuid')
        """
        result = execute_query(
            """
            UPDATE users
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
            >>> UserRepository.admin_delete_user(
            ...     'user-uuid', 'GDPR request', 'admin-uuid', hard_delete=False
            ... )
        """
        if hard_delete:
            # Hard delete - permanently remove user
            result = execute_query(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,),
                fetch_one=False
            )
        else:
            # Soft delete - set status to deleted
            result = execute_query(
                """
                UPDATE users
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
            >>> UserRepository.admin_verify_creator('user-uuid', True, 'admin-uuid')
        """
        result = execute_query(
            """
            UPDATE users
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

    # ============================================================================
    # THEME PREFERENCE METHODS (Phase B24 - Theme Support)
    # ============================================================================

    @classmethod
    def get_theme_preference(cls, user_id: str) -> str:
        """
        Get user's theme preference

        Args:
            user_id: User ID (UUID)

        Returns:
            Theme preference ('system', 'light', or 'dark')
            Returns 'dark' as fallback if not found

        Example:
            >>> theme = UserRepository.get_theme_preference('user-uuid')
            >>> print(theme)  # 'dark'
        """
        user = fetch_one(
            "SELECT theme_preference FROM users WHERE user_id = %s",
            (user_id,)
        )

        if user and user.get('theme_preference'):
            return user['theme_preference']

        # Fallback to 'dark' if user not found or theme_preference is NULL
        return 'dark'

    @classmethod
    def update_theme_preference(cls, user_id: str, theme: str) -> str:
        """
        Update user's theme preference

        Args:
            user_id: User ID (UUID)
            theme: New theme preference ('system', 'light', or 'dark')

        Returns:
            Updated theme preference value

        Raises:
            ValueError: If theme is not one of the valid values

        Example:
            >>> new_theme = UserRepository.update_theme_preference('user-uuid', 'light')
            >>> print(new_theme)  # 'light'
        """
        # Validate theme value (defensive check, already validated by Pydantic)
        valid_themes = ['system', 'light', 'dark']
        if theme not in valid_themes:
            raise ValueError(f'Theme must be one of: {", ".join(valid_themes)}')

        # Update theme preference
        result = execute_query(
            """
            UPDATE users
            SET theme_preference = %s, updated_at = NOW()
            WHERE user_id = %s
            RETURNING theme_preference
            """,
            (theme, user_id),
            fetch_one=True
        )

        if not result:
            raise ValueError(f'User with ID {user_id} not found')

        return result['theme_preference']
