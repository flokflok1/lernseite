# Migration Guide: Phase 8 API Refactoring

**Version:** 1.0
**Date:** 2026-01-08
**Phase:** Phase 8a-8h Complete
**Audience:** Developers, API Consumers

---

## Table of Contents

1. [Overview](#1-overview)
2. [For Backend Developers](#2-for-backend-developers)
3. [For Frontend Developers](#3-for-frontend-developers)
4. [Breaking Changes](#4-breaking-changes)
5. [Deprecation Timeline](#5-deprecation-timeline)
6. [Testing Checklist](#6-testing-checklist)

---

## 1. Overview

Phase 8 refactored the backend API layer to improve modularity and comply with the 500 LOC per file limit (Quality Gate G01). This guide helps you migrate to the new structure.

**Key Principles:**
- ✅ **All API endpoints remain unchanged** - No URL changes
- ✅ **Bridge files provide backward compatibility** - Old imports still work (deprecated)
- ⚠️ **Update imports gradually** - New package structure recommended
- ❌ **Some internal file paths changed** - Update imports in backend code

---

## 2. For Backend Developers

### 2.1 Import Changes

#### Tokens API (Phase 8b)

**OLD (deprecated, but still works):**
```python
from app.api.tokens import (
    get_my_token_balance,
    get_my_transactions,
    manual_topup
)
```

**NEW (recommended):**
```python
# Option 1: Import specific functions from modules
from app.api.tokens.wallet import get_my_token_balance
from app.api.tokens.transactions import get_my_transactions
from app.api.tokens.admin import manual_topup

# Option 2: Import blueprint (unchanged)
from app.api.tokens import tokens_bp  # Still works via bridge file
```

**Module Mapping:**
| Old Function | New Location |
|--------------|--------------|
| `get_my_token_balance()` | `tokens/wallet.py` |
| `get_my_transactions()` | `tokens/transactions.py` |
| `get_my_usage()` | `tokens/stats.py` |
| `manual_topup()` | `tokens/admin.py` |
| `get_token_stats()` | `tokens/admin.py` |

---

#### Math Toolkit API (Phase 8c)

**OLD (deprecated):**
```python
from app.api.math_toolkit import math_toolkit_bp
```

**NEW (recommended):**
```python
# Option 1: Import blueprint
from app.api.math import math_toolkit_bp

# Option 2: Import specific functions
from app.api.math.reference import (
    get_math_categories,
    get_formulas,
    search_formulas
)
from app.api.math.calculator import (
    calculate_expression,
    get_calculation_history
)
from app.api.math.sessions import (
    create_math_session,
    get_session_progress
)
from app.api.math.interactive import (
    get_interactive_tasks,
    submit_task_solution
)
```

**Module Mapping:**
| Old Function | New Location |
|--------------|--------------|
| Reference endpoints | `math/reference.py` |
| Calculator endpoints | `math/calculator.py` |
| Session endpoints | `math/sessions.py` |
| Interactive endpoints | `math/interactive.py` |

---

#### Exam Simulations API (Phase 8d)

**OLD:**
```python
from app.api.exam_simulations import exam_simulations_bp
```

**NEW (consolidated):**
```python
# Unified exams package
from app.api.exams import exams_bp

# Or import specific modules
from app.api.exams.simulations import create_exam_simulation
from app.api.exams.attempts import start_exam_attempt
from app.api.exams.generation import generate_exam_ai
```

**IMPORTANT:** The `exam_simulations/` package has been **removed**. All functionality is now in `exams/`.

---

#### TTS API (Phase 8d)

**OLD:**
```python
from app.api.tts import tts_bp
```

**NEW (consolidated):**
```python
# TTS is now under media/
from app.api.media.tts import tts_bp

# Or import specific modules
from app.api.media.tts.synthesis import synthesize_speech
from app.api.media.tts.voices import get_available_voices
from app.api.media.tts.tutor import generate_tutor_audio
```

**IMPORTANT:** The root-level `tts/` package has been **removed**. Use `media/tts/` instead.

---

#### Admin API (Phase 8a)

Admin API has been heavily refactored into 13 sub-packages. Most imports remain the same at the package level.

**Example - Admin Courses:**
```python
# OLD (if you imported from monolithic file):
from app.api.admin_courses import create_course, get_course_analytics

# NEW (recommended - import from admin package):
from app.api.admin.courses.crud import create_course
from app.api.admin.courses.analytics import get_course_analytics

# Or import blueprint:
from app.api.admin.courses import courses_admin_bp
```

**Admin Sub-Packages:**
| Old File | New Package | Description |
|----------|-------------|-------------|
| `admin_courses.py` | `admin/courses/` | 10 modules |
| `admin_ai_models.py` | `admin/ai_models/` | 5 modules |
| `admin_ai_authoring.py` | `admin/ai_authoring/` | 7 modules |
| `admin_ai_studio_generation.py` | `admin/ai_generation/` | 5 modules |
| `admin_ai_tutor.py` | `admin/ai_tutor/` | 5 modules |
| `admin_system.py` | `admin/system/` | 9 modules |
| `admin_lm_routing.py` | `admin/lm_routing/` | 9 modules |

---

### 2.2 Blueprint Registration

If you're registering blueprints in `app/__init__.py`, no changes needed:

```python
# These still work (via bridge files or package __init__.py):
from app.api.tokens import tokens_bp
from app.api.math import math_toolkit_bp
from app.api.exams import exams_bp
from app.api.media.tts import tts_bp

app.register_blueprint(tokens_bp)
app.register_blueprint(math_toolkit_bp)
app.register_blueprint(exams_bp)
app.register_blueprint(tts_bp)
```

---

### 2.3 Repository/Service Layer

No changes required in repositories or services. All database access patterns remain the same.

---

### 2.4 Testing

Update test imports:

```python
# OLD:
from app.api.tokens import get_my_token_balance

# NEW:
from app.api.tokens.wallet import get_my_token_balance
```

---

## 3. For Frontend Developers

### 3.1 API Endpoints (No Changes)

**IMPORTANT:** All API endpoint URLs remain **unchanged**. No frontend code changes required.

**Examples:**
```typescript
// Tokens API - URLs unchanged
GET /api/v1/tokens/me
GET /api/v1/tokens/transactions
POST /api/v1/tokens/manual-topup

// Math Toolkit - URLs unchanged
GET /api/v1/math-toolkit/categories
POST /api/v1/math-toolkit/calculate

// Exams - URLs unchanged
GET /api/v1/exam-simulations/
POST /api/v1/exam-simulations/:id/start

// TTS - URLs unchanged
POST /api/v1/tts/synthesize
GET /api/v1/tts/voices
```

---

### 3.2 TypeScript Types (No Changes)

All TypeScript interfaces and types in `frontend/src/api/` remain valid.

---

### 3.3 API Client (No Changes)

No changes required in:
- `frontend/src/api/http.ts`
- `frontend/src/api/admin.api.ts`
- `frontend/src/api/admin/*.api.ts`

All existing API client code continues to work.

---

## 4. Breaking Changes

### 4.1 Backend Breaking Changes

#### Removed Packages:
1. **`app/api/exam_simulations/`** - Use `app/api/exams/` instead
2. **`app/api/tts/`** (root level) - Use `app/api/media/tts/` instead

#### Removed Empty Folders:
1. **`app/api/_shared/`** - No replacement (was empty)
2. **`app/api/media/videos/`** - No replacement (was empty)
3. **`app/api/media/audio/`** - Use `app/api/media/audio.py` instead

**Impact:** If you have imports from these packages, update them immediately.

---

### 4.2 Frontend Breaking Changes

**None.** All API endpoints unchanged.

---

## 5. Deprecation Timeline

| Item | Status | Removal Date | Action Required |
|------|--------|--------------|-----------------|
| **Bridge Files** | Deprecated | TBD | Update imports to new packages |
| `tokens.py` | Active (530 LOC) | After all imports updated | Use `tokens/` package |
| `math_toolkit.py` | Active (25 LOC) | After all imports updated | Use `math/` package |
| `tts.py.deprecated` | Marker only | Can be removed now | Already removed |
| **Duplicate Packages** | Removed | N/A | Already migrated |
| `exam_simulations/` | Removed | N/A | Use `exams/` |
| Root `tts/` | Removed | N/A | Use `media/tts/` |

---

## 6. Testing Checklist

### 6.1 Backend Testing

After updating imports, run:

```bash
cd backend

# 1. Run all tests
pytest

# 2. Check specific test files
pytest tests/test_tokens.py
pytest tests/test_math_toolkit.py
pytest tests/test_exams.py
pytest tests/test_admin.py

# 3. Verify no import errors
python -c "from app.api.tokens.wallet import get_my_token_balance; print('OK')"
python -c "from app.api.math.reference import get_math_categories; print('OK')"
python -c "from app.api.exams.simulations import create_exam_simulation; print('OK')"
```

---

### 6.2 Frontend Testing

No changes required, but verify API connectivity:

```bash
cd frontend

# 1. Build frontend
npm run build

# 2. Run type checking
vue-tsc --noEmit

# 3. Start dev server and test
npm run dev
```

**Manual Testing:**
- ✅ Test token wallet page
- ✅ Test math toolkit
- ✅ Test exam simulations
- ✅ Test admin panels

---

## 7. Common Migration Scenarios

### Scenario 1: Updating a Service File

**Before:**
```python
# app/services/billing_service.py
from app.api.tokens import get_my_token_balance

class BillingService:
    @staticmethod
    def check_balance(user_id):
        return get_my_token_balance(user_id)
```

**After:**
```python
# app/services/billing_service.py
from app.api.tokens.wallet import get_my_token_balance

class BillingService:
    @staticmethod
    def check_balance(user_id):
        return get_my_token_balance(user_id)
```

---

### Scenario 2: Updating Tests

**Before:**
```python
# tests/test_tokens.py
from app.api.tokens import get_my_token_balance, get_my_transactions

def test_token_balance():
    result = get_my_token_balance(user_id=42)
    assert result['balance'] > 0
```

**After:**
```python
# tests/test_tokens.py
from app.api.tokens.wallet import get_my_token_balance
from app.api.tokens.transactions import get_my_transactions

def test_token_balance():
    result = get_my_token_balance(user_id=42)
    assert result['balance'] > 0
```

---

### Scenario 3: Updating Admin Routes

**Before:**
```python
# app/__init__.py
from app.api.admin_courses import courses_admin_bp
app.register_blueprint(courses_admin_bp)
```

**After:**
```python
# app/__init__.py
from app.api.admin.courses import courses_admin_bp
app.register_blueprint(courses_admin_bp)
```

---

## 8. Rollback Plan

If issues arise after migration:

1. **Revert imports** to bridge files (they still work)
2. **Report issues** to development team
3. **Bridge files will remain** until all imports are updated

**Example Rollback:**
```python
# If new import causes issues:
from app.api.tokens.wallet import get_my_token_balance  # ❌ Issues

# Temporarily revert to bridge file:
from app.api.tokens import get_my_token_balance  # ✅ Still works
```

---

## 9. Support

### Documentation
- **Backend Structure:** See `BACKEND_STRUCTURE_PHASE8.md`
- **Developer Guide:** See `LernsystemX-Doku/07_Setup-Dev/03_Developer-Guide-KI.md`
- **API Docs:** See `backend/docs/api/`

### Questions
- **Architecture:** Check `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`
- **Quality Gates:** Check `.claude/rules/general.md`

---

**Document Version:** 1.0
**Last Updated:** 2026-01-08
**Phase:** Phase 8h Complete
