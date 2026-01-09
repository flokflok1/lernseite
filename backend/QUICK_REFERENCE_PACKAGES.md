# Quick Reference: auth, dashboard, exams Packages

**Date:** 2026-01-08
**Status:** ✅ ALL COMPLETE

---

## Package Overview

| Package | Status | Modules | Endpoints | Max LOC |
|---------|--------|---------|-----------|---------|
| **auth/** | ✅ Refactored | 7 | 11 | 290 |
| **dashboard/** | ✅ Refactored | 9 | 14 | 400 |
| **exams/** | ✅ Refactored | 7 | 11 | 383 |

---

## 1. auth/ Package

### Structure
```
auth/
├── login.py           - /login, /refresh, /logout, /me (4 endpoints)
├── register.py        - /register, /verify-email (2 endpoints)
├── password.py        - /forgot-password, /reset-password (2 endpoints)
└── two_factor.py      - /2fa/setup, /verify, /disable (3 endpoints)
```

### Key Endpoints
```bash
# Login & Session
POST /api/v1/auth/login              # Login with 2FA support
POST /api/v1/auth/refresh            # Refresh JWT token
POST /api/v1/auth/logout             # Revoke token
GET  /api/v1/auth/me                 # Current user info

# Registration
POST /api/v1/auth/register           # User registration
POST /api/v1/auth/verify-email       # Email verification

# Password Recovery
POST /api/v1/auth/forgot-password    # Request reset
POST /api/v1/auth/reset-password     # Reset with token

# Two-Factor Authentication
POST /api/v1/auth/2fa/setup          # Setup 2FA
POST /api/v1/auth/2fa/verify         # Verify TOTP code
POST /api/v1/auth/2fa/disable        # Disable 2FA
```

---

## 2. dashboard/ Package

### Structure
```
dashboard/
├── layouts/
│   └── endpoints.py   - Layout management (3 endpoints)
├── widgets/
│   ├── models.py      - Pydantic models
│   ├── registry.py    - Widget registry (1 endpoint)
│   └── instances.py   - Widget CRUD (6 endpoints)
└── recommendations/
    └── endpoints.py   - KI recommendations (4 endpoints)
```

### Key Endpoints

#### Layouts (3)
```bash
GET  /api/v1/dashboard/layout        # Get user's layout
PUT  /api/v1/dashboard/layout        # Save custom layout
POST /api/v1/dashboard/layout/reset  # Reset to default
```

#### Widgets (7)
```bash
GET    /api/v1/dashboard/widgets             # Available widgets
GET    /api/v1/dashboard/widgets/user        # User's widgets
POST   /api/v1/dashboard/widgets/add         # Add widget
DELETE /api/v1/dashboard/widgets/{id}        # Remove widget
PATCH  /api/v1/dashboard/widgets/{id}/position  # Update position
PATCH  /api/v1/dashboard/widgets/{id}/settings  # Update settings
PATCH  /api/v1/dashboard/widgets/{id}/toggle    # Toggle visibility
```

#### Recommendations (4)
```bash
GET  /api/v1/dashboard/recommendations           # Get recommendations
POST /api/v1/dashboard/recommendations/{id}/dismiss  # Dismiss
POST /api/v1/dashboard/recommendations/{id}/accept   # Accept
GET  /api/v1/dashboard/recommendations/stats     # Statistics
```

---

## 3. exams/ Package

### Structure
```
exams/
├── context.py         - Exam context detection (1 endpoint)
├── simulations.py     - Exam CRUD (4 endpoints)
├── generation.py      - KI generation (1 endpoint)
├── attempts.py        - Attempt lifecycle (3 endpoints)
└── user_profile.py    - User settings (2 endpoints)
```

### Key Endpoints

#### Context & Creation (2)
```bash
GET  /api/v1/courses/{id}/exam-context       # Detect exam context
POST /api/v1/courses/{id}/exam-simulations   # Create simulation
```

#### Simulation Management (4)
```bash
GET    /api/v1/exam-simulations              # List simulations
GET    /api/v1/exam-simulations/{id}         # Get details
DELETE /api/v1/exam-simulations/{id}         # Delete simulation
POST   /api/v1/exam-simulations/{id}/generate # Generate (Celery)
```

#### Attempts (3)
```bash
POST /api/v1/exam-simulations/{id}/start     # Start attempt
GET  /api/v1/exam-simulations/{id}/attempts  # Get attempts
POST /api/v1/exam-simulations/{id}/submit    # Submit attempt
```

#### User Profile (2)
```bash
GET /api/v1/user-profile/exam-settings       # Get settings
PUT /api/v1/user-profile/exam-settings       # Update settings
```

---

## Import Examples

### Backend (Python)

```python
# Import entire package
from app.api import auth
from app.api import dashboard
from app.api import exams

# Import specific blueprints
from app.api.auth.login import auth_login_bp
from app.api.dashboard.widgets import widgets_registry_bp
from app.api.exams.simulations import exam_simulations_bp

# Import models
from app.api.dashboard.widgets.models import AddWidgetRequest
from app.api.exams.models import ExamSimulationCreate
```

### Service Layer

```python
# Use in services
from app.api.dashboard.widgets.models import AddWidgetRequest

def add_widget_to_dashboard(user, widget_key):
    request = AddWidgetRequest(
        widget_key=widget_key,
        position_x=0,
        position_y=0,
        width=2,
        height=2
    )
    # Use request...
```

---

## Testing Endpoints

### With curl

```bash
# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'

# Get Dashboard Layout (requires token)
curl -X GET http://localhost:5000/api/v1/dashboard/layout \
  -H "Authorization: Bearer YOUR_TOKEN"

# List Exam Simulations (requires token)
curl -X GET http://localhost:5000/api/v1/exam-simulations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### With Python requests

```python
import requests

# Login
response = requests.post(
    'http://localhost:5000/api/v1/auth/login',
    json={'email': 'user@example.com', 'password': 'SecurePass123!'}
)
token = response.json()['access_token']

# Get widgets
response = requests.get(
    'http://localhost:5000/api/v1/dashboard/widgets',
    headers={'Authorization': f'Bearer {token}'}
)
widgets = response.json()['widgets']
```

---

## Common Tasks

### Add New Endpoint

1. **Choose appropriate sub-package:**
   - `auth/` for authentication
   - `dashboard/layouts/` for layout management
   - `dashboard/widgets/` for widget operations
   - `dashboard/recommendations/` for KI recommendations
   - `exams/` for exam operations

2. **Add endpoint to module:**
   ```python
   @blueprint.route('/new-endpoint', methods=['POST'])
   @token_required
   def new_endpoint():
       # Implementation
       pass
   ```

3. **Test endpoint:**
   ```bash
   curl -X POST http://localhost:5000/api/v1/module/new-endpoint
   ```

### Add New Blueprint

1. **Create new module:**
   ```python
   # app/api/dashboard/new_feature/endpoints.py
   from flask import Blueprint

   new_feature_bp = Blueprint('new_feature', __name__, url_prefix='/dashboard/new-feature')
   ```

2. **Register in package __init__.py:**
   ```python
   # app/api/dashboard/__init__.py
   from .new_feature import new_feature_bp

   ALL_BLUEPRINTS = [
       # ... existing ...
       new_feature_bp,
   ]
   ```

---

## Troubleshooting

### Blueprint Not Found
```
Error: Blueprint 'auth_login' not registered
```
**Solution:** Check that `app/api/__init__.py` imports the package:
```python
from app.api import auth  # This triggers registration
```

### Import Errors
```
ImportError: cannot import name 'auth_login_bp'
```
**Solution:** Use package import:
```python
# Instead of:
from app.api.auth import auth_login_bp  # ❌

# Use:
from app.api.auth.login import auth_login_bp  # ✅
```

### 404 Not Found
```
GET /api/v1/auth/login → 404
```
**Solution:** Check blueprint `url_prefix` chain:
- `api_v1` → `/api/v1`
- `auth_login_bp` → `/auth`
- Endpoint → `/login`
- **Result:** `/api/v1/auth/login`

---

## File Locations

```
backend/
├── app/api/
│   ├── auth/                    # Authentication package
│   ├── dashboard/               # Dashboard package
│   └── exams/                   # Exam simulations package
├── REFACTORING_AUTH_DASHBOARD_EXAMS.md  # Full refactoring report
└── QUICK_REFERENCE_PACKAGES.md  # This file
```

---

## Related Documentation

- **Full Refactoring Report:** `backend/REFACTORING_AUTH_DASHBOARD_EXAMS.md`
- **Backend Structure:** `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`
- **Developer Guide:** `LernsystemX-Doku/07_Setup-Dev/03_Developer-Guide-KI.md`
- **API Specification:** `LernsystemX-Doku/05_Technical/15_API-Spezifikation.md`

---

*Last Updated: 2026-01-08*
*Refactored by: Agent 4 - Package Structure*
