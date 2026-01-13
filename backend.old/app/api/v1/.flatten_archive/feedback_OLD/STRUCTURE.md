# Feedback Domain Structure

**Date:** 2026-01-08
**Type:** DDD-Organized Structure

---

## Directory Tree

```
app/api/feedback/
│
├── __init__.py                     # Main blueprint registration
│   └── Registers: admin_bp, user_bp
│
├── admin/                          # Admin Domain
│   ├── __init__.py
│   └── management.py               # 10 admin endpoints
│       ├── List & Details (2)
│       │   ├── list_feedback()
│       │   └── get_feedback()
│       │
│       ├── Status & Priority (2)
│       │   ├── update_status()
│       │   └── update_priority()
│       │
│       ├── Responses & Notes (2)
│       │   ├── respond_to_feedback()
│       │   └── add_note()
│       │
│       ├── Dashboard (1)
│       │   └── get_dashboard()
│       │
│       └── AI Summaries (3)
│           ├── generate_summary()
│           ├── get_summaries()
│           └── get_summary()
│
├── user/                           # User Domain
│   ├── __init__.py
│   └── submit.py                   # 2 user endpoints
│       ├── submit_feedback()       # POST /feedback/submit (public/auth)
│       └── get_my_feedback()       # GET /feedback/my (auth)
│
└── core/                           # Factory Domain
    ├── __init__.py
    └── factory.py                  # DDD Factory Pattern
        ├── FeedbackFactory
        │   ├── Constants
        │   │   ├── VALID_TYPES
        │   │   ├── VALID_STATUSES
        │   │   └── VALID_PRIORITIES
        │   │
        │   ├── Creation Methods
        │   │   ├── create_feedback_data()
        │   │   ├── create_anonymous_feedback()
        │   │   ├── create_note_data()
        │   │   └── create_batch_summary_data()
        │   │
        │   └── Validation Methods
        │       ├── validate_status()
        │       └── validate_priority()
```

---

## API Routes

### Base Path: `/api/v1/feedback`

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Domain (Public)                        │
├─────────────────────────────────────────────────────────────────┤
│ POST   /submit          Submit feedback (anonymous OK)          │
│ GET    /my              Get my feedback (auth required)          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Admin Domain (admin/moderator/support)              │
├─────────────────────────────────────────────────────────────────┤
│ GET    /                List all feedback with filters           │
│ GET    /<id>            Get feedback details                     │
│ PATCH  /<id>/status     Update status                            │
│ PATCH  /<id>/priority   Update priority                          │
│ POST   /<id>/respond    Add admin response                       │
│ POST   /<id>/notes      Add internal note                        │
│ GET    /dashboard       Dashboard statistics                     │
│ POST   /generate-summary Generate AI summary (admin only)        │
│ GET    /summaries       Get recent summaries                     │
│ GET    /summaries/<id>  Get specific summary                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         Feedback API                             │
│                    (app/api/feedback)                            │
└──────────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
         ┌───────▼──────┐  ┌──▼─────┐  ┌──▼─────────┐
         │  admin/      │  │ user/  │  │  core/     │
         │  management  │  │ submit │  │  factory   │
         └───────┬──────┘  └──┬─────┘  └──┬─────────┘
                 │            │            │
                 └────────────┼────────────┘
                              │
                 ┌────────────▼────────────┐
                 │   FeedbackService       │
                 │   (Business Logic)      │
                 └────────────┬────────────┘
                              │
                 ┌────────────▼────────────┐
                 │  FeedbackRepository     │
                 │  (Database Access)      │
                 └─────────────────────────┘
```

---

## Data Flow

### User Submits Feedback

```
1. Client Request
   POST /api/v1/feedback/submit
   {
     "type": "bug",
     "message": "Something is broken",
     "context": {"course_id": "123"}
   }

2. API Layer (user/submit.py)
   └── submit_feedback()
       └── Validates basic input
       └── Checks optional auth

3. Service Layer (FeedbackService)
   └── submit_feedback()
       └── Business validation
       └── Call repository
       └── Trigger AI analysis

4. Repository Layer (FeedbackRepository)
   └── create_feedback()
       └── SQL INSERT
       └── Return feedback data

5. Response
   {
     "success": true,
     "data": {
       "feedback_id": "uuid",
       "message": "Feedback erfolgreich gesendet"
     }
   }
```

### Admin Updates Status

```
1. Client Request
   PATCH /api/v1/feedback/<id>/status
   {
     "status": "in_progress"
   }
   Authorization: Bearer <admin_token>

2. API Layer (admin/management.py)
   └── update_status()
       └── @role_required(['admin', 'moderator', 'support'])
       └── Validates status in request

3. Service Layer (FeedbackService)
   └── update_status()
       └── Business validation
       └── Call repository

4. Repository Layer (FeedbackRepository)
   └── update_status()
       └── SQL UPDATE
       └── Return updated feedback

5. Response
   {
     "success": true,
     "data": {
       "feedback_id": "uuid",
       "status": "in_progress",
       "assigned_to": "admin-id"
     }
   }
```

---

## Factory Pattern Usage

### Creating Feedback Data

```python
from app.api.feedback.core import FeedbackFactory

# With Factory (validated)
try:
    feedback_data = FeedbackFactory.create_feedback_data(
        feedback_type='bug',
        message='This is a bug with more than 10 characters',
        user_id='user-123',
        context={'course_id': 'course-456'}
    )
    # feedback_data is now validated and ready for repository
except ValueError as e:
    # Handle validation error
    return {"error": str(e)}, 400
```

### Without Factory (manual validation)

```python
# Manual validation (old way)
if feedback_type not in ['question', 'bug', 'suggestion', 'praise', 'other']:
    return {"error": "Invalid type"}, 400

if not message or len(message) < 10:
    return {"error": "Message too short"}, 400

# ... more validation ...
```

**Factory Benefits:**
- ✅ Single source of truth for validation
- ✅ Consistent error messages
- ✅ Reusable across endpoints
- ✅ Easier to test

---

## Authentication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Request Flow                               │
└──────────────────────────────────────────────────────────────┘

1. User Endpoint (submit.py)
   ├── Optional Auth: verify_jwt_in_request(optional=True)
   └── Anonymous OK

2. User Endpoint (my feedback)
   ├── Required Auth: @jwt_required()
   └── Returns current user's feedback only

3. Admin Endpoint (all)
   ├── Required Auth: @jwt_required()
   ├── Role Check: @role_required(['admin', 'moderator', 'support'])
   └── Full access to all feedback
```

---

## File Sizes

| File | LOC | Status |
|------|-----|--------|
| `admin/management.py` | 307 | ✅ < 500 |
| `user/submit.py` | 110 | ✅ < 500 |
| `core/factory.py` | 235 | ✅ < 500 |
| `__init__.py` | 42 | ✅ |
| `admin/__init__.py` | 12 | ✅ |
| `user/__init__.py` | 11 | ✅ |
| `core/__init__.py` | 14 | ✅ |
| **Total** | **731** | ✅ |

---

## Dependencies

```
app/api/feedback/
│
├── Flask (Blueprint, request, jsonify)
├── Flask-JWT-Extended (jwt_required, get_jwt_identity)
│
├── app.services.feedback_service (FeedbackService)
├── app.repositories.feedback.core (FeedbackRepository)
├── app.middleware.auth (role_required)
├── app.api (api_v1 blueprint)
```

**No circular dependencies!**

---

## Summary

**Structure Type:** Domain-Driven Design (DDD)
**Organization:** Role-based (admin/user/core)
**Pattern:** Factory Pattern for validation
**Endpoints:** 12 total (10 admin, 2 user)
**Files:** 9 files (8 Python, 1 Markdown)
**Total LOC:** 731 lines
**Quality:** All Quality Gates passed

---

**Version:** 1.0
**Last Updated:** 2026-01-08
