"""
Admin System Operations

System-Einstellungen, Analytics, Audit.

Struktur:
- settings/ - System Settings (von system_settings.py)
- system/ - System Admin (Stats, Audit, Providers)

Migration Status: IN PROGRESS
"""

# Import from system-operations submodules
from app.api.admin.system_operations.system import settings as system_settings_module

__all__ = ['system_settings_module']
