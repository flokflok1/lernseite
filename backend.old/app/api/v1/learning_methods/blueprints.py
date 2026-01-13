"""
Learning Methods Blueprints

Centralized blueprint definitions for learning methods API.
Avoids circular imports by defining all blueprints in one place.
"""

from flask import Blueprint

# Learning method operations (publish/unpublish/reorder)
lm_operations_bp = Blueprint(
    'learning_methods_operations',
    __name__,
    url_prefix='/api/v1'
)

# Learning method types
lm_types_bp = Blueprint(
    'learning_methods_types',
    __name__,
    url_prefix='/api/v1'
)
