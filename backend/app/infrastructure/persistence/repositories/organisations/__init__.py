"""
Organisations Repository Package

Organisation management repository for schools and companies.

Example usage:
    >>> from app.infrastructure.persistence.repositories.organisations import OrganisationRepository
"""

from app.infrastructure.persistence.repositories.organisations.core import OrganisationRepository
from app.infrastructure.persistence.repositories.organisations.core_part2 import OrganisationUsersMixin

__all__ = ['OrganisationRepository', 'OrganisationUsersMixin']
