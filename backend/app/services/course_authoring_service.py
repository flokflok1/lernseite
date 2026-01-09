"""
LernsystemX Course Authoring Service - Bridge Module

This module provides backward compatibility by re-exporting from the
course_authoring package. All functionality has been refactored into
modular components for better maintainability.

For new code, import directly from:
    from app.services.course_authoring import CourseAuthoringService

Legacy imports still work:
    from app.services.course_authoring_service import CourseAuthoringService
"""

# Re-export all public API from the package
from app.services.course_authoring import (
    CourseAuthoringService,
    CourseAuthoringSession,
    CourseAuthoringError,
    get_course_authoring_service,
)

__all__ = [
    "CourseAuthoringService",
    "CourseAuthoringSession",
    "CourseAuthoringError",
    "get_course_authoring_service",
]
