"""
AI Models Default Management Repository

Handles default model selection and active status management:
- Get default model for category
- Set default model
- Set model active status
- Clear previous defaults

Phase KI-Architektur - Model Management
"""

from typing import Optional, Dict, Any
from app.database.connection import fetch_one, execute_query


class AIModelsDefaultRepository:
    """
    Repository for AI Models default model operations

    Handles:
    - Default model selection by category
    - Setting models as default
    - Managing active/inactive status
    """

    table_name = 'ai_pipeline.ai_models'

    @classmethod
    def get_default_model(cls, category: str = 'chat') -> Optional[Dict[str, Any]]:
        """
        Get default model for a category

        Args:
            category: Model category (default: 'chat')

        Returns:
            Default model dict or None
        """
        query = """
            SELECT
                m.model_id,
                m.provider_id,
                p.name as provider_name,
                m.model_name,
                m.display_name,
                m.category,
                m.input_price_per_1k,
                m.output_price_per_1k,
                m.context_window,
                m.max_output_tokens
            FROM ai_pipeline.ai_models m
            LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
            WHERE m.category = %s AND m.is_default = TRUE AND m.active = TRUE
            LIMIT 1
        """
        return fetch_one(query, (category,))

    @classmethod
    def set_default(
        cls,
        model_id: int,
        category: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Set model as default for its category

        Automatically clears other defaults in the same category.

        Args:
            model_id: Model ID to set as default
            category: Optional category override

        Returns:
            Updated model dict or None
        """
        # Import here to avoid circular dependency
        from .query import AIModelsQueryRepository

        # Get the model to find its category
        model = AIModelsQueryRepository.get_by_id(model_id)
        if not model:
            return None

        cat = category or model.get('category', 'chat')

        # Unset other defaults in same category
        execute_query("""
            UPDATE ai_pipeline.ai_models SET is_default = FALSE
            WHERE category = %s AND is_default = TRUE
        """, (cat,))

        # Set this model as default
        query = """
            UPDATE ai_pipeline.ai_models
            SET is_default = TRUE, updated_at = NOW()
            WHERE model_id = %s
            RETURNING *
        """
        return fetch_one(query, (model_id,))

    @classmethod
    def set_active(cls, model_id: int, active: bool) -> Optional[Dict[str, Any]]:
        """
        Set model active status

        Args:
            model_id: Model ID
            active: Active status (True/False)

        Returns:
            Updated model dict or None
        """
        query = """
            UPDATE ai_pipeline.ai_models
            SET active = %s, updated_at = NOW()
            WHERE model_id = %s
            RETURNING model_id, model_name, active
        """
        return fetch_one(query, (active, model_id))
