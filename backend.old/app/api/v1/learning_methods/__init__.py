"""
Learning Methods API Package

Feature-based structure (flattened role-based, kept feature subdirectories):

**Flat files (from role-based structure):**
- admin_instances_crud.py: Learning method instance CRUD (374 LOC)
  - From admin/instances/crud.py

- admin_management.py: Admin learning method management (310 LOC)
  - From admin/management.py

- admin_operations_reorder.py: Reordering operations (121 LOC)
  - From admin/operations/reorder.py

- admin_operations_status.py: Status operations (194 LOC)
  - From admin/operations/status.py

- admin_types_endpoints.py: Learning method types endpoints (80 LOC)
  - From admin/types/endpoints.py

- factory.py: Learning method factory (182 LOC)
  - From core/factory.py

- services.py: Learning method services (206 LOC)
  - From core/services.py

- value_objects.py: Value object definitions (157 LOC)
  - From core/value_objects.py

- public_catalog.py: Public learning method catalog (246 LOC)
  - From public/catalog.py

**Feature subdirectories (TRUE FEATURES/SUBDOMAINS - kept separate):**
- admin/routing/: AI routing subdomain (7 files, ~1498 LOC)
  - AI model assignment and resolution for learning methods
  - ai_setup, assignments, bulk, overview, recommendations, resolution, slots

- core/routing/: Routing domain logic (4 files, ~888 LOC)
  - events, factory, services, value_objects

- execution/: Execution engine (2 files, 453 LOC)
  - runner, validator

Total: 4709 LOC (flat files: 1870 LOC, feature subdirs: 2839 LOC)

Architecture Pattern:
- Role-based subdirectories (admin/instances, admin/operations, etc.) → Flattened
- Feature subdirectories (admin/routing, core/routing, execution) → Kept

Domain: Learning Methods (12 Content-LMs LM00-LM11)
Subdomain: Routing (AI Model Assignment)

All routes: /api/v1/learning-methods/*
"""

# Import blueprints first to avoid circular imports
from app.api.v1.learning_methods.blueprints import lm_operations_bp, lm_types_bp

# Import all admin endpoints
from app.api.v1.learning_methods.admin_instances_crud import lm_instances_bp
from app.api.v1.learning_methods import (
    admin_management,
    admin_operations_reorder,
    admin_operations_status,
    admin_types_endpoints,
)

# Import domain logic (factory, services, value_objects)
from app.api.v1.learning_methods import factory, services, value_objects

# Import public endpoints
from app.api.v1.learning_methods import public_catalog
from app.api.v1.learning_methods.public_catalog import lm_public_bp

# Import admin management blueprint
from app.api.v1.learning_methods.admin_management import lm_admin_bp

# Import subdomain packages
from app.api.v1.learning_methods.admin import routing as admin_routing
from app.api.v1.learning_methods.core import routing as core_routing
from app.api.v1.learning_methods import execution

# All blueprints to register
ALL_BLUEPRINTS = [
    lm_instances_bp,      # Admin: Instances CRUD
    lm_operations_bp,     # Admin: Operations (publish/unpublish/reorder)
    lm_types_bp,          # Admin: Types
    lm_admin_bp,          # Admin: Management
    lm_public_bp,         # Public: Catalog
]

# Register all blueprints to api_v1
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)

# Also register routing sub-blueprints if they exist
if hasattr(admin_routing, 'ALL_BLUEPRINTS'):
    for bp in admin_routing.ALL_BLUEPRINTS:
        api_v1.register_blueprint(bp)

if hasattr(core_routing, 'ALL_BLUEPRINTS'):
    for bp in core_routing.ALL_BLUEPRINTS:
        api_v1.register_blueprint(bp)

__all__ = [
    # Blueprints
    'lm_instances_bp',
    'lm_operations_bp',
    'lm_types_bp',
    'lm_admin_bp',
    'lm_public_bp',
    'ALL_BLUEPRINTS',
    # Modules
    'admin_management',
    'admin_operations_reorder',
    'admin_operations_status',
    'admin_types_endpoints',
    'factory',
    'services',
    'value_objects',
    'public_catalog',
    'admin_routing',
    'core_routing',
    'execution'
]
