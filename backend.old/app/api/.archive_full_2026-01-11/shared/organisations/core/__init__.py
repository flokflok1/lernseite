"""
Organisation Core Domain (DDD Components)

Exports:
    - OrganisationFactory: Factory for creating organisations
    - OrganisationService: Business logic service layer
    - OrgType: Organisation type value object
    - MemberRole: Member role value object
    - BillingModel: Billing model value object

DDD Pattern Implementation:
    - Factory Pattern for complex entity creation
    - Service Layer for business logic orchestration
    - Value Objects for domain concepts with validation

Usage:
    >>> from app.api.shared.organisations.core import OrganisationFactory, OrgType
    >>> org = OrganisationFactory.create_school('Tech Uni', 'tech.edu')
    >>> org_type = OrgType(OrgType.SCHOOL)
"""

from .factory import OrganisationFactory
from .services import OrganisationService
from .value_objects import OrgType, MemberRole, BillingModel

__all__ = [
    'OrganisationFactory',
    'OrganisationService',
    'OrgType',
    'MemberRole',
    'BillingModel',
]
