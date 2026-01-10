"""
AI Jobs Admin Package (DDD)

Endpoints for AI job management using DDD patterns:
- Uses AIJobFactory for job creation
- Publishes AIJobCompletedEvent, AIJobCancelledEvent
- Uses Repository Pattern for persistence

Job Lifecycle:
    pending → processing → completed/failed/cancelled

Blueprints:
    - jobs_creation_bp: Job creation and submission
    - jobs_management_bp: Status tracking, cancellation
    - jobs_finalization_bp: Job completion and course creation
"""

from .creation import jobs_creation_bp
from .management import jobs_management_bp
from .finalization import jobs_finalization_bp

__all__ = [
    'jobs_creation_bp',
    'jobs_management_bp',
    'jobs_finalization_bp'
]
