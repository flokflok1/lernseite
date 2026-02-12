"""
Shared Course Editor Utilities

Permission decorators, shared logic, and publishing workflow for Course Editor.
"""

from app.api.v1.courses.editor.shared.permissions import (
    check_course_permission,
    can_edit_course,
    can_publish_course,
    can_delete_course
)

# Import publishing workflow modules to register routes
from app.api.v1.courses.editor.shared import (
    publishing,
    publishing_decisions,
    publishing_visibility,
    publishing_queue
)

__all__ = [
    'check_course_permission',
    'can_edit_course',
    'can_publish_course',
    'can_delete_course'
]
