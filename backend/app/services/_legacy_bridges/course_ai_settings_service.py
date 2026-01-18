"""Backward Compatibility Bridge: course_ai_settings_service
DEPRECATED: Use 'from app.services.ai.course_settings import CourseAiSettingsService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.ai.course_settings import CourseAiSettingsService
__all__ = ['CourseAiSettingsService']
