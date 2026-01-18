"""
Admin Repository Package

Administrative operations repository.

Example usage:
    >>> from app.infrastructure.persistence.repositories.admin.core import AdminRepository
    >>> from app.infrastructure.persistence.repositories.admin.roles import RolesRepository
"""

from app.infrastructure.persistence.repositories.admin.core import AdminRepository
from app.infrastructure.persistence.repositories.admin.roles import RolesRepository

__all__ = ['AdminRepository', 'RolesRepository']
