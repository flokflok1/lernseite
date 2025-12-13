"""
LernsystemX AI Models Repository

Data access layer for AI Models:
- CRUD operations for AI models
- Model synchronization with providers
- Default model management

Phase KI-Architektur - Model Management
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from app.database.connection import fetch_one, fetch_all, execute_query


class AIModelsRepository:
    """
    Repository for AI Models entity

    Handles all database operations for AI models including:
    - Model CRUD operations
    - Provider-based model queries
    - Default model management
    - Sync status tracking
    """

    table_name = 'ai_models'

    @classmethod
    def get_all(cls, include_inactive: bool = False, provider_id: int = None) -> List[Dict[str, Any]]:
        """
        Get all AI models

        Args:
            include_inactive: Include inactive models
            provider_id: Filter by provider

        Returns:
            List of models
        """
        query = """
            SELECT
                m.model_id,
                m.provider_id,
                p.name as provider_name,
                p.display_name as provider_display_name,
                m.model_name,
                m.display_name,
                m.model_type,
                m.category,
                m.subcategory,
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
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
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
    def get_models_by_category(cls, category: str, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all AI models by category (e.g., 'audio', 'chat', 'embedding')

        Args:
            category: Model category
            include_inactive: Include inactive models

        Returns:
            List of models
        """
        query = """
            SELECT
                m.model_id,
                m.provider_id,
                p.name as provider_name,
                p.display_name as provider_display_name,
                m.model_name,
                m.display_name,
                m.model_type,
                m.category,
                m.subcategory,
                m.description,
                m.cost_level,
                m.speed,
                m.context_window,
                m.max_output_tokens,
                m.supports_vision,
                m.supports_functions,
                m.input_price_per_1k,
                m.output_price_per_1k,
                m.cost_per_1k_input,
                m.cost_per_1k_output,
                m.active,
                m.is_default,
                m.created_at,
                m.updated_at
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.category = %s
        """
        params = [category]

        if not include_inactive:
            query += " AND m.active = TRUE"

        query += " ORDER BY m.model_name ASC"

        return fetch_all(query, tuple(params))

    @classmethod
    def get_by_id(cls, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Get model by ID

        Args:
            model_id: Model ID

        Returns:
            Model dict or None
        """
        query = """
            SELECT
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
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.model_id = %s
        """
        return fetch_one(query, (model_id,))

    @classmethod
    def get_by_name(cls, model_name: str, provider_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get model by name

        Args:
            model_name: Model name (e.g., 'gpt-4o', 'claude-3-5-sonnet')
            provider_name: Optional provider name filter

        Returns:
            Model dict or None
        """
        query = """
            SELECT
                m.model_id,
                m.provider_id,
                p.name as provider_name,
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
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.model_name = %s
        """
        params = [model_name]

        if provider_name:
            query += " AND p.name = %s"
            params.append(provider_name)

        return fetch_one(query, tuple(params))

    @classmethod
    def get_by_category(cls, category: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get models by category

        Args:
            category: Model category (chat, reasoning, audio, image, etc.)
            active_only: Only return active models

        Returns:
            List of models
        """
        query = """
            SELECT
                m.model_id,
                m.provider_id,
                p.name as provider_name,
                m.model_name,
                m.display_name,
                m.category,
                m.description,
                m.cost_level,
                m.speed,
                m.context_window,
                m.max_output_tokens,
                m.input_price_per_1k,
                m.output_price_per_1k,
                m.active,
                m.is_default
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.category = %s
        """
        params = [category]

        if active_only:
            query += " AND m.active = TRUE"

        query += " ORDER BY m.is_default DESC, m.cost_level ASC, m.model_name ASC"

        return fetch_all(query, tuple(params))

    @classmethod
    def get_default_model(cls, category: str = 'chat') -> Optional[Dict[str, Any]]:
        """
        Get default model for a category

        Args:
            category: Model category (default: 'chat')

        Returns:
            Default model or None
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
            FROM ai_models m
            LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
            WHERE m.category = %s AND m.is_default = TRUE AND m.active = TRUE
            LIMIT 1
        """
        return fetch_one(query, (category,))

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create new AI model

        Args:
            data: Model data

        Returns:
            Created model or None
        """
        query = """
            INSERT INTO ai_models (
                provider_id, model_name, display_name, model_type, category,
                description, cost_level, speed, context_window, max_output_tokens,
                supports_vision, supports_functions, input_price_per_1k, output_price_per_1k,
                active, is_default
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s
            )
            RETURNING *
        """
        params = (
            data.get('provider_id'),
            data.get('model_name'),
            data.get('display_name'),
            data.get('model_type', 'chat'),
            data.get('category', 'chat'),
            data.get('description'),
            data.get('cost_level', 'medium'),
            data.get('speed', 'medium'),
            data.get('context_window'),
            data.get('max_output_tokens'),
            data.get('supports_vision', False),
            data.get('supports_functions', False),
            data.get('input_price_per_1k'),
            data.get('output_price_per_1k'),
            data.get('active', True),
            data.get('is_default', False)
        )
        return fetch_one(query, params)

    @classmethod
    def update(cls, model_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update AI model

        Args:
            model_id: Model ID
            data: Update data

        Returns:
            Updated model or None
        """
        allowed_fields = [
            'display_name', 'model_type', 'category', 'description',
            'cost_level', 'speed', 'context_window', 'max_output_tokens',
            'supports_vision', 'supports_functions', 'input_price_per_1k',
            'output_price_per_1k', 'active', 'is_default'
        ]
        updates = []
        params = []

        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])

        if not updates:
            return cls.get_by_id(model_id)

        updates.append("updated_at = NOW()")
        params.append(model_id)

        query = f"""
            UPDATE ai_models
            SET {', '.join(updates)}
            WHERE model_id = %s
            RETURNING *
        """

        return fetch_one(query, tuple(params))

    @classmethod
    def upsert(cls, provider_id: int, model_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert or update model by provider_id and model_name

        Args:
            provider_id: Provider ID
            model_name: Model name
            data: Model data

        Returns:
            Upserted model or None
        """
        query = """
            INSERT INTO ai_models (
                provider_id, model_name, display_name, model_type, category,
                description, cost_level, speed, context_window, max_output_tokens,
                supports_vision, supports_functions, input_price_per_1k, output_price_per_1k,
                active, is_default
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s
            )
            ON CONFLICT (provider_id, model_name) DO UPDATE SET
                display_name = EXCLUDED.display_name,
                model_type = EXCLUDED.model_type,
                category = EXCLUDED.category,
                description = COALESCE(EXCLUDED.description, ai_models.description),
                cost_level = EXCLUDED.cost_level,
                speed = EXCLUDED.speed,
                context_window = COALESCE(EXCLUDED.context_window, ai_models.context_window),
                max_output_tokens = COALESCE(EXCLUDED.max_output_tokens, ai_models.max_output_tokens),
                supports_vision = EXCLUDED.supports_vision,
                supports_functions = EXCLUDED.supports_functions,
                input_price_per_1k = COALESCE(EXCLUDED.input_price_per_1k, ai_models.input_price_per_1k),
                output_price_per_1k = COALESCE(EXCLUDED.output_price_per_1k, ai_models.output_price_per_1k),
                updated_at = NOW()
            RETURNING *
        """
        params = (
            provider_id,
            model_name,
            data.get('display_name'),
            data.get('model_type', 'chat'),
            data.get('category', 'chat'),
            data.get('description'),
            data.get('cost_level', 'medium'),
            data.get('speed', 'medium'),
            data.get('context_window'),
            data.get('max_output_tokens'),
            data.get('supports_vision', False),
            data.get('supports_functions', False),
            data.get('input_price_per_1k'),
            data.get('output_price_per_1k'),
            data.get('active', True),
            data.get('is_default', False)
        )
        return fetch_one(query, params)

    @classmethod
    def set_default(cls, model_id: int, category: str = None) -> Optional[Dict[str, Any]]:
        """
        Set model as default for its category

        Args:
            model_id: Model ID
            category: Optional category override

        Returns:
            Updated model or None
        """
        # First, get the model to find its category
        model = cls.get_by_id(model_id)
        if not model:
            return None

        cat = category or model.get('category', 'chat')

        # Unset other defaults in same category
        execute_query("""
            UPDATE ai_models SET is_default = FALSE
            WHERE category = %s AND is_default = TRUE
        """, (cat,))

        # Set this model as default
        query = """
            UPDATE ai_models
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
            active: Active status

        Returns:
            Updated model or None
        """
        query = """
            UPDATE ai_models
            SET active = %s, updated_at = NOW()
            WHERE model_id = %s
            RETURNING model_id, model_name, active
        """
        return fetch_one(query, (active, model_id))

    @classmethod
    def delete(cls, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete AI model

        Args:
            model_id: Model ID

        Returns:
            Deleted model or None
        """
        query = """
            DELETE FROM ai_models WHERE model_id = %s
            RETURNING model_id, model_name
        """
        return fetch_one(query, (model_id,))

    @classmethod
    def count(cls, provider_id: int = None, category: str = None, active_only: bool = True) -> int:
        """
        Count models

        Args:
            provider_id: Filter by provider
            category: Filter by category
            active_only: Only count active models

        Returns:
            Count of models
        """
        query = "SELECT COUNT(*) as count FROM ai_models WHERE 1=1"
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
    def get_categories(cls) -> List[str]:
        """
        Get all unique model categories

        Returns:
            List of category names
        """
        query = """
            SELECT DISTINCT category
            FROM ai_models
            WHERE category IS NOT NULL
            ORDER BY category
        """
        results = fetch_all(query)
        return [r['category'] for r in results] if results else []

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        Get model statistics

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

    @classmethod
    def mark_synced(cls, model_id: int) -> None:
        """
        Update the updated_at timestamp to mark model as synced

        Args:
            model_id: Model ID
        """
        execute_query("""
            UPDATE ai_models SET updated_at = NOW()
            WHERE model_id = %s
        """, (model_id,))
