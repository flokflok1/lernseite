"""
Admin Course Management Package

Course management operations: CRUD, files, prompts.

Modules:
- crud.py: Course CRUD operations (13K LOC, 329 lines)
- files.py: File attachments (14K LOC, 346 lines)
- prompts.py: Prompt overrides (11K LOC, 302 lines)

Endpoints (all under /api/v1/admin/courses/):
CRUD:
- GET    /courses             - List courses
- POST   /courses             - Create course
- GET    /courses/<course_id> - Get course
- PUT    /courses/<course_id> - Update course
- DELETE /courses/<course_id> - Delete course
- POST   /courses/<course_id>/publish - Publish course
- POST   /courses/<course_id>/clone   - Clone course

Files:
- GET    /<course_id>/files      - List files
- POST   /<course_id>/files      - Upload file
- GET    /files/<file_id>        - Get file
- DELETE /files/<file_id>        - Delete file
- GET    /files/<file_id>/preview - Preview file

Prompts:
- GET    /<course_id>/prompts    - List prompt overrides
- POST   /<course_id>/prompts    - Create override
- PUT    /prompts/<prompt_id>    - Update override
- DELETE /prompts/<prompt_id>    - Delete override
- POST   /<course_id>/prompts/reset - Reset to defaults

Refactored: 2026-01-08 per Developer-Guide-KI Section 10
Original: 3 files (~1000 LOC) → 3 modules in management/ (~1000 LOC)
"""

from app.api.admin.content_management.courses.management import crud, files, prompts

__all__ = ['crud', 'files', 'prompts']
