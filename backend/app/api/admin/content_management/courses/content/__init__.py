"""
Admin Course Content Management Package

Content CRUD operations for chapters, lessons, and exams.

Modules:
- chapters.py: Chapter management (5 endpoints, 200 LOC)
- lessons.py: Lesson management (5 endpoints, 228 LOC)
- exams.py: Exam management (6 endpoints, 318 LOC)

Endpoints (all under /api/v1/admin/courses/):
Chapters:
- GET    /<course_id>/chapters     - List chapters
- POST   /<course_id>/chapters     - Create chapter
- PUT    /chapters/<chapter_id>    - Update chapter
- DELETE /chapters/<chapter_id>    - Delete chapter
- PUT    /chapters/<chapter_id>/reorder - Reorder chapters

Lessons:
- GET    /chapters/<chapter_id>/lessons - List lessons
- POST   /chapters/<chapter_id>/lessons - Create lesson
- PUT    /lessons/<lesson_id>           - Update lesson
- DELETE /lessons/<lesson_id>           - Delete lesson
- PUT    /lessons/<lesson_id>/reorder   - Reorder lessons

Exams:
- GET    /<course_id>/exams         - List exams
- POST   /<course_id>/exams         - Create exam
- GET    /exams/<exam_id>            - Get exam
- PUT    /exams/<exam_id>            - Update exam
- DELETE /exams/<exam_id>            - Delete exam
- POST   /exams/<exam_id>/questions - Add questions

Refactored: 2026-01-08 per Developer-Guide-KI Section 10
Original: 3 separate files (746 LOC) → 3 modules in content/ (746 LOC)
"""

# Re-export from modules for backward compatibility
from app.api.admin.content_management.courses.content import chapters, lessons, exams

__all__ = ['chapters', 'lessons', 'exams']
