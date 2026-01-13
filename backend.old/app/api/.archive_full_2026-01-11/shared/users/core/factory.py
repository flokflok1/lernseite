"""
LernsystemX Users Domain - Factory

Domain-Driven Design (DDD) Factory Pattern for User aggregate creation.
Encapsulates complex user creation logic and ensures invariants.

Per DDD: Factories handle complex object creation and ensure domain rules.

ISO 27001:2013 A.9 - Access control implementation
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash

from .value_objects import UserRole, AccountStatus, UserId, Email, OrganisationId


class UserFactory:
    """
    Factory for creating User aggregates.

    Responsibilities:
    - Create users with proper defaults
    - Ensure password hashing
    - Generate unique identifiers
    - Apply business rules for user creation
    """

    @staticmethod
    def create_user(
        email: Email,
        password: str,
        first_name: str,
        last_name: str,
        role: UserRole | str = UserRole.FREE,
        organization_id: OrganisationId = None,
        email_verified: bool = False,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new user with all required fields.

        Args:
            email: User email (unique)
            password: Plain text password (will be hashed)
            first_name: First name
            last_name: Last name
            role: User role (defaults to FREE)
            organization_id: Optional organisation ID
            email_verified: Email verification status
            is_active: Active status

        Returns:
            Dict with user data ready for database insertion

        Raises:
            ValueError: If validation fails
        """
        # Validate email
        if not email or '@' not in email:
            raise ValueError("Invalid email address")

        # Validate password
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Validate names
        if not first_name or not last_name:
            raise ValueError("First name and last name are required")

        # Ensure role is enum
        role_enum = UserRole(role) if isinstance(role, str) else role

        # Generate user ID
        user_id = str(uuid.uuid4())

        # Hash password
        password_hash = generate_password_hash(password)

        # Determine initial status
        status = AccountStatus.ACTIVE if email_verified and is_active else AccountStatus.PENDING

        return {
            'user_id': user_id,
            'email': email.lower().strip(),
            'password_hash': password_hash,
            'first_name': first_name.strip(),
            'last_name': last_name.strip(),
            'role': role_enum.value,
            'organization_id': organization_id,
            'email_verified': email_verified,
            'is_active': is_active,
            'status': status.value,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }

    @staticmethod
    def create_with_role(
        email: Email,
        role: UserRole | str,
        first_name: str = "User",
        last_name: str = "Account",
        organization_id: OrganisationId = None,
        auto_verify: bool = False
    ) -> Dict[str, Any]:
        """
        Create user with specific role and sensible defaults.

        Useful for admin-initiated user creation or imports.

        Args:
            email: User email
            role: User role
            first_name: Optional first name
            last_name: Optional last name
            organization_id: Optional organisation
            auto_verify: Whether to auto-verify email

        Returns:
            Dict with user data
        """
        # Generate temporary password (must be changed on first login)
        temp_password = f"Temp{uuid.uuid4().hex[:12]}!"

        return UserFactory.create_user(
            email=email,
            password=temp_password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            organization_id=organization_id,
            email_verified=auto_verify,
            is_active=True
        )

    @staticmethod
    def create_system_user(email: Email, role: UserRole | str) -> Dict[str, Any]:
        """
        Create a system user (for background tasks, integrations).

        Args:
            email: System email
            role: System role

        Returns:
            Dict with user data
        """
        return UserFactory.create_with_role(
            email=email,
            role=role,
            first_name="System",
            last_name="Account",
            auto_verify=True
        )

    @staticmethod
    def activate_user(user_id: UserId, activated_by: UserId) -> Dict[str, Any]:
        """
        Create activation command data.

        Args:
            user_id: User to activate
            activated_by: Admin performing activation

        Returns:
            Activation data
        """
        return {
            'user_id': user_id,
            'is_active': True,
            'status': AccountStatus.ACTIVE.value,
            'activated_at': datetime.utcnow(),
            'activated_by': activated_by,
        }

    @staticmethod
    def deactivate_user(
        user_id: UserId,
        deactivated_by: UserId,
        reason: str = "Deactivated by admin"
    ) -> Dict[str, Any]:
        """
        Create deactivation command data.

        Args:
            user_id: User to deactivate
            deactivated_by: Admin performing deactivation
            reason: Reason for deactivation

        Returns:
            Deactivation data
        """
        return {
            'user_id': user_id,
            'is_active': False,
            'status': AccountStatus.INACTIVE.value,
            'deactivated_at': datetime.utcnow(),
            'deactivated_by': deactivated_by,
            'deactivation_reason': reason,
        }

    @staticmethod
    def ban_user(
        user_id: UserId,
        banned_by: UserId,
        reason: str,
        banned_until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create ban command data.

        Args:
            user_id: User to ban
            banned_by: Admin performing ban
            reason: Reason for ban
            banned_until: Optional expiry date (None = permanent)

        Returns:
            Ban data
        """
        return {
            'user_id': user_id,
            'is_active': False,
            'status': AccountStatus.BANNED.value,
            'banned_at': datetime.utcnow(),
            'banned_by': banned_by,
            'ban_reason': reason,
            'banned_until': banned_until,
        }

    @staticmethod
    def unban_user(user_id: UserId, unbanned_by: UserId) -> Dict[str, Any]:
        """
        Create unban command data.

        Args:
            user_id: User to unban
            unbanned_by: Admin performing unban

        Returns:
            Unban data
        """
        return {
            'user_id': user_id,
            'is_active': True,
            'status': AccountStatus.ACTIVE.value,
            'unbanned_at': datetime.utcnow(),
            'unbanned_by': unbanned_by,
            'banned_until': None,
        }


__all__ = ['UserFactory']
