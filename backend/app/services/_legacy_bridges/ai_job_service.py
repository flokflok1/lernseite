"""Backward Compatibility Bridge: ai_job_service
DEPRECATED: Use 'from app.services.ai.job_service import AIJobService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.ai.job_service import AIJobService
__all__ = ['AIJobService']
