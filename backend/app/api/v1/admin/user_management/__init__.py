"""
Admin User Management

Admin endpoints for user CRUD operations, role management, and moderation actions.

Struktur:
- users.py - User CRUD, Roles, Ban/Unban, Delete, Verify (7 endpoints) ✅
- organisations/ - Organisation Management (handled by /api/v1/organisations/)
- roles/ - Role Management (handled by /api/v1/admin/roles/)

Phase B24 - Admin User Management Implementation
"""

# Import user management endpoints
from app.api.v1.admin.user_management import users

__all__ = ['users']
