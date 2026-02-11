"""
Courses API Package

Feature-based structure with role separation (Phase 3 Consolidation).

Structure:
├── admin/                   # Admin course management
│   ├── ai_settings.py      # AI configuration for courses (437 LOC)
│   └── analytics.py        # Course analytics (436 LOC)
│
├── editor/                  # Course editor (3786 LOC)
│   ├── ai/                 # AI editor (596 LOC)
│   │   ├── actions.py      # AI editor actions
│   │   └── authoring.py    # AI course authoring
│   ├── manual/             # Manual editor (2450 LOC)
│   │   ├── chapters.py     # Chapter management
│   │   ├── course_files.py # Course file management
│   │   ├── course_prompts.py # Course prompts
│   │   ├── courses.py      # Course management
│   │   ├── exams.py        # Exam management
│   │   ├── lessons.py      # Lesson management
│   │   └── theory_sheets.py # Theory sheet management
│   └── shared/             # Shared editor services (914 LOC)
│       ├── permissions.py  # Editor permissions
│       ├── publishing_decisions.py # Publishing decisions
│       ├── publishing.py   # Publishing logic
│       ├── publishing_queue.py # Publishing queue
│       └── publishing_visibility.py # Visibility settings
│
└── public/                  # Public course endpoints (862 LOC)
    ├── core.py             # Core course operations
    ├── crud.py             # Course CRUD
    ├── enrollment.py       # Course enrollment
    └── publishing.py       # Course publishing

Consolidated from:
- api/v1/admin/courses/ → courses/admin/
- api/v1/course_editor/ → courses/editor/
- api/v1/courses/*.py → courses/public/*.py

Total: ~5570 LOC in organized feature-based structure

All routes:
- /api/v1/courses/* (public - unchanged)
- /api/v1/course-editor/* (editor - unchanged)
- /api/v1/admin/courses/* (admin - unchanged)

Part of: Phase 3 Courses Consolidation (Feature-based structure)
"""

from app.api.v1.courses import admin, editor, public

__all__ = ['admin', 'editor', 'public']
