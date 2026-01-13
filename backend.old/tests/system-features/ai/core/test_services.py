"""
Tests for AI Domain Services

Tests business logic in domain services.
"""

import pytest
from decimal import Decimal

from app.api.system_features.ai.core.services import (
    AIModelSelectionService,
    AIUsageService,
    AISyncService,
    AIHealthMonitoringService
)
from app.api.system_features.ai.core.value_objects import (
    ProviderHealth,
    ProviderHealthStatus
)


class TestAIModelSelectionService:
    """Tests for AIModelSelectionService."""

    def test_select_model_for_category_default(self):
        """Test selecting default model for category."""
        models = [
            {
                'model_id': '1',
                'category': 'chat',
                'active': True,
                'is_default': True,
                'input_price_per_1k': 0.01
            },
            {
                'model_id': '2',
                'category': 'chat',
                'active': True,
                'is_default': False,
                'input_price_per_1k': 0.005
            }
        ]

        selected = AIModelSelectionService.select_model_for_category(
            category='chat',
            models=models,
            prefer_default=True
        )

        assert selected['model_id'] == '1'  # Default model

    def test_select_model_fallback_to_cheapest(self):
        """Test fallback to cheapest model when no default."""
        models = [
            {
                'model_id': '1',
                'category': 'chat',
                'active': True,
                'is_default': False,
                'input_price_per_1k': 0.01
            },
            {
                'model_id': '2',
                'category': 'chat',
                'active': True,
                'is_default': False,
                'input_price_per_1k': 0.005
            }
        ]

        selected = AIModelSelectionService.select_model_for_category(
            category='chat',
            models=models,
            prefer_default=True
        )

        assert selected['model_id'] == '2'  # Cheapest

    def test_select_model_with_cost_constraint(self):
        """Test selecting model with cost constraint."""
        models = [
            {
                'model_id': '1',
                'category': 'chat',
                'active': True,
                'is_default': True,
                'input_price_per_1k': 0.01
            },
            {
                'model_id': '2',
                'category': 'chat',
                'active': True,
                'is_default': False,
                'input_price_per_1k': 0.005
            }
        ]

        selected = AIModelSelectionService.select_model_for_category(
            category='chat',
            models=models,
            max_cost_per_1k=0.007
        )

        assert selected['model_id'] == '2'  # Only one within budget

    def test_select_model_no_suitable_model(self):
        """Test that None is returned when no suitable model."""
        models = [
            {
                'model_id': '1',
                'category': 'chat',
                'active': False,  # Inactive
                'input_price_per_1k': 0.01
            }
        ]

        selected = AIModelSelectionService.select_model_for_category(
            category='chat',
            models=models
        )

        assert selected is None

    def test_select_model_from_profile(self):
        """Test selecting model from profile slot."""
        profile = {
            'model_slots': {
                'chat': 'model-123'
            }
        }
        models = [
            {
                'model_id': 'model-123',
                'category': 'chat',
                'active': True
            }
        ]

        selected = AIModelSelectionService.select_model_from_profile(
            profile=profile,
            slot_name='chat',
            all_models=models
        )

        assert selected['model_id'] == 'model-123'


class TestAIUsageService:
    """Tests for AIUsageService."""

    def test_calculate_operation_cost(self):
        """Test calculating cost and price for operation."""
        model = {
            'input_cost_per_1k': 0.003,
            'output_cost_per_1k': 0.015,
            'input_price_per_1k': 0.004,
            'output_price_per_1k': 0.020
        }

        result = AIUsageService.calculate_operation_cost(
            model=model,
            input_tokens=1000,
            output_tokens=500
        )

        # Cost: (0.003 * 1) + (0.015 * 0.5) = 0.0105
        assert result['total_cost'] == Decimal('0.0105')
        # Price: (0.004 * 1) + (0.020 * 0.5) = 0.014
        assert result['total_price'] == Decimal('0.014')
        assert result['margin'] == Decimal('0.0035')
        assert result['total_tokens'] == 1500

    def test_estimate_operation_price(self):
        """Test estimating operation price."""
        model = {
            'input_cost_per_1k': 0.003,
            'output_cost_per_1k': 0.015,
            'input_price_per_1k': 0.004,
            'output_price_per_1k': 0.020
        }

        price = AIUsageService.estimate_operation_price(
            model=model,
            estimated_input_tokens=2000,
            estimated_output_tokens=1000
        )

        # Price: (0.004 * 2) + (0.020 * 1) = 0.028
        assert price == Decimal('0.028')


class TestAISyncService:
    """Tests for AISyncService."""

    def test_prepare_sync_operations_new_models(self):
        """Test identifying new models to add."""
        provider_models = [
            {'model_identifier': 'gpt-4', 'input_cost_per_1k': 0.003},
            {'model_identifier': 'gpt-3.5', 'input_cost_per_1k': 0.001}
        ]
        existing_models = []

        operations = AISyncService.prepare_sync_operations(
            provider_models=provider_models,
            existing_models=existing_models
        )

        assert len(operations['add']) == 2
        assert len(operations['update']) == 0
        assert len(operations['deactivate']) == 0

    def test_prepare_sync_operations_deactivate_removed(self):
        """Test identifying models to deactivate."""
        provider_models = [
            {'model_identifier': 'gpt-4', 'input_cost_per_1k': 0.003}
        ]
        existing_models = [
            {
                'model_id': '1',
                'model_identifier': 'gpt-4',
                'active': True,
                'input_cost_per_1k': 0.003
            },
            {
                'model_id': '2',
                'model_identifier': 'gpt-3',  # Removed from provider
                'active': True,
                'input_cost_per_1k': 0.001
            }
        ]

        operations = AISyncService.prepare_sync_operations(
            provider_models=provider_models,
            existing_models=existing_models
        )

        assert len(operations['add']) == 0
        assert len(operations['deactivate']) == 1
        assert operations['deactivate'][0]['model_identifier'] == 'gpt-3'

    def test_prepare_sync_operations_update_pricing(self):
        """Test identifying models with pricing changes."""
        provider_models = [
            {'model_identifier': 'gpt-4', 'input_cost_per_1k': 0.004}  # Price changed
        ]
        existing_models = [
            {
                'model_id': '1',
                'model_identifier': 'gpt-4',
                'active': True,
                'input_cost_per_1k': 0.003,  # Old price
                'output_cost_per_1k': 0.015
            }
        ]

        operations = AISyncService.prepare_sync_operations(
            provider_models=provider_models,
            existing_models=existing_models
        )

        assert len(operations['add']) == 0
        assert len(operations['update']) == 1
        assert operations['update'][0]['model_id'] == '1'


class TestAIHealthMonitoringService:
    """Tests for AIHealthMonitoringService."""

    def test_evaluate_health_healthy(self):
        """Test evaluating healthy provider."""
        health = AIHealthMonitoringService.evaluate_health_status(
            response_time_ms=2000,
            error_occurred=False
        )

        assert health.status == ProviderHealthStatus.HEALTHY
        assert health.is_healthy() is True
        assert health.is_operational() is True

    def test_evaluate_health_degraded_slow(self):
        """Test evaluating degraded provider (slow response)."""
        health = AIHealthMonitoringService.evaluate_health_status(
            response_time_ms=8000,
            error_occurred=False
        )

        assert health.status == ProviderHealthStatus.DEGRADED
        assert health.is_healthy() is False
        assert health.is_operational() is True

    def test_evaluate_health_down(self):
        """Test evaluating down provider."""
        health = AIHealthMonitoringService.evaluate_health_status(
            response_time_ms=None,
            error_occurred=True,
            error_message='Connection timeout'
        )

        assert health.status == ProviderHealthStatus.DOWN
        assert health.is_operational() is False

    def test_should_failover_yes(self):
        """Test that failover is recommended when primary down."""
        primary = ProviderHealth.down(
            error_message='Connection failed',
            checked_at='2026-01-08T10:00:00'
        )
        backup = ProviderHealth.healthy(
            response_time_ms=2000,
            checked_at='2026-01-08T10:00:00'
        )

        should_failover = AIHealthMonitoringService.should_failover(
            primary_health=primary,
            backup_health=backup
        )

        assert should_failover is True

    def test_should_failover_no_backup_down(self):
        """Test that failover is not recommended when backup also down."""
        primary = ProviderHealth.down(
            error_message='Connection failed',
            checked_at='2026-01-08T10:00:00'
        )
        backup = ProviderHealth.down(
            error_message='Connection failed',
            checked_at='2026-01-08T10:00:00'
        )

        should_failover = AIHealthMonitoringService.should_failover(
            primary_health=primary,
            backup_health=backup
        )

        assert should_failover is False
