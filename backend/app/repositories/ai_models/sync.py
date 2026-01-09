"""
AI Models Synchronization Repository

Handles model synchronization tracking:
- Mark models as synced
- Track synchronization timestamps

Phase KI-Architektur - Model Management
"""

from app.database.connection import execute_query


class AIModelsSyncRepository:
    """
    Repository for AI Models synchronization operations

    Handles:
    - Sync status tracking
    - Timestamp management for sync operations
    """

    table_name = 'ai_pipeline.ai_models'

    @classmethod
    def mark_synced(cls, model_id: int) -> None:
        """
        Mark model as synced by updating the updated_at timestamp

        Called after successful synchronization with external AI providers.

        Args:
            model_id: Model ID to mark as synced

        Returns:
            None
        """
        execute_query("""
            UPDATE ai_pipeline.ai_models SET updated_at = NOW()
            WHERE model_id = %s
        """, (model_id,))
