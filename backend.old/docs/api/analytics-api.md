# LernsystemX Analytics API Documentation

**Version:** 1.0.0
**Standard:** ISO/IEC/IEEE 26515:2018 - API Documentation
**Compliance:** ISO 27001:2013 - Analytics & Privacy
**Last Updated:** 2025-11-16

## Overview

The Analytics API provides event tracking and statistical analysis capabilities for LernsystemX. It enables tracking of user interactions, learning progress, and organisation-wide metrics while maintaining GDPR compliance through IP anonymization and data protection.

### Key Features

- **Event Tracking:** Track user interactions with the platform
- **User Statistics:** Personal learning analytics and progress
- **Organisation Analytics:** Organisation-wide statistics and insights
- **Privacy-First:** IP address hashing, GDPR compliant
- **Real-Time:** Immediate event tracking and statistics
- **Multi-Tenant:** Organisation-aware analytics
- **RBAC:** Role-based access to statistics

### Base URL

```
http://localhost:5000/api/v1
```

---

## Authentication

All analytics endpoints (except health check) require JWT authentication.

### Headers

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Required Permissions

| Operation | Roles Allowed | Roles Denied |
|-----------|---------------|--------------|
| Track events | All authenticated users | None |
| View user stats | All authenticated users | None |
| View org stats | Teacher, School Admin, Company Admin, Admin, Superadmin | Free User, Premium, Creator, Moderator, Support |

---

## Data Models

### EventType (Enum)

Supported event types for analytics tracking:

```typescript
enum EventType {
  // Authentication
  LOGIN = 'login',
  LOGOUT = 'logout',

  // Navigation
  PAGE_VIEW = 'page_view',

  // Courses
  COURSE_VIEW = 'course_view',
  COURSE_ENROLL = 'course_enroll',

  // Modules
  MODULE_START = 'module_start',
  MODULE_COMPLETE = 'module_complete',

  // Lessons
  LESSON_START = 'lesson_start',
  LESSON_COMPLETE = 'lesson_complete',

  // Learning Methods
  METHOD_EXECUTE = 'method_execute',

  // Exams
  EXAM_START = 'exam_start',
  EXAM_COMPLETE = 'exam_complete',

  // LiveRoom
  LIVEROOM_JOIN = 'liveroom_join',
  LIVEROOM_LEAVE = 'liveroom_leave',

  // KI
  KI_JOB_START = 'ki_job_start',
  KI_JOB_COMPLETE = 'ki_job_complete',

  // Purchases
  PURCHASE = 'purchase',
  SUBSCRIPTION_START = 'subscription_start',
  SUBSCRIPTION_CANCEL = 'subscription_cancel'
}
```

### ResourceType (Enum)

```typescript
enum ResourceType {
  COURSE = 'course',
  MODULE = 'module',
  LESSON = 'lesson',
  METHOD = 'method',
  EXAM = 'exam',
  LIVEROOM = 'liveroom',
  SUBSCRIPTION = 'subscription',
  PAGE = 'page'
}
```

### AnalyticsEvent

```typescript
interface AnalyticsEvent {
  event_id: number
  user_id: number
  organisation_id?: number
  event_type: EventType
  resource_type?: ResourceType
  resource_id?: number
  payload?: Record<string, any>
  session_id?: string
  ip_address_hash?: string
  created_at: string  // ISO 8601
}
```

### AnalyticsUserStats

```typescript
interface AnalyticsUserStats {
  user_id: number
  total_events: number
  event_counts_by_type: Record<string, number>
  recent_events: AnalyticsEvent[]
  first_event_at?: string
  last_event_at?: string
  courses_viewed: number
  courses_enrolled: number
  modules_completed: number
  lessons_completed: number
}
```

### AnalyticsOrgStats

```typescript
interface AnalyticsOrgStats {
  organisation_id: number
  total_events: number
  total_users: number
  active_users_30d: number
  event_counts_by_type: Record<string, number>
  top_courses: Array<{course_id: number, event_count: number}>
  first_event_at?: string
  last_event_at?: string
  total_course_enrollments: number
  total_modules_completed: number
  total_exams_completed: number
  avg_completion_rate: number
}
```

---

## Endpoints

### 1. Track Analytics Event

Track user interaction or system event.

**Endpoint:**
```http
POST /api/v1/analytics/event
```

**Authentication:** Required (JWT)

**Request Headers:**
```http
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
  "event_type": "course_view",
  "resource_type": "course",
  "resource_id": 42,
  "payload": {
    "duration_seconds": 120,
    "page_number": 1,
    "interaction_count": 5
  },
  "session_id": "abc123xyz"
}
```

**Request Body Fields:**
- `event_type` (required): Type of event (see EventType enum)
- `resource_type` (optional): Type of resource being tracked
- `resource_id` (optional): ID of the resource
- `payload` (optional): Additional event data as JSON object
- `session_id` (optional): Session identifier for tracking user sessions

**Response: 200 OK**
```json
{
  "success": true,
  "message": "Event tracked successfully",
  "event": {
    "event_id": 12345,
    "user_id": 123,
    "organisation_id": 5,
    "event_type": "course_view",
    "resource_type": "course",
    "resource_id": 42,
    "payload": {
      "duration_seconds": 120,
      "page_number": 1,
      "interaction_count": 5
    },
    "session_id": "abc123xyz",
    "ip_address_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "created_at": "2025-11-16T20:00:00Z"
  }
}
```

**Response: 400 Bad Request (Invalid Event Type)**
```json
{
  "success": false,
  "error": "Invalid request",
  "message": "Invalid event_type: invalid_event"
}
```

**Response: 400 Bad Request (Validation Error)**
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "type": "missing",
      "loc": ["event_type"],
      "msg": "Field required"
    }
  ]
}
```

**Response: 401 Unauthorized**
```json
{
  "success": false,
  "error": "Authorization required",
  "message": "Missing authorization token. Please login."
}
```

---

### 2. Get User Analytics

Get analytics statistics for the authenticated user.

**Endpoint:**
```http
GET /api/v1/analytics/user
```

**Authentication:** Required (JWT)

**Request Headers:**
```http
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response: 200 OK**
```json
{
  "success": true,
  "stats_type": "user",
  "stats": {
    "user_id": 123,
    "total_events": 150,
    "event_counts_by_type": {
      "login": 25,
      "course_view": 50,
      "module_complete": 10,
      "lesson_complete": 45,
      "exam_complete": 5
    },
    "recent_events": [
      {
        "event_id": 12345,
        "user_id": 123,
        "event_type": "course_view",
        "resource_type": "course",
        "resource_id": 42,
        "created_at": "2025-11-16T20:00:00Z"
      },
      {
        "event_id": 12344,
        "user_id": 123,
        "event_type": "module_complete",
        "resource_type": "module",
        "resource_id": 15,
        "created_at": "2025-11-16T19:30:00Z"
      }
    ],
    "first_event_at": "2025-01-01T10:00:00Z",
    "last_event_at": "2025-11-16T20:00:00Z",
    "courses_viewed": 50,
    "courses_enrolled": 15,
    "modules_completed": 10,
    "lessons_completed": 45
  }
}
```

**Response: 401 Unauthorized**
```json
{
  "success": false,
  "error": "Authorization required",
  "message": "Missing authorization token. Please login."
}
```

**Response: 500 Internal Server Error**
```json
{
  "success": false,
  "error": "Failed to get user analytics",
  "details": "Database connection error"
}
```

---

### 3. Get Organisation Analytics

Get analytics statistics for the user's organisation.

**Endpoint:**
```http
GET /api/v1/analytics/organisation
```

**Authentication:** Required (JWT)

**Permissions:** Teacher, School Admin, Company Admin, Admin, or Superadmin

**Request Headers:**
```http
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response: 200 OK**
```json
{
  "success": true,
  "stats_type": "organisation",
  "stats": {
    "organisation_id": 5,
    "total_events": 5000,
    "total_users": 150,
    "active_users_30d": 85,
    "event_counts_by_type": {
      "login": 850,
      "course_view": 1200,
      "module_complete": 450,
      "exam_complete": 95
    },
    "top_courses": [
      {
        "course_id": 10,
        "event_count": 320
      },
      {
        "course_id": 15,
        "event_count": 280
      },
      {
        "course_id": 22,
        "event_count": 195
      }
    ],
    "first_event_at": "2024-09-01T08:00:00Z",
    "last_event_at": "2025-11-16T20:00:00Z",
    "total_course_enrollments": 450,
    "total_modules_completed": 1200,
    "total_exams_completed": 95,
    "avg_completion_rate": 78.5
  }
}
```

**Response: 403 Forbidden (Insufficient Permissions)**
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Role 'premium' cannot view organisation analytics. Requires: Teacher, School Admin, Company Admin, or Admin."
}
```

**Response: 400 Bad Request (User Not in Organisation)**
```json
{
  "success": false,
  "error": "Invalid request",
  "message": "User not in organisation"
}
```

**Response: 401 Unauthorized**
```json
{
  "success": false,
  "error": "Authorization required",
  "message": "Missing authorization token. Please login."
}
```

---

### 4. Analytics Health Check

Check if analytics system is operational.

**Endpoint:**
```http
GET /api/v1/analytics/health
```

**Authentication:** None (Public endpoint)

**Response: 200 OK**
```json
{
  "success": true,
  "message": "Analytics system operational",
  "version": "1.0.0"
}
```

---

## Event Payload Examples

### Module Complete Event

```json
{
  "event_type": "module_complete",
  "resource_type": "module",
  "resource_id": 15,
  "payload": {
    "time_spent_minutes": 45,
    "methods_used": ["flashcards", "quiz", "video"],
    "errors": 3,
    "retries": 1,
    "score": 85.5
  }
}
```

### Exam Complete Event

```json
{
  "event_type": "exam_complete",
  "resource_type": "exam",
  "resource_id": 8,
  "payload": {
    "score": 92.5,
    "max_score": 100,
    "time_taken_minutes": 60,
    "questions_answered": 40,
    "questions_correct": 37,
    "passed": true
  }
}
```

### LiveRoom Join Event

```json
{
  "event_type": "liveroom_join",
  "resource_type": "liveroom",
  "resource_id": 42,
  "payload": {
    "room_name": "Math Class A",
    "participant_count": 15,
    "role": "student"
  }
}
```

### Course Enrollment Event

```json
{
  "event_type": "course_enroll",
  "resource_type": "course",
  "resource_id": 25,
  "payload": {
    "enrollment_type": "free",
    "source": "recommendation",
    "category": "programming"
  }
}
```

---

## Business Rules

### Event Tracking

1. **Automatic Fields:**
   - `user_id`: Extracted from JWT token
   - `organisation_id`: Extracted from JWT token (if user in organisation)
   - `ip_address_hash`: Automatically hashed from request IP
   - `created_at`: Set to current timestamp

2. **Validation:**
   - `event_type` must be from EventType enum
   - `resource_type` must be from ResourceType enum (if provided)
   - `payload` is optional and can be any valid JSON

3. **Privacy:**
   - IP addresses are SHA-256 hashed before storage
   - No personally identifiable information in payload
   - GDPR compliant data handling

### Analytics Access

1. **User Statistics:**
   - All authenticated users can view their own statistics
   - Users can only see their own data
   - No cross-user visibility

2. **Organisation Statistics:**
   - Only Teachers, Org Admins, and System Admins can view
   - Only for user's own organisation
   - Aggregated data only (no individual user details)

3. **Data Retention:**
   - Events stored indefinitely by default
   - Users can request data deletion (GDPR right to be forgotten)
   - Organisation events deleted when organisation deleted

---

## Error Codes

| HTTP Code | Error | Description |
|-----------|-------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Validation error or invalid event type |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions |
| 500 | Internal Server Error | Server error (database, etc.) |

---

## Database Schema

### Table: analytics_events

```sql
CREATE TABLE analytics_events (
    event_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organisation_id INTEGER REFERENCES organisations(organisation_id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id INTEGER,
    payload JSONB,
    session_id VARCHAR(255),
    ip_address_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT check_event_type CHECK (event_type IN (
        'login', 'logout', 'page_view', 'course_view', 'course_enroll',
        'module_start', 'module_complete', 'lesson_start', 'lesson_complete',
        'method_execute', 'exam_start', 'exam_complete',
        'liveroom_join', 'liveroom_leave', 'ki_job_start', 'ki_job_complete',
        'purchase', 'subscription_start', 'subscription_cancel'
    ))
);

-- Indexes for performance
CREATE INDEX idx_analytics_user ON analytics_events(user_id);
CREATE INDEX idx_analytics_org ON analytics_events(organisation_id);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_resource ON analytics_events(resource_type, resource_id);
CREATE INDEX idx_analytics_created_at ON analytics_events(created_at DESC);
CREATE INDEX idx_analytics_user_created ON analytics_events(user_id, created_at DESC);
```

---

## Testing Examples

### cURL Examples

**Track Event:**
```bash
curl -X POST http://localhost:5000/api/v1/analytics/event \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "course_view",
    "resource_type": "course",
    "resource_id": 42,
    "payload": {
      "duration_seconds": 120
    }
  }'
```

**Get User Stats:**
```bash
curl -X GET http://localhost:5000/api/v1/analytics/user \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Get Organisation Stats:**
```bash
curl -X GET http://localhost:5000/api/v1/analytics/organisation \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Health Check:**
```bash
curl -X GET http://localhost:5000/api/v1/analytics/health
```

### Python Example

```python
import requests

# Login to get JWT
login_response = requests.post('http://localhost:5000/api/v1/auth/login', json={
    'email': 'user@example.com',
    'password': 'SecurePassword123!'
})
token = login_response.json()['access_token']

# Track course view event
headers = {'Authorization': f'Bearer {token}'}
event_data = {
    'event_type': 'course_view',
    'resource_type': 'course',
    'resource_id': 42,
    'payload': {
        'duration_seconds': 120,
        'page_number': 1
    }
}
event_response = requests.post(
    'http://localhost:5000/api/v1/analytics/event',
    headers=headers,
    json=event_data
)
print(event_response.json())

# Get user statistics
user_stats_response = requests.get(
    'http://localhost:5000/api/v1/analytics/user',
    headers=headers
)
print(user_stats_response.json())

# Get organisation statistics (if user has permission)
org_stats_response = requests.get(
    'http://localhost:5000/api/v1/analytics/organisation',
    headers=headers
)
print(org_stats_response.json())
```

### TypeScript/Frontend Example

```typescript
import { http } from '@/lib/http'

// Track event
export const trackEvent = async (
  eventType: string,
  resourceType?: string,
  resourceId?: number,
  payload?: Record<string, any>
) => {
  const response = await http.post('/analytics/event', {
    event_type: eventType,
    resource_type: resourceType,
    resource_id: resourceId,
    payload
  })
  return response.data
}

// Get user statistics
export const getUserAnalytics = async () => {
  const response = await http.get('/analytics/user')
  return response.data.stats
}

// Get organisation statistics
export const getOrgAnalytics = async () => {
  const response = await http.get('/analytics/organisation')
  return response.data.stats
}

// Usage in component
const handleCourseView = async (courseId: number) => {
  await trackEvent('course_view', 'course', courseId, {
    duration_seconds: 120
  })
}
```

---

## Future Enhancements

### Planned Features

1. **Advanced Filtering:**
   - Filter events by date range
   - Filter by event type
   - Filter by resource

2. **Aggregation Endpoints:**
   - Daily/weekly/monthly aggregates
   - Custom time range statistics
   - Trend analysis

3. **Export Functionality:**
   - Export events as CSV
   - Export statistics as PDF reports
   - Scheduled report generation

4. **Real-Time Analytics:**
   - WebSocket streaming of events
   - Live dashboard updates
   - Real-time user activity tracking

5. **AI-Powered Insights:**
   - Learning pattern analysis
   - Personalized recommendations
   - Knowledge gap detection

6. **Comparison Metrics:**
   - Compare user performance to cohort average
   - Organisation benchmarking
   - Course effectiveness metrics

---

## Compliance & Security

### ISO 27001:2013

- **Access Control:** JWT-based authentication on all endpoints
- **Data Validation:** Pydantic validation on all inputs
- **Audit Trail:** All events timestamped and immutable
- **Least Privilege:** Role-based access to statistics

### GDPR Compliance

- **Data Minimization:** Only necessary event data stored
- **Pseudonymization:** IP addresses hashed (SHA-256)
- **Right to Deletion:** Users can request data deletion
- **Transparency:** Clear documentation of data usage
- **Purpose Limitation:** Data only used for analytics and improvement

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-16 | Initial release - Event tracking, User stats, Org stats |

---

## Support & Contact

For API support, please contact:
- **Documentation:** https://code.lernsystemx.com/docs
- **GitHub Issues:** https://github.com/lernsystemx/backend/issues
- **Email:** api-support@lernsystemx.com

---

**End of Analytics API Documentation**
