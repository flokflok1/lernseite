"""
Categories Domain - Journeys Layer

Journeys organize routes by user type/flow:
- public: Public category browsing (hierarchical navigation) - 9 endpoints
- admin: Category management (CRUD, operations) - 7 endpoints

Total: 16 endpoints

Architecture: Journey-Based DDD
"""

from src.api.categories.journeys.public.api.routes import (
    categories_browse_bp,
    categories_hierarchy_bp,
)
from src.api.categories.journeys.admin.api.routes import (
    categories_admin_crud_bp,
    categories_admin_ops_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    # Public Journey (9 endpoints)
    categories_browse_bp,
    categories_hierarchy_bp,
    # Admin Journey (7 endpoints)
    categories_admin_crud_bp,
    categories_admin_ops_bp,
]

__all__ = ['ALL_JOURNEY_BLUEPRINTS']
