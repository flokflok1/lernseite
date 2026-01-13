"""
Admin Organisation Management

Admin-only endpoints for organisation CRUD and member management.

Modules:
    - crud.py: Organisation CRUD operations (list, create, get, update)
    - members.py: Member management (list users, assign user)
    - _helpers: Helper functions (re-exported from parent)

Permissions:
    - All endpoints require @admin_required or @token_required + org_admin

Endpoints:
    - GET/POST /api/v1/organisations
    - GET/PUT /api/v1/organisations/<id>
    - GET/POST /api/v1/organisations/<id>/users
    - POST /api/v1/organisations/<id>/assign-user
"""

# Import modules to trigger blueprint registration
from app.api.shared.organisations.admin import crud
from app.api.shared.organisations.admin import members

# Re-export helpers from parent package for backward compatibility
from app.api.shared.organisations import _helpers

__all__ = ['crud', 'members', '_helpers']
