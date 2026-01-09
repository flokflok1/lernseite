"""
User Authentication Operations

Handles user authentication, password hashing/verification, and email verification.
ISO 27001 compliant - Secure user data handling
"""

from typing import Optional, Dict
from datetime import datetime
import bcrypt
import logging

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, execute_query

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
            >>> user = UserAuthRepository.create_user(
            ...     email='user@example.com',
            ...     password='SecurePass123!',
            ...     first_name='John',
            ...     last_name='Doe',
            ...     role='premium'
            ... )
        """
        # Check if email already exists
        existing_user = fetch_one("SELECT user_id FROM core.users WHERE email = %s", (email,))
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Get role_id from role name
        role_data = fetch_one("SELECT role_id FROM core.roles WHERE role_name = %s", (role,))
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
            >>> user = UserAuthRepository.authenticate(
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
            FROM core.users u
            JOIN core.roles r ON u.role_id = r.role_id
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
            "UPDATE core.users SET last_login = %s WHERE user_id = %s",
            (datetime.utcnow(), user['user_id'])
        )

        # Remove password_hash from return value
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
