"""
Admin Settings Package

Contains all admin settings modules:
- ai: AI configuration (providers, models, jobs, pricing, profiles)
- system: System settings (environment, maintenance, monitoring)
- permissions: Roles & permission thresholds
- feature_flags: Feature flag management

All blueprints are auto-registered on import.
"""

# Import subpackages to trigger blueprint registration
from . import ai, permissions, feature_flags

__all__ = ['ai', 'permissions', 'feature_flags']
