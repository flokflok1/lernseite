# LernSystemX Backend Architecture

**Status:** Clean, Structured, Consistent (2026-01-17)
**Consolidation Date:** 2026-01-17

---

## Overview

The app root directory is organized following **clean architecture principles** with clear separation of concerns:

```
app/                              # Application root
├── __init__.py                  # Flask app factory (consolidated)
├── config.py                    # Configuration classes
├── extensions.py                # Flask extensions (db_pool, jwt, etc.)
├── ARCHITECTURE.md              # This file
│
├── api/                         # API Layer (Routes/Blueprints)
│   └── v1/                      # API Version 1
│       ├── admin/               # Admin endpoints
│       ├── admin-panel/         # Admin panel endpoints
│       ├── public/              # Public endpoints
│       └── social/              # Social feature endpoints
│
├── repositories/                # Data Access Layer (BaseRepository)
│   ├── base_repository.py       # Abstract base class
│   ├── user.py                  # User data access
│   ├── post.py                  # Post data access
│   ├── ai/                      # AI data access (editor, jobs, profiles, providers, usage)
│   ├── course.py                # Course data access
│   └── ...                      # Other repositories
│
├── services/                    # Business Logic Layer
│   ├── user_service.py          # User business logic
│   ├── ai/                      # AI business logic
│   │   ├── adapter.py           # AI API adapter
│   │   ├── config.py            # AI configuration
│   │   ├── static.py            # AI helpers
│   │   ├── exceptions.py        # AI exceptions
│   │   └── providers/           # AI providers (anthropic, openai, etc.)
│   ├── compliance/              # Compliance service (stub - planned)
│   ├── feature_flags/           # Feature flags service (stub - planned)
│   ├── drm/                     # DRM service (stub - planned)
│   ├── moderation/              # Content moderation (stub - planned)
│   └── system/                  # System service (stub - planned)
│
├── models/                      # Domain Models (Pydantic/Dataclasses)
│   ├── user.py                  # User model
│   ├── post.py                  # Post model
│   ├── course.py                # Course model
│   └── ...                      # Other models
│
├── ai/                          # AI Configuration & Mapping
│   ├── configuration/           # AI configuration layer (consolidated from app/ki/)
│   │   ├── prompt_models.py     # Prompt template models
│   │   ├── prompt_registry.py   # Prompt registry
│   │   ├── learning_method_mapping.py  # Learning method mappings
│   │   ├── system_features_mapping.py  # System feature mappings
│   │   ├── capability_slots.py  # AI capability slots
│   │   ├── ai_editor_prompts.py # AI editor prompts
│   │   ├── prompts/             # Prompt templates by type
│   │   └── slots/               # Capability slot definitions
│   ├── ai_course_generator.py   # Course generation logic
│   ├── content_moderation/      # Content moderation (stub)
│   ├── generation/              # Generation features (stub)
│   ├── recommendation/          # Recommendation engine
│   └── safety/                  # Safety modules
│
├── i18n/                        # Internationalization (20 languages)
│   ├── public/                  # Public API endpoints
│   ├── management/              # i18n management
│   ├── translation/             # Translation services
│   ├── moderation/              # Moderation-related i18n
│   ├── error_codes.py           # Standardized error codes
│   ├── message_codes.py         # Message codes
│   ├── _helpers.py              # i18n helpers
│   └── __init__.py              # Package init
│
├── middleware/                  # Middleware & Interceptors
│   ├── auth.py                  # Authentication middleware
│   ├── rate_limit.py            # Rate limiting
│   ├── cors.py                  # CORS headers
│   └── ...                      # Other middleware
│
├── utils/                       # Utility Functions
│   ├── exceptions.py            # Custom exceptions
│   ├── validators.py            # Input validators
│   ├── jwt.py                   # JWT utilities
│   ├── logger.py                # Logging setup
│   └── ...                      # Other utilities
│
├── security/                    # Security Features
│   ├── drm/                     # Digital Rights Management (stubs - planned)
│   │   ├── watermarking/
│   │   ├── core/
│   │   ├── license/
│   │   ├── licensing/
│   │   ├── monitoring/
│   │   ├── anti_tamper/
│   │   ├── analytics/
│   │   ├── encryption/
│   │   ├── streaming/
│   │   ├── access_control/
│   │   └── enforcement/
│   └── encryption/              # General encryption (stub - planned)
│
├── monitoring/                  # Monitoring & Observability
│   ├── alerting/                # Alert system (stub - planned)
│   ├── tracing/                 # Distributed tracing (stub - planned)
│   ├── logging/                 # Structured logging (stub - planned)
│   └── __init__.py
│
├── websocket/                   # WebSocket Support (stub - planned)
│   └── __init__.py
│
└── core/                        # Core utilities (stub - planned)
    └── __init__.py
```

---

## Architecture Principles

### 1. **Layered Architecture**

The application follows a strict layered architecture:

```
API Layer (Routes/Blueprints)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database (PostgreSQL)
```

**Rules:**
- **API Layer** (`app/api/v1/*`) - Only route handlers, validation, response formatting
- **Service Layer** (`app/services/*`) - Business logic, orchestration, transactions
- **Repository Layer** (`app/repositories/*`) - Database queries, abstractions
- **Models** (`app/models/*`) - Pydantic schemas, domain models

### 2. **Separation of Concerns**

Each module has a single responsibility:

- `app/repositories/` - "How to get data from database"
- `app/services/` - "What business logic to apply"
- `app/api/` - "How to present data to users"
- `app/models/` - "What shape is the data"
- `app/ai/` - "AI configuration and mapping"
- `app/i18n/` - "Internationalization and translations"

### 3. **No ORM Policy**

This project uses **direct SQL with psycopg3** (no SQLAlchemy, no Django ORM).

- All database access goes through `BaseRepository`
- Type hints required on all repository methods
- Parameterized queries (prevent SQL injection)
- Connection pooling via `psycopg_pool`

### 4. **Configuration Consolidation (2026-01-17)**

The Flask application factory was consolidated from 5 fragmented `__init__*.py` files into a single `app/__init__.py`:

**Before (Fragmented):**
```
app/__init__.py (main)
app/__init__extensions.py (Flask extensions)
app/__init__security.py (Security configuration)
app/__init__errors.py (Error handlers)
app/__init__middleware.py (Middleware setup)
```

**After (Consolidated):**
```
app/__init__.py (single, organized file with 6 sections)
```

This consolidation improves:
- ✓ Clarity (everything in one place)
- ✓ Maintainability (no scattered configuration)
- ✓ Initialization order control (explicit and clear)

---

## Module Status

### ✅ **Fully Implemented**

| Module | Status | Notes |
|--------|--------|-------|
| `app/api/v1/` | ✅ Active | REST API endpoints |
| `app/repositories/` | ✅ Active | Data access layer |
| `app/services/ai/` | ✅ Active | AI service layer |
| `app/ai/configuration/` | ✅ Active | Consolidated from app/ki/ |
| `app/i18n/` | ✅ Active | Multi-language support (20 langs) |
| `app/models/` | ✅ Active | Domain models |
| `app/middleware/` | ✅ Active | Authentication, CORS, rate limiting |
| `app/utils/` | ✅ Active | Utility functions |

### ⚠️ **Stub Modules (Planned Features)**

The following modules are **placeholder structures** for planned features. They have proper `__init__.py` with docstrings explaining their purpose, but contain no implementation:

| Module | Purpose | Timeline | Notes |
|--------|---------|----------|-------|
| `app/services/compliance/` | GDPR/DSA/NetzDG compliance | Phase 3 | Stub for future implementation |
| `app/services/feature_flags/` | Progressive feature rollout | Phase 2 | Stub for future implementation |
| `app/services/drm/` | Digital Rights Management | Phase 3 | Stub for future implementation |
| `app/services/moderation/` | Content moderation orchestration | Phase 2 | Stub for future implementation |
| `app/services/system/` | System-level services | Phase 3 | Stub for future implementation |
| `app/security/drm/` | DRM subsystems | Phase 3 | Multiple stubs (watermarking, encryption, etc.) |
| `app/security/encryption/` | General encryption | Phase 3 | Stub for future implementation |
| `app/monitoring/` | Observability subsystems | Phase 3 | Stubs (alerting, tracing, logging) |
| `app/websocket/` | WebSocket support | Phase 2 | Stub for future implementation |
| `app/ai/generation/` | AI content generation | Phase 2 | Stub for future implementation |
| `app/ai/content_moderation/` | AI moderation integration | Phase 2 | Stub for future implementation |

**Important:** Stub modules have docstrings making their purpose clear:
```python
"""Placeholder module for planned feature implementation."""
```

### ❌ **Removed (Dead Code)**

The following were removed on 2026-01-17 to maintain cleanliness:

| Module | Reason | Date |
|--------|--------|------|
| `app/social/` | Dead code (no implementation) | 2026-01-17 |
| `app/services/social/` | Mirror of app/social/ (empty) | 2026-01-17 |
| `app/compliance/` | 60+ empty stubs (no implementation) | 2026-01-17 |

**Note:** Social API endpoints are implemented in `app/api/v1/social/` (the correct location).

---

## File Size Limits (Quality Gate G04)

All files follow the 500-line maximum:

```bash
# Check file sizes
find app -type f -name "*.py" -exec wc -l {} \; | sort -rn | head -20
```

Current largest files:
- `app/ai/configuration/system_features_mapping.py` (~450 lines)
- `app/ai/configuration/learning_method_mapping.py` (~400 lines)
- `app/ai/configuration/prompt_models.py` (~350 lines)

All are within limits.

---

## Database Layer

### BaseRepository Pattern

All data access goes through `BaseRepository`:

```python
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = "users"
        self.model_class = User

    # Inherits: find_by_id(), find_all(), find_by(), create(), update(), delete()
    # Can extend with custom queries
```

**Methods available on all repositories:**
- `find_by_id(id)` - Get single record
- `find_all(limit, offset)` - Get paginated records
- `find_by(filters)` - Get filtered records
- `create(data)` - Insert new record
- `update(id, data)` - Update record
- `delete(id)` - Delete record
- `count(filters)` - Count records
- `exists(id)` - Check if record exists

---

## API Versioning

Current API version: **v1** (routes at `/api/v1/*`)

**Structure:**
```
/api/v1/
├── /public/ - Unauthenticated endpoints
├── /users/ - User endpoints
├── /courses/ - Course endpoints
├── /admin/ - Admin endpoints
├── /admin-panel/ - Admin panel endpoints
├── /social/ - Social feature endpoints
└── ...
```

---

## Initialization Order (Critical)

The Flask app factory initializes in this specific order:

1. **Extensions** (database pool, JWT, etc.)
2. **Security** (JWT config, CORS, rate limiting)
3. **Error Handlers** (custom exception handlers)
4. **Middleware** (authentication, logging)
5. **Gateway** (route logging, analytics tracking)
6. **Blueprints** (API routes)
7. **Monitoring** (Prometheus metrics, health checks)
8. **Prompts** (AI prompt registry)
9. **WebSocket** (SocketIO events)

**See:** `app/__init__.py`, function `create_app()`

---

## Cleanliness Metrics

**As of 2026-01-17:**

| Metric | Value | Status |
|--------|-------|--------|
| Total directories | 297 | ✅ Reduced from 353 |
| Total Python files | 637 | ✅ Optimized |
| Total `__init__.py` files | 162 | ✅ All documented |
| Empty `__init__.py` files | 0 | ✅ All have docstrings |
| Dead code modules | 0 | ✅ Removed |
| Stub modules with docs | 25+ | ✅ Clearly marked |
| Code duplication | Minimal | ✅ Follows DRY principle |

---

## Migration History

### Latest: 2026-01-17 - App Root Cleanup

**Changes:**
1. ✅ Deleted `app/social/` (dead code)
2. ✅ Deleted `app/services/social/` (dead code)
3. ✅ Deleted `app/compliance/` (60+ empty stubs)
4. ✅ Added docstrings to all remaining stub modules
5. ✅ Documented all stubs as "Placeholder modules for planned features"
6. ✅ Verified structure is clean, structured, and consistent

**Result:** All `__init__.py` files now have purpose, dead code removed, stubs documented.

### Previous: 2026-01-17 - Flask App Factory Consolidation

**Changes:**
1. ✅ Consolidated 5 fragmented `__init__*.py` files into single `app/__init__.py`
2. ✅ Updated `run.py` to import from consolidated location
3. ✅ Verified all imports and registrations still work
4. ✅ Deleted 5 fragmented files

**Files deleted:**
- `app/__init__extensions.py`
- `app/__init__security.py`
- `app/__init__errors.py`
- `app/__init__middleware.py`
- (merged into main `app/__init__.py`)

**Result:** Cleaner, more maintainable application factory.

---

## Best Practices

### When Adding New Features

1. **Create in correct layer:**
   - Route handler → `app/api/v1/[feature]/`
   - Business logic → `app/services/[feature]/`
   - Database queries → `app/repositories/[feature]/`

2. **Keep under 500 lines per file**
   - If exceeding 500 lines, split into logical modules

3. **Add to correct API version**
   - New endpoints go in `app/api/v1/`

4. **Use BaseRepository for all DB access**
   - Never import database directly in routes/services

5. **Document stubs**
   - If creating placeholder structure, add docstring

### When Refactoring

1. **Check consolidation opportunities**
   - Can 3+ small modules be combined?
   - Is there duplication across layers?

2. **Remove dead code immediately**
   - Stale code reduces clarity

3. **Update this documentation**
   - Keep architecture docs in sync with implementation

---

## Related Files

- `app/__init__.py` - Flask application factory (consolidated)
- `run.py` - Application entry point
- `.claude/APP_ROOT_AUDIT_2026-01-17.md` - Detailed audit report
- `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md` - Official documentation

---

**Last Updated:** 2026-01-17
**Status:** ✅ Clean, Structured, Consistent
**Maintainer:** Development Team
