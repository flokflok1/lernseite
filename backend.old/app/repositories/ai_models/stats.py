"""
AI Models Statistics Repository

Handles statistical queries and aggregation:
- Count models with filters
- Get comprehensive statistics
- Aggregate model information

Phase KI-Architektur - Model Management
"""

from typing import Optional, Dict, Any
from app.database.connection import fetch_one


class AIModelsStatsRepository:
    """
    Repository for AI Models statistics and aggregation

    Handles:
    - Model counting with filters
    - Statistics aggregation
    - Summary information
    """

    table_name = 'ai_pipeline.ai_models'

    @classmethod
    def count(
        cls,
        provider_id: int = None,
        category: str = None,
        active_only: bool = True
    ) -> int:
        """
        Count models with optional filtering

        Args:
            provider_id: Filter by provider ID (optional)
            category: Filter by category (optional)
            active_only: Only count active models (default: True)

        Returns:
            Count of models matching filters
        """
        query = "SELECT COUNT(*) as count FROM ai_pipeline.ai_models WHERE 1=1"
        params = []

        if active_only:
            query += " AND active = TRUE"

        if provider_id:
            query += " AND provider_id = %s"
            params.append(provider_id)

        if category:
            query += " AND category = %s"
            params.append(category)

        result = fetch_one(query, tuple(params) if params else None)
        return result.get('count', 0) if result else 0

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        Get comprehensive model statistics

        Returns statistics including:
        - total_models: Total count of all models
        - active_models: Count of active models
        - providers: Count of distinct providers
        - categories: Count of distinct categories
        - default_models: Count of models marked as default

        Returns:
            Stats dictionary
        """
        query = """
            SELECT
                COUNT(*) as total_models,
                COUNT(*) FILTER (WHERE active = TRUE) as active_models,
                COUNT(DISTINCT provider_id) as providers,
                COUNT(DISTINCT category) as categories,
                COUNT(*) FILTER (WHERE is_default = TRUE) as default_models
            FROM ai_models
        """
        return fetch_one(query) or {}
