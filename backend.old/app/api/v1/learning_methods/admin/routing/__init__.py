"""
Learning Methods Admin Routing Feature

AI routing subdomain - determines which AI model to use for each learning method.

Files:
- ai_setup.py: AI auto-setup operations (197 LOC)
- assignments.py: Routing assignments (291 LOC)
- bulk.py: Bulk routing operations (150 LOC)
- overview.py: Routing overview (206 LOC)
- recommendations.py: Routing recommendations (290 LOC)
- resolution.py: Routing resolution logic (98 LOC)
- slots.py: Capability slots (266 LOC)

Total: ~1498 LOC

This is a TRUE FEATURE SUBDIRECTORY (subdomain) - kept separate.
"""

from app.api.v1.learning_methods.admin.routing import (
    ai_setup,
    assignments,
    bulk,
    overview,
    recommendations,
    resolution,
    slots
)

__all__ = [
    'ai_setup',
    'assignments',
    'bulk',
    'overview',
    'recommendations',
    'resolution',
    'slots'
]
