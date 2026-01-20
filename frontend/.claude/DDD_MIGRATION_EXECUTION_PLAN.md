# Frontend DDD Migration - Comprehensive Execution Plan

**Target:** Reorganize frontend/src/ to match documented structure (v4.0.2)
**Date:** 2026-01-20
**Status:** IN PROGRESS

---

## Current Structure vs Target Structure

### CURRENT (BEFORE):
```
src/
├── /api/                    ← API clients (scattered across domains)
├── /components/             ← ALL components mixed here
├── /pages/ (views)         ← Views scattered
├── /domain/                ← Models scattered
├── /store/                 ← OLD Pinia location
├── /config/                ← Configuration
├── /utils/                 ← Utilities
└── /router/                ← Router
```

### TARGET (AFTER - v4.0.2):
```
src/
├── /presentation/          ← UI LAYER
│   ├── /components/        ← 18 domain-organized components
│   ├── /views/             ← Page views
│   ├── /layouts/           ← Layout components
│   └── /router/            ← Router config
│
├── /application/           ← BUSINESS LOGIC
│   ├── /services/          ← Business logic services
│   ├── /stores/            ← Pinia stores (moved from /store/)
│   ├── /composables/       ← Vue composables
│   └── /use-cases/         ← Use case orchestration
│
├── /domain/                ← DOMAIN MODELS
│   ├── /models/            ← 7 domain-organized models
│   ├── /value-objects/     ← Immutable value objects
│   ├── /factories/         ← Factory pattern
│   ├── /events/            ← Domain events
│   └── /repositories/      ← Repository interfaces
│
├── /infrastructure/        ← EXTERNAL INTEGRATIONS
│   ├── /api/               ← API clients (7 clients)
│   ├── /repositories/      ← Repository implementations
│   ├── /websocket/         ← WebSocket client
│   ├── /cache/             ← Cache layer
│   ├── /i18n/              ← i18n setup
│   └── /persistence/       ← Local storage
│
├── /shared/                ← CROSS-CUTTING
│   ├── /types/             ← Shared types
│   ├── /constants/         ← Constants
│   ├── /utils/             ← Utilities
│   └── /guards/            ← Type guards
│
├── App.vue
└── main.ts
```

---

## 7 Domains to Reorganize

1. **content** - Courses, chapters, lessons, materials
2. **course-editor** - ⭐ Manual + AI editors (NEW domain structure!)
3. **learning** - Learning methods, flashcards, quizzes
4. **social** - Posts, comments, feeds, follows
5. **user** - Auth, profiles, settings
6. **admin** - User management, moderation, feature flags
7. **compliance** - GDPR, COPPA, DSA, age gates, consent
8. **moderation** - Content review, reports
9. **security** - 2FA, sessions, DRM

---

## 8-STEP MIGRATION PLAN

### STEP 1: PRESENTATION LAYER REORGANIZATION
**Files to move:** `src/components/` → `src/presentation/components/`

**Mappings:**
```
src/components/
├── /admin/                → src/presentation/components/admin/
├── /compliance/           → src/presentation/components/compliance/
├── /social/              → src/presentation/components/social/
├── /security/            → src/presentation/components/security/
├── /moderation/          → src/presentation/components/moderation/
├── /feature-flags/       → src/presentation/components/admin/ (move here)
├── /base/                → src/presentation/components/shared/ui/
├── /studio/ (IMPORTANT!) → src/presentation/components/course-editor/
│                            (NO /studio/ parent! Direct as domain)
└── NEW: /content/        ← Consolidate content components here
└── NEW: /learning/       ← Consolidate learning components here
└── NEW: /user/           ← Consolidate user components here
```

**Views mapping:**
```
src/pages/
├── /admin/              → src/presentation/views/admin/
├── /auth/               → src/presentation/views/auth/
├── /courses/            → src/presentation/views/content/
├── /dashboard/          → src/presentation/views/dashboard/
├── /social/             → src/presentation/views/social/
├── /creator/            → src/presentation/views/course-editor/ (ProjectsView, EditorView)
└── /moderation/         → src/presentation/views/moderation/
```

**Router reorganization:**
```
src/router/
├── index.ts             ← Update route paths
├── routes.ts            ← Update component imports
└── guards.ts / middleware.ts ← Keep as-is
```

---

### STEP 2: APPLICATION LAYER REORGANIZATION
**Create:** `src/application/`

**Stores reorganization:**
```
src/store/modules/
├── /content/            → src/application/stores/modules/content/
├── /ai/                 → src/application/stores/modules/course-editor/
├── /course-editor/      → src/application/stores/modules/course-editor/
├── /social/             → src/application/stores/modules/social/
├── /user/               → src/application/stores/modules/user/
└── /core/               → src/application/stores/modules/core/
```

**Services reorganization:**
```
CREATE: src/application/services/
├── /content/
│   ├── CourseService.ts
│   └── LessonService.ts
├── /course-editor/
│   ├── EditorService.ts
│   ├── AIService.ts
│   ├── ChatService.ts
│   ├── VariantService.ts
│   └── TemplateService.ts
├── /social/
├── /user/
├── /admin/
├── /compliance/
└── /moderation/
```

**Composables reorganization:**
```
CREATE/MOVE: src/application/composables/
├── useAuth.ts
├── useSocial.ts
├── useContent.ts
├── useCourseEditor.ts       ← IMPORTANT!
├── useAIEditor.ts           ← IMPORTANT!
├── useFeatureFlags.ts
└── usePagination.ts
```

---

### STEP 3: DOMAIN LAYER REORGANIZATION
**Reorganize:** `src/domain/`

**Models reorganization:**
```
src/domain/models/
├── /content/               ← NEW domain folder
│   ├── /course/            ← Existing models reorganized here
│   │   ├── Course.model.ts
│   │   ├── Chapter.model.ts
│   │   └── Lesson.model.ts
│   └── index.ts
│
├── /course-editor/         ← NEW domain folder (IMPORTANT!)
│   ├── Project.model.ts
│   ├── ChatSession.model.ts
│   ├── GeneratedContent.model.ts
│   ├── Variant.model.ts
│   ├── Template.model.ts
│   └── index.ts
│
├── /social/
│   ├── Post.model.ts
│   ├── Comment.model.ts
│   └── Like.model.ts
│
├── /user/
│   ├── User.model.ts
│   ├── Profile.model.ts
│   └── Session.model.ts
│
├── /compliance/
│   ├── Consent.model.ts
│   └── Report.model.ts
│
└── /moderation/
    ├── ContentReport.model.ts
    └── ModerationAction.model.ts
```

**Value Objects:**
```
src/domain/value-objects/
├── Email.vo.ts
├── UserId.vo.ts
├── PostId.vo.ts
├── CourseId.vo.ts
├── ProjectId.vo.ts          ← NEW for course-editor
└── Timestamp.vo.ts
```

**Factories:**
```
src/domain/factories/
├── /content/
│   ├── Course.factory.ts
│   └── index.ts
├── /course-editor/          ← NEW
│   ├── Project.factory.ts
│   ├── ChatSession.factory.ts
│   ├── Template.factory.ts
│   └── index.ts
├── /social/
└── /user/
```

---

### STEP 4: INFRASTRUCTURE LAYER REORGANIZATION
**Create:** `src/infrastructure/`

**API clients reorganization:**
```
src/infrastructure/api/clients/
├── content.client.ts       ← Consolidate from src/api/content/
├── social.client.ts        ← Consolidate from src/api/social/
├── user.client.ts          ← Consolidate from src/api/core/
├── courseEditor.client.ts  ← NEW (from src/api/ai-editor/)
├── admin.client.ts         ← From src/api/admin/
├── compliance.client.ts    ← From src/api/compliance/
├── moderation.client.ts    ← From src/api/moderation/
├── http.ts                 ← Base client (moved from src/api/)
├── interceptors.ts         ← Auth interceptors
└── api-error.ts            ← Error handling
```

**Repositories:**
```
src/infrastructure/repositories/
├── UserRepository.ts
├── PostRepository.ts
├── CourseRepository.ts
└── ProjectRepository.ts    ← NEW for course-editor
```

**WebSocket:**
```
src/infrastructure/websocket/
├── websocket.client.ts
├── events.ts
└── handlers.ts
```

---

### STEP 5: SHARED LAYER CREATION
**Create:** `src/shared/`

```
src/shared/
├── /types/
│   ├── api.types.ts
│   ├── common.types.ts
│   ├── courseEditor.types.ts
│   └── index.ts
│
├── /constants/
│   ├── api.constants.ts
│   ├── events.constants.ts
│   ├── feature-flags.ts
│   └── errors.ts
│
├── /utils/
│   ├── date.utils.ts
│   ├── format.utils.ts
│   ├── validation.utils.ts
│   └── crypto.utils.ts
│
└── /guards/
    ├── user.guards.ts
    └── post.guards.ts
```

---

### STEP 6: BACKWARD-COMPATIBLE BARRELS
**Generate re-export barrels** at old locations for 12-month backward compatibility:

```
src/api/                    ← Barrel exports pointing to infrastructure
├── content.api.ts          → export * from '@/infrastructure/api/clients/content.client.ts'
├── social.api.ts           → export * from '@/infrastructure/api/clients/social.client.ts'
└── etc...

src/store/                  ← Barrel exports pointing to application
├── modules/
│   ├── content/index.ts    → export * from '@/application/stores/modules/content'
│   └── etc...

src/components/            ← Barrel exports pointing to presentation
├── admin/index.ts         → export * from '@/presentation/components/admin'
└── etc...
```

---

### STEP 7: VALIDATION & TESTING
```bash
npm run validate:imports          # Check all imports resolve
npm run typecheck                 # TypeScript type checking
npm run test                      # Run all tests (maintain >75%)
npm run build                     # Full production build
```

---

### STEP 8: DOCUMENTATION & CLEANUP
- Update `package.json` paths if needed
- Update `tsconfig.json` path aliases
- Delete old `/config/` if empty
- Remove `/pages/` (now `/views/`)
- Update README with new structure

---

## CRITICAL NOTES

### ⭐ COURSE EDITOR IS NOT UNDER /studio/!
```
❌ WRONG:  src/presentation/components/studio/course-editor/
✅ CORRECT: src/presentation/components/course-editor/
```

### 🎯 DOMAINS (Not to be confused with folders):
1. **content** - Course viewing, lessons
2. **course-editor** - MANUAL + AI editors (independent domain!)
3. **learning** - Learning methods, flashcards
4. **social** - Posts, feeds, engagement
5. **user** - Auth, profiles
6. **admin** - Admin panel
7. **compliance** - GDPR, privacy
8. **moderation** - Content review
9. **security** - 2FA, DRM

---

## EXECUTION CHECKLIST

### Phase 1: Presentation Layer (Components)
- [ ] Create `src/presentation/components/` directory structure
- [ ] Move all components from `src/components/*` (8 domains)
- [ ] Move all views from `src/pages/*` (9 views)
- [ ] Move layouts (NEW: create `/layouts/`)
- [ ] Move router config (NEW: create `/router/`)
- [ ] Update ALL imports in components
- [ ] Generate barrel exports at old locations

### Phase 2: Application Layer
- [ ] Create `src/application/` directory structure
- [ ] Move stores from `src/store/modules/` (6 store modules)
- [ ] Create NEW services (`src/application/services/`)
- [ ] Move/create composables
- [ ] Update store imports throughout app
- [ ] Generate barrel exports

### Phase 3: Domain Layer
- [ ] Reorganize models into 7 domains
- [ ] Move value-objects
- [ ] Move factories
- [ ] Create domain events (if not exists)
- [ ] Create repository interfaces

### Phase 4: Infrastructure Layer
- [ ] Create `src/infrastructure/api/clients/`
- [ ] Consolidate API clients (7 clients)
- [ ] Create repository implementations
- [ ] Move WebSocket client
- [ ] Move cache layer
- [ ] Move i18n setup
- [ ] Move persistence layer

### Phase 5: Shared Layer
- [ ] Create `src/shared/` directory structure
- [ ] Move/create types
- [ ] Move/create constants
- [ ] Move/create utils
- [ ] Move type guards

### Phase 6: Backward Compatibility
- [ ] Run `npm run validate:imports`
- [ ] Generate barrels with `scripts/generate-barrels.js`
- [ ] Verify all old imports still work

### Phase 7: Validation
- [ ] Run `npm run typecheck`
- [ ] Run `npm run test`
- [ ] Run `npm run build`
- [ ] Check bundle size didn't increase

### Phase 8: Cleanup
- [ ] Delete old empty directories
- [ ] Update documentation
- [ ] Create migration summary

---

## TIME ESTIMATE

- Phase 1 (Presentation): 2-3 hours
- Phase 2 (Application): 1-2 hours
- Phase 3 (Domain): 1 hour
- Phase 4 (Infrastructure): 1-2 hours
- Phase 5 (Shared): 30 mins
- Phase 6 (Barrels): 15 mins
- Phase 7 (Validation): 30 mins
- Phase 8 (Cleanup): 30 mins

**TOTAL: 7-10 hours**

---

**Status:** Phase 1 COMPLETE - Presentation Layer ✅
**Current:** Phase 2 IN PROGRESS - Application Layer
**Next:** Phase 2 - Complete Application Layer Structure

## PHASE 1 COMPLETION SUMMARY (2026-01-20)

✅ **All Presentation Layer Files Copied:**
- Components: 8 domain folders moved to `src/presentation/components/`
- Views: 7 view folders moved to `src/presentation/views/`
- Router: Configuration moved to `src/presentation/router/`
- Course Editor: Correctly placed as direct domain (NOT under /studio/)

**Old Directories Still Exist (for validation before deletion):**
- `src/components/` - OLD
- `src/pages/` - OLD
- `src/router/` - OLD (partial)

---

## PHASE 2 PROGRESS (2026-01-20)

✅ **Stores Already Migrated to Application Layer:**
- `src/application/stores/modules/` - All stores moved (14 store files across 8 domains)
- Index.ts files created for each domain module
- Updated `src/store/index.ts` with backward-compatible barrel exports

✅ **Created Application Layer Structure:**
- `src/application/services/` - Created with 8 domain subdirectories
- `src/application/composables/` - Created for Vue 3 hooks
- `src/application/index.ts` - Created main barrel export
- `src/application/stores/index.ts` - Created stores barrel export

**Remaining Phase 2 Tasks:**
- [ ] Find and consolidate existing services into application/services/
- [ ] Find and consolidate existing composables into application/composables/
- [ ] Create @/ path imports for services and composables
- [ ] Update all imports throughout codebase
