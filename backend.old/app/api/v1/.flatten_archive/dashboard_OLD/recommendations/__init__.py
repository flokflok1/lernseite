"""
LernsystemX Dashboard Recommendations Package

KI-powered recommendation system.

Endpoints:
- GET    /api/v1/dashboard/recommendations           - Get recommendations
- POST   /api/v1/dashboard/recommendations/{id}/dismiss - Dismiss
- POST   /api/v1/dashboard/recommendations/{id}/accept  - Accept
- GET    /api/v1/dashboard/recommendations/stats     - Get statistics

ISO 27001:2013 compliant - Recommendation system
Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .endpoints import recommendations_bp

__all__ = ['recommendations_bp']
