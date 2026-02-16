"""
Admin Settings - System Configuration

System-wide settings, configuration, and monitoring.

Subdirectories:
- config/: System settings and configuration management
- monitoring/: System monitoring, health checks, and statistics

All routes: /api/v1/admin/settings/system/*
Refactored: 2026-01-16 - Reorganized to /admin/settings/system/
"""

# Configuration (6 functions)
from app.api.v1.panel.admin.system.settings.config import (
    switch_system_mode,
    toggle_maintenance_mode,
    get_system_status,
    get_all_settings,
    get_setting,
    update_setting
)

# Monitoring (6 functions)
from app.api.v1.panel.admin.system.settings.monitoring import (
    # System info
    get_system_version,
    get_deprecated_endpoints,
    get_detailed_health,
    # System stats
    get_admin_dashboard_user_stats,
    get_admin_dashboard_course_stats,
    get_admin_dashboard_system_stats
)

__all__ = [
    # Config
    'switch_system_mode',
    'toggle_maintenance_mode',
    'get_system_status',
    'get_all_settings',
    'get_setting',
    'update_setting',

    # Monitoring - System info
    'get_system_version',
    'get_deprecated_endpoints',
    'get_detailed_health',

    # Monitoring - System stats
    'get_admin_dashboard_user_stats',
    'get_admin_dashboard_course_stats',
    'get_admin_dashboard_system_stats'
]
