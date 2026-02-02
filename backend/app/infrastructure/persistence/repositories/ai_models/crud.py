"""
AI Models CRUD Operations Repository

Handles Create, Read, Update, Delete and Upsert operations for AI models.

Phase KI-Architektur - Model Management
"""

from typing import Optional, Dict, Any
from app.infrastructure.persistence.database.connection import fetch_one


class AIModelsCRUDRepository:
    """
    Repository for AI Models CRUD operations

    Handles:
    - Model creation
    - Model updates
    - Model deletion
    - Upsert operations (insert or update)
    """

    table_name = 'ai_pipeline.ai_models'

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create new AI model

        Args:
            data: Model data with keys:
                - provider_id: Provider ID (required)
                - model_name: Model name (required)
                - display_name: Display name (required)
                - model_type: Type of model (default: 'chat')
                - category: Model category (default: 'chat')
                - description: Model description (optional)
                - cost_level: Cost level (default: 'medium')
                - speed: Speed rating (default: 'medium')
                - context_window: Context window size (optional)
                - max_output_tokens: Max output tokens (optional)
                - supports_vision: Vision support (default: False)
                - supports_functions: Function calling support (default: False)
                - input_price_per_1k: Input price per 1k tokens (optional)
                - output_price_per_1k: Output price per 1k tokens (optional)
                - active: Is model active (default: True)
                - is_default: Is default model (default: False)

        Returns:
            Created model dict or None
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
        Update AI model by ID

        Args:
            model_id: Model ID
            data: Update data with allowed fields:
                - display_name, model_type, category, description
                - cost_level, speed, context_window, max_output_tokens
                - supports_vision, supports_functions
                - input_price_per_1k, output_price_per_1k
                - cost_per_1k_input, cost_per_1k_output
                - active, is_default

        Returns:
            Updated model dict or None
        """
        allowed_fields = [
            'display_name', 'model_type', 'category', 'description',
            'cost_level', 'speed', 'context_window', 'max_output_tokens',
            'supports_vision', 'supports_functions', 'input_price_per_1k',
            'output_price_per_1k', 'cost_per_1k_input', 'cost_per_1k_output',
            'active', 'is_default'
        ]
        updates = []
        params = []

        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])

        if not updates:
            from .query import AIModelsQueryRepository
            return AIModelsQueryRepository.get_by_id(model_id)

        updates.append("updated_at = NOW()")
        params.append(model_id)

        query = f"""
            UPDATE ai_pipeline.ai_models
            SET {', '.join(updates)}
            WHERE model_id = %s
            RETURNING *
        """

        return fetch_one(query, tuple(params))

    @classmethod
    def upsert(
        cls,
        provider_id: int,
        model_name: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update model by provider_id and model_name

        Args:
            provider_id: Provider ID
            model_name: Model name
            data: Model data

        Returns:
            Upserted model dict or None
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
    def delete(cls, model_id: int) -> Optional[Dict[str, Any]]:
        """
        Delete AI model by ID

        Args:
            model_id: Model ID

        Returns:
            Deleted model dict or None
        """
        query = """
            DELETE FROM ai_pipeline.ai_models WHERE model_id = %s
            RETURNING model_id, model_name
        """
        return fetch_one(query, (model_id,))
