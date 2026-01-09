"""
Admin Organisation Management

Admin-only endpoints for organisation CRUD and member management.

Modules:
    - crud.py: Organisation CRUD operations (list, create, get, update)
    - members.py: Member management (list users, assign user)

Permissions:
    - All endpoints require @admin_required or @token_required + org_admin

Endpoints:
    - GET/POST /api/v1/organisations
    - GET/PUT /api/v1/organisations/<id>
    - GET/POST /api/v1/organisations/<id>/users
    - POST /api/v1/organisations/<id>/assign-user
"""

# Placeholder - will contain actual crud.py and members.py
# For now, keep using the old structure for backward compatibility

__all__ = []
