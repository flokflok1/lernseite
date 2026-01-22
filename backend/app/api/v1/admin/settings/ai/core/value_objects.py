"""
AI Domain - Value Objects (DDD)

Immutable value objects representing business concepts in the AI domain.
Value objects are defined by their attributes, not identity.

Reference: Eric Evans - Domain-Driven Design, Chapter 5
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from enum import Enum


class ModelCategoryEnum(str, Enum):
    """
    AI Model Categories.

    These categories define the primary capability of an AI model.
    """
    CHAT = 'chat'
    REASONING = 'reasoning'
    AUDIO = 'audio'
    IMAGE = 'image'
    VIDEO = 'video'
    TRANSLATION = 'translation'
    EMBEDDING = 'embedding'


@dataclass(frozen=True)
class ModelCategory:
    """
    Model Category Value Object.

    Represents the primary capability category of an AI model.
    Immutable to ensure category consistency across the domain.
    """
    category: ModelCategoryEnum

    def __post_init__(self):
        """Validate category value."""
        if not isinstance(self.category, ModelCategoryEnum):
            raise ValueError(f"Invalid category: {self.category}")

    def __str__(self) -> str:
        return self.category.value

    def is_multimodal(self) -> bool:
        """Check if category supports multimodal capabilities."""
        return self.category in [
            ModelCategoryEnum.CHAT,
            ModelCategoryEnum.REASONING
        ]


@dataclass(frozen=True)
class CapabilitySlot:
    """
    Capability Slot Value Object.

    Represents a specific AI capability slot used in model profiles.
    Examples: chat, reasoning, image_generation, audio_synthesis
    """
    slot_name: str
    required: bool = True

    def __post_init__(self):
        """Validate slot name."""
        if not self.slot_name or not isinstance(self.slot_name, str):
            raise ValueError("Slot name must be a non-empty string")
        if len(self.slot_name) > 50:
            raise ValueError("Slot name too long (max 50 characters)")

    def __str__(self) -> str:
        return f"{self.slot_name}{'*' if self.required else ''}"


@dataclass(frozen=True)
class Margin:
    """
    Pricing Margin Value Object.

    Represents the markup percentage applied to provider costs.
    Business Rule: Margin typically ranges from 20-50% for AI services.

    Formula: customer_price = cost * (1 + margin_percent/100)
    """
    margin_percent: float

    def __post_init__(self):
        """Validate margin percentage."""
        if not isinstance(self.margin_percent, (int, float)):
            raise ValueError("Margin must be a number")
        if not 0 <= self.margin_percent <= 100:
            raise ValueError("Margin must be between 0-100%")

    def apply_to_cost(self, cost: Decimal) -> Decimal:
        """
        Apply margin to a cost to calculate customer price.

        Args:
            cost: Provider cost per 1K tokens

        Returns:
            Customer price with margin applied

        Example:
            >>> margin = Margin(margin_percent=33.33)
            >>> margin.apply_to_cost(Decimal('0.003'))
            Decimal('0.003999')
        """
        if cost < 0:
            raise ValueError("Cost cannot be negative")
        multiplier = Decimal(1 + self.margin_percent / 100)
        return round(cost * multiplier, 6)

    def calculate_from_cost_and_price(cost: Decimal, price: Decimal) -> Optional['Margin']:
        """
        Calculate margin from cost and price.

        Args:
            cost: Provider cost
            price: Customer price

        Returns:
            Margin object or None if not calculable

        Example:
            >>> Margin.calculate_from_cost_and_price(
            ...     Decimal('0.003'), Decimal('0.004')
            ... )
            Margin(margin_percent=33.33)
        """
        if cost <= 0:
            return None
        margin_percent = float((price - cost) / cost * 100)
        return Margin(margin_percent=round(margin_percent, 2))


@dataclass(frozen=True)
class PricingTier:
    """
    Pricing Tier Value Object.

    Represents a pricing tier for AI model usage.
    Combines cost structure with margin to determine customer pricing.
    """
    input_cost_per_1k: Decimal
    output_cost_per_1k: Decimal
    margin: Margin

    def __post_init__(self):
        """Validate pricing tier."""
        if self.input_cost_per_1k < 0:
            raise ValueError("Input cost cannot be negative")
        if self.output_cost_per_1k < 0:
            raise ValueError("Output cost cannot be negative")
        if not isinstance(self.margin, Margin):
            raise ValueError("Margin must be a Margin value object")

    def get_customer_input_price(self) -> Decimal:
        """Calculate customer price for input tokens."""
        return self.margin.apply_to_cost(self.input_cost_per_1k)

    def get_customer_output_price(self) -> Decimal:
        """Calculate customer price for output tokens."""
        return self.margin.apply_to_cost(self.output_cost_per_1k)

    def calculate_total_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate total cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in currency units
        """
        input_cost = self.input_cost_per_1k * Decimal(input_tokens) / Decimal(1000)
        output_cost = self.output_cost_per_1k * Decimal(output_tokens) / Decimal(1000)
        return round(input_cost + output_cost, 6)

    def calculate_total_price(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Calculate total customer price for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total price with margin applied
        """
        input_price = self.get_customer_input_price() * Decimal(input_tokens) / Decimal(1000)
        output_price = self.get_customer_output_price() * Decimal(output_tokens) / Decimal(1000)
        return round(input_price + output_price, 6)


class ProviderHealthStatus(str, Enum):
    """Provider health status enumeration."""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    DOWN = 'down'
    UNKNOWN = 'unknown'


@dataclass(frozen=True)
class ProviderHealth:
    """
    Provider Health Value Object.

    Represents the operational health status of an AI provider.
    Used for monitoring and failover decisions.
    """
    status: ProviderHealthStatus
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    checked_at: Optional[str] = None  # ISO 8601 timestamp

    def __post_init__(self):
        """Validate health status."""
        if not isinstance(self.status, ProviderHealthStatus):
            raise ValueError(f"Invalid status: {self.status}")
        if self.response_time_ms is not None and self.response_time_ms < 0:
            raise ValueError("Response time cannot be negative")

    def is_operational(self) -> bool:
        """Check if provider is operational (healthy or degraded)."""
        return self.status in [ProviderHealthStatus.HEALTHY, ProviderHealthStatus.DEGRADED]

    def is_healthy(self) -> bool:
        """Check if provider is fully healthy."""
        return self.status == ProviderHealthStatus.HEALTHY

    @staticmethod
    def healthy(response_time_ms: int, checked_at: str) -> 'ProviderHealth':
        """Create a healthy status."""
        return ProviderHealth(
            status=ProviderHealthStatus.HEALTHY,
            response_time_ms=response_time_ms,
            checked_at=checked_at
        )

    @staticmethod
    def degraded(response_time_ms: int, error_message: str, checked_at: str) -> 'ProviderHealth':
        """Create a degraded status."""
        return ProviderHealth(
            status=ProviderHealthStatus.DEGRADED,
            response_time_ms=response_time_ms,
            error_message=error_message,
            checked_at=checked_at
        )

    @staticmethod
    def down(error_message: str, checked_at: str) -> 'ProviderHealth':
        """Create a down status."""
        return ProviderHealth(
            status=ProviderHealthStatus.DOWN,
            error_message=error_message,
            checked_at=checked_at
        )
