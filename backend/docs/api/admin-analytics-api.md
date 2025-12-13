# Admin Analytics API Documentation

**Version:** 1.0.0
**Phase:** B10
**Base URL:** `/api/v1/admin/analytics`

---

## Overview

The Admin Analytics API provides system-wide analytics endpoints for system administrators. These endpoints require `VIEW_SYSTEM_ANALYTICS` permission (granted to `admin` and `superadmin` roles).

### Features

- **Time Series Data:** Events and active users over time
- **Top Lists:** Most active courses and learning methods
- **Flexible Filtering:** Support for date ranges (7d, 30d, 90d) or custom dates
- **Performance Optimized:** Queries use indexed fields and aggregations
- **Security:** RBAC-protected, JWT-authenticated

---

## Authentication

All endpoints require a valid JWT access token:

```http
Authorization: Bearer <access_token>
```

### Required Permission

```
VIEW_SYSTEM_ANALYTICS
```

Granted to roles: `admin`, `superadmin`

---

## Endpoints

### 1. Get Events Time Series

Retrieve system-wide events aggregated by day.

**Endpoint:**
```
GET /api/v1/admin/analytics/events/time-series
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `range` | string | No | `7d` | Time range: `7d`, `30d`, `90d` |
| `from` | string | No | - | Start date (YYYY-MM-DD) - overrides `range` |
| `to` | string | No | - | End date (YYYY-MM-DD) - overrides `range` |

**Example Requests:**

```bash
# Last 7 days (default)
curl -X GET "https://api.lernsystemx.com/api/v1/admin/analytics/events/time-series" \
  -H "Authorization: Bearer <token>"

# Last 30 days
curl -X GET "https://api.lernsystemx.com/api/v1/admin/analytics/events/time-series?range=30d" \
  -H "Authorization: Bearer <token>"

# Custom date range
curl -X GET "https://api.lernsystemx.com/api/v1/admin/analytics/events/time-series?from=2025-01-01&to=2025-01-15" \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "data": [
    {
      "date": "2025-01-15",
      "value": 245
    },
    {
      "date": "2025-01-16",
      "value": 312
    },
    {
      "date": "2025-01-17",
      "value": 289
    }
  ],
  "total": 846
}
```

**Error Responses:**

| Code | Description |
|------|-------------|
| 400 | Invalid date format |
| 401 | Unauthorized (no valid token) |
| 403 | Forbidden (insufficient permissions) |
| 500 | Server error |

---

### 2. Get Active Users Time Series

Retrieve count of unique active users per day.

**Endpoint:**
```
GET /api/v1/admin/analytics/active-users/time-series
```

**Query Parameters:**

Same as Events Time Series (see above).

**Example Request:**

```bash
curl -X GET "https://api.lernsystemx.com/api/v1/admin/analytics/active-users/time-series?range=30d" \
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

**Note:** `total` represents the maximum number of unique users across any single day (peak active users).

---

### 3. Get Top Courses

Retrieve top courses by activity (events, enrollments, completions).

**Endpoint:**
```
GET /api/v1/admin/analytics/top-courses
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | `10` | Number of top courses (max: 100) |
| `range` | string | No | - | Time range: `7d`, `30d`, `90d` |
| `from` | string | No | - | Start date (YYYY-MM-DD) |
| `to` | string | No | - | End date (YYYY-MM-DD) |

**Example Request:**

```bash
curl -X GET "https://api.lernsystemx.com/api/v1/admin/analytics/top-courses?limit=5&range=30d" \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "courses": [
    {
      "course_id": 42,
      "title": "Python for Beginners",
      "events_count": 1250,
      "enrollments": 145,
      "completions": 67,
      "avg_completion_rate": 46.2
    },
    {
      "course_id": 15,
      "title": "Web Development Bootcamp",
      "events_count": 980,
      "enrollments": 120,
      "completions": 85,
      "avg_completion_rate": 70.8
    }
  ],
  "total": 5
}
```

**Response Fields:**

- `events_count`: Total number of analytics events (views, starts, completions, etc.)
- `enrollments`: Number of course enrollments
- `completions`: Number of users who completed the course (100%)
- `avg_completion_rate`: Percentage of enrolled users who completed (calculated)

---

### 4. Get Top Learning Methods

Retrieve top learning methods by usage and token consumption.

**Endpoint:**
```
GET /api/v1/admin/analytics/top-methods
```

**Query Parameters:**

Same as Top Courses (see above).

**Example Request:**

```bash
curl -X GET "https://api.lernsystemx.com/api/v1/admin/analytics/top-methods?limit=10&range=7d" \
  -H "Authorization: Bearer <token>"
```

**Success Response (200 OK):**

```json
{
  "success": true,
  "methods": [
    {
      "method_id": 5,
      "name": "Flashcards",
      "calls": 2450,
      "tokens_used": 125000,
      "avg_tokens": 51
    },
    {
      "method_id": 12,
      "name": "Mind Maps",
      "calls": 1820,
      "tokens_used": 98000,
      "avg_tokens": 54
    }
  ],
  "total": 10
}
```

**Response Fields:**

- `calls`: Number of times this method was executed
- `tokens_used`: Total AI tokens consumed by this method
- `avg_tokens`: Average tokens per method execution

---

## Integration with Frontend (F8)

The Admin Analytics API is designed to work seamlessly with the Frontend Phase F8 implementation:

### TypeScript Client Example

```typescript
// frontend/src/api/admin.api.ts

export const adminGetEventsTimeSeries = async (params: {
  from?: string
  to?: string
  days?: 7 | 30 | 90
}): Promise<TimeSeriesPoint[]> => {
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
  }>(`/admin/analytics/events/time-series?${queryParams}`)

  return response.data.data
}
```

### Vue Component Usage

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminGetEventsTimeSeries } from '@/api/admin.api'

const eventsData = ref([])

onMounted(async () => {
  eventsData.value = await adminGetEventsTimeSeries({ days: 7 })
})
</script>
```

---

## Performance & Caching

### Query Optimization

- All queries use indexed fields (`created_at`, `organisation_id`, `resource_type`)
- Aggregations are performed at database level
- Date range filters prevent full table scans

### Recommended Caching Strategy

For high-traffic scenarios, implement caching:

```python
from app.services.cache_service import CacheService

cache_key = f"ANALYTICS:SYSTEM:EVENTS:{from_date}:{to_date}"
cached_data = CacheService.get(cache_key)

if not cached_data:
    raw_data = AnalyticsRepository.get_events_time_series(from_date, to_date)
    CacheService.set(cache_key, raw_data, ttl=300)  # 5 minutes
```

**Suggested TTL:**
- Time series: 5-10 minutes
- Top lists: 10-15 minutes

---

## Security Considerations

### RBAC Matrix

| Role | Permission | Access |
|------|-----------|--------|
| `user` | - | ❌ No access |
| `premium` | - | ❌ No access |
| `creator` | - | ❌ No access |
| `teacher` | - | ❌ No access |
| `school_admin` | - | ❌ No access |
| `company_admin` | - | ❌ No access |
| `moderator` | `VIEW_SYSTEM_ANALYTICS` | ✅ Full access |
| `support` | `VIEW_SYSTEM_ANALYTICS` | ✅ Full access |
| `admin` | `VIEW_SYSTEM_ANALYTICS` | ✅ Full access |
| `superadmin` | `*` | ✅ Full access |

### Audit Logging

All analytics requests can be logged for compliance:

```python
from app.services.audit_service import AuditService

AuditService.log_event(
    user_id=user['user_id'],
    action='ANALYTICS:VIEW:SYSTEM_EVENTS',
    resource_type='analytics',
    ip_address=request.remote_addr
)
```

---

## Error Handling

### Common Errors

**Invalid Date Format (400):**

```json
{
  "success": false,
  "error": "Invalid date format",
  "message": "Date must be in format YYYY-MM-DD"
}
```

**Forbidden (403):**

```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Insufficient permissions. Requires VIEW_SYSTEM_ANALYTICS"
}
```

**Server Error (500):**

```json
{
  "success": false,
  "error": "Failed to fetch events time series",
  "details": "Database connection failed"
}
```

---

## Testing

### cURL Examples

```bash
# Get events time series (7 days)
curl -X GET "http://localhost:5000/api/v1/admin/analytics/events/time-series" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get active users (30 days)
curl -X GET "http://localhost:5000/api/v1/admin/analytics/active-users/time-series?range=30d" \
  -H "Authorization: Bearer <token>"

# Get top 5 courses
curl -X GET "http://localhost:5000/api/v1/admin/analytics/top-courses?limit=5" \
  -H "Authorization: Bearer <token>"

# Get top methods (custom date range)
curl -X GET "http://localhost:5000/api/v1/admin/analytics/top-methods?from=2025-01-01&to=2025-01-31" \
  -H "Authorization: Bearer <token>"
```

### Python Requests Example

```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}"
}

# Get events time series
response = requests.get(
    "http://localhost:5000/api/v1/admin/analytics/events/time-series",
    headers=headers,
    params={"range": "30d"}
)

data = response.json()
print(data['total'])  # Total events
for point in data['data']:
    print(f"{point['date']}: {point['value']}")
```

---

## Related Documentation

- [26_Analytics-System.md](../../../LernsystemX-Doku/26_Analytics-System.md) - Analytics architecture
- [31_Security-Architecture.md](../../../LernsystemX-Doku/31_Security-Architecture.md) - RBAC & permissions
- [Organisation Analytics API](./org-analytics-api.md) - Org-specific analytics
- [Frontend F8 Documentation](../../../frontend/docs/F8_AnalyticsUI.md) - UI integration

---

## Changelog

### Version 1.0.0 (Phase B10)

- ✅ Initial release
- ✅ Events time series endpoint
- ✅ Active users time series endpoint
- ✅ Top courses endpoint
- ✅ Top learning methods endpoint
- ✅ RBAC integration
- ✅ Multi-tenant support
- ✅ Query optimization
