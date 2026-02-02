"""
LernsystemX - Authoring Action Repository Package

Provides database access for authoring actions (Quick-Actions) used in KI-Studio.

The package is split into logical modules for maintainability:
- crud.py: Create, update, delete, duplicate operations
- queries.py: Find and retrieve operations with various filters
- analytics.py: Usage tracking and analytics
- reorder.py: Display order management

For backward compatibility, all methods are re-exported through the main
AuthoringActionRepository class.
"""

from typing import Optional, List, Dict, Any

# Import all sub-module classes
from app.infrastructure.persistence.repositories.authoring_action.crud import AuthoringActionCRUD
from app.infrastructure.persistence.repositories.authoring_action.queries import AuthoringActionQueries
from app.infrastructure.persistence.repositories.authoring_action.analytics import AuthoringActionAnalytics
from app.infrastructure.persistence.repositories.authoring_action.reorder import AuthoringActionReorder


class AuthoringActionRepository:
    """
    Unified interface for all authoring action repository operations.

    This class provides backward compatibility by re-exporting all methods
    from the sub-modules (CRUD, Queries, Analytics, Reorder).

    All methods are static - no instance state is maintained.

    Usage:
        from app.infrastructure.persistence.repositories.authoring_action import AuthoringActionRepository

        # CRUD operations
        action = AuthoringActionRepository.create(action_data)
        updated = AuthoringActionRepository.update(action_id, update_data)
        deleted = AuthoringActionRepository.delete(action_id)
        dup = AuthoringActionRepository.duplicate(action_id, new_key)

        # Queries
        action = AuthoringActionRepository.find_by_id(action_id)
        action = AuthoringActionRepository.find_by_key(action_key)
        actions = AuthoringActionRepository.get_by_category(category)
        actions = AuthoringActionRepository.get_all_active()

        # Analytics
        AuthoringActionRepository.log_usage(action_id, user_id, ...)
        stats = AuthoringActionRepository.get_usage_stats(action_id)
        popular = AuthoringActionRepository.get_popular_actions()

        # Reorder
        AuthoringActionRepository.reorder(category, order_updates)
    """

    # ========== CRUD Operations ==========

    @staticmethod
    def create(action_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new authoring action. See AuthoringActionCRUD.create()"""
        return AuthoringActionCRUD.create(action_data)

    @staticmethod
    def update(action_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing action. See AuthoringActionCRUD.update()"""
        return AuthoringActionCRUD.update(action_id, update_data)

    @staticmethod
    def delete(action_id: str) -> bool:
        """Delete an action (soft delete). See AuthoringActionCRUD.delete()"""
        return AuthoringActionCRUD.delete(action_id)

    @staticmethod
    def duplicate(action_id: str, new_key: str, created_by: str = None) -> Optional[Dict[str, Any]]:
        """Duplicate an action with a new key. See AuthoringActionCRUD.duplicate()"""
        return AuthoringActionCRUD.duplicate(action_id, new_key, created_by)

    # ========== Query Operations ==========

    @staticmethod
    def find_by_id(action_id: str) -> Optional[Dict[str, Any]]:
        """Find an action by UUID. See AuthoringActionQueries.find_by_id()"""
        return AuthoringActionQueries.find_by_id(action_id)

    @staticmethod
    def find_by_key(action_key: str) -> Optional[Dict[str, Any]]:
        """Find an action by key. See AuthoringActionQueries.find_by_key()"""
        return AuthoringActionQueries.find_by_key(action_key)

    @staticmethod
    def get_by_category(category: str, roles: List[str] = None) -> List[Dict[str, Any]]:
        """Get actions by category. See AuthoringActionQueries.get_by_category()"""
        return AuthoringActionQueries.get_by_category(category, roles)

    @staticmethod
    def get_all_active(roles: List[str] = None) -> List[Dict[str, Any]]:
        """Get all active actions. See AuthoringActionQueries.get_all_active()"""
        return AuthoringActionQueries.get_all_active(roles)

    @staticmethod
    def get_by_context_entity(entity: str) -> List[Dict[str, Any]]:
        """Get actions by context entity. See AuthoringActionQueries.get_by_context_entity()"""
        return AuthoringActionQueries.get_by_context_entity(entity)

    @staticmethod
    def get_by_lm_type(lm_type: int) -> List[Dict[str, Any]]:
        """Get actions by learning method type. See AuthoringActionQueries.get_by_lm_type()"""
        return AuthoringActionQueries.get_by_lm_type(lm_type)

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """Get all categories with counts. See AuthoringActionQueries.get_categories()"""
        return AuthoringActionQueries.get_categories()

    # ========== Analytics Operations ==========

    @staticmethod
    def log_usage(
        action_id: str,
        user_id: str,
        session_id: str = None,
        context_data: Dict = None,
        was_successful: bool = True,
        was_confirmed: bool = None,
        result_entity_id: str = None,
        tokens_input: int = None,
        tokens_output: int = None,
        cost_eur: float = None,
        response_time_ms: int = None
    ) -> Optional[Dict[str, Any]]:
        """Log action usage. See AuthoringActionAnalytics.log_usage()"""
        return AuthoringActionAnalytics.log_usage(
            action_id=action_id,
            user_id=user_id,
            session_id=session_id,
            context_data=context_data,
            was_successful=was_successful,
            was_confirmed=was_confirmed,
            result_entity_id=result_entity_id,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_eur=cost_eur,
            response_time_ms=response_time_ms
        )

    @staticmethod
    def get_usage_stats(action_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics. See AuthoringActionAnalytics.get_usage_stats()"""
        return AuthoringActionAnalytics.get_usage_stats(action_id, days)

    @staticmethod
    def get_popular_actions(limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        """Get popular actions by usage. See AuthoringActionAnalytics.get_popular_actions()"""
        return AuthoringActionAnalytics.get_popular_actions(limit, days)

    # ========== Reorder Operations ==========

    @staticmethod
    def reorder(category: str, order_updates: List[Dict[str, Any]]) -> bool:
        """Reorder actions in a category. See AuthoringActionReorder.reorder()"""
        return AuthoringActionReorder.reorder(category, order_updates)


__all__ = [
    'AuthoringActionRepository',
    'AuthoringActionCRUD',
    'AuthoringActionQueries',
    'AuthoringActionAnalytics',
    'AuthoringActionReorder',
]
