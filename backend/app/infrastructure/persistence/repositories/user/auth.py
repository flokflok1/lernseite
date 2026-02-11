"""
User Authentication Operations

Handles user authentication, password hashing/verification, and email verification.
ISO 27001 compliant - Secure user data handling
"""

from typing import Optional, Dict
from datetime import datetime
import bcrypt
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, execute_query

logger = logging.getLogger(__name__)


class UserAuthRepository(BaseRepository):
    """User authentication and credential management"""

    table_name = 'core.users'
    pk_column = 'user_id'

    @classmethod
    def create_user(
        cls,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        organisation_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Create new user with hashed password

        Args:
            email: User email (unique)
            password: Plain text password (will be hashed)
            first_name: User first name
            last_name: User last name
            organisation_id: Organization ID (optional)

        Returns:
            Created user as dictionary (without password_hash)

        Raises:
            ValueError: If email already exists

        Note:
            PHASE B: Users no longer have a single role. Instead, they are assigned to groups
            via the users_groups junction table. Admin status is determined by the is_owner flag
            and membership in the system-admin group.

        Example:
            >>> user = UserAuthRepository.create_user(
            ...     email='user@example.com',
            ...     password='SecurePass123!',
            ...     first_name='John',
            ...     last_name='Doe'
            ... )
        """
        # Check if email already exists
        existing_user = fetch_one("SELECT user_id FROM core.users WHERE email = %s", (email,))
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Hash password
        password_hash = cls._hash_password(password)

        # Create user (PHASE B: no role column - users belong to groups instead)
        # Combine first_name + last_name into full_name
        full_name = f"{first_name} {last_name}".strip()

        # Generate username from email (before @) or full_name
        # Username must be 3-50 alphanumeric chars with _ and -
        import re
        base_username = email.split('@')[0].lower()
        # Remove invalid characters (keep only alphanumeric, _, -)
        username = re.sub(r'[^a-z0-9_-]', '', base_username)
        # Ensure minimum length of 3
        if len(username) < 3:
            username = f"user_{username}"
        # Ensure max length of 50
        username = username[:50]

        # Check if username exists, append number if needed
        existing_username = fetch_one("SELECT user_id FROM core.users WHERE username = %s", (username,))
        if existing_username:
            import uuid
            username = f"{username[:42]}_{str(uuid.uuid4())[:6]}"

        user = execute_query(
            """
            INSERT INTO core.users (email, username, password_hash, full_name, is_active, email_verified)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (email, username, password_hash, full_name, True, False),
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

        Note:
            PHASE B: User roles/permissions are now managed through the groups system
            (users_groups junction table). This method returns basic user data; group
            memberships should be queried separately.

        Example:
            >>> user = UserAuthRepository.authenticate(
            ...     'user@example.com',
            ...     'SecurePass123!'
            ... )
            >>> if user:
            ...     print(f"Welcome {user['firstname']}!")
            ... else:
            ...     print("Invalid credentials")
        """
        # Get user with their primary group (highest hierarchy level)
        user = fetch_one(
            """
            SELECT
                u.*,
                COALESCE(
                    (SELECT g.slug
                     FROM core.users_groups ug
                     JOIN core.groups g ON ug.group_id = g.id
                     WHERE ug.user_id = u.user_id
                       AND ug.is_active = TRUE
                       AND ug.left_at IS NULL
                     ORDER BY g.hierarchy_level DESC
                     LIMIT 1),
                    'user'
                ) AS role
            FROM core.users u
            WHERE u.email = %s
            """,
            (email,)
        )

        if not user:
            # User not found - perform dummy hash to prevent timing attacks
            bcrypt.hashpw(b'dummy', bcrypt.gensalt())
            return None

        # Check if user is active (using is_active column, not status)
        if not user.get('is_active', False):
            return None

        # Verify password
        if not cls._verify_password(password, user['password_hash']):
            return None

        # Update last login
        execute_query(
            "UPDATE core.users SET last_login_at = %s WHERE user_id = %s",
            (datetime.utcnow(), user['user_id'])
        )

        # Remove password_hash from return value
        user.pop('password_hash', None)

        # Convert UUIDs to strings for Pydantic
        if 'user_id' in user and user['user_id']:
            user['user_id'] = str(user['user_id'])
        if 'organisation_id' in user and user['organisation_id']:
            user['organisation_id'] = str(user['organisation_id'])

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
            >>> success = UserAuthRepository.update_password(123, 'NewSecurePass456!')
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
            >>> UserAuthRepository.verify_email(123)
        """
        result = cls.update(user_id, {'email_verified': True})
        return result is not None

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password

        Example (internal use only):
            >>> hashed = UserAuthRepository._hash_password('SecurePass123!')
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
            >>> is_valid = UserAuthRepository._verify_password('password', hashed)
        """
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False
