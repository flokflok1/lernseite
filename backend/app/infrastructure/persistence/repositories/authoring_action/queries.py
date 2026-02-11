"""
LernsystemX - Authoring Action Query Operations

Database queries for finding and retrieving authoring actions
with various filters and sorting options.
"""

from typing import Optional, List, Dict, Any
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all

logger = logging.getLogger(__name__)


# Standard SELECT clause to avoid duplication
SELECT_FIELDS = """
    action_id, action_key, category, label, description, icon, color,
    prompt_template, mode, context_entity, requires_context,
    action_type, requires_confirmation, confirmation_label,
    output_format, output_entity, lm_types,
    is_premium, order_index, is_system
"""


class AuthoringActionQueries(BaseRepository):
    """
    Query operations for authoring actions.

    Provides read-only access to actions with various filters
    (by key, ID, category, entity type, learning method type).
    """

    table_name = 'learning_methods.authoring_actions'
    pk_column = 'action_id'

    @staticmethod
    def find_by_key(action_key: str) -> Optional[Dict[str, Any]]:
        """
        Find an action by its unique key.

        Args:
            action_key: Unique action identifier (e.g., 'structure_suggest')

        Returns:
            Action dict or None if not found
        """
        query = f"""
            SELECT {SELECT_FIELDS}
            FROM learning_methods.authoring_actions
            WHERE action_key = %s AND is_active = true
        """
        return fetch_one(query, (action_key,))

    @staticmethod
    def find_by_id(action_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an action by its UUID.

        Args:
            action_id: Action UUID

        Returns:
            Action dict or None if not found
        """
        query = f"""
            SELECT {SELECT_FIELDS}
            FROM learning_methods.authoring_actions
            WHERE action_id = %s
        """
        return fetch_one(query, (action_id,))

    @staticmethod
    def get_by_category(category: str, roles: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active actions for a specific category.

        Optionally filters by user roles.

        Args:
            category: Action category ('course_builder', 'chat', 'chapter', 'lesson', 'method', 'content')
            roles: Optional list of user roles to filter by (checks roles_allowed)

        Returns:
            List of actions for this category, ordered by order_index
        """
        if roles:
            # Filter by roles if provided
            query = f"""
                SELECT {SELECT_FIELDS}
                FROM learning_methods.authoring_actions
                WHERE category = %s
                  AND is_active = true
                  AND (roles_allowed IS NULL OR roles_allowed && %s)
                ORDER BY order_index, label
            """
            return fetch_all(query, (category, roles))
        else:
            query = f"""
                SELECT {SELECT_FIELDS}
                FROM learning_methods.authoring_actions
                WHERE category = %s AND is_active = true
                ORDER BY order_index, label
            """
            return fetch_all(query, (category,))

    @staticmethod
    def get_all_active(roles: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active actions, grouped by category.

        Optionally filters by user roles.

        Args:
            roles: Optional list of user roles to filter by

        Returns:
            List of all active actions, ordered by category and order_index
        """
        if roles:
            query = f"""
                SELECT {SELECT_FIELDS}
                FROM learning_methods.authoring_actions
                WHERE is_active = true
                  AND (roles_allowed IS NULL OR roles_allowed && %s)
                ORDER BY category, order_index, label
            """
            return fetch_all(query, (roles,))
        else:
            query = f"""
                SELECT {SELECT_FIELDS}
                FROM learning_methods.authoring_actions
                WHERE is_active = true
                ORDER BY category, order_index, label
            """
            return fetch_all(query)

    @staticmethod
    def get_by_context_entity(entity: str) -> List[Dict[str, Any]]:
        """
        Get actions that apply to a specific entity type.

        Args:
            entity: Entity type ('course', 'chapter', 'lesson', 'method')

        Returns:
            List of active actions for this entity, ordered by order_index
        """
        query = f"""
            SELECT {SELECT_FIELDS}
            FROM learning_methods.authoring_actions
            WHERE context_entity = %s AND is_active = true
            ORDER BY order_index, label
        """
        return fetch_all(query, (entity,))

    @staticmethod
    def get_by_lm_type(lm_type: int) -> List[Dict[str, Any]]:
        """
        Get actions that apply to a specific learning method type.

        Applies to actions where lm_types is NULL (all methods) or
        contains the given lm_type.

        Args:
            lm_type: Learning method type (0-11 for content methods)

        Returns:
            List of active actions for this LM type, ordered by order_index
        """
        query = f"""
            SELECT {SELECT_FIELDS}
            FROM learning_methods.authoring_actions
            WHERE (lm_types IS NULL OR %s = ANY(lm_types))
              AND is_active = true
            ORDER BY order_index, label
        """
        return fetch_all(query, (lm_type,))

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """
        Get list of all categories with action counts.

        Returns:
            List of dicts with keys:
                - category: Category name
                - action_count: Total count of active actions
                - system_count: Count of system actions
        """
        query = """
            SELECT
                category,
                COUNT(*) as action_count,
                COUNT(CASE WHEN is_system THEN 1 END) as system_count
            FROM learning_methods.authoring_actions
            WHERE is_active = true
            GROUP BY category
            ORDER BY category
        """
        return fetch_all(query)
