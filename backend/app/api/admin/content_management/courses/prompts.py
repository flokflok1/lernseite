"""
Admin Course Prompts API - Bridge Module

DEPRECATED: This file is a bridge module for backward compatibility.
All functionality has been moved into the admin/courses/management/ package.

Original: 302 LOC
Refactored: admin/courses/management/prompts.py (302 LOC)
"""

from app.api.admin.content_management.courses.management.prompts import *

__all__ = ['prompts']
