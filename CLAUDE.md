# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **CRITICAL: DOCUMENTATION-FIRST APPROACH**
>
> Before writing ANY code, you MUST:
> 1. Read the relevant documentation in `/LernsystemX-Doku/`
> 2. Check `.claude/rules/` for specific development rules
> 3. Verify component/file size limits (max 500 lines per file)
> 4. Check the **git status** to understand ongoing work
>
> **Key Documents (READ IN THIS ORDER):**
> - `.claude/rules/general.md` - Quality Gates (G01-G10), architecture constraints (MANDATORY)
> - `LernsystemX-Doku/07_Setup-Dev/03_Developer-Guide-KI.md` - Developer standards
> - `.claude/rules/backend.1.md` or `.claude/rules/frontend.1.md` - Language-specific rules
> - `LernsystemX-Doku/05_Technical/17_Backend-Struktur.md` - Backend architecture (if modifying backend)
> - `LernsystemX-Doku/05_Technical/16_Frontend-Struktur.md` - Frontend architecture (if modifying frontend)

## Auto-Loaded Rules

Comprehensive development rules in `.claude/rules/`:
- `general.md` - Quality Gates, architecture constraints, architektur-facts
- `backend.1.md` & `backend.2.md` - Python/Flask development standards
- `frontend.1.md` & `frontend.2.md` - Vue.js 3 development standards
- `component-structure.md` - ISO/IEC 26515 role-based component organization
- `architecture.md` - Content-Lernmethoden (12) and System-Features (25) definitions
- `development-priority.md` - Factory pattern, DDD principles, file extension strategy
- `naming-conventions.md` - Functional vs technical naming (CRITICAL for frontend)
- `commands.md` - Bash command preferences (use `tree`, not `ls`)

## Current Work (refactor/backend-ddd-journey-architecture)

**Branch Status:** Working on DDD refactoring and error handling standardization
- Recently completed: Phase 1, Part 3 - Error Code to i18n Mapping
- Current focus: Normalizing error codes, circular import fixes, i18n barrel exports
- API structure: `/api/v1/admin-panel/`, `/api/v1/course_editor/`, `/api/v1/learning_methods/`
- Error handling: Transitioning to ErrorCode system with i18n mapping

**Key files recently modified:**
- `backend/app/api/v1/` - New API v1 structure
- `backend/app/i18n/error_code_i18n_mapping.py` - Error code localization
- `backend/app/models/` - Pydantic validation models

## Project Overview

**LernsystemX (LSX)** - AI-powered enterprise learning platform
- **Backend:** Flask 3.0 + Python 3.12+, psycopg3 (no ORM), Redis, Celery
- **Frontend:** Vue.js 3 (Composition API) + TypeScript, Vite, Pinia, TailwindCSS
- **Database:** PostgreSQL 16, 153 tables, 66 migrations, row-level security
- **Architecture:** 12 Content-Lernmethoden (LM00-LM11), 25 System-Features, DDD principles
- **Features:** AI content generation, real-time LiveRoom (WebRTC), token-based premium, multi-language (20 langs)

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                       # Starts at http://localhost:5000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev                         # Starts at http://localhost:5173
```

### Required External Services
```bash
# PostgreSQL - CRITICAL: Must use this connection method
psql service=devdb

# Redis - CRITICAL: Must use this address (NOT localhost)
redis-cli -h 10.0.43.2 -p 6379

# FORBIDDEN:
# - psql -h localhost ...
# - redis-cli -h localhost ...
# - PGPASSWORD=... psql ...
```

### First Time Setup
Navigate to `http://localhost:5000/setup/status` - the Setup Wizard initializes database, creates admin user, and configures AI providers.

## Common Development Commands

### Backend (from `backend/` directory with venv activated)

**Running & Development:**
```bash
python run.py                        # Start dev server with SocketIO
flask routes                         # List all registered API routes
flask shell                          # Interactive Python shell with app context
```

**Testing & Code Quality:**
```bash
pytest                               # Run all backend tests
pytest tests/test_auth.py            # Run specific test file
pytest tests/test_auth.py::test_login -v  # Run specific test function
pytest --cov=app --cov-report=html   # Coverage report (opens htmlcov/index.html)
pytest -x                            # Stop on first failure
pytest -s                            # Show print statements during tests
```

**Code Analysis:**
```bash
# Linting (if configured)
flake8 app/

# Type checking (if mypy configured)
mypy app/

# Find large files (>500 lines = refactor needed)
find app -name "*.py" -exec wc -l {} + | sort -rn | head -20
```

### Frontend (from `frontend/` directory)

**Development:**
```bash
npm run dev                          # Start Vite dev server
npm run build                        # Production build
npm run build:typecheck             # Build with TypeScript checking
npm run preview                      # Preview production build
```

**Type Checking & Testing:**
```bash
npm run typecheck                    # Check TypeScript without building
npm run test                         # Run Vitest unit tests
npm run test:watch                   # Watch mode for tests
npm run test:coverage               # Coverage report
npm run test:ui                     # UI test runner
npm run check                        # Project setup validation
```

### Database

**Connections:**
```bash
psql service=devdb                  # Connect to PostgreSQL
```

**Migrations:**
```bash
# From backend/
python run_migration.py             # Run all pending migrations
python check_migrations.py          # Check migration status
python test_migration.py            # Test before applying
```

**Direct SQL:**
```sql
-- Connect with: psql service=devdb
SELECT table_name FROM information_schema.tables WHERE table_schema='public';
```

## Critical Architecture Patterns

### 1. Repository Pattern + Direct SQL (NO ORM)

**MANDATORY:** All database access MUST go through repositories. SQLAlchemy/ORMs are forbidden.

```python
# ✅ CORRECT
from app.repositories.user import UserRepository

with get_db_connection() as conn:
    user_repo = UserRepository(conn)
    user = user_repo.find_by_id(user_id)
    users = user_repo.find_by_email(email)

# ❌ FORBIDDEN - Direct queries outside repositories
cursor.execute("SELECT * FROM users")

# ❌ FORBIDDEN - ORM usage
User.query.filter_by(email=email).first()
```

**Key Repository Methods:**
- `find_by_id(id)` - Single record by primary key
- `find_all(limit, offset)` - Paginated list
- `find_by(filters)` - Multiple filters with AND logic
- `create(data)` - Insert new record
- `update(id, data)` - Update existing record
- `delete(id)` - Delete record
- `count(filters)` - Record count

**Parameterized Queries (CRITICAL for security):**
```python
# ✅ CORRECT - SQL injection proof
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# ❌ CRITICAL SECURITY VULNERABILITY - SQL injection
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### 2. API v1 Structure (Blueprint-Based Gateway)

```
backend/app/api/v1/
├── admin-panel/              # Admin operations (40+ endpoints)
│   ├── courses/
│   ├── role_studio.py
│   ├── settings/
│   │   └── ai/              # AI model/provider management
│   └── permissions/
│
├── course_editor/           # Content authoring
│   ├── ai_editor/
│   ├── manual_editor/
│   └── publishing/
│
├── learning_methods/        # LM execution (12 methods)
├── courses/                 # User course operations
├── auth.py                  # Authentication endpoints
├── social/                  # Social network (posts, comments)
└── ...
```

**Rate Limiting by Segment:**
- `/api/v1/public/*` - 10/min (unauthenticated)
- `/api/v1/*` - 100/min (authenticated users)
- `/api/v1/admin/*` - 500/min (admin operations)
- `/api/v1/organisations/*` - 100/min (org management)

### 3. Error Handling with ErrorCode System

**NEW (Phase 1, Part 3):** All errors now use standardized ErrorCode with i18n mapping.

```python
# ✅ CORRECT - Use ErrorCode system
from app.i18n.error_codes import ErrorCode
from app.utils.validation_exception_wrapper import ValidationException

if not user:
    raise ValidationException(
        error_code=ErrorCode.USER_NOT_FOUND,
        field="user_id"
    )

# Error automatically maps to i18n: error_codes.de.json, en.json, pl.json
# Response includes: code, message (localized), field

# ❌ DEPRECATED - Hardcoded error messages
raise ValueError("User not found")
return {"error": "Invalid input"}, 400
```

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validierungsfehler",  // Localized from i18n
    "field": "email",
    "details": {}
  }
}
```

### 4. Vue.js Component Organization (Role-Based)

**CRITICAL:** Components organized by USER ROLE, NOT by technology type.

```
✅ CORRECT (Role-Based + Domain-Based):
frontend/src/components/
├── admin/                        # Admin-specific
│   ├── ai-operations/           # AI authoring features
│   │   ├── studio/
│   │   ├── authoring/
│   │   └── management/
│   ├── content-management/      # Course/content management
│   └── user-management/
│
├── user/                        # End-user features
│   ├── lessons/                # Learning experiences
│   ├── courses/                # Course browsing
│   └── dashboard/              # User dashboard
│
└── shared/                      # Role-independent
    ├── ui/                     # Base components (Button, Input, Card)
    ├── charts/                 # Analytics visualization
    └── layout/                 # Headers, footers, navigation

❌ FORBIDDEN (Technical):
├── desktop/                    # Technology detail
├── windows/                    # Technology detail
├── modals/                     # Technology detail
└── forms/                      # Technology detail
```

**Complex Component Pattern:**
```
admin/ai-operations/authoring/kurs-builder/
├── types/                      # TypeScript interfaces (barrel export)
│   ├── session.types.ts
│   └── index.ts
├── composables/                # Shared business logic (barrel export)
│   ├── useSessionManager.ts
│   └── index.ts
├── ChatPanel.vue               # Components (<500 LOC each)
├── MaterialsPanel.vue
└── index.ts                    # Exports all
```

### 5. i18n (Internationalization - MANDATORY)

**All user-facing text MUST be internationalized. Hardcoded strings are forbidden.**

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

// In script: t('key.path')
const errorMsg = t('common.unknownError')
</script>

<template>
  <!-- In template: $t('key.path') -->
  <h1>{{ $t('admin.users.title') }}</h1>
  <p v-if="error">{{ $t('errors.loadingFailed') }}</p>
</template>
```

**Supported Languages:** de (German), en (English), pl (Polish)
**Location:** `frontend/src/locales/{de,en,pl}/`
**CRITICAL:** Add keys to ALL 3 language files. Incomplete translations cause runtime errors.

## Content-Lernmethoden (12 Methods) & System-Features (25)

### Content-Lernmethoden - EXACTLY 12 (LM00-LM11)

| Group | IDs | Count | Type | Database Constraint |
|-------|-----|-------|------|-------------------|
| **A** Erklärend | LM00-LM04 | 5 | Explanation/Theory | `method_type BETWEEN 0 AND 11` |
| **B** Praxis | LM05-LM08 | 4 | Practice/Exercises | |
| **C** Prüfung | LM09-LM11 | 3 | Assessment/Exams | |

**CRITICAL CONSTRAINTS:**
- ❌ Do NOT use LM12-LM32 (don't exist)
- ❌ Do NOT use group_code D, E, F (don't exist)
- ❌ Do NOT allow method_type > 11 (violates DB constraint)

**Reference:** `backend/app/ki/learning_method_mapping.py`

### System-Features - 25 Total

Separate from Content-LMs. Infrastructure-level features (not learning experiences).

**Categories:** audio, collaboration, exam_systems, gamification, interactive_tools, it_environments, learning_paths, meta_features, tutor, visualization

**Examples:**
- `whiteboard_engine` - Interactive whiteboard with formula recognition
- `ihk_exam_system` - IHK-style exam format
- `npc_tutor` - AI-powered tutor companion
- `code_sandbox` - IT practice environment
- `livestream` - Live video streaming

**Reference:** `LernsystemX-Doku/01_Core/02a_System-Features.md`

## File Size Limits & Quality Gates

### Mandatory Limits (Quality Gate G01)

| Component Type | Max Lines | Action if Exceeded |
|----------------|-----------|-------------------|
| Python file | 500 | Split into `_part2.py`, `_part3.py` |
| Vue component | 500 | Extract into sub-components |
| Function | 50 | Extract helper functions |
| Function parameters | 5 | Use dataclass/Pydantic model |

### File Naming Convention

**Python:**
- `user.py` - Module for user domain
- `user_part2.py` - Continuation when >500 lines
- `test_user.py` - Test file
- `user.service.py` - Service layer (Flask)

**Vue:**
- `UserProfile.vue` - PascalCase, multi-word required
- `UserProfile.types.ts` - Types in sub-folder
- `useUserProfile.ts` - Composable in sub-folder

**NEVER:**
- `utils.py`, `common.py`, `helpers.py` - Too generic
- `Button.vue` - Single word (except shared/ui)
- `user.js` - Lowercase for Vue

## Database Schema

**153 Tables, 66 Migrations** - Organized by domain:

| Category | Migrations | Content |
|----------|-----------|---------|
| Core | 001-007 | Users, roles, organizations, permissions |
| Content | 008-016 | Courses, chapters, lessons, learning methods |
| AI | 017-021 | AI models, prompts, jobs, usage |
| Analytics | 022-023 | System & user analytics |
| Gamification | 024-025 | XP, badges, quests |
| LiveRoom | 026-027 | WebRTC, whiteboard, recordings |
| Notifications | 028-030 | Notification system |
| Storage | 031-032 | Files, versions, media |
| Billing | 033-035 | Subscriptions, transactions, tokens |
| Community | 036-037 | Groups, forums, social |
| System | 038-040 | Translations (i18n), rate limits, config |

**Key Tables:**
- `users` - User accounts (with roles)
- `courses` → `chapters` → `lessons` - Course hierarchy
- `learning_method_instances` - Content execution
- `subscriptions`, `token_wallets` - Premium/billing
- `translations` - i18n cache (permanent TTL)
- `error_codes` - Standardized error mapping (NEW)

**Row-Level Security:** Organizations isolate tenant data automatically.

## Common Development Tasks

### Adding a New API Endpoint

1. **Choose location:** Find existing file in `backend/app/api/v1/` or create if new domain
2. **Add route:**
   ```python
   @bp.route('/users/<user_id>', methods=['GET'])
   @require_auth
   def get_user(user_id: str):
       with get_db_connection() as conn:
           repo = UserRepository(conn)
           user = repo.find_by_id(user_id)
       return jsonify(user.to_dict()), 200
   ```
3. **Add Pydantic model:** `backend/app/models/user.py` for request/response validation
4. **Add repository methods:** `backend/app/repositories/user.py` (inherit BaseRepository)
5. **Update documentation:** `LernsystemX-Doku/05_Technical/17_Backend-Struktur.md`

### Adding a New Vue Component

1. **Determine role:** admin, user, teacher, parent, moderator, or shared
2. **Place in domain:** `frontend/src/components/{role}/{domain}/{Component}.vue`
3. **Create types** if needed: `types/component.types.ts` + `types/index.ts` (barrel export)
4. **Create composables** if needed: `composables/useComponent.ts` + `composables/index.ts`
5. **Add ALL i18n keys:** Must add to `de.json`, `en.json`, `pl.json` - incomplete causes errors
6. **Keep <500 LOC:** Split into sub-components if needed
7. **Update documentation:** `LernsystemX-Doku/05_Technical/16_Frontend-Struktur.md`

### Adding a New Database Table

1. **Create migration:** `backend/migrations/[category]/0XX_description.sql`
2. **Run migration:** `python run_migration.py`
3. **Create repository:** `backend/app/repositories/[domain].py` (inherit BaseRepository)
4. **Create model:** `backend/app/models/[domain].py` (Pydantic + dataclass)
5. **Add endpoints:** In corresponding API v1 blueprint
6. **Update documentation:** `LernsystemX-Doku/05_Technical/14_DB-Struktur.md`

### Fixing Circular Imports

**Common Issue:** `from app.services.X import Y` → `from app.models.X import Z` → `from app.services...`

**Solution:** Avoid importing at module level in services. Import inside functions:
```python
# ❌ Circular
from app.models import User  # At top level

# ✅ Correct
def create_user():
    from app.models import User  # Import inside function
    return User(...)
```

### Working with Error Codes

**Recent change (Phase 1, Part 3):** All errors now use i18n mapping.

1. **Add error code:** `backend/app/i18n/error_codes.py`
2. **Add i18n mapping:** `backend/app/i18n/error_code_i18n_mapping.py`
3. **Add translations:** `backend/app/i18n/` (de.json, en.json, pl.json)
4. **Use in route:**
   ```python
   from app.i18n.error_codes import ErrorCode
   from app.utils.validation_exception_wrapper import ValidationException

   if not valid:
       raise ValidationException(
           error_code=ErrorCode.VALIDATION_ERROR,
           field="email"
       )
   ```

## Important Technical Constraints

### Backend

- ✅ **Direct SQL with psycopg3** - No ORMs (SQLAlchemy, Peewee forbidden)
- ✅ **Repository Pattern** - All DB access through repositories
- ✅ **Parameterized Queries** - Always use `%s` placeholders (prevents SQL injection)
- ✅ **Type Hints** - Required on all functions
- ✅ **Pydantic Validation** - All API input validated
- ✅ **ErrorCode System** - Standardized errors with i18n
- ✅ **Factory Pattern** - `create_app(environment)` for app initialization
- ✅ **Max 500 lines/file** - Split when exceeded
- ❌ **Never hardcode secrets** - Use environment variables
- ❌ **Never use `flask run`** - Use `python run.py` (SocketIO compatibility)

### Frontend

- ✅ **Vue.js 3 Composition API** - Only `<script setup>` syntax allowed
- ✅ **TypeScript** - Type all props, emits, variables
- ✅ **i18n Mandatory** - All user text must be translated
- ✅ **Role-Based Components** - Organized by role, not technology
- ✅ **DOMPurify** - Sanitize user input before rendering as HTML
- ✅ **Pinia Stores** - For shared state (not localStorage)
- ✅ **Barrel Exports** - Use `index.ts` for complex domains
- ✅ **Max 500 lines/component** - Split into sub-components
- ❌ **No hardcoded strings** - Use i18n
- ❌ **No v-html without sanitization** - XSS vulnerability risk

## Testing Strategy

### Backend (pytest)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test function
pytest tests/test_auth.py::test_login_success -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

**Coverage Target:** >80% for repositories, services; >70% for routes

### Frontend (Vitest)

```bash
# Run all tests
npm run test

# Watch mode (rerun on file change)
npm run test:watch

# Coverage report
npm run test:coverage

# UI mode (browser interface)
npm run test:ui
```

**Coverage Target:** >75% overall

## Environment Setup

### Backend `.env`
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lernsystemx

# Redis (MUST be 10.0.43.2, NOT localhost)
REDIS_URL=redis://10.0.43.2:6379/0

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-min-32-chars

# AI Providers (optional)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPL_API_KEY=...

# Server
FLASK_ENV=development
```

### Frontend `.env`
```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

## Troubleshooting

### Backend Won't Start

**"Module not found" errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (must be 3.12+)
python --version

# Clear cache
find . -type d -name __pycache__ -exec rm -r {} +
```

**"Redis connection refused":**
```bash
# Check Redis is running on correct address
redis-cli -h 10.0.43.2 -p 6379 ping
# Should return: PONG

# Database issues
psql service=devdb -c "SELECT 1"
# Should return: (1 row)
```

### Frontend Build Issues

**"i18n keys missing" error:**
- Error: Some keys are missing in one of the language files
- Fix: Add missing keys to ALL 3 files (de.json, en.json, pl.json)
- Run: `npm run build:typecheck` to validate before building

**TypeScript errors:**
```bash
npm run typecheck          # Check without building
npm run build:typecheck    # Build with type checking
```

### Circular Import Error

**"ImportError: cannot import name X from app.services"**
- Move import inside the function that uses it (late binding)
- Check for A imports B, B imports A pattern
- Reference recent fix: `fix(circular-imports): resolve circular dependency in services layer`

## Project Documentation

**German Technical Docs** (`/LernsystemX-Doku/`) - MUST READ:
- `07_Setup-Dev/03_Developer-Guide-KI.md` - Developer standards & Quality Gates
- `01_Core/02_Lernmethoden.md` - Content-Lernmethoden specification
- `01_Core/02a_System-Features.md` - System-Features specification
- `05_Technical/14_DB-Struktur.md` - Complete database schema
- `05_Technical/16_Frontend-Struktur.md` - Frontend architecture
- `05_Technical/17_Backend-Struktur.md` - Backend architecture
- `06_Security/01_Security-Architecture.md` - Security implementation
- `09_KI-Pipeline.md` - AI integration workflows

## Key Statistics

- **Language:** Python 3.12+ (backend), TypeScript (frontend)
- **Database:** 153 tables, 66 migrations, row-level security
- **API:** 40+ admin endpoints, 20+ user endpoints, REST + WebSocket
- **Components:** 300+ Vue components, 12 Content-LMs, 25 System-Features
- **i18n:** 20 languages supported, 3 primary (de, en, pl)
- **Users:** 9 roles (Free, Premium, Creator, Teacher, School, Company, Support, Moderator, Admin)
- **Premium Model:** Token-based (10,000/month), PayPal + Stripe integration

## Git Workflow

**Current Branch:** `refactor/backend-ddd-journey-architecture`

**Commit Naming:**
```bash
git commit -m "feat(auth): add two-factor authentication"
git commit -m "fix(circular-imports): resolve dependency in services"
git commit -m "refactor(error-handling): standardize ErrorCode system"
```

**Recent Work:**
```
f5148c1 Phase 1, Part 3: Error Code to i18n Mapping - COMPLETE
3b11f76 fix(error-handling): standardize 14 HTTP error handlers
88b0a2d fix(auth): convert JWT auth errors to ErrorCode
ecf54ec fix(security): eliminate SQL injection in setup
fa7b58b fix(database): remove duplicate chapter_theory table
```

**Before Pushing:**
```bash
pytest                              # All tests pass?
npm run build:typecheck             # Frontend TypeScript OK?
git status                          # Committed all changes?
```
