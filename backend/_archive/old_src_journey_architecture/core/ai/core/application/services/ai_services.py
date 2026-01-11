"""
AI Domain - Domain Services (DDD)

Domain services contain business logic that:
- Doesn't naturally belong to a single entity
- Requires coordination between multiple aggregates
- Implements core business rules

Reference: Eric Evans - Domain-Driven Design, Chapter 5
Pattern: Domain Service Pattern
"""

from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta

from ...domain.value_objects import (
    ModelCategory,
    ModelCategoryEnum,
    PricingTier,
    Margin,
    ProviderHealth,
    ProviderHealthStatus
)


class AIModelSelectionService:
    """
    Domain Service for AI model selection logic.

    Responsibilities:
    - Select best model for a given category and requirements
    - Consider cost, performance, availability
    - Apply fallback logic when preferred model unavailable
    """

    @staticmethod
    def select_model_for_category(
        category: str,
        models: List[Dict[str, Any]],
        max_cost_per_1k: Optional[float] = None,
        prefer_default: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Select best model for a category.

        Business Rules:
        1. Prefer default model if available and active
        2. Filter by max_cost if specified
        3. Fallback to cheapest active model
        4. Return None if no suitable model found

        Args:
            category: Model category (chat, reasoning, etc.)
            models: List of available models
            max_cost_per_1k: Optional maximum cost constraint
            prefer_default: Whether to prefer default model

        Returns:
            Selected model or None if no suitable model found
        """
        # Filter by category and active status
        category_models = [
            m for m in models
            if m.get('category') == category and m.get('active', False)
        ]

        if not category_models:
            return None

        # Apply cost constraint
        if max_cost_per_1k is not None:
            category_models = [
                m for m in category_models
                if m.get('input_price_per_1k', float('inf')) <= max_cost_per_1k
            ]

        if not category_models:
            return None

        # Prefer default model
        if prefer_default:
            default_models = [m for m in category_models if m.get('is_default', False)]
            if default_models:
                return default_models[0]

        # Fallback: Select cheapest model
        return min(
            category_models,
            key=lambda m: m.get('input_price_per_1k', float('inf'))
        )

    @staticmethod
    def select_model_from_profile(
        profile: Dict[str, Any],
        slot_name: str,
        all_models: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Select model from profile configuration.

        Business Rule: Use profile slot mapping if exists, otherwise fallback to default.

        Args:
            profile: AI profile configuration
            slot_name: Capability slot name (chat, reasoning, etc.)
            all_models: All available models

        Returns:
            Selected model or None
        """
        model_slots = profile.get('model_slots', {})
        model_id = model_slots.get(slot_name)

        if not model_id:
            # Fallback: Use slot_name as category
            return AIModelSelectionService.select_model_for_category(
                category=slot_name,
                models=all_models,
                prefer_default=True
            )

        # Find specific model by ID
        for model in all_models:
            if model.get('model_id') == model_id and model.get('active', False):
                return model

        return None


class AIUsageService:
    """
    Domain Service for AI usage tracking and cost calculation.

    Responsibilities:
    - Calculate costs and prices for AI operations
    - Track token usage
    - Apply pricing tiers
    """

    @staticmethod
    def calculate_operation_cost(
        model: Dict[str, Any],
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, Decimal]:
        """
        Calculate cost and price for an AI operation.

        Args:
            model: Model configuration with pricing
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Dictionary with cost, price, and margin information
        """
        # Extract pricing from model
        input_cost = Decimal(str(model.get('input_cost_per_1k', 0)))
        output_cost = Decimal(str(model.get('output_cost_per_1k', 0)))
        input_price = Decimal(str(model.get('input_price_per_1k', 0)))
        output_price = Decimal(str(model.get('output_price_per_1k', 0)))

        # Calculate totals
        total_input_cost = input_cost * Decimal(input_tokens) / Decimal(1000)
        total_output_cost = output_cost * Decimal(output_tokens) / Decimal(1000)
        total_input_price = input_price * Decimal(input_tokens) / Decimal(1000)
        total_output_price = output_price * Decimal(output_tokens) / Decimal(1000)

        total_cost = total_input_cost + total_output_cost
        total_price = total_input_price + total_output_price
        margin = total_price - total_cost if total_cost > 0 else Decimal(0)

        return {
            'total_cost': round(total_cost, 6),
            'total_price': round(total_price, 6),
            'margin': round(margin, 6),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens
        }

    @staticmethod
    def estimate_operation_price(
        model: Dict[str, Any],
        estimated_input_tokens: int,
        estimated_output_tokens: int
    ) -> Decimal:
        """
        Estimate price for an operation before execution.

        Business Rule: Use customer price, not cost.

        Args:
            model: Model configuration
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens

        Returns:
            Estimated total price
        """
        result = AIUsageService.calculate_operation_cost(
            model=model,
            input_tokens=estimated_input_tokens,
            output_tokens=estimated_output_tokens
        )
        return result['total_price']


class AISyncService:
    """
    Domain Service for AI model synchronization.

    Responsibilities:
    - Synchronize models from providers
    - Deactivate removed models (don't delete)
    - Update pricing when changed
    - Emit domain events
    """

    @staticmethod
    def prepare_sync_operations(
        provider_models: List[Dict[str, Any]],
        existing_models: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Prepare sync operations for models.

        Business Rules:
        1. New models → Add as active
        2. Existing models with price changes → Update
        3. Missing models → Deactivate (don't delete)

        Args:
            provider_models: Models from provider API
            existing_models: Current models in database

        Returns:
            Dictionary with 'add', 'update', 'deactivate' lists
        """
        existing_identifiers = {
            m.get('model_identifier'): m for m in existing_models
        }
        provider_identifiers = {
            m.get('model_identifier') for m in provider_models
        }

        operations = {
            'add': [],
            'update': [],
            'deactivate': []
        }

        # Identify new and updated models
        for provider_model in provider_models:
            identifier = provider_model.get('model_identifier')
            existing = existing_identifiers.get(identifier)

            if not existing:
                # New model
                operations['add'].append(provider_model)
            else:
                # Check if pricing changed
                if AISyncService._has_pricing_changed(provider_model, existing):
                    operations['update'].append({
                        'model_id': existing.get('model_id'),
                        'changes': provider_model
                    })

        # Identify models to deactivate
        for existing in existing_models:
            identifier = existing.get('model_identifier')
            if identifier not in provider_identifiers and existing.get('active', False):
                operations['deactivate'].append(existing)

        return operations

    @staticmethod
    def _has_pricing_changed(
        provider_model: Dict[str, Any],
        existing_model: Dict[str, Any]
    ) -> bool:
        """
        Check if model pricing has changed.

        Args:
            provider_model: Model from provider
            existing_model: Existing model in database

        Returns:
            True if pricing changed
        """
        provider_input = Decimal(str(provider_model.get('input_cost_per_1k', 0)))
        provider_output = Decimal(str(provider_model.get('output_cost_per_1k', 0)))
        existing_input = Decimal(str(existing_model.get('input_cost_per_1k', 0)))
        existing_output = Decimal(str(existing_model.get('output_cost_per_1k', 0)))

        return provider_input != existing_input or provider_output != existing_output


class AIHealthMonitoringService:
    """
    Domain Service for provider health monitoring.

    Responsibilities:
    - Evaluate provider health status
    - Recommend failover when necessary
    - Track health history
    """

    # Thresholds
    HEALTHY_THRESHOLD_MS = 5000
    DEGRADED_THRESHOLD_MS = 15000

    @staticmethod
    def evaluate_health_status(
        response_time_ms: Optional[int],
        error_occurred: bool,
        error_message: Optional[str] = None
    ) -> ProviderHealth:
        """
        Evaluate provider health status.

        Business Rules:
        1. Error → Down
        2. Response time < 5s → Healthy
        3. Response time 5-15s → Degraded
        4. Response time > 15s → Degraded (slow)

        Args:
            response_time_ms: Response time in milliseconds
            error_occurred: Whether an error occurred
            error_message: Optional error message

        Returns:
            ProviderHealth value object
        """
        checked_at = datetime.utcnow().isoformat()

        if error_occurred:
            return ProviderHealth.down(
                error_message=error_message or 'Unknown error',
                checked_at=checked_at
            )

        if response_time_ms is None:
            return ProviderHealth(
                status=ProviderHealthStatus.UNKNOWN,
                checked_at=checked_at
            )

        if response_time_ms < AIHealthMonitoringService.HEALTHY_THRESHOLD_MS:
            return ProviderHealth.healthy(
                response_time_ms=response_time_ms,
                checked_at=checked_at
            )

        if response_time_ms < AIHealthMonitoringService.DEGRADED_THRESHOLD_MS:
            return ProviderHealth.degraded(
                response_time_ms=response_time_ms,
                error_message='Slow response time',
                checked_at=checked_at
            )

        return ProviderHealth.degraded(
            response_time_ms=response_time_ms,
            error_message='Very slow response time',
            checked_at=checked_at
        )

    @staticmethod
    def should_failover(
        primary_health: ProviderHealth,
        backup_health: ProviderHealth
    ) -> bool:
        """
        Determine if failover to backup provider is recommended.

        Business Rule: Failover if primary is down and backup is operational.

        Args:
            primary_health: Primary provider health
            backup_health: Backup provider health

        Returns:
            True if failover recommended
        """
        return (
            not primary_health.is_operational() and
            backup_health.is_operational()
        )
