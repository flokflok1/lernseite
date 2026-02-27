"""
AI Models Query Repository

Handles specialized query operations for AI models:
- Get by ID, name, category
- Get all models with filtering
- List categories
- Provider-based queries

Phase KI-Architektur - Model Management
"""

from typing import Optional, Dict, List, Any
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class AIModelsQueryRepository:
    """
    Repository for AI Models query operations

    Handles specialized queries including:
    - Retrieval by ID, name, category
    - Filtered list operations
    - Category enumeration
    - Provider-based filtering
    """

    table_name = 'ai_pipeline.ai_models'

    # SQL fragment for standard model fields
    _BASE_FIELDS = """
        m.model_id,
        m.provider_id,
        p.name as provider_name,
        p.display_name as provider_display_name,
        m.model_name,
        m.display_name,
        m.model_type,
        m.category,
        m.description,
        m.cost_level,
        m.speed,
        m.context_window,
        m.max_output_tokens,
        m.supports_vision,
        m.supports_functions,
        m.input_price_per_1k,
        m.output_price_per_1k,
        m.active,
        m.is_default,
        m.created_at,
        m.updated_at
    """

    @classmethod
    def get_by_id(cls, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Get model by ID

        Args:
            model_id: Model ID

        Returns:
            Model dict or None
        """
        query = f"""
            SELECT {cls._BASE_FIELDS}
            FROM ai_pipeline.ai_models m
            LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
            WHERE m.model_id = %s
        """
        return fetch_one(query, (model_id,))

    @classmethod
    def get_by_name(
        cls,
        model_name: str,
        provider_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get model by name

        Args:
            model_name: Model name (e.g., 'gpt-4o', 'claude-3-5-sonnet')
            provider_name: Optional provider name filter

        Returns:
            Model dict or None
        """
        query = f"""
            SELECT {cls._BASE_FIELDS}
            FROM ai_pipeline.ai_models m
            LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
            WHERE m.model_name = %s
        """
        params = [model_name]

        if provider_name:
            query += " AND p.name = %s"
            params.append(provider_name)

        return fetch_one(query, tuple(params))

    @classmethod
    def get_by_category(
        cls,
        category: str,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get models by category

        Args:
            category: Model category (chat, reasoning, audio, image, etc.)
            active_only: Only return active models

        Returns:
            List of model dicts
        """
        query = f"""
            SELECT {cls._BASE_FIELDS}
            FROM ai_pipeline.ai_models m
            LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
            WHERE m.category = %s
        """
        params = [category]

        if active_only:
            query += " AND m.active = TRUE"

        query += " ORDER BY m.is_default DESC, m.cost_level ASC, m.model_name ASC"

        return fetch_all(query, tuple(params))

    @classmethod
    def get_all(
        cls,
        include_inactive: bool = False,
        provider_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get all AI models with optional filtering

        Args:
            include_inactive: Include inactive models
            provider_id: Filter by provider ID

        Returns:
            List of model dicts
        """
        query = f"""
            SELECT {cls._BASE_FIELDS}
            FROM ai_pipeline.ai_models m
            LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
            WHERE 1=1
        """
        params = []

        if not include_inactive:
            query += " AND m.active = TRUE"

        if provider_id:
            query += " AND m.provider_id = %s"
            params.append(provider_id)

        query += " ORDER BY p.name ASC, m.category ASC, m.model_name ASC"

        return fetch_all(query, tuple(params) if params else None)

    @classmethod
    def get_models_by_category(
        cls,
        category: str,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all AI models by category (e.g., 'audio', 'chat', 'embedding')

        Args:
            category: Model category
            include_inactive: Include inactive models

        Returns:
            List of model dicts
        """
        query = f"""
            SELECT {cls._BASE_FIELDS},
                m.cost_per_1k_input,
                m.cost_per_1k_output
            FROM ai_pipeline.ai_models m
            LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
            WHERE m.category = %s
        """
        params = [category]

        if not include_inactive:
            query += " AND m.active = TRUE"

        query += " ORDER BY m.model_name ASC"

        return fetch_all(query, tuple(params))

    @classmethod
    def get_by_provider(
        cls,
        provider_id: int,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all models for a specific provider.

        Args:
            provider_id: Provider ID
            active_only: Only return active models

        Returns:
            List of model dicts
        """
        return cls.get_all(
            include_inactive=not active_only,
            provider_id=provider_id,
        )

    @classmethod
    def get_categories(cls) -> List[str]:
        """
        Get all unique model categories

        Returns:
            List of category names (sorted)
        """
        query = """
            SELECT DISTINCT category
            FROM ai_pipeline.ai_models
            WHERE category IS NOT NULL
            ORDER BY category
        """
        results = fetch_all(query)
        return [r['category'] for r in results] if results else []
