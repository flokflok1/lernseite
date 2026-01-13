# Dashboard Domain - Quick Reference

**Version:** 1.0
**Date:** 2026-01-08

---

## Import Patterns

### Using Core Services (Recommended)

```python
# Import centralized services
from app.api.dashboard.core import (
    DashboardLayoutService,
    DashboardWidgetService,
    DashboardRecommendationService
)

# Use in your code
layout = DashboardLayoutService.get_effective_layout(user)
widgets = DashboardWidgetService.get_available_widgets(user)
recommendations = DashboardRecommendationService.get_recommendations(user)
```

### Using Blueprints (for registration)

```python
# Import blueprints for API registration
from app.api.dashboard import (
    admin_dashboard_bp,         # Admin system dashboard
    layouts_bp,                 # Layout management
    widgets_registry_bp,        # Widget registry
    widgets_instances_bp,       # Widget instances
    recommendations_bp          # KI recommendations
)
```

---

## Service Methods

### DashboardLayoutService

| Method | Args | Returns | Description |
|--------|------|---------|-------------|
| `get_effective_layout(user)` | `user: Dict` | `DashboardLayout` | Get user's layout or role default |
| `save_layout(user, layout)` | `user: Dict, layout: DashboardLayout` | `DashboardLayout` | Save custom layout (Premium+) |
| `reset_layout(user)` | `user: Dict` | `DashboardLayout` | Reset to role default (Premium+) |

**Permissions:**
- `get_effective_layout`: All users
- `save_layout`, `reset_layout`: Premium, Creator, Teacher, School Admin, Company Admin, Admin only

---

### DashboardWidgetService

| Method | Args | Returns | Description |
|--------|------|---------|-------------|
| `get_available_widgets(user)` | `user: Dict` | `List[Dict]` | Get widgets for user's role |
| `get_user_widgets(user, layout_id)` | `user: Dict, layout_id: Optional[str]` | `List[Dict]` | Get user's widget instances |
| `add_widget(user, widget_key, ...)` | `user: Dict, widget_key: str, ...` | `Dict` | Add widget to dashboard |
| `remove_widget(user, widget_instance_id)` | `user: Dict, widget_instance_id: str` | `bool` | Remove widget |
| `update_widget_position(user, ...)` | `user: Dict, widget_instance_id: str, ...` | `Dict` | Update widget position |
| `update_widget_settings(user, ...)` | `user: Dict, widget_instance_id: str, ...` | `Dict` | Update widget settings |
| `toggle_widget_visibility(user, ...)` | `user: Dict, widget_instance_id: str` | `bool` | Toggle visibility |

**Permissions:**
- `get_available_widgets`: All users (filtered by role)
- All other methods: Premium+ roles only

---

### DashboardRecommendationService

| Method | Args | Returns | Description |
|--------|------|---------|-------------|
| `get_recommendations(user, limit, include_dismissed)` | `user: Dict, limit: int = 10, include_dismissed: bool = False` | `List[Dict]` | Get KI recommendations |
| `dismiss_recommendation(user, rec_id)` | `user: Dict, recommendation_id: str` | `bool` | Dismiss recommendation |
| `accept_recommendation(user, rec_id)` | `user: Dict, recommendation_id: str` | `Dict` | Accept and perform action |
| `get_stats(user)` | `user: Dict` | `Dict` | Get recommendation stats |

**Permissions:**
- All methods: Premium+ roles only

---

## API Endpoints

### Admin Endpoints (Admin Only)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/dashboard/admin/system/overview` | GET | System overview stats |
| `/api/v1/dashboard/admin/system/activity?hours=24&limit=50` | GET | Recent activity |
| `/api/v1/dashboard/admin/system/users` | GET | User statistics |
| `/api/v1/dashboard/admin/system/courses` | GET | Course statistics |
| `/api/v1/dashboard/admin/system/ai-usage?days=7` | GET | AI usage stats |

**Headers:**
```
Authorization: Bearer <access_token>
```

**Role Required:** `admin`

---

### User Endpoints (All Users)

#### Layout Management

| Endpoint | Method | Description | Permission |
|----------|--------|-------------|------------|
| `/api/v1/dashboard/layout` | GET | Get dashboard layout | All users |
| `/api/v1/dashboard/layout` | PUT | Save dashboard layout | Premium+ |
| `/api/v1/dashboard/layout/reset` | POST | Reset to default | Premium+ |

#### Widget Management

| Endpoint | Method | Description | Permission |
|----------|--------|-------------|------------|
| `/api/v1/dashboard/widgets` | GET | Available widgets | All users |
| `/api/v1/dashboard/widgets/user?layout_id=<uuid>` | GET | User's widgets | All users |
| `/api/v1/dashboard/widgets/add` | POST | Add widget | Premium+ |
| `/api/v1/dashboard/widgets/{id}` | DELETE | Remove widget | Premium+ |
| `/api/v1/dashboard/widgets/{id}/position` | PATCH | Update position | Premium+ |
| `/api/v1/dashboard/widgets/{id}/settings` | PATCH | Update settings | Premium+ |
| `/api/v1/dashboard/widgets/{id}/toggle` | PATCH | Toggle visibility | Premium+ |

#### KI Recommendations

| Endpoint | Method | Description | Permission |
|----------|--------|-------------|------------|
| `/api/v1/dashboard/recommendations?limit=10&include_dismissed=false` | GET | Get recommendations | Premium+ |
| `/api/v1/dashboard/recommendations/{id}/dismiss` | POST | Dismiss recommendation | Premium+ |
| `/api/v1/dashboard/recommendations/{id}/accept` | POST | Accept recommendation | Premium+ |
| `/api/v1/dashboard/recommendations/stats` | GET | Recommendation stats | Premium+ |

---

## Example Usage

### Get User Dashboard

```python
from app.api.dashboard.core import DashboardLayoutService

def load_user_dashboard(user):
    """Load complete dashboard for user."""
    layout = DashboardLayoutService.get_effective_layout(user)

    return {
        'userId': layout.userId,
        'role': layout.role,
        'widgets': [w.model_dump() for w in layout.widgets],
        'isCustomized': not layout.isDefault
    }
```

### Add Widget with Validation

```python
from app.api.dashboard.core import DashboardWidgetService

def add_widget_safe(user, widget_key, position_x, position_y):
    """Add widget with error handling."""
    try:
        widget = DashboardWidgetService.add_widget(
            user=user,
            widget_key=widget_key,
            position_x=position_x,
            position_y=position_y,
            width=2,
            height=2
        )
        return {'success': True, 'widget': widget}
    except PermissionError as e:
        return {'success': False, 'error': 'permission_denied', 'message': str(e)}
    except ValueError as e:
        return {'success': False, 'error': 'invalid_widget', 'message': str(e)}
```

### Process Recommendations

```python
from app.api.dashboard.core import DashboardRecommendationService

def process_recommendations(user, limit=5):
    """Get and process recommendations."""
    try:
        recommendations = DashboardRecommendationService.get_recommendations(
            user=user,
            limit=limit,
            include_dismissed=False
        )

        # Filter by confidence
        high_confidence = [
            r for r in recommendations
            if r.get('confidence', 0) >= 0.8
        ]

        return high_confidence
    except PermissionError:
        return []  # User is not Premium+
```

---

## Error Handling

### Common Exceptions

| Exception | When | HTTP Code | Handling |
|-----------|------|-----------|----------|
| `PermissionError` | User lacks permission | 403 | Return error message |
| `ValueError` | Invalid input | 400 | Validate and return details |
| `ValidationError` | Pydantic validation failed | 400 | Return field errors |
| `Exception` | Unexpected error | 500 | Log and return generic error |

### Example Error Response

```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Role 'user' cannot customize dashboard. Upgrade to Premium for custom dashboards."
}
```

---

## Testing

### Unit Test Example

```python
import pytest
from app.api.dashboard.core import DashboardLayoutService

def test_get_effective_layout_for_free_user():
    """Test that free user gets role default."""
    user = {'user_id': 123, 'role': 'user'}

    layout = DashboardLayoutService.get_effective_layout(user)

    assert layout.role == 'user'
    assert layout.isDefault is True
    assert layout.source == 'role'

def test_save_layout_permission_denied():
    """Test that free user cannot save layout."""
    user = {'user_id': 123, 'role': 'user'}
    layout = DashboardLayout(userId=123, role='user', widgets=[])

    with pytest.raises(PermissionError, match="cannot customize dashboard"):
        DashboardLayoutService.save_layout(user, layout)
```

### Integration Test Example

```python
def test_get_dashboard_layout_endpoint(client, auth_headers):
    """Test GET /dashboard/layout endpoint."""
    response = client.get('/api/v1/dashboard/layout', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'layout' in data
    assert 'widgets' in data['layout']
```

---

## Performance Tips

### 1. Cache Layout for Session

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_layout(user_id: int, cache_key: str):
    """Cache layout during user session."""
    user = {'user_id': user_id, 'role': get_user_role(user_id)}
    return DashboardLayoutService.get_effective_layout(user)
```

### 2. Batch Widget Queries

```python
def get_widgets_with_instances(user):
    """Get available widgets + user instances in one batch."""
    available = DashboardWidgetService.get_available_widgets(user)
    instances = DashboardWidgetService.get_user_widgets(user)

    # Merge data
    for widget in available:
        widget['user_instances'] = [
            i for i in instances if i['widget_key'] == widget['widget_key']
        ]

    return available
```

---

## Common Patterns

### Role-Based Feature Gates

```python
def is_premium_user(user: Dict) -> bool:
    """Check if user has Premium+ access."""
    premium_roles = [
        'premium', 'creator', 'teacher',
        'school_admin', 'company_admin',
        'admin', 'superadmin'
    ]
    return user.get('role', 'user') in premium_roles

def can_customize_dashboard(user: Dict) -> bool:
    """Check if user can customize dashboard."""
    return is_premium_user(user)
```

### Widget Availability Check

```python
def get_widgets_for_role(role: str) -> List[str]:
    """Get widget keys available for role."""
    user = {'user_id': None, 'role': role}
    widgets = DashboardWidgetService.get_available_widgets(user)
    return [w['widget_key'] for w in widgets if w['is_available']]
```

---

## Troubleshooting

### Issue: Layout not saving

**Symptom:** PUT /dashboard/layout returns 403

**Cause:** User role cannot customize dashboard

**Solution:** Check user role, only Premium+ can customize

---

### Issue: Widget not appearing

**Symptom:** Widget added but not visible

**Cause:** Widget visibility toggled off or requires Premium

**Solution:**
1. Check `is_visible` field
2. Verify user has Premium+ subscription

---

### Issue: Recommendations empty

**Symptom:** GET /recommendations returns empty array

**Cause:** User is not Premium+ OR no recommendations generated yet

**Solution:**
1. Check user role (Premium+ required)
2. Trigger recommendation generation job

---

## Additional Resources

- **Full Refactoring Summary:** `REFACTORING_SUMMARY.md`
- **Structure Diagram:** `STRUCTURE.txt`
- **Backend Documentation:** `/LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`
- **API Specification:** `/LernsystemX-Doku/05_Technical/15_API-Spezifikation.md`

---

**Last Updated:** 2026-01-08
**Version:** 1.0
