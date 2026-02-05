# LernsystemX Permissions Reference

This document describes the permission codes used in the LernsystemX backend for Group-Based Access (GBA) control.

## Permission Format

Permissions follow the format: `category.resource.action`

- **category**: Domain area (e.g., `admin`, `content`, `runner`)
- **resource**: Specific resource type (e.g., `users`, `courses`, `sessions`)
- **action**: Operation type (e.g., `read`, `write`, `execute`, `delete`)

> **Note**: Some legacy permissions use colon (`:`) as action separator. New permissions should use dot (`.`) for consistency with decorator usage.

## Runner Permissions

The Runner API controls learning method session execution. These permissions gate access to session operations.

| Permission Code | Display Name | Description | Usage |
|----------------|--------------|-------------|-------|
| `runner.sessions.execute` | Execute Runner Sessions | Start, submit answers, and complete learning method sessions | Required for `POST /api/v1/runner/sessions`, `PATCH /api/v1/runner/sessions/{id}/state`, `POST /api/v1/runner/sessions/{id}/finish` |
| `runner.sessions.read` | Read Runner Sessions | View session state, progress, and history | Required for `GET /api/v1/runner/sessions/{id}` |

### Typical Group Assignments

- **Students/Learners**: Both `runner.sessions.execute` and `runner.sessions.read`
- **Teachers**: Both permissions (to monitor student progress)
- **Content Creators**: `runner.sessions.read` (for testing content)
- **Admins**: All permissions

## Admin Permissions

| Permission Code | Description |
|----------------|-------------|
| `admin.ai-jobs:read` | View AI job details, history, and status |
| `admin.ai-jobs:write` | Create, update, cancel, or manage AI jobs |
| `admin.analytics:read` | View system-wide analytics and reports |
| `admin.courses:write` | Create, edit, publish, or delete courses as admin |
| `admin.system:read` | View system configuration, settings, and status |
| `admin.system:write` | Modify system configuration and settings |
| `admin.users:read` | View user accounts, roles, and information |
| `admin.users:write` | Create, edit, or modify user accounts |
| `admin.users:delete` | Delete or deactivate user accounts |

## Content Permissions

| Permission Code | Description |
|----------------|-------------|
| `content.courses:read` | View course details, chapters, and lessons |
| `content.courses:write` | Create, edit, or update courses |
| `content.courses:delete` | Delete courses and associated content |
| `content.moderation:moderate` | Review, approve, or reject user-generated content |

## Moderation Permissions

| Permission Code | Description |
|----------------|-------------|
| `moderation.feedback:read` | View feedback on moderated content |
| `moderation.feedback:write` | Add feedback or notes on moderation decisions |

## Organization Permissions

| Permission Code | Description |
|----------------|-------------|
| `org.analytics:read` | View organization-level analytics and statistics |

## Database Schema

Permissions are stored in `core.permissions` table:

```sql
CREATE TABLE core.permissions (
    id UUID PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,  -- e.g. 'runner.sessions.execute'
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    permission_type VARCHAR(50) NOT NULL DEFAULT 'general',
    category VARCHAR(100),
    is_system_permission BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## Usage in Code

### Decorators (Flask Routes)

```python
from app.api.middleware.auth import require_auth, require_permission

@bp.route('/sessions/start', methods=['POST'])
@require_auth
@require_permission('runner.sessions.execute')
def start_session():
    # Only users with runner.sessions.execute can access
    pass
```

### Service-Level Checks

```python
from app.application.services.system.auth.permission import PermissionService

if not PermissionService.check_permission(user, 'runner.sessions.execute'):
    return None, ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS
```

## Seeding Permissions

Permissions are seeded via SQL migration `022_permissions_registry.sql`:

```sql
INSERT INTO core.permissions (code, display_name, description, permission_type, category, is_system_permission) VALUES
    ('runner.sessions.execute', 'Execute Runner Sessions', 'Start, submit answers, and complete learning method sessions', 'general', 'runner', TRUE),
    ('runner.sessions.read', 'Read Runner Sessions', 'View session state, progress, and history', 'general', 'runner', TRUE)
ON CONFLICT (code) DO NOTHING;
```

## Related Documentation

- `docs/runner/` - Runner API architecture and endpoints
- `LernsystemX-Doku/05_Technical/02_API-Spezifikation.md` - Full API specification
- `LernsystemX-Doku/01_Core/05_Sicherheit-Berechtigungen.md` - Security architecture
