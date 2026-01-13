"""
Admin Repository Package

Administrative operations repository.

Example usage:
    >>> from app.repositories.admin.core import AdminRepository
    >>> from app.repositories.admin.roles import RolesRepository
"""

from app.repositories.admin.core import AdminRepository
from app.repositories.admin.roles import RolesRepository

__all__ = ['AdminRepository', 'RolesRepository']
