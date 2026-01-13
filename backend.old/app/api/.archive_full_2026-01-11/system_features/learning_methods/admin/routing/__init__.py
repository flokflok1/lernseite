"""
Routing Admin Endpoints (DDD)

AI model assignment and routing configuration for learning methods.

Blueprints:
- lm_routing_overview_bp: Overview, unconfigured, requirements
- lm_routing_resolution_bp: Model resolution testing
- lm_routing_assignments_bp: CRUD for individual LM assignments
- lm_routing_bulk_bp: Bulk operations
- lm_routing_recommendations_bp: Model recommendations
- lm_routing_auto_setup_bp: Auto-setup with recommendations
- lm_routing_ai_setup_bp: AI-powered auto-setup
- lm_routing_slots_bp: Capability slot management

URL Prefix: /api/v1/admin/learning-methods/routing
"""

from flask import Blueprint

# Define all blueprints
lm_routing_overview_bp = Blueprint(
    'lm_routing_overview',
    __name__,
    url_prefix='/admin/learning-methods/routing'
)

lm_routing_resolution_bp = Blueprint(
    'lm_routing_resolution',
    __name__,
    url_prefix='/admin/learning-methods/routing'
)

lm_routing_assignments_bp = Blueprint(
    'lm_routing_assignments',
    __name__,
    url_prefix='/admin/learning-methods/routing'
)

lm_routing_bulk_bp = Blueprint(
    'lm_routing_bulk',
    __name__,
    url_prefix='/admin/learning-methods/routing'
)

lm_routing_recommendations_bp = Blueprint(
    'lm_routing_recommendations',
    __name__,
    url_prefix='/admin/learning-methods/routing'
)

lm_routing_auto_setup_bp = Blueprint(
    'lm_routing_auto_setup',
    __name__,
    url_prefix='/admin/learning-methods/routing'
)

lm_routing_ai_setup_bp = Blueprint(
    'lm_routing_ai_setup',
    __name__,
    url_prefix='/admin/learning-methods/routing'
)

lm_routing_slots_bp = Blueprint(
    'lm_routing_slots',
    __name__,
    url_prefix='/admin/learning-methods/routing'
)

# Import route handlers (registers endpoints with blueprints)
from . import (
    overview,
    resolution,
    assignments,
    bulk,
    recommendations,
    ai_setup,
    slots
)

# Export all blueprints
__all__ = [
    'lm_routing_overview_bp',
    'lm_routing_resolution_bp',
    'lm_routing_assignments_bp',
    'lm_routing_bulk_bp',
    'lm_routing_recommendations_bp',
    'lm_routing_auto_setup_bp',
    'lm_routing_ai_setup_bp',
    'lm_routing_slots_bp'
]
