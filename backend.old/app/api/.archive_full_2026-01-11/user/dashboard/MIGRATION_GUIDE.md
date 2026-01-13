# Dashboard DDD Migration Guide

**Version:** 1.0
**Date:** 2026-01-08
**Target:** Developers migrating to new dashboard structure

---

## Overview

The dashboard domain has been refactored to follow **Domain-Driven Design (DDD)** pattern with clear separation between:
- **admin/** - System analytics (admin-only)
- **user/** - User-facing features
- **core/** - Shared business logic

---

## Breaking Changes

### 1. Service Imports Changed

#### Old Import Paths (DEPRECATED)

```python
# ❌ DEPRECATED - Do not use
from app.services.dashboard_service import DashboardService
from app.services.dashboard.widget_service import WidgetService
from app.services.dashboard.recommendation_service import RecommendationService
```

#### New Import Paths (USE THESE)

```python
# ✅ NEW - Use these imports
from app.api.dashboard.core import (
    DashboardLayoutService,
    DashboardWidgetService,
    DashboardRecommendationService
)
```

---

### 2. Service Method Names Changed

#### Layout Management

| Old Method | New Method | Notes |
|------------|------------|-------|
| `DashboardService.get_effective_layout()` | `DashboardLayoutService.get_effective_layout()` | Same signature |
| `DashboardService.save_layout()` | `DashboardLayoutService.save_layout()` | Same signature |
| `DashboardService.reset_layout()` | `DashboardLayoutService.reset_layout()` | Same signature |

#### Widget Management

| Old Method | New Method | Notes |
|------------|------------|-------|
| `WidgetService.get_available_widgets()` | `DashboardWidgetService.get_available_widgets()` | Same signature |
| `WidgetService.get_user_widgets()` | `DashboardWidgetService.get_user_widgets()` | Same signature |
| `WidgetService.add_widget()` | `DashboardWidgetService.add_widget()` | Same signature |
| `WidgetService.remove_widget()` | `DashboardWidgetService.remove_widget()` | Same signature |
| `WidgetService.update_widget_position()` | `DashboardWidgetService.update_widget_position()` | Same signature |
| `WidgetService.update_widget_settings()` | `DashboardWidgetService.update_widget_settings()` | Same signature |
| `WidgetService.toggle_widget_visibility()` | `DashboardWidgetService.toggle_widget_visibility()` | Same signature |

#### Recommendation Management

| Old Method | New Method | Notes |
|------------|------------|-------|
| `RecommendationService.get_recommendations()` | `DashboardRecommendationService.get_recommendations()` | Same signature |
| `RecommendationService.dismiss_recommendation()` | `DashboardRecommendationService.dismiss_recommendation()` | Same signature |
| `RecommendationService.accept_recommendation()` | `DashboardRecommendationService.accept_recommendation()` | Same signature |
| `RecommendationService.get_stats()` | `DashboardRecommendationService.get_stats()` | Same signature |

---

## Step-by-Step Migration

### Step 1: Update Imports

**Find and replace in your codebase:**

```bash
# Search for old imports
grep -r "from app.services.dashboard_service import" .
grep -r "from app.services.dashboard.widget_service import" .
grep -r "from app.services.dashboard.recommendation_service import" .

# Replace with new imports
sed -i 's/from app.services.dashboard_service import DashboardService/from app.api.dashboard.core import DashboardLayoutService/g' *.py
sed -i 's/from app.services.dashboard.widget_service import WidgetService/from app.api.dashboard.core import DashboardWidgetService/g' *.py
sed -i 's/from app.services.dashboard.recommendation_service import RecommendationService/from app.api.dashboard.core import DashboardRecommendationService/g' *.py
```

---

### Step 2: Update Service References

**Find and replace service names:**

```bash
# Replace service class names
sed -i 's/DashboardService\./DashboardLayoutService\./g' *.py
sed -i 's/WidgetService\./DashboardWidgetService\./g' *.py
sed -i 's/RecommendationService\./DashboardRecommendationService\./g' *.py
```

---

### Step 3: Test Your Changes

#### Unit Tests

```python
# Example: Update test imports
# BEFORE
from app.services.dashboard_service import DashboardService

def test_get_layout():
    layout = DashboardService.get_effective_layout(user)

# AFTER
from app.api.dashboard.core import DashboardLayoutService

def test_get_layout():
    layout = DashboardLayoutService.get_effective_layout(user)
```

#### Integration Tests

```python
# No changes needed for integration tests
# Endpoints remain the same:
# GET /api/v1/dashboard/layout (unchanged)
# PUT /api/v1/dashboard/layout (unchanged)
# etc.
```

---

## Migration Examples

### Example 1: Simple Layout Loading

#### Before

```python
from app.services.dashboard_service import DashboardService

def get_user_dashboard(user_id):
    user = get_user_by_id(user_id)
    layout = DashboardService.get_effective_layout(user)
    return layout.model_dump()
```

#### After

```python
from app.api.dashboard.core import DashboardLayoutService

def get_user_dashboard(user_id):
    user = get_user_by_id(user_id)
    layout = DashboardLayoutService.get_effective_layout(user)
    return layout.model_dump()
```

**Changes:**
- Import changed: `DashboardService` → `DashboardLayoutService`
- Service call changed: `DashboardService.` → `DashboardLayoutService.`

---

### Example 2: Widget Management

#### Before

```python
from app.services.dashboard.widget_service import WidgetService

def add_course_widget(user, course_id):
    widget = WidgetService.add_widget(
        user=user,
        widget_key='course_progress',
        position_x=0,
        position_y=0,
        width=2,
        height=1,
        custom_settings={'course_id': course_id}
    )
    return widget
```

#### After

```python
from app.api.dashboard.core import DashboardWidgetService

def add_course_widget(user, course_id):
    widget = DashboardWidgetService.add_widget(
        user=user,
        widget_key='course_progress',
        position_x=0,
        position_y=0,
        width=2,
        height=1,
        custom_settings={'course_id': course_id}
    )
    return widget
```

**Changes:**
- Import changed: `WidgetService` → `DashboardWidgetService`
- Service call changed: `WidgetService.` → `DashboardWidgetService.`

---

### Example 3: Recommendations

#### Before

```python
from app.services.dashboard.recommendation_service import RecommendationService

def get_top_recommendations(user, limit=5):
    try:
        recommendations = RecommendationService.get_recommendations(
            user=user,
            limit=limit,
            include_dismissed=False
        )
        return recommendations
    except PermissionError:
        return []
```

#### After

```python
from app.api.dashboard.core import DashboardRecommendationService

def get_top_recommendations(user, limit=5):
    try:
        recommendations = DashboardRecommendationService.get_recommendations(
            user=user,
            limit=limit,
            include_dismissed=False
        )
        return recommendations
    except PermissionError:
        return []
```

**Changes:**
- Import changed: `RecommendationService` → `DashboardRecommendationService`
- Service call changed: `RecommendationService.` → `DashboardRecommendationService.`

---

### Example 4: Complex Dashboard Controller

#### Before

```python
from app.services.dashboard_service import DashboardService
from app.services.dashboard.widget_service import WidgetService
from app.services.dashboard.recommendation_service import RecommendationService

class DashboardController:
    def get_full_dashboard(self, user):
        layout = DashboardService.get_effective_layout(user)
        widgets = WidgetService.get_user_widgets(user)
        recommendations = RecommendationService.get_recommendations(user)

        return {
            'layout': layout.model_dump(),
            'widgets': widgets,
            'recommendations': recommendations
        }
```

#### After

```python
from app.api.dashboard.core import (
    DashboardLayoutService,
    DashboardWidgetService,
    DashboardRecommendationService
)

class DashboardController:
    def get_full_dashboard(self, user):
        layout = DashboardLayoutService.get_effective_layout(user)
        widgets = DashboardWidgetService.get_user_widgets(user)
        recommendations = DashboardRecommendationService.get_recommendations(user)

        return {
            'layout': layout.model_dump(),
            'widgets': widgets,
            'recommendations': recommendations
        }
```

**Changes:**
- Combined imports into single statement
- Updated all service references

---

## Backward Compatibility

### Temporary Compatibility Layer

If you need time to migrate, create a compatibility module:

```python
# app/services/dashboard_service.py (compatibility layer)
"""
Backward compatibility layer for dashboard services.

DEPRECATED: Use app.api.dashboard.core services directly.
This module will be removed in future versions.
"""

from app.api.dashboard.core import (
    DashboardLayoutService,
    DashboardWidgetService,
    DashboardRecommendationService
)

# Alias for backward compatibility
DashboardService = DashboardLayoutService
WidgetService = DashboardWidgetService
RecommendationService = DashboardRecommendationService

# Deprecation warning
import warnings
warnings.warn(
    "app.services.dashboard_service is deprecated. "
    "Use app.api.dashboard.core services instead.",
    DeprecationWarning,
    stacklevel=2
)
```

---

## New Features

### Admin System Dashboard (NEW)

New admin-only endpoints for system analytics:

```python
from app.api.dashboard import admin_dashboard_bp

# Register in your app
app.register_blueprint(admin_dashboard_bp)

# Available endpoints:
# GET /api/v1/dashboard/admin/system/overview
# GET /api/v1/dashboard/admin/system/activity
# GET /api/v1/dashboard/admin/system/users
# GET /api/v1/dashboard/admin/system/courses
# GET /api/v1/dashboard/admin/system/ai-usage
```

---

## Common Migration Issues

### Issue 1: ImportError

**Error:**
```
ImportError: cannot import name 'DashboardService' from 'app.services.dashboard_service'
```

**Solution:**
```python
# Change
from app.services.dashboard_service import DashboardService

# To
from app.api.dashboard.core import DashboardLayoutService
```

---

### Issue 2: AttributeError

**Error:**
```
AttributeError: type object 'DashboardService' has no attribute 'get_effective_layout'
```

**Solution:**
Ensure you've updated the service name:
```python
# Wrong
DashboardService.get_effective_layout(user)

# Correct
DashboardLayoutService.get_effective_layout(user)
```

---

### Issue 3: Old Service Files Still Present

**Issue:** Code still imports from old service files

**Solution:**
1. Check if old service files exist:
   ```bash
   ls app/services/dashboard_service.py
   ls app/services/dashboard/widget_service.py
   ls app/services/dashboard/recommendation_service.py
   ```

2. If they exist, replace them with compatibility layer or delete

---

## Testing Your Migration

### Checklist

- [ ] All imports updated to new paths
- [ ] All service references updated
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing of dashboard features
- [ ] No deprecation warnings in logs

### Test Commands

```bash
# Run backend tests
cd backend
pytest tests/test_dashboard.py -v

# Check for old imports
grep -r "from app.services.dashboard_service" app/
grep -r "from app.services.dashboard.widget_service" app/
grep -r "from app.services.dashboard.recommendation_service" app/

# Should return no results
```

---

## Timeline

### Immediate (Now)
- ✅ New services available
- ✅ All internal endpoints updated
- ✅ Backward compatibility maintained

### Short-term (1-2 weeks)
- Migrate all internal code
- Update tests
- Deploy to staging

### Medium-term (1 month)
- Deploy to production
- Monitor for issues
- Remove old service files

### Long-term (3 months)
- Remove compatibility layer
- Archive old code
- Update documentation

---

## Support

If you encounter issues during migration:

1. **Check this guide:** Most common issues are documented above
2. **Review Quick Reference:** `QUICK_REFERENCE.md`
3. **Review Refactoring Summary:** `REFACTORING_SUMMARY.md`
4. **Check test examples:** Look at updated tests in `tests/test_dashboard.py`

---

## Additional Resources

- **Refactoring Summary:** `REFACTORING_SUMMARY.md`
- **Quick Reference:** `QUICK_REFERENCE.md`
- **Structure Diagram:** `STRUCTURE.txt`
- **Backend Documentation:** `/LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`

---

**Last Updated:** 2026-01-08
**Version:** 1.0
