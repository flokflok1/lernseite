"""
System Features Domain

Domain for managing System Features configuration at course/chapter/lesson level.

Journeys:
- Admin Journey: Feature types listing, course-level configuration (5 endpoints)

Features:
- 25 System-Features (tools/services separate from 12 Content-LMs)
- Course-level enable/disable with inheritance
- Feature-specific configuration
- Bulk operations

Phase: 5.3.1 - System-Features Management Migration
"""

from .journeys import ALL_JOURNEY_BLUEPRINTS

__all__ = ['ALL_JOURNEY_BLUEPRINTS']
