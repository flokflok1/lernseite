"""
LernsystemX Gamification API Package

User gamification endpoints:
- GET /api/v1/gamification/me - Complete gamification data
- GET /api/v1/gamification/stats - Basic stats (XP, Level)
- GET /api/v1/gamification/skills - Skills (Strength, Intelligence, Stamina)
- GET /api/v1/gamification/achievements - User achievements

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    Final URLs: /api/v1/gamification/...
"""

from .stats import gamification_stats_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    gamification_stats_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'gamification_stats_bp',
    'ALL_BLUEPRINTS',
]
