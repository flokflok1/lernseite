"""
System Monitoring Module

Provides system monitoring, health checks, and statistics.
"""

# System information
from app.api.v1.panel.admin.system.settings.monitoring.info import (
    get_system_version,
    get_deprecated_endpoints,
    get_detailed_health
)

# System statistics
from app.api.v1.panel.admin.system.settings.monitoring.stats import (
    get_admin_dashboard_user_stats,
    get_admin_dashboard_course_stats,
    get_admin_dashboard_system_stats
)

__all__ = [
    # System info
    'get_system_version',
    'get_deprecated_endpoints',
    'get_detailed_health',

    # System stats
    'get_admin_dashboard_user_stats',
    'get_admin_dashboard_course_stats',
    'get_admin_dashboard_system_stats'
]
