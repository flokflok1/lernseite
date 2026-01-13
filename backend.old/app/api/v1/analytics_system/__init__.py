"""
Analytics System API Package

Feature-based structure (flattened from admin/core/user structure):
- admin_time_series.py: Time series analytics (188 LOC)
  - From admin/time_series.py

- admin_rankings.py: Rankings and leaderboards (234 LOC)
  - From admin/rankings.py

- metrics.py: Core metrics definitions (195 LOC)
  - From core/metrics.py

- services.py: Analytics services (116 LOC)
  - From core/services.py

- factory.py: Analytics object factory (155 LOC)
  - From core/factory.py

- value_objects.py: Value object definitions (169 LOC)
  - From core/value_objects.py

- user_tracking.py: User analytics tracking (272 LOC)
  - From user/tracking.py

Total: 1329 LOC across 7 feature files

All routes: /api/v1/analytics/*
"""

# Import blueprints first to avoid circular imports
from app.api.v1.analytics_system.blueprints import analytics_time_series_bp

# Import domain logic (factory, services, value_objects, metrics)
from app.api.v1.analytics_system import (
    factory,
    services,
    value_objects,
    metrics
)

# Import endpoint modules
from app.api.v1.analytics_system import (
    admin_time_series,
    admin_rankings,
    user_tracking
)

# All blueprints to register
ALL_BLUEPRINTS = [
    analytics_time_series_bp
]

# Register all blueprints to api_v1
from app.api import api_v1
for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)

__all__ = [
    'admin_time_series',
    'admin_rankings',
    'metrics',
    'services',
    'factory',
    'value_objects',
    'user_tracking',
    'analytics_time_series_bp',
    'ALL_BLUEPRINTS'
]
