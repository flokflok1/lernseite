"""
LernsystemX Organisations API Package (DDD Refactored)

Organisation management with Domain-Driven Design (DDD) architecture.

DDD Components (core/):
    - OrganisationFactory: Factory pattern for entity creation
    - OrganisationService: Business logic orchestration
    - OrgType, MemberRole, BillingModel: Value objects with domain rules

Structure:
    admin/          - Admin-only endpoints (CRUD, member management)
    user/           - User-facing endpoints (my org, my stats)
    core/           - Domain logic (Factory, Service, Value Objects)
    analytics/      - Advanced analytics (time series, reports)

Modules:
    - core/factory.py: Create organisations with business rules
    - core/services.py: Business logic (ownership transfer, upgrades, etc.)
    - core/value_objects.py: OrgType, MemberRole, BillingModel
    - admin/crud.py: List, create, get, update (admin only)
    - admin/members.py: Member management (admin only)
    - user/my_organisation.py: Current user's organisation
    - user/stats.py: Organisation statistics for members
    - analytics/time_series.py: Time series analytics
    - analytics/reports.py: Top reports

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    When this package is imported, blueprints are auto-registered on api_v1.
    Final URLs: /api/v1/organisations/...

Endpoints (11 total):
    Admin:
        GET    /api/v1/organisations              - List organisations (admin only)
        POST   /api/v1/organisations              - Create organisation (admin only)
        GET    /api/v1/organisations/<id>         - Get organisation details
        PUT    /api/v1/organisations/<id>         - Update organisation
        GET    /api/v1/organisations/<id>/users   - List organisation users
        POST   /api/v1/organisations/<id>/assign-user - Assign user to organisation
    User:
        GET    /api/v1/organisations/my           - Get current user's organisation
        GET    /api/v1/organisations/my/stats     - Get stats for current user's org
    Analytics:
        GET    /api/v1/organisations/<id>/analytics/events/time-series
        GET    /api/v1/organisations/<id>/analytics/active-members/time-series
        GET    /api/v1/organisations/<id>/analytics/top-courses

ISO 27001:2013 compliant - Multi-tenant organisation management with DDD

Refactored: 2026-01-07 per Developer-Guide-KI Section 10
DDD Refactored: 2026-01-08 - Added Factory, Service, Value Objects
"""

from .admin.crud import organisations_core_bp
from .admin.members import organisations_members_bp
from .analytics.stats import organisations_stats_bp
from .analytics.time_series import time_series_bp
from .analytics.reports import reports_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    organisations_core_bp,
    organisations_members_bp,
    organisations_stats_bp,
    time_series_bp,
    reports_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/api/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export DDD components
from .core import (
    OrganisationFactory,
    OrganisationService,
    OrgType,
    MemberRole,
    BillingModel
)

# Export all blueprints and DDD components for direct import
__all__ = [
    # Blueprints
    'organisations_core_bp',
    'organisations_members_bp',
    'organisations_stats_bp',
    'time_series_bp',
    'reports_bp',
    'ALL_BLUEPRINTS',
    # DDD Components
    'OrganisationFactory',
    'OrganisationService',
    'OrgType',
    'MemberRole',
    'BillingModel',
]
