"""
Admin Course CRUD API - Bridge Module

DEPRECATED: This file is a bridge module for backward compatibility.
All functionality has been moved into the admin/courses/management/ package.

Original: 329 LOC
Refactored: admin/courses/management/crud.py (329 LOC)
"""

from app.api.admin.content_management.courses.management.crud import *

__all__ = ['crud']
