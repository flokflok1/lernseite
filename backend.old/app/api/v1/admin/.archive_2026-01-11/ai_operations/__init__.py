"""
Admin AI Operations

Contains:
- actions.py - AI Studio Actions endpoints (Quick Actions for Course Builder)

Note: AI blueprints (jobs, models, pricing, profiles) have been moved to direct imports
      from system_features/ai in app/api/admin/__init__.py (removed proxy layer).
"""

# Import AI Studio Actions endpoints (registers routes on api_v1)
try:
    from app.api.admin.ai_operations import actions
except ImportError as e:
    print(f"Warning: AI Studio Actions import failed: {e}")
    actions = None

__all__ = ['actions']
