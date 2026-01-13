"""
Users API Package

Feature-based structure (flattened from admin/core/management/search/user):
- management_crud.py: Management-level user CRUD
- management_profile.py: Management-level profile operations
- management_status.py: Management-level status operations
- user_crud.py: User-level CRUD operations
- user_profile.py: User-level profile operations
- user_status.py: User-level status operations
- search.py: User search functionality

Note: Admin user operations (admin/) moved to /admin/users_*.py

All routes: /api/v1/users/*
"""

from app.api.v1.users import (
    management_crud,
    management_profile,
    management_status,
    user_crud,
    user_profile,
    user_status,
    search
)

__all__ = [
    'management_crud',
    'management_profile',
    'management_status',
    'user_crud',
    'user_profile',
    'user_status',
    'search'
]
