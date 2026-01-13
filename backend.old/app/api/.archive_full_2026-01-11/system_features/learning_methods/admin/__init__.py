"""
Learning Methods Admin Package (DDD)

Admin endpoints for learning methods management.

Endpoints:
- Instances CRUD (create, read, update, delete)
- Types (get all method types)
- Operations (reorder, publish, unpublish)
- Routing (AI model assignment) - TODO
"""

from .instances import lm_instances_bp
from .types import lm_types_bp
from .operations import lm_operations_bp

__all__ = [
    'lm_instances_bp',
    'lm_types_bp',
    'lm_operations_bp'
]
