"""
Admin User Management

Admin endpoints for user CRUD operations, role management, and moderation actions.

Struktur:
- users.py - User CRUD, Groups (5 endpoints)
- users_part2.py - Moderation: Ban/Unban, Delete, Verify (4 endpoints)

Phase B24 - Admin User Management Implementation
"""

# Import user management endpoints (CRUD & groups)
from . import users

# Import moderation endpoints (ban, unban, delete, verify)
from . import users_part2

__all__ = ['users', 'users_part2']
