"""
Progressive Rollout System

Enables gradual feature rollout with percentage-based, segment-based,
and organisation-based controls, including A/B testing capabilities.
"""

# Re-export from strategies
from app.core.rollout.strategies import (
    ABTestingRepository,
    ABTesting,
    PercentageRollout
)

# Re-export from targeting
from app.core.rollout.targeting import (
    OrganizationRolloutRepository,
    OrganizationRollout,
    UserSegmentsRepository,
    UserSegments
)

__all__ = [
    # Strategies
    'ABTestingRepository',
    'ABTesting',
    'PercentageRollout',

    # Targeting
    'OrganizationRolloutRepository',
    'OrganizationRollout',
    'UserSegmentsRepository',
    'UserSegments'
]
