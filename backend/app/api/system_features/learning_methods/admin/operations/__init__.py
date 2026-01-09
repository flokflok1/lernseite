"""
Learning Method Operations Admin (DDD)

Admin endpoints for reorder, publish, unpublish operations.
"""

from flask import Blueprint

lm_operations_bp = Blueprint(
    'lm_operations',
    __name__,
    url_prefix='/api/v1/admin'
)

# Import routes
from . import reorder, status

__all__ = ['lm_operations_bp']
