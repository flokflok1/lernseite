"""Analytics Module - System and Organization Analytics"""

from app.api.v1.analytics.core import analytics_bp, analytics_admin_bp
from app.api.v1.analytics.organisations import org_analytics_bp

__all__ = ['analytics_bp', 'analytics_admin_bp', 'org_analytics_bp']
