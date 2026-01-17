"""
Admin Settings - System Configuration

System-wide settings, configuration, and monitoring.

Modules:
- settings: System settings and environment management
- system_info: Version, system information
- system_stats: System statistics and metrics

All routes: /api/v1/admin/settings/system/*
Refactored: 2026-01-16 - Reorganized to /admin/settings/system/
"""

from . import (
    settings,
    system_info,
    system_stats
)

__all__ = ['settings', 'system_info', 'system_stats']
