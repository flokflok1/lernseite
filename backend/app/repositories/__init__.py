"""
LernsystemX Repository Package

Implements Repository Pattern for data access layer.
Each repository handles database operations for a specific entity.

ISO 9001:2015 compliant - Data access standardization
"""

from app.repositories.base_repository import BaseRepository
from app.repositories.user import UserRepository

__all__ = [
    'BaseRepository',
    'UserRepository'
]
