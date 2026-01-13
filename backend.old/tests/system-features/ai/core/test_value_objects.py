"""
Tests for AI Domain Value Objects

Tests immutability, validation, and business logic of value objects.
"""

import pytest
from decimal import Decimal

from app.api.system_features.ai.core.value_objects import (
    ModelCategory,
    ModelCategoryEnum,
    CapabilitySlot,
    Margin,
    PricingTier,
    ProviderHealth,
    ProviderHealthStatus
)


class TestModelCategory:
    """Tests for ModelCategory value object."""

    def test_create_valid_category(self):
        """Test creating valid model category."""
        category = ModelCategory(category=ModelCategoryEnum.CHAT)
        assert category.category == ModelCategoryEnum.CHAT
        assert str(category) == 'chat'

    def test_chat_is_multimodal(self):
        """Test that chat category is multimodal."""
        category = ModelCategory(category=ModelCategoryEnum.CHAT)
        assert category.is_multimodal() is True

    def test_audio_not_multimodal(self):
        """Test that audio category is not multimodal."""
        category = ModelCategory(category=ModelCategoryEnum.AUDIO)
        assert category.is_multimodal() is False

    def test_immutability(self):
        """Test that ModelCategory is immutable."""
        category = ModelCategory(category=ModelCategoryEnum.CHAT)
        with pytest.raises(AttributeError):
            category.category = ModelCategoryEnum.AUDIO


class TestCapabilitySlot:
    """Tests for CapabilitySlot value object."""

    def test_create_required_slot(self):
        """Test creating required capability slot."""
        slot = CapabilitySlot(slot_name='chat', required=True)
        assert slot.slot_name == 'chat'
        assert slot.required is True
        assert '*' in str(slot)

    def test_create_optional_slot(self):
        """Test creating optional capability slot."""
        slot = CapabilitySlot(slot_name='image', required=False)
        assert slot.required is False
        assert '*' not in str(slot)

    def test_empty_slot_name_raises(self):
        """Test that empty slot name raises ValueError."""
        with pytest.raises(ValueError, match="non-empty string"):
            CapabilitySlot(slot_name='')

    def test_long_slot_name_raises(self):
        """Test that too long slot name raises ValueError."""
        with pytest.raises(ValueError, match="too long"):
            CapabilitySlot(slot_name='a' * 51)


class TestMargin:
    """Tests for Margin value object."""

    def test_create_valid_margin(self):
        """Test creating valid margin."""
        margin = Margin(margin_percent=33.33)
        assert margin.margin_percent == 33.33

    def test_negative_margin_raises(self):
        """Test that negative margin raises ValueError."""
        with pytest.raises(ValueError, match="between 0-100"):
            Margin(margin_percent=-10)

    def test_margin_over_100_raises(self):
        """Test that margin over 100% raises ValueError."""
        with pytest.raises(ValueError, match="between 0-100"):
            Margin(margin_percent=150)

    def test_apply_margin_to_cost(self):
        """Test applying margin to cost."""
        margin = Margin(margin_percent=33.33)
        cost = Decimal('0.003')
        price = margin.apply_to_cost(cost)
        assert price == Decimal('0.003999')

    def test_apply_margin_20_percent(self):
        """Test applying 20% margin."""
        margin = Margin(margin_percent=20)
        cost = Decimal('0.010')
        price = margin.apply_to_cost(cost)
        assert price == Decimal('0.012')

    def test_negative_cost_raises(self):
        """Test that negative cost raises ValueError."""
        margin = Margin(margin_percent=20)
        with pytest.raises(ValueError, match="cannot be negative"):
            margin.apply_to_cost(Decimal('-0.001'))

    def test_calculate_margin_from_cost_and_price(self):
        """Test calculating margin from cost and price."""
        cost = Decimal('0.003')
        price = Decimal('0.004')
        margin = Margin.calculate_from_cost_and_price(cost, price)
        assert margin is not None
        assert margin.margin_percent == 33.33

    def test_calculate_margin_zero_cost_returns_none(self):
        """Test that zero cost returns None."""
        cost = Decimal('0')
        price = Decimal('0.004')
        margin = Margin.calculate_from_cost_and_price(cost, price)
        assert margin is None


class TestPricingTier:
    """Tests for PricingTier value object."""

    def test_create_valid_pricing_tier(self):
        """Test creating valid pricing tier."""
        margin = Margin(margin_percent=33.33)
        tier = PricingTier(
            input_cost_per_1k=Decimal('0.003'),
            output_cost_per_1k=Decimal('0.015'),
            margin=margin
        )
        assert tier.input_cost_per_1k == Decimal('0.003')
        assert tier.output_cost_per_1k == Decimal('0.015')

    def test_negative_input_cost_raises(self):
        """Test that negative input cost raises ValueError."""
        margin = Margin(margin_percent=20)
        with pytest.raises(ValueError, match="cannot be negative"):
            PricingTier(
                input_cost_per_1k=Decimal('-0.001'),
                output_cost_per_1k=Decimal('0.015'),
                margin=margin
            )

    def test_get_customer_prices(self):
        """Test calculating customer prices."""
        margin = Margin(margin_percent=20)
        tier = PricingTier(
            input_cost_per_1k=Decimal('0.003'),
            output_cost_per_1k=Decimal('0.015'),
            margin=margin
        )
        input_price = tier.get_customer_input_price()
        output_price = tier.get_customer_output_price()
        assert input_price == Decimal('0.0036')
        assert output_price == Decimal('0.018')

    def test_calculate_total_cost(self):
        """Test calculating total cost for token usage."""
        margin = Margin(margin_percent=20)
        tier = PricingTier(
            input_cost_per_1k=Decimal('0.003'),
            output_cost_per_1k=Decimal('0.015'),
            margin=margin
        )
        total = tier.calculate_total_cost(input_tokens=1000, output_tokens=500)
        # (0.003 * 1000/1000) + (0.015 * 500/1000) = 0.003 + 0.0075 = 0.0105
        assert total == Decimal('0.0105')

    def test_calculate_total_price(self):
        """Test calculating total price with margin."""
        margin = Margin(margin_percent=20)
        tier = PricingTier(
            input_cost_per_1k=Decimal('0.003'),
            output_cost_per_1k=Decimal('0.015'),
            margin=margin
        )
        total = tier.calculate_total_price(input_tokens=1000, output_tokens=500)
        # (0.0036 * 1000/1000) + (0.018 * 500/1000) = 0.0036 + 0.009 = 0.0126
        assert total == Decimal('0.0126')


class TestProviderHealth:
    """Tests for ProviderHealth value object."""

    def test_create_healthy_status(self):
        """Test creating healthy provider status."""
        health = ProviderHealth.healthy(
            response_time_ms=1000,
            checked_at='2026-01-08T10:00:00'
        )
        assert health.status == ProviderHealthStatus.HEALTHY
        assert health.response_time_ms == 1000
        assert health.is_healthy() is True
        assert health.is_operational() is True

    def test_create_degraded_status(self):
        """Test creating degraded provider status."""
        health = ProviderHealth.degraded(
            response_time_ms=8000,
            error_message='Slow response',
            checked_at='2026-01-08T10:00:00'
        )
        assert health.status == ProviderHealthStatus.DEGRADED
        assert health.is_healthy() is False
        assert health.is_operational() is True

    def test_create_down_status(self):
        """Test creating down provider status."""
        health = ProviderHealth.down(
            error_message='Connection failed',
            checked_at='2026-01-08T10:00:00'
        )
        assert health.status == ProviderHealthStatus.DOWN
        assert health.is_operational() is False

    def test_negative_response_time_raises(self):
        """Test that negative response time raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            ProviderHealth(
                status=ProviderHealthStatus.HEALTHY,
                response_time_ms=-100
            )
