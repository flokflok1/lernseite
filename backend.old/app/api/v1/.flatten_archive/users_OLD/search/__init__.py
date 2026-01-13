"""
LernsystemX Users API - Search Package

User search and statistics endpoints.

Structure:
    queries.py  ~107 lines  - /users/search, /users/stats

Refactored from users/search.py - 2026-01-08
Per Developer-Guide-KI Section 10.2 (Max 500 lines per file)
"""

from .queries import users_search_bp

__all__ = ['users_search_bp']
