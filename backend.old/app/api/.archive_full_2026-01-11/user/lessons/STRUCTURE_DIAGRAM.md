# Lessons API - Structure Diagram

**Current Structure (Production-Ready)**

```
lessons/ (878 LOC total)
│
├── __init__.py (44 LOC)
│   └── Registers: video_operations_bp, video_config_bp
│
├── explanations.py (281 LOC)
│   ├── GET /lessons/{id}/explanations     [USER + ADMIN]
│   ├── GET /lesson-explanation/{id}       [USER + ADMIN]
│   ├── PATCH /lesson-explanation/{id}     [ADMIN]
│   └── DELETE /lesson-explanation/{id}    [ADMIN]
│
└── videos/
    ├── __init__.py (49 LOC)
    │   └── Re-exports from operations.py + config.py
    │
    ├── operations.py (348 LOC) ⭐ Largest file
    │   ├── GET /lessons/{id}/video        [USER + ADMIN]
    │   ├── POST /lessons/{id}/video       [ADMIN] - Sora 2 generation
    │   ├── GET /lessons/{id}/video/status [USER + ADMIN]
    │   ├── DELETE /lessons/{id}/video     [ADMIN]
    │   └── GET /lessons/{id}/audio        [USER + ADMIN]
    │
    └── config.py (156 LOC)
        ├── GET /video/avatar-styles       [PUBLIC]
        ├── GET /video/sora-status         [USER + ADMIN]
        └── GET /video/models              [PUBLIC]
```

---

## Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Files** | 5 | ✅ Manageable |
| **Total LOC** | 878 | ✅ Reasonable |
| **Largest File** | 348 LOC | ✅ Under 500 limit |
| **Avg LOC/File** | 176 | ✅ Good |
| **Endpoints** | 12 | ✅ Clear separation |
| **Role Separation** | Mixed | ⚠️ Could improve |

---

## Optional DDD Structure (IF Refactoring)

```
lessons/ (Same 878 LOC, reorganized)
│
├── __init__.py
│   └── Barrel exports from admin/, user/, config/
│
├── admin/                          [ADMIN ONLY]
│   ├── __init__.py
│   ├── explanations.py             # PATCH, DELETE explanation
│   ├── video_generation.py         # POST video generation
│   └── video_management.py         # DELETE video
│
├── user/                           [USER + ADMIN]
│   ├── __init__.py
│   ├── explanations.py             # GET explanations
│   └── videos.py                   # GET video, audio, status
│
└── config/                         [PUBLIC]
    ├── __init__.py
    └── video_models.py             # Avatar styles, Sora, models
```

**Trade-offs:**
- ✅ Clearer role boundaries
- ✅ Easier permission auditing
- ❌ More files to maintain
- ❌ More complex imports
- ❌ Higher refactoring effort

---

## Decision Matrix

| Criteria | Keep Current | DDD Refactor |
|----------|--------------|--------------|
| **Complexity** | ⭐ Low | ⭐⭐⭐ Medium |
| **Maintainability** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Effort** | 0 hours | 5.5 hours |
| **Risk** | None | Medium |
| **ROI** | N/A | **LOW** |

**Recommendation:** ✅ **KEEP CURRENT STRUCTURE**

---

## Service Layer Architecture

```
API Layer (lessons/)
     │
     ├── explanations.py
     │   └── Direct DB access (fetch_one, fetch_all)
     │
     └── videos/
         ├── operations.py
         │   └── LessonVideoService
         │       └── app.services.lesson_video/
         │           ├── generator.py
         │           ├── cache.py
         │           └── sora_client.py
         │
         └── config.py
             └── LessonVideoService
                 └── AVATAR_STYLES, get_available_models()
```

**Notes:**
- Explanations use **direct DB access** (simple CRUD)
- Videos use **service layer** (complex generation logic)
- Service already extracted → No factory needed in API layer

---

## External Dependencies

```
lessons/
├── Middleware
│   └── @token_required (app.middleware.auth)
│
├── Extensions
│   └── @limiter.limit() (app.extensions)
│
├── Database
│   └── fetch_one(), fetch_all() (app.database.connection)
│
└── Services
    └── LessonVideoService (app.services.lesson_video)
        ├── Sora 2 API Client
        ├── Video Cache Manager
        └── Audio Extraction
```

---

## API Contract Summary

### Explanations Domain (4 endpoints)

| Method | Path | Auth | Role | Purpose |
|--------|------|------|------|---------|
| GET | `/lessons/{id}/explanations` | ✅ | User+ | List all explanations |
| GET | `/lesson-explanation/{id}` | ✅ | User+ | Get explanation details |
| PATCH | `/lesson-explanation/{id}` | ✅ | Admin | Update title |
| DELETE | `/lesson-explanation/{id}` | ✅ | Admin | Delete explanation |

### Videos Domain (8 endpoints)

#### Operations (5 endpoints)
| Method | Path | Auth | Role | Purpose |
|--------|------|------|------|---------|
| GET | `/lessons/{id}/video` | ✅ | User+ | Get cached video |
| POST | `/lessons/{id}/video` | ✅ | Admin | Generate with Sora 2 |
| GET | `/lessons/{id}/video/status` | ✅ | User+ | Check generation status |
| DELETE | `/lessons/{id}/video` | ✅ | Admin | Delete cached video |
| GET | `/lessons/{id}/audio` | ✅ | User+ | Get audio track |

#### Config (3 endpoints)
| Method | Path | Auth | Role | Purpose |
|--------|------|------|------|---------|
| GET | `/video/avatar-styles` | ❌ | Public | List avatar styles |
| GET | `/video/sora-status` | ✅ | User+ | Check Sora API status |
| GET | `/video/models` | ❌ | Public | Compare Sora models |

---

## Performance Characteristics

| Endpoint | Response Time | Caching | Cost |
|----------|---------------|---------|------|
| `GET /explanations` | <100ms | DB only | Free |
| `GET /video` (cached) | <500ms | File cache | Free |
| `POST /video` (generate) | 30-120s | Async job | $12-24 |
| `GET /video/status` | <50ms | In-memory | Free |
| `GET /config/*` | <50ms | Static | Free |

---

## Future Growth Scenarios

**Scenario 1:** Videos grow to 500+ LOC
- **Action:** Split `operations.py` → `generation.py` + `streaming.py`
- **Effort:** 2 hours
- **Risk:** Low

**Scenario 2:** Role-based permissions required
- **Action:** Full DDD refactoring (admin/user split)
- **Effort:** 5.5 hours
- **Risk:** Medium

**Scenario 3:** New content types (slides, PDFs)
- **Action:** Add `slides/` subdomain (parallel to `videos/`)
- **Effort:** 4 hours
- **Risk:** Low

---

**END OF DIAGRAM**
