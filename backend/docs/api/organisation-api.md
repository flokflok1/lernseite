# LernsystemX Organisation API Documentation

**Version:** 1.0.0
**Standard:** ISO/IEC/IEEE 26515:2018 - API Documentation
**Compliance:** ISO 27001:2013 - Multi-tenant Data Security
**Last Updated:** 2025-11-16

## Overview

The Organisation API manages multi-tenant organisation structures for schools, companies, teacher teams, and creator teams. It provides comprehensive organisation management, user assignments, token pool management, and integration with subscription and billing systems.

### Key Features

- **Multi-Tenancy:** Complete data isolation between organisations
- **4 Organisation Types:** School, Company, Teacher Team, Creator Team
- **User Management:** Assign users to organisations with specific roles
- **Token Pooling:** Shared AI token pools for organisation members
- **Custom Branding:** Logo, colors, custom CSS per organisation
- **Domain Binding:** Custom domains with CNAME verification
- **DSGVO Compliance:** Special privacy mode for schools
- **Billing Integration:** Per-user, flat, or hybrid billing models
- **Class Management:** Classes for schools (organisation_classes)
- **Statistics:** Comprehensive org stats with subscription & token info

### Base URL

```
http://localhost:5000/api/v1
```

---

## Authentication

- **Admin Endpoints:** Create, list, delete organisations (admin/superadmin only)
- **Org Admin Endpoints:** Update organisation, assign users (org_admin role)
- **Member Endpoints:** View organisation details (organisation members)

### Headers

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## Organisation Types

### 1. School
```json
{
  "org_type": "school",
  "features": {
    "class_management": true,
    "student_role": true,
    "teacher_role": true,
    "exam_management": true,
    "dsgvo_mode": true,
    "liveroom_pro": true
  },
  "typical_use": "K-12 schools, universities, educational institutions"
}
```

### 2. Company
```json
{
  "org_type": "company",
  "features": {
    "employee_role": true,
    "trainer_role": true,
    "scorm_support": true,
    "compliance_reporting": true,
    "corporate_security": true
  },
  "typical_use": "Corporate training, enterprise learning"
}
```

### 3. Teacher Team
```json
{
  "org_type": "teacher_team",
  "features": {
    "small_groups": true,
    "course_collaboration": true,
    "shared_token_pool": true
  },
  "typical_use": "Small teacher collaboration groups"
}
```

### 4. Creator Team
```json
{
  "org_type": "creator_team",
  "features": {
    "content_collaboration": true,
    "course_co_authoring": true,
    "revenue_sharing": true,
    "marketplace_publishing": true
  },
  "typical_use": "Content creator teams, course authors"
}
```

---

## Organisation Roles

### Within Organisations

| Role | Description | Permissions |
|------|-------------|-------------|
| `org_admin` | Organisation Administrator | Full org management, user assignment, billing, domain, branding |
| `teacher` | Teacher/Instructor (Schools) | Class management, course assignment, student stats, exams |
| `trainer` | Corporate Trainer (Companies) | Employee training, course assignment, compliance reporting |
| `student` | Student (Schools) | Assigned courses, exams, LiveRoom participation |
| `employee` | Employee (Companies) | Assigned courses, compliance training |

---

## Billing Models

### 1. Per User
```json
{
  "billing_model": "per_user",
  "description": "Charge per active user per month",
  "example": "10 EUR/user/month"
}
```

### 2. Flat
```json
{
  "billing_model": "flat",
  "description": "Fixed monthly/annual fee regardless of users",
  "example": "500 EUR/month for unlimited users"
}
```

### 3. Hybrid
```json
{
  "billing_model": "hybrid",
  "description": "Base fee + per user above threshold",
  "example": "200 EUR base + 5 EUR/user above 50 users"
}
```

---

## Organisation Endpoints

### 1. List Organisations

Get all organisations with pagination and filtering (admin only).

**Endpoint:** `GET /organisations`

**Authentication:** Bearer Token (admin/superadmin required)

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| per_page | integer | No | 10 | Items per page (max: 100) |
| org_type | string | No | - | Filter by type (school, company, teacher_team, creator_team) |
| status | string | No | active | Filter by status (active, suspended, deleted) |

**Example Request:**
```http
GET /api/v1/organisations?page=1&per_page=10&org_type=school&status=active
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "items": [
    {
      "org_id": 1,
      "name": "Tech University",
      "org_type": "school",
      "domain": "tech.edu",
      "billing_model": "per_user",
      "token_pool": 100000,
      "token_used": 25000,
      "branding": {
        "primary_color": "#1E40AF",
        "secondary_color": "#F59E0B",
        "logo_url": "https://cdn.lsx.de/org/1/logo.png"
      },
      "settings": {
        "liveroom_enabled": true,
        "exams_enabled": true,
        "ai_enabled": true,
        "max_users": 1000,
        "dsgvo_mode": true
      },
      "status": "active",
      "created_at": "2025-01-01T10:00:00",
      "updated_at": "2025-11-15T14:30:00",
      "user_count": 750,
      "course_count": 120
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10,
  "total_pages": 3,
  "has_prev": false,
  "has_next": true
}
```

**Error Responses:**
- `403 Forbidden` - User is not admin/superadmin
- `500 Internal Server Error` - Server error

---

### 2. Create Organisation

Create a new organisation (admin only).

**Endpoint:** `POST /organisations`

**Authentication:** Bearer Token (admin/superadmin required)

**Request Body:**
```json
{
  "name": "Tech University",
  "org_type": "school",
  "domain": "tech.edu",
  "billing_model": "per_user",
  "token_pool": 100000,
  "branding": {
    "primary_color": "#1E40AF",
    "secondary_color": "#F59E0B",
    "logo_url": "https://cdn.lsx.de/org/logo.png",
    "custom_css": "body { font-family: 'Inter'; }"
  },
  "settings": {
    "liveroom_enabled": true,
    "whiteboard_enabled": true,
    "exams_enabled": true,
    "ai_enabled": true,
    "max_users": 1000,
    "max_classes": 50,
    "max_courses": 200,
    "language": "de",
    "timezone": "Europe/Berlin",
    "dsgvo_mode": true,
    "welcome_message": "Willkommen an der Tech University!"
  }
}
```

**Required Fields:**
- `name` (string, 2-255 chars)
- `org_type` (enum: school, company, teacher_team, creator_team)

**Optional Fields:**
- `domain` (string, must be unique)
- `billing_model` (enum: per_user, flat, hybrid, default: per_user)
- `token_pool` (integer, default: 0)
- `branding` (object)
- `settings` (object)

**Example Request:**
```http
POST /api/v1/organisations
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Tech University",
  "org_type": "school",
  "domain": "tech.edu",
  "token_pool": 100000
}
```

**Example Response (201 Created):**
```json
{
  "success": true,
  "message": "Organisation created successfully",
  "organisation": {
    "org_id": 5,
    "name": "Tech University",
    "org_type": "school",
    "domain": "tech.edu",
    "billing_model": "per_user",
    "token_pool": 100000,
    "token_used": 0,
    "status": "active",
    "created_at": "2025-11-16T10:00:00",
    "updated_at": "2025-11-16T10:00:00"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Validation error or domain already exists
- `403 Forbidden` - User is not admin/superadmin
- `500 Internal Server Error` - Server error

---

### 3. Get Organisation Details

Get organisation by ID.

**Endpoint:** `GET /organisations/<org_id>`

**Authentication:** Bearer Token

**Permissions:**
- Admins can view all organisations
- Organisation members can view their own organisation

**Example Request:**
```http
GET /api/v1/organisations/5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "organisation": {
    "org_id": 5,
    "name": "Tech University",
    "org_type": "school",
    "domain": "tech.edu",
    "billing_model": "per_user",
    "token_pool": 100000,
    "token_used": 25000,
    "branding": {
      "primary_color": "#1E40AF",
      "secondary_color": "#F59E0B",
      "logo_url": "https://cdn.lsx.de/org/5/logo.png"
    },
    "settings": {
      "liveroom_enabled": true,
      "exams_enabled": true,
      "ai_enabled": true,
      "max_users": 1000,
      "dsgvo_mode": true
    },
    "status": "active",
    "created_at": "2025-01-01T10:00:00",
    "updated_at": "2025-11-15T14:30:00"
  }
}
```

**Error Responses:**
- `403 Forbidden` - User cannot view this organisation
- `404 Not Found` - Organisation not found
- `500 Internal Server Error` - Server error

---

### 4. Update Organisation

Update organisation details.

**Endpoint:** `PUT /organisations/<org_id>`

**Authentication:** Bearer Token

**Permissions:**
- Admins can update all organisations
- org_admin can update their own organisation

**Request Body (all fields optional):**
```json
{
  "name": "Updated Name",
  "domain": "newdomain.edu",
  "billing_model": "flat",
  "branding": {
    "primary_color": "#2563EB"
  },
  "settings": {
    "max_users": 2000
  },
  "status": "active"
}
```

**Example Request:**
```http
PUT /api/v1/organisations/5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Tech University Berlin",
  "settings": {
    "max_users": 1500
  }
}
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Organisation updated successfully",
  "organisation": {
    "org_id": 5,
    "name": "Tech University Berlin",
    "org_type": "school",
    "settings": {
      "max_users": 1500
    },
    "updated_at": "2025-11-16T11:00:00"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Validation error
- `403 Forbidden` - User cannot update this organisation
- `404 Not Found` - Organisation not found
- `500 Internal Server Error` - Server error

---

### 5. List Organisation Users

List users for an organisation.

**Endpoint:** `GET /organisations/<org_id>/users`

**Authentication:** Bearer Token

**Permissions:**
- Admins can view users of all organisations
- org_admin can view users in their organisation
- teacher/trainer can view users in their organisation

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| per_page | integer | No | 50 | Items per page (max: 100) |
| org_role | string | No | - | Filter by org role (org_admin, teacher, student, etc.) |
| status | string | No | active | Filter by status |

**Example Request:**
```http
GET /api/v1/organisations/5/users?page=1&per_page=50&org_role=teacher
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "items": [
    {
      "id": 1,
      "org_id": 5,
      "user_id": 123,
      "org_role": "teacher",
      "status": "active",
      "joined_at": "2025-01-15T10:00:00",
      "created_at": "2025-01-15T10:00:00",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@tech.edu"
    },
    {
      "id": 2,
      "org_id": 5,
      "user_id": 124,
      "org_role": "teacher",
      "status": "active",
      "joined_at": "2025-02-01T09:00:00",
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane.smith@tech.edu"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 50,
  "total_pages": 1,
  "has_prev": false,
  "has_next": false
}
```

**Error Responses:**
- `403 Forbidden` - User cannot view users of this organisation
- `500 Internal Server Error` - Server error

---

### 6. Assign User to Organisation

Assign a user to an organisation with a specific role.

**Endpoint:** `POST /organisations/<org_id>/assign-user`

**Authentication:** Bearer Token

**Permissions:**
- Admins can assign users to any organisation
- org_admin can assign users to their organisation

**Request Body:**
```json
{
  "user_id": 123,
  "org_role": "student"
}
```

**Fields:**
- `user_id` (integer, required) - User ID to assign
- `org_role` (string, default: student) - Role (org_admin, teacher, trainer, student, employee)

**Example Request:**
```http
POST /api/v1/organisations/5/assign-user
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "user_id": 456,
  "org_role": "teacher"
}
```

**Example Response (201 Created):**
```json
{
  "success": true,
  "message": "User assigned to organisation successfully",
  "organisation_user": {
    "id": 10,
    "org_id": 5,
    "user_id": 456,
    "org_role": "teacher",
    "status": "active",
    "joined_at": "2025-11-16T12:00:00",
    "created_at": "2025-11-16T12:00:00"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Validation error or user already assigned
- `403 Forbidden` - User cannot assign users to this organisation
- `404 Not Found` - Organisation or user not found
- `500 Internal Server Error` - Server error

---

### 7. Get Organisation Statistics

Get comprehensive statistics for an organisation.

**Endpoint:** `GET /organisations/<org_id>/stats`

**Authentication:** Bearer Token

**Permissions:**
- Admins can view stats of all organisations
- org_admin can view stats of their organisation

**Example Request:**
```http
GET /api/v1/organisations/5/stats
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "org_id": 5,
    "total_users": 750,
    "active_users": 720,
    "users_by_role": {
      "org_admin": 2,
      "teacher": 15,
      "student": 703
    },
    "total_courses": 120,
    "active_courses": 95,
    "total_enrollments": 4500,
    "total_classes": 25,
    "token_wallet": {
      "balance": 100000,
      "used": 25000,
      "available": 75000
    },
    "subscription_plan": "school_plan",
    "subscription_status": "active",
    "subscription_expires_at": "2026-01-01T00:00:00",
    "ai_usage": {
      "total_requests": 1200,
      "total_tokens": 25000,
      "avg_tokens_per_request": 20.8
    }
  }
}
```

**Response Fields:**
- `org_id` - Organisation ID
- `total_users` - Total number of users
- `active_users` - Number of active users
- `users_by_role` - User counts by organisation role
- `total_courses` - Total courses
- `active_courses` - Published/active courses
- `total_enrollments` - Total course enrollments
- `total_classes` - Number of classes (schools only)
- `token_wallet` - Token pool info (balance, used, available)
- `subscription_plan` - Subscription plan name
- `subscription_status` - Subscription status
- `subscription_expires_at` - Subscription expiry date
- `ai_usage` - AI usage statistics (optional)

**Error Responses:**
- `403 Forbidden` - User cannot view stats of this organisation
- `404 Not Found` - Organisation not found
- `500 Internal Server Error` - Server error

---

## Integration with Billing & Token Systems

### Token Pool Management

Organisations have a shared token pool that all members can use for AI features.

**Key Points:**
- Token pool is stored in `organisations.token_pool` (available balance)
- `organisations.token_used` tracks consumed tokens
- Available tokens = `token_pool - token_used`
- Members of organisation use organisation token pool instead of personal wallets
- Token consumption is tracked via `OrganisationRepository.consume_tokens(org_id, amount)`

**Example Token Consumption Flow:**
```python
# When a user from organisation uses AI features:
org_id = user['organisation_id']
tokens_needed = 500

# Check available tokens
org = OrganisationRepository.get_organisation_by_id(org_id)
available = org['token_pool'] - org['token_used']

if available >= tokens_needed:
    # Consume tokens from organisation pool
    OrganisationRepository.consume_tokens(org_id, tokens_needed)
else:
    # Insufficient tokens - show upgrade message
    raise InsufficientTokensError()
```

### Subscription Integration

Organisations can have subscriptions (school_plan, company_plan).

**Integration Points:**
- `SubscriptionRepository.get_subscription_for_organisation(org_id)`
- Subscription features apply to all organisation members
- Organisation subscription takes precedence over individual user subscriptions
- Monthly token grants are added to organisation token pool

**Example Subscription Check:**
```python
# Get effective plan for user in organisation
user = get_current_user()
if user['organisation_id']:
    subscription = SubscriptionRepository.get_subscription_for_organisation(
        user['organisation_id']
    )
    if subscription:
        plan_features = subscription['features']
        # Apply org features to user
```

### BillingService Integration

The `BillingService.get_effective_plan_for_user(user_id)` returns organisation plan if user is in an organisation:

```python
plan_info = BillingService.get_effective_plan_for_user(user_id)

# Returns:
{
    "plan_name": "school_plan",
    "tier": "enterprise",
    "features": {...},
    "source": "organisation"  # or "user" or "default"
}
```

---

## Example Workflows

### 1. School Setup Workflow

**Step 1: Admin creates school organisation**
```http
POST /api/v1/organisations
{
  "name": "Berlin Tech School",
  "org_type": "school",
  "domain": "berlin-tech.edu",
  "token_pool": 500000,
  "settings": {
    "max_users": 2000,
    "dsgvo_mode": true
  }
}
```

**Step 2: Admin assigns school subscription**
```http
POST /api/v1/subscriptions
{
  "organisation_id": 5,
  "plan_id": 5,
  "billing_cycle": "annual"
}
```

**Step 3: School admin assigns teachers**
```http
POST /api/v1/organisations/5/assign-user
{
  "user_id": 100,
  "org_role": "org_admin"
}

POST /api/v1/organisations/5/assign-user
{
  "user_id": 101,
  "org_role": "teacher"
}
```

**Step 4: Teachers assign students**
```http
POST /api/v1/organisations/5/assign-user
{
  "user_id": 200,
  "org_role": "student"
}
```

**Step 5: Students use AI features (from org token pool)**
- Student uses AI tutor
- Tokens consumed from organisation pool: `token_used += tokens`
- Student doesn't need personal subscription

### 2. Company Training Workflow

**Step 1: Create company organisation**
```http
POST /api/v1/organisations
{
  "name": "TechCorp GmbH",
  "org_type": "company",
  "billing_model": "per_user",
  "token_pool": 1000000
}
```

**Step 2: Assign company subscription**
```http
POST /api/v1/subscriptions
{
  "organisation_id": 6,
  "plan_id": 6,
  "billing_cycle": "annual"
}
```

**Step 3: HR assigns employees and trainers**
```http
POST /api/v1/organisations/6/assign-user
{"user_id": 300, "org_role": "org_admin"}

POST /api/v1/organisations/6/assign-user
{"user_id": 301, "org_role": "trainer"}

POST /api/v1/organisations/6/assign-user
{"user_id": 400, "org_role": "employee"}
```

**Step 4: Monitor usage via stats**
```http
GET /api/v1/organisations/6/stats
```

### 3. Token Management Workflow

**Check organisation token balance:**
```http
GET /api/v1/organisations/5/stats

Response:
{
  "token_wallet": {
    "balance": 500000,
    "used": 125000,
    "available": 375000
  }
}
```

**Add tokens to organisation (admin only):**
```python
# Via repository (internal)
OrganisationRepository.add_tokens(org_id=5, amount=100000)
```

**Token consumption tracking:**
```python
# When AI feature is used
OrganisationRepository.consume_tokens(org_id=5, amount=500)
```

---

## Security & Compliance

### Multi-Tenant Isolation
- Complete data isolation between organisations
- Users can only access their own organisation data
- org_admin cannot access other organisations
- Row-level security enforced in queries

### DSGVO School Mode
- Enable `settings.dsgvo_mode: true` for schools
- Strict privacy controls
- Limited data retention
- Parental consent tracking

### Corporate Security Mode
- Enable `settings.corporate_security: true` for companies
- SSO integration
- Audit logging
- Compliance reporting

### Domain Verification
- Custom domains require CNAME verification
- TLS certificate management
- Domain ownership validation

---

## Error Codes

| Status Code | Error | Description |
|-------------|-------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Validation error or invalid data |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

---

## Rate Limiting

- **Standard:** 100 requests/minute per user
- **Admin:** 500 requests/minute
- **Subscription:** Based on plan tier

---

## Changelog

### Version 1.0.0 (2025-11-16)
- Initial release
- 7 organisation endpoints
- 4 organisation types
- 5 organisation roles
- 3 billing models
- Integration with subscription and token systems
- Comprehensive statistics endpoint

---

## Support

For questions or issues, contact:
- **Email:** support@lernsystemx.de
- **Documentation:** https://docs.lernsystemx.de
- **API Status:** https://status.lernsystemx.de
