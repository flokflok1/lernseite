"""
Authentication API package

Exports:
- auth_bp: Blueprint for authentication routes
"""

from app.api.v1.public.auth.routes import auth_bp

__all__ = ['auth_bp']
