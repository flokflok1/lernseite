"""User Service (DDD Application Layer)

Business logic for user management.
Auth logic is in AuthService (Auth Domain).
"""

from typing import Optional, List
from datetime import datetime
import logging

from src.core.events.event_bus import EventBus, DomainEvent, EventType
from src.api.auth.core.domain.entities.user import User
from src.api.users.core.infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """
    User management service.
    
    Handles user CRUD, search, profile management.
    Publishes domain events for all state changes.
    """
    
    # ====================================================================
    # READ OPERATIONS
    # ====================================================================
    
    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        """Get user by ID."""
        return UserRepository.find_by_id(user_id)
    
    @staticmethod
    def list_users(limit: int = 100, offset: int = 0) -> List[User]:
        """List users (paginated)."""
        return UserRepository.list_users(limit, offset)
    
    @staticmethod
    def search_users(query: str, limit: int = 50) -> List[User]:
        """Search users."""
        return UserRepository.search_users(query, limit)
    
    # ====================================================================
    # UPDATE OPERATIONS
    # ====================================================================
    
    @staticmethod
    def update_profile(
        user_id: str,
        **kwargs
    ) -> None:
        """
        Update user profile.
        
        Args:
            user_id: User UUID
            **kwargs: Profile fields to update
        """
        UserRepository.update_profile(user_id, **kwargs)
        
        # Publish event
        event = DomainEvent(
            event_type=EventType.USER_PROFILE_UPDATED,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow(),
            data=kwargs
        )
        EventBus.publish(event)
        
        logger.info(f"User profile updated: {user_id}")
    
    @staticmethod
    def deactivate_user(user_id: str) -> None:
        """Deactivate user account."""
        UserRepository.update_status(user_id, 'deactivated')
        
        event = DomainEvent(
            event_type=EventType.USER_DEACTIVATED,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow()
        )
        EventBus.publish(event)
        
        logger.info(f"User deactivated: {user_id}")
    
    @staticmethod
    def reactivate_user(user_id: str) -> None:
        """Reactivate user account."""
        UserRepository.update_status(user_id, 'active')
        
        event = DomainEvent(
            event_type=EventType.USER_REACTIVATED,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow()
        )
        EventBus.publish(event)
        
        logger.info(f"User reactivated: {user_id}")
    
    # ====================================================================
    # DELETE OPERATIONS
    # ====================================================================
    
    @staticmethod
    def delete_user(user_id: str) -> None:
        """Soft delete user."""
        UserRepository.soft_delete(user_id)
        
        event = DomainEvent(
            event_type=EventType.USER_DELETED,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow()
        )
        EventBus.publish(event)
        
        logger.info(f"User deleted: {user_id}")
    
    @staticmethod
    def restore_user(user_id: str) -> None:
        """Restore soft-deleted user."""
        UserRepository.restore_user(user_id)
        
        event = DomainEvent(
            event_type=EventType.USER_RESTORED,
            aggregate_id=user_id,
            occurred_at=datetime.utcnow()
        )
        EventBus.publish(event)
        
        logger.info(f"User restored: {user_id}")
    
    # ====================================================================
    # STATISTICS
    # ====================================================================
    
    @staticmethod
    def get_user_count() -> int:
        """Get total user count."""
        return UserRepository.count_users()
    
    @staticmethod
    def get_users_by_role(role_id: int) -> int:
        """Get user count by role."""
        return UserRepository.count_by_role(role_id)
