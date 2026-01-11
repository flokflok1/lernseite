"""
Admin System Operations

System-Einstellungen, Analytics, Audit.

Struktur:
- settings/ - System Settings (von system_settings.py)
- system/ - System Admin (Stats, Audit, Providers)

Migration Status: IN PROGRESS
"""

# Import from system-operations submodules to trigger blueprint registration
# Note: Import subpackage to trigger its __init__.py which registers routes
try:
    from app.api.admin.system_operations import system
    from app.api.admin.system_operations.system import settings as system_settings_module
except ImportError as e:
    import sys
    print(f"Warning: Failed to import system_operations modules: {e}", file=sys.stderr)
    system = None
    system_settings_module = None

__all__ = ['system', 'system_settings_module']
