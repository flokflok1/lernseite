"""
Admin Courses API Package

Flat structure matching 05_Backend-Struktur.md documentation.

Modules:
- courses.py: Course CRUD operations
- chapters.py: Chapter management
- lessons.py: Lesson management
- exams.py: Exam management
- course_files.py: File attachments
- course_prompts.py: Prompt overrides
- course_authoring.py: AI-powered authoring
- course_ai_settings.py: AI settings per course
- course_analytics.py: Course analytics
- theory_sheets.py: Theory sheets for chapters and lessons
- course_publishing.py: Publishing workflow and moderation queue

All routes: /api/v1/admin/courses/*, /api/v1/admin/chapters/*, /api/v1/admin/lessons/*, /api/v1/admin/theory-sheets/*, /api/v1/admin/publishing/*
"""

# Import all route handlers (they register with api_v1 directly via decorators)
from app.api.v1.admin.courses import (
    courses,
    chapters,
    lessons,
    exams,
    course_files,
    course_prompts,
    course_authoring,
    course_ai_settings,
    course_analytics,
    theory_sheets,
    course_publishing
)

__all__ = [
    'courses',
    'chapters',
    'lessons',
    'exams',
    'course_files',
    'course_prompts',
    'course_authoring',
    'course_ai_settings',
    'course_analytics',
    'theory_sheets',
    'course_publishing'
]
