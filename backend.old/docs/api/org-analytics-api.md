# Organisation Analytics API Documentation

**Version:** 1.0.0
**Phase:** B10
**Base URL:** `/api/v1/organisations/{org_id}/analytics`

---

## Overview

The Organisation Analytics API provides organisation-specific analytics endpoints for organisation administrators (school admins, company admins, teachers). These endpoints require `VIEW_ORG_ANALYTICS` permission and enforce multi-tenancy (users can only access their own organisation's data).

### Features

- **Multi-Tenancy:** Users can only access data from their own organisation
- **Time Series Data:** Organisation events and active members over time
- **Top Lists:** Most popular courses and modules within the organisation
- **Flexible Filtering:** Support for date ranges and custom dates
- **Performance Optimized:** Organisation-scoped queries with proper indexes

---

## Authentication

All endpoints require a valid JWT access token:

```http
Authorization: Bearer <access_token>
```

### Required Permission

```
VIEW_ORG_ANALYTICS
```

Granted to roles: `teacher`, `school_admin`, `company_admin`, `admin`, `superadmin`

### Multi-Tenancy Rules

- Users with `organisation_id` can **only** access analytics for their own organisation
- `admin` and `superadmin` roles can access **any** organisation's analytics
- Attempting to access another organisation's data returns `403 Forbidden`

---

## Endpoints

### 1. Get Organisation Events Time Series

Retrieve organisation-specific events aggregated by day.

**Endpoint:**
```
GET /api/v1/organisations/{org_id}/analytics/events/time-series
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | integer | Yes | Organisation ID |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `range` | string | No | `7d` | Time range: `7d`, `30d`, `90d` |
| `from` | string | No | - | Start date (YYYY-MM-DD) |
| `to` | string | No | - | End date (YYYY-MM-DD) |

**Example Requests:**

```bash
# Last 7 days for organisation 5
curl -X GET "https://api.lernsystemx.com/api/v1/organisations/5/analytics/events/time-series" \
  -H "Authorization: Bearer <token>"

# Last 30 days
curl -X GET "https://api.lernsystemx.com/api/v1/organisations/5/analytics/events/time-series?range=30d" \
  -H "Authorization: Bearer <token>"

# Custom date range
curl -X GET "https://api.lernsystemx.com/api/v1/organisations/5/analytics/events/time-series?from=2025-01-01&to=2025-01-15" \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "date": "2025-01-15",
      "value": 42
    },
    {
      "date": "2025-01-16",
      "value": 58
    }
  ],
  "total": 100
}
```

**Error Responses:**

| Code | Description |
|------|-------------|
| 400 | Invalid date format |
| 401 | Unauthorized |
| 403 | Forbidden (user not in organisation) |
| 500 | Server error |

---

### 2. Get Organisation Active Members Time Series

Retrieve count of unique active members per day within the organisation.

**Endpoint:**
```
GET /api/v1/organisations/{org_id}/analytics/active-members/time-series
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | integer | Yes | Organisation ID |

**Query Parameters:**

Same as Events Time Series (see above).

**Example Request:**

```bash
curl -X GET "https://api.lernsystemx.com/api/v1/organisations/5/analytics/active-members/time-series?range=30d" \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "date": "2025-01-15",
      "value": 12
    },
    {
      "date": "2025-01-16",
      "value": 15
    }
  ],
  "total": 27
}
```

**Note:** `total` represents the peak number of unique active members across any single day.

---

### 3. Get Organisation Top Courses

Retrieve top courses by activity within the organisation.

**Endpoint:**
```
GET /api/v1/organisations/{org_id}/analytics/top-courses
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | integer | Yes | Organisation ID |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | `10` | Number of top courses (max: 100) |
| `range` | string | No | - | Time range: `7d`, `30d`, `90d` |
| `from` | string | No | - | Start date (YYYY-MM-DD) |
| `to` | string | No | - | End date (YYYY-MM-DD) |

**Example Request:**

```bash
curl -X GET "https://api.lernsystemx.com/api/v1/organisations/5/analytics/top-courses?limit=5&range=30d" \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "courses": [
    {
      "course_id": 42,
      "title": "Python Basics",
      "enrolled_count": 25,
      "avg_progress": 68.5,
      "completion_rate": 44.0,
      "events_count": 320
    },
    {
      "course_id": 15,
      "title": "Data Structures",
      "enrolled_count": 18,
      "avg_progress": 52.3,
      "completion_rate": 27.8,
      "events_count": 215
    }
  ],
  "total": 5
}
```

**Response Fields:**

- `enrolled_count`: Number of organisation members enrolled in this course
- `avg_progress`: Average progress percentage across all enrolled members
- `completion_rate`: Percentage of enrolled members who completed the course
- `events_count`: Total number of analytics events for this course

---

### 4. Get Organisation Top Modules

Retrieve top modules by completion count within the organisation.

**Endpoint:**
```
GET /api/v1/organisations/{org_id}/analytics/top-modules
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | integer | Yes | Organisation ID |

**Query Parameters:**

Same as Top Courses (see above).

**Example Request:**

```bash
curl -X GET "https://api.lernsystemx.com/api/v1/organisations/5/analytics/top-modules?limit=10&range=7d" \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "modules": [
    {
      "module_id": 15,
      "module_title": "Variables & Data Types",
      "course_title": "Python Basics",
      "completions": 18,
      "avg_time_spent": 45
    },
    {
      "module_id": 23,
      "module_title": "Arrays & Lists",
      "course_title": "Data Structures",
      "completions": 14,
      "avg_time_spent": 62
    }
  ],
  "total": 10
}
```

**Response Fields:**

- `completions`: Number of times organisation members completed this module
- `avg_time_spent`: Average time spent on this module (in minutes)

---

## Integration with Frontend (F8)

### TypeScript Client Example

```typescript
// frontend/src/api/orgAdmin.api.ts

export const orgGetEventsTimeSeries = async (
  orgId: number,
  params: {
    from?: string
    to?: string
    days?: 7 | 30 | 90
  }
): Promise<TimeSeriesPoint[]> => {
  const queryParams = new URLSearchParams()

  if (params.days) {
    queryParams.append('range', `${params.days}d`)
  } else if (params.from && params.to) {
    queryParams.append('from', params.from)
    queryParams.append('to', params.to)
  }

  const response = await http.get<{
    success: boolean
    data: TimeSeriesPoint[]
  }>(`/organisations/${orgId}/analytics/events/time-series?${queryParams}`)

  return response.data.data
}
```

### Vue Component Usage

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useOrgAdminStore } from '@/store/orgAdmin.store'

const orgAdminStore = useOrgAdminStore()

const orgId = computed(() => orgAdminStore.organisation?.organisation_id || 0)
const eventsData = ref([])

onMounted(async () => {
  if (orgId.value) {
    await orgAdminStore.loadOrgAdvancedAnalytics(orgId.value, 7)
    eventsData.value = orgAdminStore.orgAnalytics?.eventsTimeSeries || []
  }
})
</script>
```

---

## Multi-Tenancy Security

### Access Control Flow

```python
def check_org_access(user, org_id: int):
    """
    Enforce multi-tenancy: user can only access their own organisation
    """
    # Admin/Superadmin can access all orgs
    if user.get('role') in ['admin', 'superadmin']:
        return

    # Regular users must belong to the organisation
    user_org_id = user.get('organisation_id')
    if user_org_id != org_id:
        raise PermissionError(f"Access denied to organisation {org_id}")
```

### Security Matrix

| User Org ID | Requested Org ID | User Role | Access |
|-------------|------------------|-----------|--------|
| 5 | 5 | `school_admin` | ✅ Allowed |
| 5 | 7 | `school_admin` | ❌ Forbidden (403) |
| 5 | 7 | `admin` | ✅ Allowed (system admin) |
| NULL | 5 | `teacher` | ❌ Forbidden (no org) |

---

## Performance & Caching

### Query Optimization

All queries are scoped to `organisation_id` and use composite indexes:

```sql
CREATE INDEX idx_analytics_events_org_date
ON analytics_events(organisation_id, created_at);

CREATE INDEX idx_analytics_events_org_resource
ON analytics_events(organisation_id, resource_type, resource_id);
```

### Recommended Caching

```python
cache_key = f"ANALYTICS:ORG:{org_id}:EVENTS:{from_date}:{to_date}"
cached_data = CacheService.get(cache_key)

if not cached_data:
    raw_data = AnalyticsRepository.get_events_time_series(
        from_date, to_date, organisation_id=org_id
    )
    CacheService.set(cache_key, raw_data, ttl=180)  # 3 minutes
```

**Suggested TTL:**
- Time series: 3-5 minutes
- Top lists: 5-10 minutes

---

## Error Handling

### Common Errors

**Forbidden (403) - Not in Organisation:**

```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Access denied to organisation 7"
}
```

**Invalid Date Format (400):**

```json
{
  "success": false,
  "error": "Invalid date format",
  "message": "Date must be in format YYYY-MM-DD"
}
```

**Organisation Not Found:**

The API will return empty data arrays if the organisation has no analytics data, rather than throwing an error.

---

## Testing

### cURL Examples

```bash
# Assumes user is member of organisation 5

# Get events time series (7 days)
curl -X GET "http://localhost:5000/api/v1/organisations/5/analytics/events/time-series" \
  -H "Authorization: Bearer <token>"

# Get active members (30 days)
curl -X GET "http://localhost:5000/api/v1/organisations/5/analytics/active-members/time-series?range=30d" \
  -H "Authorization: Bearer <token>"

# Get top 5 courses
curl -X GET "http://localhost:5000/api/v1/organisations/5/analytics/top-courses?limit=5" \
  -H "Authorization: Bearer <token>"

# Get top modules (custom date range)
curl -X GET "http://localhost:5000/api/v1/organisations/5/analytics/top-modules?from=2025-01-01&to=2025-01-31" \
  -H "Authorization: Bearer <token>"
```

### Testing Multi-Tenancy

```bash
# User from org 5 trying to access org 7 - should fail with 403
curl -X GET "http://localhost:5000/api/v1/organisations/7/analytics/events/time-series" \
  -H "Authorization: Bearer <school_admin_org5_token>"

# Expected response:
# {
#   "success": false,
#   "error": "Forbidden",
#   "message": "Access denied to organisation 7"
# }

# System admin can access any org
curl -X GET "http://localhost:5000/api/v1/organisations/7/analytics/events/time-series" \
  -H "Authorization: Bearer <admin_token>"
# Should succeed with 200 OK
```

---

## Use Cases

### 1. School Dashboard

A school admin viewing student progress across all courses:

```bash
# Get active students last 30 days
GET /organisations/5/analytics/active-members/time-series?range=30d

# Get top courses by engagement
GET /organisations/5/analytics/top-courses?limit=10&range=30d

# Get most completed modules
GET /organisations/5/analytics/top-modules?limit=10&range=30d
```

### 2. Company Training Dashboard

A company admin tracking employee training:

```bash
# Get training activity
GET /organisations/12/analytics/events/time-series?range=90d

# Get completion rates
GET /organisations/12/analytics/top-courses?limit=20
```

### 3. Teacher Class Report

A teacher viewing their class performance (assuming teacher is in org 5):

```bash
# Weekly activity
GET /organisations/5/analytics/active-members/time-series?range=7d

# Most popular modules
GET /organisations/5/analytics/top-modules?limit=5&range=7d
```

---

## Related Documentation

- [26_Analytics-System.md](../../../LernsystemX-Doku/26_Analytics-System.md) - Analytics architecture
- [25_Organisation-System.md](../../../LernsystemX-Doku/25_Organisation-System.md) - Organisation management
- [31_Security-Architecture.md](../../../LernsystemX-Doku/31_Security-Architecture.md) - Multi-tenancy & RBAC
- [Admin Analytics API](./admin-analytics-api.md) - System-wide analytics
- [Frontend F8 Documentation](../../../frontend/docs/F8_AnalyticsUI.md) - UI integration

---

## Changelog

### Version 1.0.0 (Phase B10)

- ✅ Initial release
- ✅ Events time series endpoint
- ✅ Active members time series endpoint
- ✅ Top courses endpoint
- ✅ Top modules endpoint
- ✅ Multi-tenancy enforcement
- ✅ RBAC integration
- ✅ Query optimization with org-scoped indexes
