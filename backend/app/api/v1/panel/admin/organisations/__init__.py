"""Organisations Module - Organization Management"""

from app.api.v1.panel.admin.organisations.core import organisations_bp

# Import core_part2 to register member management routes on the blueprint
import app.api.v1.panel.admin.organisations.core_part2  # noqa: F401

__all__ = ['organisations_bp']
