"""
Learning Methods Admin Routing Blueprints

Centralized blueprint definitions for admin routing API.
Avoids circular imports by defining all blueprints in one place.
"""

from flask import Blueprint

# AI Setup Blueprint
lm_routing_ai_setup_bp = Blueprint(
    'lm_routing_ai_setup',
    __name__,
    url_prefix='/api/v1/admin/learning-methods/routing'
)

# Assignments Blueprint
lm_routing_assignments_bp = Blueprint(
    'lm_routing_assignments',
    __name__,
    url_prefix='/api/v1/admin/learning-methods/routing'
)

# Bulk Operations Blueprint
lm_routing_bulk_bp = Blueprint(
    'lm_routing_bulk',
    __name__,
    url_prefix='/api/v1/admin/learning-methods/routing'
)

# Overview Blueprint
lm_routing_overview_bp = Blueprint(
    'lm_routing_overview',
    __name__,
    url_prefix='/api/v1/admin/learning-methods/routing'
)

# Recommendations Blueprint
lm_routing_recommendations_bp = Blueprint(
    'lm_routing_recommendations',
    __name__,
    url_prefix='/api/v1/admin/learning-methods/routing'
)

# Auto Setup Blueprint
lm_routing_auto_setup_bp = Blueprint(
    'lm_routing_auto_setup',
    __name__,
    url_prefix='/api/v1/admin/learning-methods/routing'
)

# Resolution Blueprint
lm_routing_resolution_bp = Blueprint(
    'lm_routing_resolution',
    __name__,
    url_prefix='/api/v1/admin/learning-methods/routing'
)

# Slots Blueprint
lm_routing_slots_bp = Blueprint(
    'lm_routing_slots',
    __name__,
    url_prefix='/api/v1/admin/learning-methods/routing'
)
