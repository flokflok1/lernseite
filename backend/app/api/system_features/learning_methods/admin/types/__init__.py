"""
Learning Method Types Admin (DDD)

Admin endpoint for learning method types.
"""

from flask import Blueprint

lm_types_bp = Blueprint(
    'lm_types',
    __name__,
    url_prefix='/api/v1/admin'
)

# Import routes
from . import endpoints

__all__ = ['lm_types_bp']
