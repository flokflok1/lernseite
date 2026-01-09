"""
Admin User Management

Proxies to users/admin/

Struktur:
- users/ - User CRUD, Roles, Actions
- organisations/ - Organisation Management
- roles/ - Role Management

Alle Blueprints werden von users/admin/ importiert und re-exportiert.
"""

# Import from users/admin and re-export
from app.api.shared.users.admin import (
    admin_users_crud_bp,
    admin_users_roles_bp,
    admin_users_actions_bp
)

__all__ = [
    'admin_users_crud_bp',
    'admin_users_roles_bp',
    'admin_users_actions_bp'
]
