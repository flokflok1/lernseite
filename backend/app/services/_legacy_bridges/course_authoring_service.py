"""Backward Compatibility Bridge: course_authoring_service
DEPRECATED: Use 'from app.services.course_authoring.session import CourseAuthoringService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.course_authoring.session import CourseAuthoringService
__all__ = ['CourseAuthoringService']
