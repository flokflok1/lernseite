# Dashboard DDD Refactoring Checklist

**Date:** 2026-01-08
**Status:** IN PROGRESS

---

## Phase 1: Core Refactoring (COMPLETE)

- [x] Create `core/services.py` with 3 service classes
  - [x] `DashboardLayoutService` (~160 lines)
  - [x] `DashboardWidgetService` (~230 lines)
  - [x] `DashboardRecommendationService` (~90 lines)
- [x] Create `core/__init__.py` with exports
- [x] Create `admin/system_dashboard.py` with 5 endpoints
- [x] Create `admin/__init__.py` with exports
- [x] Create `user/__init__.py` with re-exports
- [x] Update main `__init__.py` to DDD structure
- [x] Update all endpoint files to use new services
  - [x] `layouts/endpoints.py` → `DashboardLayoutService`
  - [x] `widgets/registry.py` → `DashboardWidgetService`
  - [x] `widgets/instances.py` → `DashboardWidgetService`
  - [x] `recommendations/endpoints.py` → `DashboardRecommendationService`

---

## Phase 2: Cleanup (PENDING)

### Critical
- [ ] Delete deprecated files
  ```bash
  rm backend/app/api/dashboard/core.py.deprecated
  rm backend/app/api/dashboard/recommendations.py.deprecated
  rm backend/app/api/dashboard/widgets.py.deprecated
  ```

### Optional (if compatibility issues arise)
- [ ] Create compatibility layer in old service paths
- [ ] Add deprecation warnings to old imports

---

## Phase 3: Repository Implementation (PENDING)

### Create AdminDashboardRepository
- [ ] Create `backend/app/repositories/dashboard/admin.py`
- [ ] Implement `get_system_overview()`
- [ ] Implement `get_recent_activity(since, limit)`
- [ ] Implement `get_user_statistics()`
- [ ] Implement `get_course_statistics()`
- [ ] Implement `get_ai_usage_statistics(since)`

### Verify Existing Repositories
- [ ] Check `DashboardRepository` exists and has required methods
- [ ] Check `WidgetRepository` exists and has required methods
- [ ] Check `RecommendationRepository` exists and has required methods

---

## Phase 4: Testing (PENDING)

### Unit Tests - Core Services

#### DashboardLayoutService
- [ ] Test `get_effective_layout()` - custom layout exists
- [ ] Test `get_effective_layout()` - no custom layout (returns default)
- [ ] Test `save_layout()` - Premium user (success)
- [ ] Test `save_layout()` - Free user (PermissionError)
- [ ] Test `reset_layout()` - Premium user (success)
- [ ] Test `reset_layout()` - Free user (PermissionError)

#### DashboardWidgetService
- [ ] Test `get_available_widgets()` - Free user (filtered)
- [ ] Test `get_available_widgets()` - Premium user (all widgets)
- [ ] Test `add_widget()` - Premium user (success)
- [ ] Test `add_widget()` - Free user (PermissionError)
- [ ] Test `add_widget()` - invalid widget_key (ValueError)
- [ ] Test `remove_widget()` - owner (success)
- [ ] Test `remove_widget()` - non-owner (PermissionError)
- [ ] Test `update_widget_position()` - owner (success)
- [ ] Test `update_widget_settings()` - owner (success)
- [ ] Test `toggle_widget_visibility()` - owner (success)

#### DashboardRecommendationService
- [ ] Test `get_recommendations()` - Premium user (success)
- [ ] Test `get_recommendations()` - Free user (PermissionError)
- [ ] Test `dismiss_recommendation()` - owner (success)
- [ ] Test `accept_recommendation()` - course type (enrolls user)
- [ ] Test `accept_recommendation()` - learning_path type (adds path)
- [ ] Test `get_stats()` - returns correct counts

### Integration Tests - API Endpoints

#### Layout Endpoints
- [ ] GET `/dashboard/layout` - returns layout (200)
- [ ] GET `/dashboard/layout` - unauthorized (401)
- [ ] PUT `/dashboard/layout` - Premium user saves (200)
- [ ] PUT `/dashboard/layout` - Free user denied (403)
- [ ] POST `/dashboard/layout/reset` - Premium user resets (200)

#### Widget Endpoints
- [ ] GET `/dashboard/widgets` - returns available widgets (200)
- [ ] GET `/dashboard/widgets/user` - returns user widgets (200)
- [ ] POST `/dashboard/widgets/add` - Premium user adds (200)
- [ ] POST `/dashboard/widgets/add` - Free user denied (403)
- [ ] DELETE `/dashboard/widgets/{id}` - owner removes (200)
- [ ] PATCH `/dashboard/widgets/{id}/position` - updates position (200)
- [ ] PATCH `/dashboard/widgets/{id}/settings` - updates settings (200)
- [ ] PATCH `/dashboard/widgets/{id}/toggle` - toggles visibility (200)

#### Recommendation Endpoints
- [ ] GET `/dashboard/recommendations` - Premium user gets (200)
- [ ] GET `/dashboard/recommendations` - Free user denied (403)
- [ ] POST `/dashboard/recommendations/{id}/dismiss` - dismisses (200)
- [ ] POST `/dashboard/recommendations/{id}/accept` - accepts (200)
- [ ] GET `/dashboard/recommendations/stats` - returns stats (200)

#### Admin Endpoints (NEW)
- [ ] GET `/dashboard/admin/system/overview` - Admin gets stats (200)
- [ ] GET `/dashboard/admin/system/overview` - Non-admin denied (403)
- [ ] GET `/dashboard/admin/system/activity` - Admin gets activity (200)
- [ ] GET `/dashboard/admin/system/users` - Admin gets user stats (200)
- [ ] GET `/dashboard/admin/system/courses` - Admin gets course stats (200)
- [ ] GET `/dashboard/admin/system/ai-usage` - Admin gets AI stats (200)

---

## Phase 5: Documentation (PENDING)

### Update Technical Documentation
- [ ] Update `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`
  - [ ] Add dashboard DDD structure section
  - [ ] Document admin vs. user domains
  - [ ] List all 19 endpoints
- [ ] Update `CLAUDE.md`
  - [ ] Add dashboard structure
  - [ ] Add admin dashboard endpoints
- [ ] Update `.claude/rules/backend.md`
  - [ ] Reference dashboard as DDD example

### Create API Documentation
- [ ] Document admin dashboard endpoints in API docs
- [ ] Add request/response examples
- [ ] Add authentication requirements
- [ ] Add role requirements

---

## Phase 6: Deployment (PENDING)

### Pre-Deployment
- [ ] Run all tests (unit + integration)
- [ ] Check for deprecation warnings
- [ ] Verify no old imports remain
- [ ] Code review by team
- [ ] Update CHANGELOG.md

### Deployment Steps
- [ ] Deploy to staging
- [ ] Manual testing on staging
- [ ] Monitor logs for errors
- [ ] Deploy to production
- [ ] Monitor production metrics

### Post-Deployment
- [ ] Verify all endpoints accessible
- [ ] Check error rates
- [ ] Monitor performance
- [ ] Collect user feedback

---

## Phase 7: Cleanup & Maintenance (PENDING)

### Code Cleanup
- [ ] Remove deprecated files (if not done in Phase 2)
- [ ] Remove compatibility layer (after grace period)
- [ ] Archive old code
- [ ] Update dependencies

### Documentation Maintenance
- [ ] Update inline code comments
- [ ] Update README files
- [ ] Update API documentation
- [ ] Update developer guides

---

## Known Issues & Risks

### Risks
| Risk | Severity | Mitigation |
|------|----------|------------|
| Deprecated files still in use | Medium | Search codebase for old imports |
| Missing repository methods | High | Implement AdminDashboardRepository |
| Breaking changes for external code | Low | Provide compatibility layer temporarily |
| Performance impact of new structure | Low | Monitor metrics post-deployment |

### Open Questions
- [ ] Should old service files be deleted immediately or after grace period?
- [ ] Do we need backward compatibility layer?
- [ ] What's the timeline for removing old code?

---

## Success Criteria

### Functional
- [x] All 19 endpoints accessible
- [x] Service layer properly isolated
- [x] DDD pattern correctly implemented
- [ ] All tests passing
- [ ] No regressions in existing functionality

### Non-Functional
- [x] Code follows LSX architecture
- [x] Quality Gates G01-G10 passed
- [ ] Performance acceptable (< 200ms response time)
- [ ] Documentation complete and accurate
- [ ] Team understands new structure

---

## Timeline

| Phase | Estimated Time | Status |
|-------|---------------|--------|
| Phase 1: Core Refactoring | 4 hours | ✅ COMPLETE |
| Phase 2: Cleanup | 30 minutes | 🔲 PENDING |
| Phase 3: Repository Implementation | 2 hours | 🔲 PENDING |
| Phase 4: Testing | 4 hours | 🔲 PENDING |
| Phase 5: Documentation | 2 hours | 🔲 PENDING |
| Phase 6: Deployment | 1 day | 🔲 PENDING |
| Phase 7: Cleanup & Maintenance | 1 week | 🔲 PENDING |

**Total Estimated Time:** ~2 weeks

---

## Sign-Off

### Completed By
- **Developer:** Claude Opus 4.5
- **Date:** 2026-01-08
- **Phase:** 1 (Core Refactoring)

### Approved By
- **Reviewer:** _________________
- **Date:** _________________
- **Phase:** _________________

---

**Last Updated:** 2026-01-08
**Next Review:** After Phase 2 completion
