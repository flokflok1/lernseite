"""Repository for AI task-specific model defaults."""
import logging
from typing import Optional, Dict, List

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)

logger = logging.getLogger(__name__)


class AITaskDefaultsRepository:
    """CRUD for ai_pipeline.ai_task_defaults."""

    @classmethod
    def get_for_task(cls, category: str) -> Optional[Dict]:
        """Get the configured model for a task category.

        Falls back to 'default' category if specific not found.
        """
        row = fetch_one(
            "SELECT d.category, d.model_name, p.name as provider_name "
            "FROM ai_pipeline.ai_task_defaults d "
            "JOIN ai_pipeline.ai_providers p ON p.provider_id = d.provider_id "
            "WHERE d.category = %s",
            (category,),
        )
        if row:
            return row
        # Fallback to default
        if category != 'default':
            return cls.get_for_task('default')
        return None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Get all task default configurations."""
        return fetch_all(
            "SELECT d.category, d.model_name, d.display_name, "
            "d.description, p.name as provider_name "
            "FROM ai_pipeline.ai_task_defaults d "
            "JOIN ai_pipeline.ai_providers p ON p.provider_id = d.provider_id "
            "ORDER BY d.category"
        )

    @classmethod
    def set_for_task(
        cls, category: str, provider_name: str, model_name: str,
    ) -> None:
        """Set or update the model for a task category."""
        execute_query(
            "UPDATE ai_pipeline.ai_task_defaults "
            "SET model_name = %s, "
            "    provider_id = (SELECT provider_id FROM ai_pipeline.ai_providers WHERE name = %s), "
            "    updated_at = NOW() "
            "WHERE category = %s",
            (model_name, provider_name, category),
        )
