"""AI Pricing Management

Pricing configuration and calculator for AI operations.

Blueprints:
- pricing_calculator_bp: Pricing calculator (pricing.py)
- pricing_plans_bp: Pricing plans (pricing_part2.py)

Part of: Phase 2 AI Consolidation
"""

from app.api.v1.panel.admin.ai.pricing import pricing
from app.api.v1.panel.admin.ai.pricing import pricing_part2

__all__ = ['pricing', 'pricing_part2']
