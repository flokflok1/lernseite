"""
Auth Core Module

JWT authentication and permissions system.

Features:
- JWT token management (access + refresh tokens)
- Device management (max 5 devices per user)
- Role-Based Access Control (RBAC)
- Permission decorators for routes

Usage:
    from src.core.auth import require_auth, require_role

    @app.route('/api/admin/users')
    @require_auth
    @require_role(['admin'])
    def admin_users():
        pass
"""

__all__ = []
