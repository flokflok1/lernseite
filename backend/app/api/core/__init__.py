"""
LernsystemX Core API Package

Framework-core endpoints: health, auth, i18n, deprecation.

Refactored: 2026-01-08 - ISO/IEC 26515 + DDD compliant

Package Structure:
├── health.py        # Health checks, system status
├── deprecation.py   # API deprecation notices
├── auth/            # Authentication (login, register, 2FA)
└── i18n/            # Internationalization (translations)

Example usage:
    >>> from app.api.core.health import health_bp
    >>> from app.api.core.auth import login
"""

__all__ = ['health', 'deprecation', 'auth', 'i18n']
