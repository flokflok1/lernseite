# ORPHANED FILES ANALYSIS REPORT
**Date:** 2026-02-10
**Status:** Phase 1 Complete - Categorization
**Total Files:** 27 orphaned files (6,000+ lines)

---

## ROOT CAUSE ANALYSIS

### Discovery
These files are NOT dead code - they contain **fully functional API endpoints, services, and features** that are simply **not registered/integrated** into the application routing system.

### Root Cause
1. **API Routes** - Blueprints created but never registered in `/api/v1/__init__.py`
2. **Services** - Service classes defined but never imported by consumers
3. **Setup Scripts** - One-time diagnostic scripts that can be archived
4. **Domain Mappings** - Configuration files that should be in different locations

---

## CATEGORIZATION

### Category A: INTEGRATE (Priority 1) - 15 files, ~3,500 LOC
**Action:** Register blueprints or integrate into active codebase

#### A1. Dashboard Endpoints (497 LOC)
- **File:** `app/api/v1/dashboard/widgets.py`
- **Issue:** Creates `widgets_registry_bp` and `widgets_instances_bp` but never registered
- **Fix:** Add to `api/v1/__init__.py`:
  ```python
  from app.api.v1.dashboard.widgets import widgets_registry_bp, widgets_instances_bp
  api_v1.register_blueprint(widgets_registry_bp)
  api_v1.register_blueprint(widgets_instances_bp)
  ```

#### A2. Dashboard Layouts (228 LOC)
- **File:** `app/api/v1/dashboard/layouts.py`
- **Issue:** Blueprint not registered
- **Fix:** Integrate blueprint registration

#### A3. Dashboard Recommendations (213 LOC)
- **File:** `app/api/v1/dashboard/recommendations.py`
- **Issue:** Blueprint not registered
- **Fix:** Integrate blueprint registration

#### A4. Admin System Dashboard (289 LOC)
- **File:** `app/api/v1/dashboard/admin_system.py`
- **Issue:** Blueprint not registered
- **Fix:** Integrate blueprint registration

#### A5. Course Prompts (305 LOC)
- **File:** `app/api/v1/course_editor/manual_editor/course_prompts.py`
- **Issue:** Imported in `__init__.py` line 31 but blueprint not registered
- **Fix:** Verify blueprint registration in course_editor_bp

#### A6. Course Files (349 LOC)
- **File:** `app/api/v1/course_editor/manual_editor/course_files.py`
- **Issue:** Imported but blueprint not registered
- **Fix:** Register in course_editor system

#### A7. Theory Sheets (446 LOC)
- **File:** `app/api/v1/course_editor/manual_editor/theory_sheets.py`
- **Issue:** Imported but blueprint not registered
- **Fix:** Register in course_editor system

#### A8. Publishing Decisions (286 LOC)
- **File:** `app/api/v1/course_editor/shared/publishing_decisions.py`
- **Issue:** Blueprint not registered
- **Fix:** Integrate into publishing workflow

#### A9. Publishing Queue (136 LOC)
- **File:** `app/api/v1/course_editor/shared/publishing_queue.py`
- **Issue:** Blueprint not registered
- **Fix:** Integrate into publishing workflow

#### A10. Publishing Visibility (131 LOC)
- **File:** `app/api/v1/course_editor/shared/publishing_visibility.py`
- **Issue:** Blueprint not registered
- **Fix:** Integrate into publishing workflow

#### A11. AI Usage Stats (102 LOC)
- **File:** `app/api/v1/admin/settings/ai/ai_usage_stats.py`
- **Issue:** Blueprint not registered
- **Fix:** Add to admin settings

#### A12. Course AI Settings (437 LOC)
- **File:** `app/api/v1/admin/courses/course_ai_settings.py`
- **Issue:** Listed in `admin/courses/__init__.py` but never registered
- **Fix:** Extract blueprint and register

#### A13. Course Analytics (436 LOC)
- **File:** `app/api/v1/admin/courses/course_analytics.py`
- **Issue:** Listed in `admin/courses/__init__.py` but never registered
- **Fix:** Extract blueprint and register

#### A14. Prompts System Admin CRUD (98 LOC)
- **File:** `app/api/v1/prompts_system/admin_crud.py`
- **Issue:** Blueprint not registered
- **Fix:** Integrate into prompts system

#### A15. Prompts System Categories (148 LOC)
- **File:** `app/api/v1/prompts_system/admin_categories.py`
- **Issue:** Blueprint not registered
- **Fix:** Integrate into prompts system

---

### Category B: MOVE TO DOMAIN/CONFIG (Priority 2) - 3 files, ~800 LOC
**Action:** These are configuration/domain files in wrong location

#### B1. System Features Mapping (477 LOC)
- **File:** `app/domain/ai/configuration/system_features_mapping.py`
- **Issue:** Domain configuration in AI folder, should be in `app/domain/features/`
- **Status:** Not imported anywhere (dead?)
- **Fix:** Move to `app/domain/features/system_features_config.py` OR delete if superseded by database

#### B2. Validation Exception Wrapper (244 LOC)
- **File:** `app/infrastructure/utils/validation_exception_wrapper.py`
- **Issue:** Error handling utility not imported
- **Status:** Check if replaced by `app/infrastructure/i18n/error_codes.py`
- **Fix:** Delete if obsolete, integrate if still needed

#### B3. Message Codes (116 LOC)
- **File:** `app/infrastructure/i18n/message_codes.py`
- **Issue:** Message code definitions not imported
- **Status:** Check if replaced by `error_codes.py`
- **Fix:** Delete if obsolete

---

### Category C: ARCHIVE (Priority 3) - 4 files, ~1,000 LOC
**Action:** One-time setup/diagnostic scripts - move to `_archive/setup/`

#### C1. Verify Final (224 LOC)
- **File:** `app/setup/diagnostics/verify_final.py`
- **Issue:** Post-installation verification (one-time use)
- **Fix:** Move to `_archive/setup/diagnostics/`

#### C2. Install (295 LOC)
- **File:** `app/setup/diagnostics/install.py`
- **Issue:** Installation script (one-time use)
- **Fix:** Move to `_archive/setup/diagnostics/`

#### C3. Environment Setup (306 LOC)
- **File:** `app/setup/initialization/environment.py`
- **Issue:** Environment initialization (one-time use)
- **Fix:** Move to `_archive/setup/initialization/`

#### C4. Prompts System Actions (103 LOC)
- **File:** `app/api/v1/prompts_system/admin_actions.py`
- **Issue:** Prompts system actions (might be superseded)
- **Fix:** Verify if still needed, archive if obsolete

---

### Category D: DELETE (Priority 4) - 5 files, ~900 LOC
**Action:** Truly dead code - superseded or never used

#### D1. LM Registry (241 LOC)
- **File:** `app/application/services/plugins/lm_registry.py`
- **Issue:** Plugin registry singleton - check if used
- **Status:** Search for `LMPluginRegistry` usage
- **Fix:** Delete if no references

#### D2. LM Discovery (135 LOC)
- **File:** `app/application/services/plugins/lm_discovery.py`
- **Issue:** Plugin discovery service
- **Status:** Search for usage
- **Fix:** Delete if no references

#### D3. Permission Repository (100 LOC)
- **File:** `app/infrastructure/persistence/repositories/admin/permission_repository.py`
- **Issue:** Admin permission repository
- **Status:** Check if GBA (Group-Based Auth) uses this
- **Fix:** Delete if superseded by core.permissions

#### D4. System Catalog (407 LOC)
- **File:** `app/infrastructure/persistence/repositories/features/system_catalog.py`
- **Issue:** System features catalog
- **Status:** Check if database-driven now
- **Fix:** Delete if superseded

#### D5. Maintenance Mode Middleware (166 LOC)
- **File:** `app/api/middleware/maintenance_mode.py`
- **Issue:** Maintenance mode middleware
- **Status:** Check if used in app factory
- **Fix:** Integrate if needed, delete if not

---

## IMPACT SUMMARY

| Category | Files | LOC | Action | Priority |
|----------|-------|-----|--------|----------|
| **A: INTEGRATE** | 15 | 3,500 | Register blueprints | 🔴 HIGH |
| **B: RELOCATE** | 3 | 800 | Move to correct location | 🟠 MEDIUM |
| **C: ARCHIVE** | 4 | 1,000 | Move to _archive/ | 🟡 LOW |
| **D: DELETE** | 5 | 900 | Delete if unused | 🟢 LOWEST |
| **TOTAL** | 27 | 6,200 | - | - |

---

## RECOMMENDED ACTION PLAN

### Phase 1A: Quick Wins - Dashboard Integration (30 min)
1. Register `widgets_registry_bp`, `widgets_instances_bp` in `api/v1/__init__.py`
2. Register `layouts_bp`, `recommendations_bp`, `admin_system_bp`
3. Test `/api/v1/dashboard/widgets` endpoint
4. **Impact:** +1,500 LOC activated

### Phase 1B: Course Editor Integration (45 min)
1. Verify `course_editor_bp` registration
2. Check if `course_prompts`, `course_files`, `theory_sheets` blueprints are exposed
3. Fix registration chain
4. **Impact:** +1,100 LOC activated

### Phase 1C: Admin Courses Integration (30 min)
1. Register `course_ai_settings_bp`, `course_analytics_bp`
2. Test admin endpoints
3. **Impact:** +900 LOC activated

### Phase 2: Relocate Domain Files (15 min)
1. Check if `system_features_mapping.py` is database-driven now
2. Delete if obsolete, move if needed
3. **Impact:** +800 LOC cleaned

### Phase 3: Archive Setup Scripts (10 min)
1. Create `_archive/setup/` folder
2. Move all setup/diagnostic scripts
3. **Impact:** +1,000 LOC archived

### Phase 4: Delete Dead Code (20 min)
1. Search for `LMPluginRegistry`, `LMDiscovery`, etc.
2. Confirm no usage
3. Delete files
4. **Impact:** +900 LOC deleted

---

## NEXT STEPS

1. **Review this report** - Confirm categorization
2. **Start Phase 1A** - Dashboard integration (highest ROI)
3. **Test each phase** - Ensure no regressions
4. **Update documentation** - Reflect new active endpoints

---

**Status:** READY FOR REVIEW
**Owner:** Pascal
**Estimated Total Time:** 2-3 hours
**Expected Result:** 3,500+ LOC of working API endpoints activated, 1,900+ LOC cleaned up
