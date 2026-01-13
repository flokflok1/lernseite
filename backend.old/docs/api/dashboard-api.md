# LernsystemX Dashboard Layout API Documentation

**Version:** 1.0.0
**Standard:** ISO/IEC/IEEE 26515:2018 - API Documentation
**Compliance:** ISO 27001:2013 - Dashboard Configuration Management
**Last Updated:** 2025-11-16

## Overview

The Dashboard Layout API provides personalized dashboard configuration management for LernsystemX users. It enables users to customize their dashboard widget layout, manage widget visibility, and configure widget-specific settings based on their subscription tier and role.

### Key Features

- **Role-Based Defaults:** Different default layouts for each user role
- **Layout Persistence:** Store custom layouts in PostgreSQL with JSONB
- **Permission-Based Access:** Only Premium+ users can customize layouts
- **Widget Management:** Add, remove, reorder, and configure widgets
- **Reset Functionality:** Restore role-based default layouts
- **Version Control:** Layout versioning for future migrations
- **Multi-Tenant Support:** Organisation-specific layouts (future)

### Base URL

```
http://localhost:5000/api/v1
```

---

## Authentication

All dashboard endpoints require JWT authentication.

### Headers

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Required Permissions

| Operation | Roles Allowed | Roles Denied |
|-----------|---------------|--------------|
| GET layout | All authenticated users | None |
| PUT layout (save) | Premium, Creator, Teacher, School Admin, Company Admin, Admin, Superadmin | Free User, Moderator, Support |
| POST layout/reset | Premium, Creator, Teacher, School Admin, Company Admin, Admin, Superadmin | Free User, Moderator, Support |

---

## Data Models

### DashboardLayout

Complete dashboard configuration for a user.

```typescript
interface DashboardLayout {
  userId: number              // User ID
  role: string               // User role (for filtering)
  widgets: DashboardWidgetInstance[]  // Widget instances
  presetId?: string          // Preset ID if using preset
  updatedAt?: string         // Last update timestamp (ISO 8601)
  version?: number           // Layout version (default: 1)
  source?: string            // Layout source: 'user' | 'role' | 'organisation' | 'system'
  isDefault?: boolean        // Whether this is a default layout
}
```

### DashboardWidgetInstance

Individual widget instance in a layout.

```typescript
interface DashboardWidgetInstance {
  instanceId: string         // Unique instance ID (e.g., "premium-welcome")
  widgetId: string          // Widget definition ID (e.g., "welcome")
  order: number             // Display order (0-based, lower = earlier)
  visible: boolean          // Widget visibility
  config?: Record<string, any>  // Widget-specific configuration
  position?: {              // Grid position (optional)
    row?: number
    col?: number
    width?: number
    height?: number
  }
}
```

---

## Endpoints

### 1. Get Dashboard Layout

Retrieves the effective dashboard layout for the authenticated user.

**Logic:**
- If user has saved a custom layout: Return custom layout
- If no custom layout exists: Return role-based default layout
- Free users always receive role default (cannot save custom layouts)

**Endpoint:**
```http
GET /api/v1/dashboard/layout
```

**Authentication:** Required (JWT)

**Request:**
```http
GET /api/v1/dashboard/layout HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response: 200 OK (Custom Layout)**
```json
{
  "success": true,
  "layout": {
    "userId": 123,
    "role": "premium",
    "widgets": [
      {
        "instanceId": "my-custom-welcome",
        "widgetId": "welcome",
        "order": 0,
        "visible": true,
        "config": {
          "theme": "dark"
        }
      },
      {
        "instanceId": "my-tokens",
        "widgetId": "plan-tokens",
        "order": 1,
        "visible": true
      },
      {
        "instanceId": "my-courses",
        "widgetId": "enrolled-courses",
        "order": 2,
        "visible": false
      }
    ],
    "presetId": null,
    "updatedAt": "2025-11-16T14:30:00Z",
    "version": 1,
    "source": "user",
    "isDefault": false
  }
}
```

**Response: 200 OK (Default Layout for Free User)**
```json
{
  "success": true,
  "layout": {
    "userId": 456,
    "role": "user",
    "widgets": [
      {
        "instanceId": "user-welcome",
        "widgetId": "welcome",
        "order": 0,
        "visible": true
      },
      {
        "instanceId": "user-profile",
        "widgetId": "profile-summary",
        "order": 1,
        "visible": true
      },
      {
        "instanceId": "user-courses",
        "widgetId": "enrolled-courses",
        "order": 2,
        "visible": true
      },
      {
        "instanceId": "user-progress",
        "widgetId": "courses-progress",
        "order": 3,
        "visible": true
      }
    ],
    "presetId": "free-default",
    "updatedAt": null,
    "version": 1,
    "source": "role",
    "isDefault": true
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
  "error": "Failed to get dashboard layout",
  "details": "Database connection error"
}
```

---

### 2. Save Dashboard Layout

Saves a custom dashboard layout for the authenticated user.

**Permissions:** Premium, Creator, Teacher, School Admin, Company Admin, Admin, Superadmin only.

**Endpoint:**
```http
PUT /api/v1/dashboard/layout
```

**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "widgets": [
    {
      "instanceId": "my-welcome-widget",
      "widgetId": "welcome",
      "order": 0,
      "visible": true,
      "config": {
        "showTips": false
      }
    },
    {
      "instanceId": "my-tokens",
      "widgetId": "plan-tokens",
      "order": 1,
      "visible": true
    },
    {
      "instanceId": "my-activity",
      "widgetId": "activity",
      "order": 2,
      "visible": false
    }
  ],
  "presetId": null
}
```

**Request:**
```http
PUT /api/v1/dashboard/layout HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "widgets": [...],
  "presetId": null
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "message": "Dashboard layout saved successfully",
  "layout": {
    "userId": 123,
    "role": "premium",
    "widgets": [
      {
        "instanceId": "my-welcome-widget",
        "widgetId": "welcome",
        "order": 0,
        "visible": true,
        "config": {
          "showTips": false
        }
      },
      {
        "instanceId": "my-tokens",
        "widgetId": "plan-tokens",
        "order": 1,
        "visible": true
      },
      {
        "instanceId": "my-activity",
        "widgetId": "activity",
        "order": 2,
        "visible": false
      }
    ],
    "presetId": null,
    "updatedAt": "2025-11-16T15:45:30Z",
    "version": 1,
    "source": "user",
    "isDefault": false
  }
}
```

**Response: 403 Forbidden (Free User)**
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Role 'user' cannot customize dashboard. Upgrade to Premium or higher to customize your dashboard."
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
      "loc": ["widgets", 0, "instanceId"],
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

### 3. Reset Dashboard Layout

Resets the user's dashboard layout to the role-based default by deleting their custom layout.

**Permissions:** Premium, Creator, Teacher, School Admin, Company Admin, Admin, Superadmin only.

**Endpoint:**
```http
POST /api/v1/dashboard/layout/reset
```

**Authentication:** Required (JWT)

**Request:**
```http
POST /api/v1/dashboard/layout/reset HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response: 200 OK**
```json
{
  "success": true,
  "message": "Dashboard layout reset to default",
  "layout": {
    "userId": 123,
    "role": "premium",
    "widgets": [
      {
        "instanceId": "premium-welcome",
        "widgetId": "welcome",
        "order": 0,
        "visible": true
      },
      {
        "instanceId": "premium-profile",
        "widgetId": "profile-summary",
        "order": 1,
        "visible": true
      },
      {
        "instanceId": "premium-tokens",
        "widgetId": "plan-tokens",
        "order": 2,
        "visible": true
      },
      {
        "instanceId": "premium-courses",
        "widgetId": "enrolled-courses",
        "order": 3,
        "visible": true
      },
      {
        "instanceId": "premium-progress",
        "widgetId": "courses-progress",
        "order": 4,
        "visible": true
      },
      {
        "instanceId": "premium-activity",
        "widgetId": "activity",
        "order": 5,
        "visible": true
      }
    ],
    "presetId": "premium-default",
    "updatedAt": null,
    "version": 1,
    "source": "role",
    "isDefault": true
  }
}
```

**Response: 403 Forbidden (Free User)**
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Role 'user' cannot reset dashboard. This role uses a fixed default layout."
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

## Role-Based Default Layouts

Each user role has a predefined default layout with specific widgets.

### Free User (role: "user")
```json
{
  "widgets": [
    {"instanceId": "user-welcome", "widgetId": "welcome", "order": 0, "visible": true},
    {"instanceId": "user-profile", "widgetId": "profile-summary", "order": 1, "visible": true},
    {"instanceId": "user-courses", "widgetId": "enrolled-courses", "order": 2, "visible": true},
    {"instanceId": "user-progress", "widgetId": "courses-progress", "order": 3, "visible": true}
  ],
  "presetId": "free-default"
}
```

### Premium User (role: "premium")
```json
{
  "widgets": [
    {"instanceId": "premium-welcome", "widgetId": "welcome", "order": 0, "visible": true},
    {"instanceId": "premium-profile", "widgetId": "profile-summary", "order": 1, "visible": true},
    {"instanceId": "premium-tokens", "widgetId": "plan-tokens", "order": 2, "visible": true},
    {"instanceId": "premium-courses", "widgetId": "enrolled-courses", "order": 3, "visible": true},
    {"instanceId": "premium-progress", "widgetId": "courses-progress", "order": 4, "visible": true},
    {"instanceId": "premium-activity", "widgetId": "activity", "order": 5, "visible": true}
  ],
  "presetId": "premium-default"
}
```

### Creator (role: "creator")
```json
{
  "widgets": [
    {"instanceId": "creator-welcome", "widgetId": "welcome", "order": 0, "visible": true},
    {"instanceId": "creator-profile", "widgetId": "profile-summary", "order": 1, "visible": true},
    {"instanceId": "creator-tokens", "widgetId": "plan-tokens", "order": 2, "visible": true},
    {"instanceId": "creator-courses", "widgetId": "enrolled-courses", "order": 3, "visible": true},
    {"instanceId": "creator-progress", "widgetId": "courses-progress", "order": 4, "visible": true},
    {"instanceId": "creator-activity", "widgetId": "activity", "order": 5, "visible": true}
  ],
  "presetId": "creator-default"
}
```

### Teacher (role: "teacher")
```json
{
  "widgets": [
    {"instanceId": "teacher-welcome", "widgetId": "welcome", "order": 0, "visible": true},
    {"instanceId": "teacher-profile", "widgetId": "profile-summary", "order": 1, "visible": true},
    {"instanceId": "teacher-tokens", "widgetId": "plan-tokens", "order": 2, "visible": true},
    {"instanceId": "teacher-courses", "widgetId": "enrolled-courses", "order": 3, "visible": true},
    {"instanceId": "teacher-progress", "widgetId": "courses-progress", "order": 4, "visible": true}
  ],
  "presetId": "teacher-default"
}
```

### School Admin (role: "school_admin")
```json
{
  "widgets": [
    {"instanceId": "school-welcome", "widgetId": "welcome", "order": 0, "visible": true},
    {"instanceId": "school-org", "widgetId": "org-overview", "order": 1, "visible": true},
    {"instanceId": "school-profile", "widgetId": "profile-summary", "order": 2, "visible": true},
    {"instanceId": "school-courses", "widgetId": "enrolled-courses", "order": 3, "visible": true}
  ],
  "presetId": "school-admin-default"
}
```

### Company Admin (role: "company_admin")
```json
{
  "widgets": [
    {"instanceId": "company-welcome", "widgetId": "welcome", "order": 0, "visible": true},
    {"instanceId": "company-org", "widgetId": "org-overview", "order": 1, "visible": true},
    {"instanceId": "company-profile", "widgetId": "profile-summary", "order": 2, "visible": true},
    {"instanceId": "company-courses", "widgetId": "enrolled-courses", "order": 3, "visible": true}
  ],
  "presetId": "company-admin-default"
}
```

### Admin (role: "admin")
```json
{
  "widgets": [
    {"instanceId": "admin-welcome", "widgetId": "welcome", "order": 0, "visible": true},
    {"instanceId": "admin-profile", "widgetId": "profile-summary", "order": 1, "visible": true},
    {"instanceId": "admin-tokens", "widgetId": "plan-tokens", "order": 2, "visible": true},
    {"instanceId": "admin-courses", "widgetId": "enrolled-courses", "order": 3, "visible": true},
    {"instanceId": "admin-activity", "widgetId": "activity", "order": 4, "visible": true}
  ],
  "presetId": "admin-default"
}
```

---

## Available Widget IDs

The following widgets are available in the LernsystemX widget registry:

| Widget ID | Description | Available To |
|-----------|-------------|--------------|
| `welcome` | Welcome message and quick actions | All users |
| `profile-summary` | User profile summary | All users |
| `plan-tokens` | Token balance and usage stats | Premium+ users |
| `enrolled-courses` | List of enrolled courses | All users |
| `courses-progress` | Course progress overview | All users |
| `activity` | Recent activity feed | Premium+ users |
| `org-overview` | Organisation overview | Org admins |

---

## Error Codes

| HTTP Code | Error | Description |
|-----------|-------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Validation error in request body |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User role does not have permission |
| 500 | Internal Server Error | Server error (database, etc.) |

---

## Business Rules

### Permission Rules

1. **Free Users:**
   - Can GET layout (receives role default)
   - Cannot PUT (save) custom layouts
   - Cannot POST (reset) layouts
   - Always see the fixed "user" role default

2. **Premium+ Users:**
   - Can GET layout (custom or role default)
   - Can PUT (save) custom layouts
   - Can POST (reset) to role default
   - Custom layouts persist in database

3. **Moderators & Support:**
   - Can GET layout (receives role default)
   - Cannot customize (similar to Free users)
   - Different default widgets than Free users

### Layout Logic

1. **GET /dashboard/layout:**
   - Check if user has custom layout in `dashboard_layouts` table
   - If yes: Return custom layout
   - If no: Return role-based default from `DEFAULT_LAYOUTS`

2. **PUT /dashboard/layout:**
   - Check if user role is in `CUSTOMIZABLE_ROLES`
   - If no: Return 403 Forbidden
   - If yes: Upsert into `dashboard_layouts` table
   - Return saved layout

3. **POST /dashboard/layout/reset:**
   - Check if user role is in `CUSTOMIZABLE_ROLES`
   - If no: Return 403 Forbidden
   - If yes: Delete row from `dashboard_layouts` table
   - Return role default from `DEFAULT_LAYOUTS`

---

## Database Schema

### Table: dashboard_layouts

Stores custom dashboard layouts for users.

```sql
CREATE TABLE dashboard_layouts (
    layout_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organisation_id INTEGER REFERENCES organisations(organisation_id) ON DELETE SET NULL,
    role VARCHAR(50) NOT NULL,
    layout_json JSONB NOT NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'user',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT check_source CHECK (source IN ('system', 'role', 'organisation', 'user'))
);

CREATE INDEX idx_dashboard_layout_user ON dashboard_layouts(user_id);
CREATE INDEX idx_dashboard_layout_source ON dashboard_layouts(source);
CREATE INDEX idx_dashboard_layout_role ON dashboard_layouts(role);
```

### JSONB Structure (layout_json)

```json
{
  "widgets": [
    {
      "instanceId": "string",
      "widgetId": "string",
      "order": 0,
      "visible": true,
      "config": {},
      "position": {
        "row": 0,
        "col": 0,
        "width": 12,
        "height": 4
      }
    }
  ],
  "presetId": "string | null",
  "version": 1
}
```

---

## Implementation Notes

### Technology Stack

- **Framework:** Flask (Python 3.11+)
- **Database:** PostgreSQL 15+ with JSONB
- **ORM:** Pure psycopg3 (no SQLAlchemy)
- **Validation:** Pydantic 2
- **Authentication:** Flask-JWT-Extended

### Repository Pattern

```python
# app/repositories/dashboard_repository.py
class DashboardRepository:
    @classmethod
    def get_user_layout(cls, user_id: int) -> Optional[Dict]:
        """Get user's custom layout from database"""

    @classmethod
    def save_user_layout(cls, user_id: int, role: str,
                        layout_json: Dict) -> Dict:
        """Save or update user's custom layout"""

    @classmethod
    def delete_user_layout(cls, user_id: int) -> bool:
        """Delete user's custom layout (for reset)"""
```

### Service Layer

```python
# app/services/dashboard_service.py
class DashboardService:
    CUSTOMIZABLE_ROLES = [
        'premium', 'creator', 'teacher',
        'school_admin', 'company_admin',
        'admin', 'superadmin'
    ]

    @classmethod
    def get_effective_layout(cls, user: Dict) -> DashboardLayout:
        """Get custom layout or role default"""

    @classmethod
    def save_layout(cls, user: Dict, layout: DashboardLayout) -> DashboardLayout:
        """Save layout with permission check"""

    @classmethod
    def reset_layout(cls, user: Dict) -> DashboardLayout:
        """Reset to role default"""
```

---

## Testing Examples

### cURL Examples

**Get Layout:**
```bash
curl -X GET http://localhost:5000/api/v1/dashboard/layout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Save Layout:**
```bash
curl -X PUT http://localhost:5000/api/v1/dashboard/layout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "widgets": [
      {
        "instanceId": "my-welcome",
        "widgetId": "welcome",
        "order": 0,
        "visible": true
      },
      {
        "instanceId": "my-courses",
        "widgetId": "enrolled-courses",
        "order": 1,
        "visible": true
      }
    ],
    "presetId": null
  }'
```

**Reset Layout:**
```bash
curl -X POST http://localhost:5000/api/v1/dashboard/layout/reset \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
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

# Get dashboard layout
headers = {'Authorization': f'Bearer {token}'}
layout_response = requests.get('http://localhost:5000/api/v1/dashboard/layout',
                               headers=headers)
print(layout_response.json())

# Save custom layout
custom_layout = {
    'widgets': [
        {'instanceId': 'my-welcome', 'widgetId': 'welcome',
         'order': 0, 'visible': True},
        {'instanceId': 'my-tokens', 'widgetId': 'plan-tokens',
         'order': 1, 'visible': True}
    ],
    'presetId': None
}
save_response = requests.put('http://localhost:5000/api/v1/dashboard/layout',
                             headers=headers, json=custom_layout)
print(save_response.json())

# Reset to default
reset_response = requests.post('http://localhost:5000/api/v1/dashboard/layout/reset',
                               headers=headers)
print(reset_response.json())
```

---

## Future Enhancements

### Planned Features

1. **Organisation-Level Layouts:**
   - Organisation admins can define default layouts for their members
   - Stored with `source='organisation'`

2. **Layout Templates/Presets:**
   - Predefined layout templates users can apply
   - "Minimalist", "Full Dashboard", "Focus Mode", etc.

3. **Widget Permissions:**
   - Fine-grained permissions per widget
   - Some widgets only visible to certain roles

4. **Layout Versioning:**
   - Track layout history
   - Rollback to previous layouts

5. **Layout Sharing:**
   - Share custom layouts between users
   - Import/export layout JSON

6. **ADHD Mode:**
   - Simplified layouts with reduced cognitive load
   - Special widgets for neurodivergent learners

---

## Compliance & Security

### ISO 27001:2013

- **Access Control:** JWT-based authentication on all endpoints
- **Data Validation:** Pydantic validation on all inputs
- **Audit Trail:** Created_at and updated_at timestamps
- **Least Privilege:** Role-based permissions enforced

### DSGVO/GDPR

- **Data Minimization:** Only necessary layout data stored
- **Right to Deletion:** Cascade delete when user deleted
- **Transparency:** Clear documentation of data usage

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-16 | Initial release - GET, PUT, POST endpoints |

---

## Support & Contact

For API support, please contact:
- **Documentation:** https://code.lernsystemx.com/docs
- **GitHub Issues:** https://github.com/lernsystemx/backend/issues
- **Email:** api-support@lernsystemx.com

---

**End of Dashboard Layout API Documentation**
