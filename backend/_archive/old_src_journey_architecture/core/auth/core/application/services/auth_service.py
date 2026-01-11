"""Auth Service (DDD Application Layer)

Business logic for authentication and authorization.
Publishes domain events via EventBus.
"""

from typing import Optional, Tuple
from datetime import datetime, timedelta
import uuid
import logging

from src.core.events.event_bus import EventBus, DomainEvent, EventType
from src.api.auth.core.domain.entities.user import User
from src.api.auth.core.domain.entities.user_session import UserSession
from src.api.auth.core.infrastructure.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service.
    
    Handles user registration, login, logout, and session management.
    Publishes domain events for all state changes.
    """
    
    # ====================================================================
    # USER REGISTRATION
    # ====================================================================
    
    @staticmethod
    def register_user(
        email: str,
        password: str,
        firstname: str,
        lastname: str,
        role_id: int,
        organization_id: Optional[str] = None
    ) -> User:
        """
        Register a new user.
        
        Args:
            email: User email
            password: Plain text password
            firstname: User first name
            lastname: User last name
            role_id: Role ID
            organization_id: Organization ID (optional)
            
        Returns:
            Created User entity
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing_user = AuthRepository.find_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Hash password
        password_hash = AuthRepository.hash_password(password)
        
        # Create user
        user = AuthRepository.create_user(
            email=email,
            password_hash=password_hash,
            firstname=firstname,
            lastname=lastname,
            role_id=role_id,
            organization_id=organization_id
        )
        
        # Publish domain event
        event = DomainEvent(
            event_type=EventType.USER_REGISTERED,
            aggregate_id=user.user_id,
            occurred_at=datetime.utcnow(),
            data={
                'email': user.email,
                'role_id': user.role_id,
                'organization_id': user.organization_id if hasattr(user, 'organization_id') else None
            }
        )
        EventBus.publish(event)
        
        logger.info(f"User registered: {user.user_id} ({user.email})")
        
        return user
    
    # ====================================================================
    # USER AUTHENTICATION
    # ====================================================================
    
    @staticmethod
    def authenticate(
        email: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[User]:
        """
        Authenticate user by email and password.
        
        Args:
            email: User email
            password: Plain text password
            ip_address: Client IP address
            
        Returns:
            User entity if authentication successful, None otherwise
        """
        # Find user by email
        user = AuthRepository.find_user_by_email(email)
        if not user:
            logger.warning(f"Authentication failed: user not found ({email})")
            return None
        
        # Verify password
        if not AuthRepository.verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password ({email})")
            return None
        
        # Check if user is active
        if not user.is_active():
            logger.warning(f"Authentication failed: user not active ({email}, status={user.status})")
            return None
        
        # Update last login
        if ip_address:
            AuthRepository.update_last_login(user.user_id, ip_address)
            user.update_last_login(ip_address)
        
        # Publish domain event
        event = DomainEvent(
            event_type=EventType.USER_LOGGED_IN,
            aggregate_id=user.user_id,
            occurred_at=datetime.utcnow(),
            data={
                'email': user.email,
                'ip_address': ip_address
            }
        )
        EventBus.publish(event)
        
        logger.info(f"User authenticated: {user.user_id} ({user.email})")
        
        return user
    
    # ====================================================================
    # SESSION MANAGEMENT
    # ====================================================================
    
    @staticmethod
    def create_session(
        user_id: str,
        jti: str,
        refresh_token_hash: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        device_info: Optional[dict],
        expires_in_days: int = 7
    ) -> UserSession:
        """
        Create a new user session.
        
        Args:
            user_id: User UUID
            jti: JWT ID
            refresh_token_hash: Hashed refresh token
            ip_address: Client IP address
            user_agent: Browser user agent
            device_info: Device information
            expires_in_days: Session expiration in days (default: 7)
            
        Returns:
            UserSession entity
        """
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        session = AuthRepository.create_session(
            user_id=user_id,
            jti=jti,
            refresh_token_hash=refresh_token_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            expires_at=expires_at
        )
        
        # Publish domain event
        event = DomainEvent(
            event_type=EventType.SESSION_CREATED,
            aggregate_id=session.session_id,
            occurred_at=datetime.utcnow(),
            data={
                'user_id': user_id,
                'jti': jti,
                'expires_at': expires_at.isoformat()
            }
        )
        EventBus.publish(event)
        
        logger.info(f"Session created: {session.session_id} for user {user_id}")
        
        return session
    
    @staticmethod
    def validate_session(jti: str) -> Optional[UserSession]:
        """
        Validate a session.
        
        Args:
            jti: JWT ID
            
        Returns:
            UserSession if valid, None otherwise
        """
        session = AuthRepository.find_session_by_jti(jti)
        
        if not session:
            return None
        
        if not session.is_valid():
            return None
        
        return session
    
    @staticmethod
    def logout(jti: str, user_id: str) -> None:
        """
        Logout user (revoke session).
        
        Args:
            jti: JWT ID
            user_id: User UUID
        """
        AuthRepository.revoke_session(jti)
        
        # Publish domain event
        event = DomainEvent(
            event_type=EventType.USER_LOGGED_OUT,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow(),
            data={'jti': jti}
        )
        EventBus.publish(event)
        
        logger.info(f"User logged out: {user_id} (jti={jti})")
    
    @staticmethod
    def logout_all_sessions(user_id: str) -> None:
        """
        Logout user from all sessions.
        
        Args:
            user_id: User UUID
        """
        AuthRepository.revoke_all_user_sessions(user_id)
        
        # Publish domain event
        event = DomainEvent(
            event_type=EventType.ALL_SESSIONS_REVOKED,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow()
        )
        EventBus.publish(event)
        
        logger.info(f"All sessions revoked for user: {user_id}")
    
    # ====================================================================
    # EMAIL VERIFICATION
    # ====================================================================
    
    @staticmethod
    def verify_email(user_id: str) -> None:
        """
        Verify user email.
        
        Args:
            user_id: User UUID
        """
        AuthRepository.verify_email(user_id)
        
        # Publish domain event
        event = DomainEvent(
            event_type=EventType.EMAIL_VERIFIED,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow()
        )
        EventBus.publish(event)
        
        logger.info(f"Email verified for user: {user_id}")
    
    # ====================================================================
    # PASSWORD OPERATIONS
    # ====================================================================
    
    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str) -> None:
        """
        Change user password.
        
        Args:
            user_id: User UUID
            old_password: Current password
            new_password: New password
            
        Raises:
            ValueError: If old password is incorrect
        """
        # Get user
        user = AuthRepository.find_user_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        # Verify old password
        if not AuthRepository.verify_password(old_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = AuthRepository.hash_password(new_password)
        
        # Update password
        AuthRepository.update_password(user_id, new_password_hash)
        
        # Revoke all sessions (force re-login)
        AuthRepository.revoke_all_user_sessions(user_id)
        
        # Publish domain event
        event = DomainEvent(
            event_type=EventType.PASSWORD_CHANGED,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow()
        )
        EventBus.publish(event)
        
        logger.info(f"Password changed for user: {user_id}")
    
    @staticmethod
    def reset_password(user_id: str, new_password: str) -> None:
        """
        Reset user password (admin/forgot password flow).
        
        Args:
            user_id: User UUID
            new_password: New password
        """
        # Hash new password
        new_password_hash = AuthRepository.hash_password(new_password)
        
        # Update password
        AuthRepository.update_password(user_id, new_password_hash)
        
        # Revoke all sessions
        AuthRepository.revoke_all_user_sessions(user_id)
        
        # Publish domain event
        event = DomainEvent(
            event_type=EventType.PASSWORD_RESET,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow()
        )
        EventBus.publish(event)
        
        logger.info(f"Password reset for user: {user_id}")
