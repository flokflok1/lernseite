"""
Admin Course Files API - Bridge Module

DEPRECATED: This file is a bridge module for backward compatibility.
All functionality has been moved into the admin/courses/management/ package.

Original: 346 LOC
Refactored: admin/courses/management/files.py (346 LOC)
"""

from app.api.admin.content_management.courses.management.files import *

__all__ = ['files']
