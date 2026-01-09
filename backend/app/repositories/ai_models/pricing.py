"""
AI Models Pricing Repository

Handles pricing-related queries and bulk price updates:
- Get all models with pricing information
- Bulk update prices for multiple models
- Pricing field validation

Phase KI-Architektur - Model Management
"""

from typing import Optional, Dict, List, Any
from app.database.connection import fetch_all, fetch_one


class AIModelsPricingRepository:
    """
    Repository for AI Models pricing operations

    Handles:
    - Pricing information retrieval
    - Bulk price updates
    - Cost and price field management
    """

    table_name = 'ai_pipeline.ai_models'

    @classmethod
    def get_all_with_pricing(
        cls,
        include_inactive: bool = False,
        provider_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get all models with full pricing information (cost AND price)

        Args:
            include_inactive: Include inactive models
            provider_id: Filter by provider ID

        Returns:
            List of model dicts with pricing data
        """
        query = """
            SELECT
                m.model_id,
                m.provider_id,
                p.name as provider_name,
                p.display_name as provider_display_name,
                m.model_name,
                m.display_name,
                m.category,
                m.cost_per_1k_input,
                m.cost_per_1k_output,
                m.input_price_per_1k,
                m.output_price_per_1k,
                m.active,
                m.is_default,
                m.updated_at
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
    def bulk_update_prices(
        cls,
        model_ids: List[int],
        updates: Dict[str, Any]
    ) -> int:
        """
        Bulk update prices for multiple models

        Allows updating these fields:
        - input_price_per_1k
        - output_price_per_1k
        - cost_per_1k_input
        - cost_per_1k_output

        Args:
            model_ids: List of model IDs to update
            updates: Dict with pricing fields to update

        Returns:
            Number of models updated
        """
        if not model_ids or not updates:
            return 0

        allowed = {
            'input_price_per_1k', 'output_price_per_1k',
            'cost_per_1k_input', 'cost_per_1k_output'
        }
        filtered_updates = {k: v for k, v in updates.items() if k in allowed}

        if not filtered_updates:
            return 0

        set_clauses = [f"{field} = %s" for field in filtered_updates.keys()]
        set_clauses.append("updated_at = NOW()")

        query = f"""
            UPDATE ai_pipeline.ai_models
            SET {', '.join(set_clauses)}
            WHERE model_id = ANY(%s)
            RETURNING model_id
        """

        params = list(filtered_updates.values()) + [model_ids]
        results = fetch_all(query, tuple(params))
        return len(results) if results else 0
