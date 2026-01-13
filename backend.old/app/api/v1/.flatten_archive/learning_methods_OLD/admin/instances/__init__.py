"""
Learning Method Instances Admin (DDD)

Admin endpoints for learning method instance CRUD.
"""

from flask import Blueprint

lm_instances_bp = Blueprint(
    'lm_instances',
    __name__,
    url_prefix='/api/v1/admin'
)

# Import routes
from . import crud

__all__ = ['lm_instances_bp']
