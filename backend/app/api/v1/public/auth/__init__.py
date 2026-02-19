"""
Authentication API package

Routes split across two files for Quality Gate G01 compliance (max 500 lines):
- routes.py: Core auth (register, login, refresh, logout, me)
- routes_part2.py: Password reset and 2FA endpoints

Exports:
- auth_bp: Blueprint for authentication routes
"""

from app.api.v1.public.auth.routes import auth_bp
import app.api.v1.public.auth.routes_part2  # noqa: F401 - registers routes on auth_bp

__all__ = ['auth_bp']
