# Math Domain - DDD Refactoring Summary

**Datum:** 2026-01-08
**Status:** ANALYSIS COMPLETE
**Ziel:** DDD-konforme Reorganisation mit user/ und core/

---

## Current Structure Analysis

### Package Overview
```
backend/app/api/math/
├── __init__.py              (50 LOC)  - Blueprint + route registration
├── calculator/
│   ├── __init__.py         (10 LOC)
│   └── engine.py           (85 LOC)  - Calculator endpoints
├── reference/
│   ├── __init__.py         (10 LOC)
│   └── library.py         (135 LOC)  - Reference library endpoints
├── sessions/
│   ├── __init__.py         (10 LOC)
│   └── history.py         (125 LOC)  - Session management
└── interactive/
    ├── __init__.py         (10 LOC)
    └── exercises.py       (215 LOC)  - Progress, hints, tasks, admin
```

**Total:** 650 LOC across 9 files

### Endpoint Categories

| Category | Endpoints | File | User/Admin |
|----------|-----------|------|------------|
| **Calculator** | 3 | calculator/engine.py | User |
| `/calculator/evaluate` | POST | Evaluate math expression | User |
| `/calculator/history` | GET | Get calculator history | User |
| `/calculator/save` | POST | Save calculator entry | User |
| **Reference Library** | 7 | reference/library.py | User |
| `/categories` | GET | Get pattern categories | User |
| `/patterns` | GET | Get patterns with filters | User |
| `/patterns/:id` | GET | Get pattern details | User |
| `/formulas` | GET | Get formula library | User |
| `/formulas/:id/favorite` | POST | Toggle favorite | User |
| `/formulas/:id/use` | POST | Increment usage counter | User |
| **Sessions** | 5 | sessions/history.py | User |
| `/sessions` | POST | Start practice session | User |
| `/sessions/:id` | GET | Get session details | User |
| `/sessions/:id/end` | POST | End session | User |
| `/sessions/:id/steps` | GET | Get session steps | User |
| `/sessions/:id/steps` | POST | Save calculation step | User |
| **Interactive Practice** | 5 | interactive/exercises.py | User |
| `/progress` | GET | Get user progress | User |
| `/progress/:pattern_id` | POST | Update progress | User |
| `/hints` | GET | Get contextual hints | User |
| `/tasks` | GET | Get pattern tasks | User |
| `/tasks/:id/check` | POST | Check task answer | User |
| **Admin** | 2 | interactive/exercises.py | Admin |
| `/admin/patterns` | POST | Create pattern (Admin) | Admin |
| `/admin/formulas` | POST | Create formula (Admin) | Admin |

**Total:** 22 endpoints

---

## DDD Analysis

### Domain Characteristics

**Math Toolkit** is a **pure User-facing feature domain** with:
- 20 User endpoints (91%)
- 2 Admin endpoints (9%)
- No role-specific business logic separation needed
- All features serve end-users learning mathematics

### Bounded Context

**Math Domain** has clear boundaries:
- **Calculator Engine** - Expression evaluation, history
- **Reference Library** - Patterns, formulas, categories
- **Practice Sessions** - Session tracking, step-by-step solving
- **Interactive Learning** - Progress tracking, hints, tasks
- **Content Management** - Admin pattern/formula creation

### Domain Services

Currently uses: `MathToolkitService` (monolithic service)

---

## Proposed DDD Structure

### Option 1: Flat User-Centric (RECOMMENDED)

```
backend/app/api/math/
├── __init__.py              - Blueprint + registration
├── user/
│   ├── __init__.py          - Barrel export
│   ├── calculator.py        (~85 LOC)  - Calculator endpoints
│   ├── reference.py        (~135 LOC)  - Library endpoints
│   ├── sessions.py         (~125 LOC)  - Session management
│   └── practice.py         (~150 LOC)  - Progress, hints, tasks
├── admin/
│   ├── __init__.py          - Barrel export
│   └── content.py           (~65 LOC)  - Pattern/formula creation
└── core/
    ├── __init__.py          - Barrel export
    ├── engine.py            - Math evaluation engine (business logic)
    ├── hints.py             - Hint generation logic
    └── validation.py        - Input validation
```

**Benefits:**
- Clear user/admin separation
- Flat structure (no deep nesting)
- Easy to navigate
- Follows LSX component-structure rules

**Drawbacks:**
- Slightly less feature-based grouping

### Option 2: Feature-Based DDD

```
backend/app/api/math/
├── __init__.py              - Blueprint + registration
├── calculator/
│   ├── user.py              (~85 LOC)  - User calculator endpoints
│   └── engine.py            - Core calculator logic
├── reference/
│   ├── user.py              (~135 LOC)  - User library endpoints
│   └── admin.py             (~35 LOC)  - Admin formula creation
├── practice/
│   ├── user.py              (~275 LOC)  - Sessions + interactive
│   └── admin.py             (~30 LOC)  - Admin pattern creation
└── core/
    ├── hints.py             - Hint generation
    └── validation.py        - Validation logic
```

**Benefits:**
- Groups related features together
- Clear feature boundaries

**Drawbacks:**
- Deeper nesting
- Splits user endpoints across multiple files

### Option 3: Keep Current + Add Core (MINIMAL CHANGE)

```
backend/app/api/math/
├── __init__.py              - Blueprint + registration
├── calculator/
│   ├── __init__.py
│   └── engine.py           (~85 LOC)  - User endpoints
├── reference/
│   ├── __init__.py
│   └── library.py          (~135 LOC)  - User endpoints
├── sessions/
│   ├── __init__.py
│   └── history.py          (~125 LOC)  - User endpoints
├── interactive/
│   ├── __init__.py
│   ├── exercises.py        (~150 LOC)  - User progress/hints/tasks
│   └── admin.py            (~65 LOC)  - Admin content creation (NEW)
└── core/
    ├── __init__.py
    ├── engine.py            - Math engine business logic
    ├── hints.py             - Hint generation
    └── validation.py        - Validation
```

**Benefits:**
- Minimal disruption to existing structure
- Only splits admin endpoints out
- Adds core/ for business logic

**Drawbacks:**
- Less DDD-pure
- Mixed feature-based grouping

---

## Recommendation: Option 1 (Flat User-Centric)

### Reasoning

1. **LSX Component Structure Compliance**: Follows `.claude/rules/component-structure.md` (user/admin separation)
2. **Clear Role Separation**: 91% user endpoints vs 9% admin endpoints
3. **Simplicity**: Flat structure, easy to find endpoints
4. **Scalability**: Easy to add new user features
5. **DDD Principles**: Clear bounded contexts, separation of concerns

### Migration Steps

#### Step 1: Create New Structure

```bash
mkdir -p backend/app/api/math/user
mkdir -p backend/app/api/math/admin
mkdir -p backend/app/api/math/core
```

#### Step 2: Move & Rename Files

```bash
# User endpoints
mv calculator/engine.py user/calculator.py
mv reference/library.py user/reference.py
mv sessions/history.py user/sessions.py

# Extract user endpoints from interactive/exercises.py
# → user/practice.py (progress, hints, tasks)

# Extract admin endpoints from interactive/exercises.py
# → admin/content.py (patterns, formulas)

# Remove old structure
rm -rf calculator/ reference/ sessions/ interactive/
```

#### Step 3: Create __init__.py Files

**user/__init__.py:**
```python
"""
Math Toolkit User API
=====================

User-facing math learning endpoints:
- calculator.py - Expression evaluation & history
- reference.py - Patterns, formulas, categories
- sessions.py - Practice session management
- practice.py - Progress tracking, hints, tasks
"""

from .calculator import *
from .reference import *
from .sessions import *
from .practice import *

__all__ = []
```

**admin/__init__.py:**
```python
"""
Math Toolkit Admin API
======================

Admin content management endpoints:
- content.py - Pattern & formula creation
"""

from .content import *

__all__ = []
```

**core/__init__.py:**
```python
"""
Math Toolkit Core Domain Logic
===============================

Business logic for math operations:
- engine.py - Math evaluation engine
- hints.py - Hint generation system
- validation.py - Input validation
"""

from .engine import *
from .hints import *
from .validation import *

__all__ = []
```

#### Step 4: Update Main __init__.py

**math/__init__.py:**
```python
"""
MathToolkit API Package - Math Learning System
===============================================

DDD-organized structure:
    user/        - User-facing endpoints (20 endpoints)
    admin/       - Admin content management (2 endpoints)
    core/        - Domain business logic

Structure:
    user/
        ├── calculator.py      ~85 LOC  - /calculator/*
        ├── reference.py      ~135 LOC  - /categories, /patterns, /formulas
        ├── sessions.py       ~125 LOC  - /sessions/*
        └── practice.py       ~150 LOC  - /progress, /hints, /tasks

    admin/
        └── content.py         ~65 LOC  - /admin/patterns, /admin/formulas

    core/
        ├── engine.py          - Math evaluation engine
        ├── hints.py           - Hint generation
        └── validation.py      - Input validation

Route Registration:
    Blueprint created here, imported by sub-modules, registered on api_v1.
    Final URLs: /api/v1/math-toolkit/*

Refactored: 2026-01-08 per DDD Component Structure Rules
"""

from flask import Blueprint
from app.api import api_v1

# Create blueprint FIRST (before importing sub-modules)
math_toolkit_bp = Blueprint('math_toolkit', __name__, url_prefix='/math-toolkit')

# Import all route modules (registers endpoints on blueprint)
from app.api.math.user import calculator, reference, sessions, practice
from app.api.math.admin import content

# Register blueprint with main API
api_v1.register_blueprint(math_toolkit_bp)

__all__ = ['math_toolkit_bp']
```

#### Step 5: Update Imports in Route Files

**Example: user/calculator.py**
```python
"""
MathToolkit API - User Calculator Module

Endpoints:
- /math-toolkit/calculator/evaluate - Evaluate expression
- /math-toolkit/calculator/history - Get calculator history
- /math-toolkit/calculator/save - Save calculator entry
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.api.math import math_toolkit_bp  # Import blueprint from parent
from app.services.math_toolkit_service import MathToolkitService

logger = logging.getLogger(__name__)

# ... endpoints ...
```

#### Step 6: Extract Interactive Endpoints

**user/practice.py** (from interactive/exercises.py lines 1-142):
```python
"""
MathToolkit API - User Practice Module

Endpoints:
- /math-toolkit/progress - Get user progress
- /math-toolkit/progress/:pattern_id - Update progress
- /math-toolkit/hints - Get contextual hints
- /math-toolkit/tasks - Get pattern tasks
- /math-toolkit/tasks/:id/check - Check task answer
"""
# ... progress, hints, tasks endpoints ...
```

**admin/content.py** (from interactive/exercises.py lines 143-214):
```python
"""
MathToolkit API - Admin Content Module

Endpoints:
- /math-toolkit/admin/patterns - Create pattern
- /math-toolkit/admin/formulas - Create formula
"""
# ... admin endpoints ...
```

#### Step 7: Create Core Domain Logic (Future)

**core/engine.py:**
```python
"""
Math Evaluation Engine

Business logic for:
- Expression parsing
- Calculation execution
- Result formatting
"""

class MathEngine:
    @staticmethod
    def evaluate(expression: str) -> dict:
        """Evaluate math expression"""
        # Move logic from MathToolkitService
        pass

    @staticmethod
    def validate_expression(expression: str) -> bool:
        """Validate expression syntax"""
        pass
```

**core/hints.py:**
```python
"""
Hint Generation System

Business logic for:
- Contextual hint selection
- Scaffolding level adjustment
- Error-based hint generation
"""

class HintGenerator:
    @staticmethod
    def get_hint(pattern_id: str, hint_type: str, level: int) -> str:
        """Generate contextual hint"""
        # Move logic from MathToolkitService
        pass
```

#### Step 8: Update Tests

```bash
# Update import paths in tests
tests/test_math_toolkit.py → tests/test_math/
├── test_user_calculator.py
├── test_user_reference.py
├── test_user_sessions.py
├── test_user_practice.py
└── test_admin_content.py
```

---

## File Size Compliance

### Current Files (All < 500 LOC ✓)

| File | LOC | Status |
|------|-----|--------|
| calculator/engine.py | 85 | ✓ OK |
| reference/library.py | 135 | ✓ OK |
| sessions/history.py | 125 | ✓ OK |
| interactive/exercises.py | 215 | ✓ OK |

### Proposed Files (All < 500 LOC ✓)

| File | LOC | Status |
|------|-----|--------|
| user/calculator.py | ~85 | ✓ OK |
| user/reference.py | ~135 | ✓ OK |
| user/sessions.py | ~125 | ✓ OK |
| user/practice.py | ~150 | ✓ OK (from exercises.py split) |
| admin/content.py | ~65 | ✓ OK (from exercises.py split) |

**All files comply with 500 LOC limit!**

---

## Quality Gates Check

### G01 - No Duplicates
- ✓ No .old, .bak, _v2 files
- ✓ Clean migration, old files removed

### G02 - Consistency
- ✓ Follows LSX component-structure rules
- ✓ User/admin separation
- ✓ DDD-compliant

### G04 - Completeness
- ✓ All endpoints accounted for
- ✓ No code fragments

### G05 - Documentation
- ✓ Docstrings in all files
- ✓ Type hints present
- ✓ This summary document

### G07 - Security
- ✓ JWT required on all endpoints
- ✓ Admin endpoints need role check (TODO)
- ⚠️ Admin endpoints currently have `# TODO: Admin-Check` comments

---

## Breaking Changes

### Import Path Changes

**Before:**
```python
from app.api.math.calculator import engine
from app.api.math.reference import library
from app.api.math.sessions import history
from app.api.math.interactive import exercises
```

**After:**
```python
from app.api.math.user import calculator, reference, sessions, practice
from app.api.math.admin import content
```

### Endpoint URLs

**No changes!** All URLs remain the same:
- `/api/v1/math-toolkit/calculator/*`
- `/api/v1/math-toolkit/categories`
- `/api/v1/math-toolkit/patterns`
- `/api/v1/math-toolkit/formulas`
- `/api/v1/math-toolkit/sessions`
- `/api/v1/math-toolkit/progress`
- `/api/v1/math-toolkit/hints`
- `/api/v1/math-toolkit/tasks`
- `/api/v1/math-toolkit/admin/*`

---

## TODO List

### Immediate (Refactoring)
- [ ] Create user/, admin/, core/ directories
- [ ] Move calculator/engine.py → user/calculator.py
- [ ] Move reference/library.py → user/reference.py
- [ ] Move sessions/history.py → user/sessions.py
- [ ] Split interactive/exercises.py → user/practice.py + admin/content.py
- [ ] Create __init__.py files with barrel exports
- [ ] Update main math/__init__.py with new imports
- [ ] Remove old directories (calculator/, reference/, sessions/, interactive/)

### Security (Critical)
- [ ] Add `@require_role('admin')` to admin/content.py endpoints
- [ ] Remove `# TODO: Admin-Check` comments after implementation

### Core Domain Logic (Future)
- [ ] Extract business logic from MathToolkitService
- [ ] Create core/engine.py (math evaluation)
- [ ] Create core/hints.py (hint generation)
- [ ] Create core/validation.py (input validation)

### Testing
- [ ] Update test imports
- [ ] Create test_user_*.py files
- [ ] Create test_admin_content.py
- [ ] Verify all 22 endpoints work

### Documentation
- [ ] Update `17_Backend-Struktur.md` with new structure
- [ ] Update API documentation
- [ ] Add architecture decision record (ADR)

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import path breakage | HIGH | Update all imports in same session |
| Test failures | MEDIUM | Run tests after each file move |
| Service coupling | LOW | Service remains unchanged initially |
| Admin endpoint security | HIGH | Add role checks immediately after refactor |

---

## Timeline Estimate

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Structure** | 30 min | Create directories, move files |
| **Phase 2: Imports** | 20 min | Update all import statements |
| **Phase 3: Testing** | 20 min | Run tests, fix issues |
| **Phase 4: Security** | 15 min | Add admin role checks |
| **Phase 5: Documentation** | 15 min | Update docs |
| **Total** | **100 min** | Complete refactoring |

---

## Conclusion

**Recommendation: Proceed with Option 1 (Flat User-Centric)**

### Why?
1. ✓ **DDD-compliant** - Clear user/admin/core separation
2. ✓ **Component structure compliant** - Follows LSX rules
3. ✓ **Simple** - Flat structure, easy to navigate
4. ✓ **Scalable** - Easy to add features
5. ✓ **Quality Gates** - All files < 500 LOC
6. ✓ **No breaking changes** - URLs stay the same

### Next Steps
1. Get approval for Option 1
2. Execute migration (100 min)
3. Add admin security checks
4. Update documentation

---

**Version:** 1.0
**Author:** Claude Sonnet 4.5
**Date:** 2026-01-08
**Status:** READY FOR REVIEW
