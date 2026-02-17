"""
LernsystemX Repository Package

Implements Repository Pattern for data access layer.
Each repository handles database operations for a specific entity.

ISO 9001:2015 compliant - Data access standardization
"""

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.repositories.user import UserRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
]
