# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **CRITICAL: DOCUMENTATION-FIRST APPROACH**
>
> Before writing ANY code, you MUST:
> 1. Read the relevant documentation in `/LernsystemX-Doku/`
> 2. Check `03_Developer-Guide-KI.md` for coding standards and limits
> 3. Verify component/file size limits (max 500 lines per file)
> 4. Plan the structure BEFORE implementation
>
> **Key Documents (in order of priority):**
> - `LernsystemX-Doku/07_Setup-Dev/03_Developer-Guide-KI.md` - Developer standards, Quality Gates, size limits
> - `LernsystemX-Doku/01_Core/02_Lernmethoden.md` - 12 Content-Lernmethoden (master document)
> - `LernsystemX-Doku/05_Technical/16_Frontend-Struktur.md` - Vue.js architecture
> - `LernsystemX-Doku/05_Technical/17_Backend-Struktur.md` - Flask backend patterns
>
> **NEVER create files >500 lines. Split into sub-components/modules immediately.**

## Auto-Loaded Rules

This repository has comprehensive development rules in `.claude/rules/`:
- `general.md` - Quality Gates (G01-G10), architecture constraints
- `backend.md` - Repository pattern, type hints, 500-line limit
- `frontend.md` - Composition API, i18n requirements
- `component-structure.md` - ISO/IEC 26515 role-based organization
- `architecture.md` - Content-LMs (12 methods), System-Features (25)
- `development-priority.md` - Factory pattern, file extension rules
- `documentation.md` - Where to document (`.claude/` only)
- `naming-conventions.md` - Functional vs technical names
- `migrations.md` - Database migration workflow

## Project Overview

**LernsystemX (LSX)** is an AI-powered learning platform with 12 Content-Lernmethoden + 25 System-Features, 9 user roles, and real-time collaboration. Flask backend (Python 3.12+) and Vue.js 3 frontend.

**Key Architecture:**
- 12 Content-Lernmethoden (LM00-LM11) in 3 groups (A-C) for learning content
- 25 System-Features (whiteboard_engine, ihk_exam_system, npc_tutor, etc.) for infrastructure
- 9 roles: Free, Premium, Creator, Teacher, School, Company, Support, Moderator, Admin
- Token-based premium model (10,000 tokens/month)
- Multi-language support (20 languages via DeepL)
- LiveRoom with WebRTC and AI-powered whiteboard

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask 3.0, Python 3.12+ |
| Database | PostgreSQL with psycopg (connection pooling, **NO ORM**) |
| Cache/Queue | Redis, Celery |
| Real-time | Flask-SocketIO |
| Auth | JWT (Flask-JWT-Extended) |
| Frontend | Vue.js 3 (Composition API), TypeScript, Vite |
| State | Pinia |
| Styling | TailwindCSS |

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate       # macOS/Linux (Windows: venv\Scripts\activate)
pip install -r requirements.txt
python run.py                  # http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

### Required Services

> **IMPORTANT: Use ONLY these connection methods!**

```bash
# PostgreSQL - ALWAYS connect this way:
psql service=devdb

# Redis - ALWAYS connect this way:
redis-cli -h 10.0.43.2 -p 6379

# FORBIDDEN (old connections):
# - psql -h ... -U ...
# - psql postgresql://...
# - PGPASSWORD=...
# - redis-cli -h localhost
```

### First Time Setup
Navigate to `http://localhost:5000/setup/status` - the Setup Wizard handles database initialization, admin user, and AI configuration.

## Common Commands

### Backend (from `backend/` with venv activated)
```bash
python run.py                           # Start dev server with SocketIO (NOT flask run)
flask routes                            # List all API routes
flask shell                             # Interactive Python shell
pytest                                  # Run all tests
pytest tests/test_auth.py               # Run specific test
pytest --cov=app --cov-report=html      # Coverage report
```

### Frontend (from `frontend/`)
```bash
npm run dev          # Development server (Vite)
npm run build        # Production build
npm run preview      # Preview production build
vue-tsc --noEmit     # Type check only
```

### Database
```bash
psql service=devdb   # Direct PostgreSQL access

# Migrations (numbered SQL files 001-066 in backend/migrations/)
python run_migration.py      # Run migration
python check_migrations.py   # Check status
python test_migration.py     # Test before applying
```

## Critical Architecture Patterns

### 1. No ORM - Direct SQL with psycopg

This project **intentionally avoids ORM** (no SQLAlchemy). All database operations use direct SQL with psycopg connection pooling.

```python
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    @staticmethod
    def find_by_id(user_id: str) -> Optional[dict]:
        query = "SELECT * FROM users WHERE user_id = %s"
        return UserRepository.fetch_one(query, (user_id,))
```

**Always use:**
- `BaseRepository` methods: `fetch_one()`, `fetch_all()`, `execute()`
- Parameterized queries (prevent SQL injection)
- Type hints for all functions

### 2. Factory Pattern with Application Context

```python
from app import create_app
app = create_app('development')  # or 'production', 'testing'
```

**Dual-Mode Operation:**
- **Setup Wizard Mode** (first run): Only `/setup/*` routes available
- **Normal Mode** (after setup): Full API via `/api/v1/*` through API Gateway

### 3. Blueprint-Based API Gateway

All routes organized under `/api/v1` with segmentation:

| Segment | Purpose | Rate Limit |
|---------|---------|------------|
| `/api/v1/public` | Unauthenticated endpoints | 10/min |
| `/api/v1/*` | Authenticated user endpoints | 100/min |
| `/api/v1/admin/*` | Admin operations | 500/min |
| `/api/v1/organisations/*` | Organization management | 100/min |

**Example admin package structure:**
```
backend/app/api/admin/          # 40 endpoints, 7 modules
├── __init__.py                 # Imports all modules
├── courses.py      (329 LOC)   # Course CRUD (7 endpoints)
├── chapters.py     (200 LOC)   # Chapter management (5 endpoints)
├── lessons.py      (228 LOC)   # Lesson management (5 endpoints)
├── ai_jobs.py      (261 LOC)   # AI job management (4 endpoints)
├── exams.py        (318 LOC)   # Exam management (6 endpoints)
├── course_prompts.py (302 LOC) # Prompt overrides (6 endpoints)
└── course_files.py (346 LOC)   # File attachments (7 endpoints)
```

> Refactored from single `admin_courses.py` (3624 LOC) → 7 modules (~2022 LOC total, -44%)

### 4. Vue.js Component Organization (ISO/IEC 26515)

**CRITICAL: Components organized by USER ROLE, NOT by technology!**

```
✅ CORRECT (role-based):
components/
├── admin/      # Admin-specific features
│   ├── ai-operations/       # AI Studio, authoring, generation
│   ├── content-management/  # Courses, chapters, lessons
│   └── user-management/     # Users, roles, organizations
├── user/       # End-user features
│   ├── lessons/             # Learning method components
│   ├── courses/             # Course views
│   └── dashboard/           # User dashboard
└── shared/     # Role-independent
    ├── ui/                  # Buttons, cards, inputs
    ├── charts/              # Analytics charts
    └── layout/              # Headers, footers

❌ FORBIDDEN (technical):
components/
├── desktop/    # ← Technical detail
├── windows/    # ← Technical detail
├── modals/     # ← Technical detail
└── forms/      # ← Technical detail
```

**Complex Component Pattern:**
```
admin/ai-operations/authoring/kurs-builder/
├── types/                      # TypeScript interfaces
│   ├── session.types.ts
│   └── index.ts                # Barrel export
├── composables/                # Shared business logic
│   ├── useSessionManager.ts
│   └── index.ts                # Barrel export
├── ChatPanel.vue               # Vue components (<500 LOC each)
├── MaterialsPanel.vue
└── index.ts                    # Exports everything
```

### 5. i18n (Internationalization)

**MANDATORY:** All user-facing text must use i18n system. Hardcoded strings are forbidden.

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

// In script: t('key.path')
const errorMessage = t('common.unknownError')
</script>

<template>
  <!-- In template: $t('key.path') -->
  <h1>{{ $t('admin.users.title') }}</h1>
  <p>{{ $t('errors.pageNotFoundDesc') }}</p>
</template>
```

**Supported languages:** de, en, pl (must add keys to ALL 3 locale files)
**Location:** `frontend/src/locales/{de,en,pl}/`

## Learning Methods Architecture

### Content-Lernmethoden (12 Methods)

**CRITICAL:** Exactly 12 Content-LMs exist (LM00-LM11) in 3 groups.

| Group | IDs | Count | Focus |
|-------|-----|-------|-------|
| **A - Erklärend** | LM00-LM04 | 5 | Understanding |
| **B - Praxis** | LM05-LM08 | 4 | Practice |
| **C - Prüfung** | LM09-LM11 | 3 | Assessment |

**Database constraint:** `method_type BETWEEN 0 AND 11`

**NEVER use:** LM12-LM32 (don't exist), Gruppen D-F (don't exist), method_type > 11 (invalid)

### System-Features (25 Features)

Separate from Content-LMs. Stored in `support_systems.system_features`.

**Categories:** audio, collaboration, exam_systems, gamification, interactive_tools, it_environments, learning_paths, meta_features, tutor, visualization

**Examples:**
- `whiteboard_engine` (interactive whiteboard)
- `ihk_exam_system` (IHK-style exams)
- `npc_tutor` (AI tutor companion)
- `code_sandbox` (IT practice environment)

**Code reference:** `backend/app/ki/learning_method_mapping.py`

## Database

**153 tables**, 66 migration files (001-066) in `backend/migrations/`:
- `01_Core/` - Users, roles, organizations (001-007)
- `02_Content/` - Courses, chapters, lessons, learning methods (008-016)
- `03_AI/` - AI models, prompts, jobs, usage tracking (017-021)
- `04_Analytics/` - System and user analytics (022-023)
- `05_Gamification/` - XP, badges, quests (024-025)
- `06_LiveRoom/` - WebRTC rooms, whiteboards (026-027)
- `07_Notifications/` - Notification system (028-030)
- `08_Storage/` - Media files, versions (031-032)
- `09_Billing/` - Subscriptions, transactions (033-035)
- `10_Community/` - Groups, forums (036-037)
- `11_System/` - Translations, rate limits (038-040)

**Key tables:**
- `users`, `roles`, `permissions` - RBAC (10 roles, hierarchy 1-9)
- `courses`, `chapters`, `lessons` - Course hierarchy
- `learning_method_instances`, `learning_method_types` - 12 Content-LMs
- `subscriptions`, `token_wallets`, `token_transactions` - Premium/billing
- `organisations`, `organisation_members` - Schools/companies
- `translations` - Multi-language cache (permanent TTL)

## Coding Standards

### Python
- PEP 8, line length 100 chars
- Type hints required for all functions
- Google-style docstrings
- **Max 500 lines per file** (split into _part2.py, _part3.py if needed)

### SQL
```python
# ✅ Good - parameterized query
query = "SELECT * FROM users WHERE email = %s"
result = UserRepository.fetch_one(query, (email,))

# ❌ Bad - SQL injection risk
query = f"SELECT * FROM users WHERE email = '{email}'"
```

### API Response Format
```json
{
  "success": true,
  "data": { ... },
  "meta": { "timestamp": "2025-01-15T10:30:00Z" }
}
```

Error:
```json
{
  "success": false,
  "error": { "code": "INVALID_INPUT", "message": "...", "field": "email" }
}
```

### Vue.js
Always use Composition API with `<script setup>`:
```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
const count = ref(0)
</script>
```

## Common Pitfalls

1. **Don't use SQLAlchemy/ORM** - This project uses direct SQL with psycopg only
2. **Always use repository methods** - They handle connection pooling
3. **Setup Wizard first** - Most routes won't work until installation complete
4. **Redis required** - For JWT blacklist, rate limiting, Celery, caching
5. **Use `python run.py`** - Not `flask run` (SocketIO needs eventlet)
6. **method_type validation** - Content-LMs: {0,1,2,3,4,5,6,7,8,9,10,11} only
7. **Max 500 lines per file** - Split immediately when exceeded
8. **i18n mandatory** - No hardcoded user-facing strings
9. **Role-based components** - Not technology-based (no desktop/, windows/ folders)
10. **Extend existing files first** - Only create new files for genuinely new domains

## AI Integration

### Providers
- **Anthropic Claude**: Content generation, validation (primary)
- **OpenAI GPT-4**: Module generation, quizzes
- **DeepL**: Translation (20 languages)

Token costs: 500-6000 tokens per AI operation.

```python
from app.services.ai_adapter import AIAdapter

result = AIAdapter.generate_content(
    prompt="Generate quiz...",
    provider="anthropic",
    user_id=user_id
)
```

### KI Request Types
`module_gen`, `method_gen`, `exam_gen`, `translation`, `summary`, `math_analysis`, `whiteboard_analysis`

## Security

- JWT tokens (15min access, 7d refresh), blacklist in Redis
- Role-based access control (RBAC) with 10 roles
- Rate limiting: 100 req/min (user), 500 req/min (admin), 10 req/min (public)
- Passwords: bcrypt (cost factor 12)
- Pydantic validation for all inputs
- Row-Level Security for organization isolation
- Parameterized queries (prevent SQL injection)

## Documentation Structure

### German Technical Docs (`/LernsystemX-Doku/`)
Comprehensive system specifications. **Read these BEFORE coding!**

| File | Content |
|------|---------|
| `00_System-Übersicht.md` | System architecture, C4 diagrams |
| `01_Rollenmodell.md` | 9 roles with permissions |
| `02_Lernmethoden.md` | **Master** - 12 Content-Lernmethoden |
| `02a_System-Features.md` | 25 System-Features |
| `03_Zugriffssystem.md` | Access control & permissions |
| `04_Kurs-Architektur.md` | Course → Chapters → Lessons → Learning Methods |
| `09_KI-Pipeline.md` | 13 KI modules & workflows |
| `14_DB-Struktur.md` | Complete database schema |
| `16_Frontend-Struktur.md` | Vue.js architecture |
| `17_Backend-Struktur.md` | Flask backend with Repository Pattern |
| `21_LiveRoom-System.md` | WebRTC, Whiteboard, Recordings |
| `35_Developer-Guide-KI.md` | **Developer standards, Quality Gates G01-G10** |

### Quality Gates (G01-G10)

From `35_Developer-Guide-KI.md` - **MANDATORY**:

| Gate | Rule | Requirement |
|------|------|-------------|
| **G01** | No duplicates (.old, .bak, _v2) | MUST |
| **G02** | Follow LSX architecture | MUST |
| **G04** | Complete files (no fragments) | MUST |
| **G05** | Docstrings, type hints | MUST |
| **G07** | OWASP-compliant, no secrets | MUST |

**Before every commit, verify:**
- [ ] No duplicate files created
- [ ] Architecture patterns followed
- [ ] Files complete (<500 lines each)
- [ ] All functions documented with type hints
- [ ] No security issues (OWASP Top 10)

## Common Tasks

### Adding a New API Endpoint
1. Find existing file or create in `app/api/` blueprint
2. Add route with proper decorators (`@require_auth`, `@require_role`)
3. Add Pydantic model in `app/models/` for validation
4. Add repository methods in `app/repositories/` (inherit `BaseRepository`)
5. Add service logic in `app/services/` if complex business rules
6. Update `LernsystemX-Doku/05_Technical/17_Backend-Struktur.md`

### Adding a New Vue Component
1. Determine user role: admin, user, or shared
2. Place in correct domain folder (ai-operations, content-management, etc.)
3. Create types/ folder if complex TypeScript interfaces needed
4. Create composables/ folder if reusable business logic needed
5. Keep component <500 lines (split into sub-components if needed)
6. Add ALL i18n keys to de.json, en.json, pl.json
7. Update `LernsystemX-Doku/05_Technical/16_Frontend-Struktur.md`

### Adding a New Database Table
1. Create SQL migration: `backend/migrations/[category]/0XX_description.sql`
2. Run: `python run_migration.py`
3. Create repository in `app/repositories/` (inherit `BaseRepository`)
4. Create Pydantic model in `app/models/`
5. Update `LernsystemX-Doku/05_Technical/14_DB-Struktur.md`

### Adding a New Content-Lernmethode (RARE)
**WARNING:** Only add with Product Owner approval!

1. Update DB constraint: `method_type BETWEEN 0 AND [NEW_MAX]`
2. Insert into `learning_method_types` table
3. Update `02_Lernmethoden.md`, `CLAUDE.md`, `.claude/rules/`
4. Create frontend editor: `components/learning-methods/LearningMethod[XX]Form.vue`
5. Update `backend/app/ki/learning_method_mapping.py`
6. Create AI prompt template if needed

### Adding a New System-Feature
1. Insert into `support_systems.system_features` table
2. Update `02a_System-Features.md`, `CLAUDE.md`, `.claude/rules/`
3. Implement backend service: `app/services/features/[feature_code]_service.py`
4. Create API endpoints if external interface needed
5. Create frontend component: `components/system-features/[FeatureName].vue`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Factory pattern (create_app)
│   ├── config.py                # Environment configs
│   ├── extensions.py            # Flask extensions
│   ├── api/                     # API blueprints (routes)
│   │   ├── admin/               # Admin package (40 endpoints, 7 modules)
│   │   ├── auth/                # Authentication endpoints
│   │   ├── courses/             # Course-related endpoints
│   │   ├── learning_methods/    # Learning method execution
│   │   └── ...
│   ├── models/                  # Pydantic validation models
│   ├── repositories/            # Database access (direct SQL)
│   │   ├── base_repository.py  # Base class for all repositories
│   │   ├── user/                # User repository
│   │   ├── courses/             # Course repositories
│   │   └── ...
│   ├── services/                # Business logic
│   ├── middleware/              # Auth, security headers
│   ├── gateway/                 # API Gateway (routing, rate limiting)
│   ├── security/                # Rate limiting, permissions
│   ├── monitoring/              # Prometheus metrics
│   └── ki/                      # AI prompt system & learning method mapping
├── setup/                       # Setup Wizard
├── migrations/                  # SQL migration files (001-066)
└── run.py                       # Entry point

frontend/
├── src/
│   ├── api/                     # API services (Axios)
│   │   ├── http.ts              # Base instance with JWT interceptor
│   │   └── admin/               # Admin API modules (14 files)
│   ├── store/                   # Pinia stores
│   ├── components/              # Vue components (role-based organization)
│   │   ├── admin/               # Admin components
│   │   ├── user/                # User components
│   │   └── shared/              # Shared components
│   ├── pages/                   # Route pages
│   ├── layouts/                 # Layout components
│   ├── router/                  # Vue Router config
│   ├── locales/                 # i18n translations
│   │   ├── de/                  # German
│   │   ├── en/                  # English
│   │   └── pl/                  # Polish
│   └── main.ts                  # Entry point
└── vite.config.ts

LernsystemX-Doku/               # German documentation (MUST READ)
├── 01_Core/                    # Core system specs
├── 02_Business/                # Business model
├── 03_Features/                # Feature specs
├── 04_KI/                      # AI integration
├── 05_Technical/               # Technical architecture
├── 06_Security/                # Security specs
└── 07_Setup-Dev/               # Developer guides

.claude/                        # Claude Code rules (auto-loaded)
├── rules/                      # Development rules
│   ├── general.md              # Quality Gates, constraints
│   ├── backend.md              # Python rules
│   ├── frontend.md             # Vue.js rules
│   ├── component-structure.md  # ISO/IEC 26515 organization
│   ├── architecture.md         # LMs & features
│   └── ...
└── [PLAN_FILES].md             # Migration/refactoring plans
```

## Environment Setup

Required environment variables (`.env` file):

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://10.0.43.2:6379/0

# Security
SECRET_KEY=your-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-change-this

# AI Integration (optional)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPL_API_KEY=...

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=...
MAIL_PASSWORD=...
```

## Testing

```bash
# Backend
cd backend
pytest                                  # Run all tests
pytest tests/test_auth.py               # Specific test file
pytest --cov=app --cov-report=html      # With coverage

# Frontend
cd frontend
npm run typecheck                       # Type checking
npm run build                           # Build test (validates i18n)
```

## LiveRoom System (WebRTC)

Real-time learning rooms with:
- **Video/Audio**: WebRTC (mediasoup/Jitsi)
- **AI Whiteboard**: Formula recognition, network diagrams
- **Transcription**: Live transcription with AI summaries
- **Recording**: Tiered storage (S3: hot 30d, warm 30-90d, cold >90d Glacier)

**Room Types:** classroom, seminar, study, exam, ai (1:1 tutor)
**Roles:** host (full control), teacher (moderation), student, guest

## Monitoring & Metrics

- **Health checks:** `/health`, `/health/detailed`, `/health/ready`, `/health/live`
- **Metrics:** `/metrics` (Prometheus format, requires MONITORING_ENABLED=True)
- **Logging:** Structured logging to `logs/lernsystemx.log`
- **Analytics:** API Gateway tracks all requests (if API_GATEWAY_TRACK_ANALYTICS=True)

## Further Reading

- **API Documentation:** `/backend/docs/api/`
- **German Technical Docs:** `/LernsystemX-Doku/` (50+ documents)
- **Developer Guide:** `LernsystemX-Doku/07_Setup-Dev/03_Developer-Guide-KI.md`
