"""
LernsystemX Dashboard API Package

DDD-structured dashboard API with clear domain separation.

Domains:
    - admin/: System dashboard analytics (admin-only)
    - user/: User-facing dashboard (layouts, widgets, recommendations)
    - core/: Shared services and business logic

Structure (DDD Pattern):
    admin/
        system_dashboard.py     ~240 lines  - System analytics (5 endpoints)
    user/
        (re-exports from existing packages)
    core/
        services.py            ~480 lines  - Centralized services
    layouts/
        endpoints.py           ~230 lines  - Layout management
    widgets/
        models.py               ~35 lines  - Pydantic models
        registry.py             ~70 lines  - Widget registry
        instances.py           ~400 lines  - Widget instances
    recommendations/
        endpoints.py           ~210 lines  - KI recommendations

All endpoints under /api/v1/dashboard/*

ISO 27001:2013 compliant - Dashboard system
DDD compliant - Domain-Driven Design
Refactored: 2026-01-08 per Developer-Guide-KI DDD pattern
"""

from flask import Blueprint

# Import domains
from .admin import admin_dashboard_bp
from .user import (
    layouts_bp,
    widgets_registry_bp,
    widgets_instances_bp,
    recommendations_bp
)

# Import core services (for internal use)
from .core import (
    DashboardLayoutService,
    DashboardWidgetService,
    DashboardRecommendationService
)

# All blueprints in this package
ALL_BLUEPRINTS = [
    # Admin domain
    admin_dashboard_bp,
    # User domain
    layouts_bp,
    widgets_registry_bp,
    widgets_instances_bp,
    recommendations_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    # Blueprints
    'admin_dashboard_bp',
    'layouts_bp',
    'widgets_registry_bp',
    'widgets_instances_bp',
    'recommendations_bp',
    'ALL_BLUEPRINTS',
    # Services
    'DashboardLayoutService',
    'DashboardWidgetService',
    'DashboardRecommendationService',
]
