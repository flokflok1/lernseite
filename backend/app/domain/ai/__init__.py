"""
LernsystemX AI Domain Module

AI domain configuration and prompt definitions.
Business logic moved to app.application.services.content.course_authoring.
"""

# Bridge import for backward compatibility
from app.application.services.content.course_authoring.ai_generator import (
    AICourseGenerator,
    run_ai_course_generation,
)

__all__ = ['AICourseGenerator', 'run_ai_course_generation']
