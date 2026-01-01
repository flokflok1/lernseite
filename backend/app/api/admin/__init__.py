"""
LernsystemX Admin API Module

Split from admin_courses.py for better maintainability.
All routes remain at /api/v1/admin/...

Modules:
- courses: Course CRUD operations (7 endpoints)
- chapters: Chapter management (5 endpoints)
- lessons: Lesson management (5 endpoints)
- ai_jobs: AI job management (4 endpoints)
- exams: Exam management (6 endpoints)
- course_prompts: Course-specific prompt overrides (6 endpoints)
- course_files: Course file attachments (7 endpoints)

Total: 40 endpoints (from original admin_courses.py 3624 lines)
Refactored: 2025-12-29 per Developer-Guide-KI Section 9
"""

# Import all route modules to register them with Flask
# Each module registers its routes with api_v1 blueprint
from app.api.admin import courses
from app.api.admin import chapters
from app.api.admin import lessons
from app.api.admin import ai_jobs
from app.api.admin import exams
from app.api.admin import course_prompts
from app.api.admin import course_files

__all__ = [
    'courses',
    'chapters',
    'lessons',
    'ai_jobs',
    'exams',
    'course_prompts',
    'course_files'
]
