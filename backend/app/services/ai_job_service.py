"""
AI Job Service Bridge - LEGACY IMPORT PATH

NOTICE: This file exists for backward compatibility only.
The actual implementation has been moved to app/services/ai/job_service.py

DEPRECATED IMPORT (old path - still works):
    from app.services.ai_job_service import AIJobService

RECOMMENDED IMPORT (new path):
    from app.services.ai.job_service import AIJobService

This bridge re-exports the AIJobService class for backward compatibility
with existing code. All new code should use the recommended import path.
"""

# Re-export from the actual location for backward compatibility
from app.services.ai.job_service import AIJobService

__all__ = ['AIJobService']
