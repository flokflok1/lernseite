"""Admin Config API — Runner modes, LM types, system features."""

from .runner_modes import bp as runner_modes_bp
from .lm_type_compatibility import bp as lm_type_compatibility_bp
from .system_features import bp as system_features_bp

__all__ = [
    'runner_modes_bp',
    'lm_type_compatibility_bp',
    'system_features_bp',
]
