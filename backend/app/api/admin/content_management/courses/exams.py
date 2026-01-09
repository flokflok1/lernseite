"""
Admin Course Exams API - Bridge Module

DEPRECATED: This file is a bridge module for backward compatibility.
All functionality has been moved into the admin/courses/content/ package.

Original: 318 LOC
Refactored: admin/courses/content/exams.py (318 LOC)

Endpoints:
- GET    /api/v1/admin/courses/<course_id>/exams    - List exams
- POST   /api/v1/admin/courses/<course_id>/exams    - Create exam
- GET    /api/v1/admin/courses/exams/<exam_id>      - Get exam
- PUT    /api/v1/admin/courses/exams/<exam_id>      - Update exam
- DELETE /api/v1/admin/courses/exams/<exam_id>      - Delete exam
- POST   /api/v1/admin/courses/exams/<exam_id>/questions - Add questions
"""

# Re-export from the refactored package
from app.api.admin.content_management.courses.content.exams import *

__all__ = ['exams']
