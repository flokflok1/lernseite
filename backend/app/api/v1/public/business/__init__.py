"""
B2B Business API Package

Public endpoints for B2B customer interaction.
"""

from app.api.v1.public.business.contact import bp
import app.api.v1.public.business.contact_part2  # noqa: F401 - registers routes on bp

__all__ = ['bp']
