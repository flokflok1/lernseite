"""
LernsystemX - Authoring Action Reordering

Database operations for managing display order of authoring actions.
"""

from typing import List, Dict, Any
import logging

from app.repositories.base_repository import BaseRepository
from app.database.connection import execute_query

logger = logging.getLogger(__name__)


class AuthoringActionReorder(BaseRepository):
    """
    Reordering operations for authoring actions.

    Handles bulk updates to action display order within a category.
    """

    table_name = 'learning_methods.authoring_actions'
    pk_column = 'action_id'

    @staticmethod
    def reorder(category: str, order_updates: List[Dict[str, Any]]) -> bool:
        """
        Update order_index for multiple actions within a category.

        Useful for reordering actions after user drag-and-drop operations.

        Args:
            category: Category to reorder
            order_updates: List of dicts with keys:
                - action_id: Action UUID
                - order_index: New order position (0-based)

        Returns:
            True if all updates succeeded
        """
        for update in order_updates:
            query = """
                UPDATE learning_methods.authoring_actions
                SET order_index = %s, updated_at = NOW()
                WHERE action_id = %s AND category = %s
            """
            execute_query(query, (update['order_index'], update['action_id'], category))

        return True
