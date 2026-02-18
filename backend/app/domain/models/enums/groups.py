"""
Group domain enumerations (GBA 2.0)
"""

from enum import Enum


class GroupTemplate(str, Enum):
    """Predefined group templates"""
    PARENT = 'parent'
    ENTERPRISE_ADMIN = 'enterprise_admin'
    AUDITOR = 'auditor'
    LIBRARIAN = 'librarian'
    COURSE_MANAGER = 'course_manager'
