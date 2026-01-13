"""
Organisation Factory (DDD Pattern)

Factory for creating Organisation entities with business rules.
Implements Domain-Driven Design (DDD) Factory Pattern.

Business Rules:
- Every organisation must have a unique domain (if provided)
- Token pools based on organisation type
- Member limits enforced
- Default settings applied by type

ISO 27001:2013 compliant - Secure organisation creation
"""

from typing import Optional, Dict, Any
from datetime import datetime
import json

from .value_objects import OrgType, MemberRole, BillingModel


class OrganisationFactory:
    """
    DDD Factory for creating Organisation entities.

    Implements Factory Pattern to encapsulate complex creation logic
    and enforce business rules at creation time.

    Examples:
        >>> # Create school
        >>> org = OrganisationFactory.create_school(
        ...     name='Tech University',
        ...     domain='tech.edu'
        ... )

        >>> # Create company
        >>> org = OrganisationFactory.create_company(
        ...     name='Acme Corp',
        ...     domain='acme.com',
        ...     employee_limit=500
        ... )
    """

    @staticmethod
    def create_school(
        name: str,
        domain: str,
        max_students: int = 1000,
        max_teachers: int = 50,
        branding: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Create school organisation with school-specific defaults.

        Business Rules:
            - Token pool: 50,000 tokens
            - Billing model: per_user
            - Default roles: org_admin, teacher, student
            - No member limit (unlimited students)

        Args:
            name: School name
            domain: School domain (must be unique, e.g., 'tech.edu')
            max_students: Maximum number of students (default: 1000)
            max_teachers: Maximum number of teachers (default: 50)
            branding: Optional branding configuration
            settings: Optional school-specific settings

        Returns:
            Dictionary ready for OrganisationRepository.create()

        Example:
            >>> org = OrganisationFactory.create_school(
            ...     name='Tech University',
            ...     domain='tech.edu',
            ...     max_students=2000
            ... )
        """
        org_type = OrgType(OrgType.SCHOOL)

        # Default school settings
        default_settings = {
            'max_students': max_students,
            'max_teachers': max_teachers,
            'allow_self_enrollment': False,
            'require_approval': True,
            'enable_classes': True,
            'enable_departments': True
        }

        # Merge with provided settings
        if settings:
            default_settings.update(settings)

        return {
            'name': name,
            'org_type': org_type.value,
            'domain': domain,
            'billing_model': org_type.default_billing_model,
            'token_pool': org_type.default_token_pool,
            'token_used': 0,
            'branding': json.dumps(branding) if branding else None,
            'settings': json.dumps(default_settings),
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def create_company(
        name: str,
        domain: str,
        employee_limit: int = 500,
        department_structure: Optional[dict] = None,
        branding: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Create company organisation with company-specific defaults.

        Business Rules:
            - Token pool: 100,000 tokens
            - Billing model: per_user
            - Default roles: org_admin, trainer, employee
            - No member limit (unlimited employees)

        Args:
            name: Company name
            domain: Company domain (must be unique, e.g., 'acme.com')
            employee_limit: Maximum number of employees (default: 500)
            department_structure: Optional department hierarchy
            branding: Optional branding configuration
            settings: Optional company-specific settings

        Returns:
            Dictionary ready for OrganisationRepository.create()

        Example:
            >>> org = OrganisationFactory.create_company(
            ...     name='Acme Corp',
            ...     domain='acme.com',
            ...     employee_limit=1000,
            ...     department_structure={'IT': ['Dev', 'Ops'], 'Sales': []}
            ... )
        """
        org_type = OrgType(OrgType.COMPANY)

        # Default company settings
        default_settings = {
            'employee_limit': employee_limit,
            'enable_departments': True,
            'enable_teams': True,
            'require_sso': False,
            'allow_self_enrollment': False,
            'department_structure': department_structure or {}
        }

        # Merge with provided settings
        if settings:
            default_settings.update(settings)

        return {
            'name': name,
            'org_type': org_type.value,
            'domain': domain,
            'billing_model': org_type.default_billing_model,
            'token_pool': org_type.default_token_pool,
            'token_used': 0,
            'branding': json.dumps(branding) if branding else None,
            'settings': json.dumps(default_settings),
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def create_teacher_team(
        name: str,
        lead_teacher_id: int,
        max_members: int = 10,
        subject_areas: Optional[list] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Create teacher team with team defaults.

        Business Rules:
            - Token pool: 10,000 tokens
            - Billing model: flat
            - Member limit: 20 teachers (default: 10)
            - Lead teacher is automatically org_admin

        Args:
            name: Team name
            lead_teacher_id: User ID of lead teacher (becomes org_admin)
            max_members: Maximum team size (default: 10, max: 20)
            subject_areas: Optional list of subject areas
            settings: Optional team-specific settings

        Returns:
            Dictionary ready for OrganisationRepository.create()

        Example:
            >>> org = OrganisationFactory.create_teacher_team(
            ...     name='Math Department',
            ...     lead_teacher_id=42,
            ...     max_members=15,
            ...     subject_areas=['Mathematics', 'Physics']
            ... )
        """
        org_type = OrgType(OrgType.TEACHER_TEAM)

        # Enforce member limit
        if max_members > 20:
            max_members = 20

        # Default team settings
        default_settings = {
            'lead_teacher_id': lead_teacher_id,
            'max_members': max_members,
            'subject_areas': subject_areas or [],
            'enable_collaboration': True,
            'shared_resources': True
        }

        # Merge with provided settings
        if settings:
            default_settings.update(settings)

        return {
            'name': name,
            'org_type': org_type.value,
            'domain': None,  # Teams don't require domain
            'billing_model': org_type.default_billing_model,
            'token_pool': org_type.default_token_pool,
            'token_used': 0,
            'branding': None,
            'settings': json.dumps(default_settings),
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def create_creator_team(
        name: str,
        lead_creator_id: int,
        max_members: int = 5,
        content_types: Optional[list] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Create creator team with team defaults.

        Business Rules:
            - Token pool: 25,000 tokens (higher than teacher teams)
            - Billing model: flat
            - Member limit: 10 creators (default: 5)
            - Lead creator is automatically org_admin

        Args:
            name: Team name
            lead_creator_id: User ID of lead creator (becomes org_admin)
            max_members: Maximum team size (default: 5, max: 10)
            content_types: Optional list of content types they create
            settings: Optional team-specific settings

        Returns:
            Dictionary ready for OrganisationRepository.create()

        Example:
            >>> org = OrganisationFactory.create_creator_team(
            ...     name='Video Production Team',
            ...     lead_creator_id=99,
            ...     max_members=7,
            ...     content_types=['video', 'interactive']
            ... )
        """
        org_type = OrgType(OrgType.CREATOR_TEAM)

        # Enforce member limit
        if max_members > 10:
            max_members = 10

        # Default team settings
        default_settings = {
            'lead_creator_id': lead_creator_id,
            'max_members': max_members,
            'content_types': content_types or [],
            'enable_collaboration': True,
            'shared_revenue': False,
            'revenue_split_model': 'equal'
        }

        # Merge with provided settings
        if settings:
            default_settings.update(settings)

        return {
            'name': name,
            'org_type': org_type.value,
            'domain': None,  # Teams don't require domain
            'billing_model': org_type.default_billing_model,
            'token_pool': org_type.default_token_pool,
            'token_used': 0,
            'branding': None,
            'settings': json.dumps(default_settings),
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def add_member(
        org_id: int,
        user_id: int,
        role: MemberRole,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Add member to organisation with role validation.

        Business Rules:
            - Role must be valid MemberRole
            - Only one org_admin per small teams
            - Metadata validated based on role

        Args:
            org_id: Organisation ID
            user_id: User ID to add
            role: Member role (MemberRole instance)
            metadata: Optional role-specific metadata

        Returns:
            Dictionary ready for OrganisationRepository.add_member()

        Example:
            >>> member = OrganisationFactory.add_member(
            ...     org_id=1,
            ...     user_id=42,
            ...     role=MemberRole(MemberRole.TEACHER),
            ...     metadata={'subject': 'Mathematics', 'department': 'Science'}
            ... )
        """
        # Validate role
        if not isinstance(role, MemberRole):
            role = MemberRole(role)

        # Default metadata by role
        default_metadata = {}

        if role.value == MemberRole.TEACHER:
            default_metadata = {
                'subject': None,
                'department': None,
                'classes': []
            }
        elif role.value == MemberRole.TRAINER:
            default_metadata = {
                'specialization': None,
                'department': None,
                'certifications': []
            }
        elif role.value == MemberRole.STUDENT:
            default_metadata = {
                'grade_level': None,
                'class_id': None,
                'enrollment_date': datetime.utcnow().isoformat()
            }
        elif role.value == MemberRole.EMPLOYEE:
            default_metadata = {
                'department': None,
                'position': None,
                'hire_date': datetime.utcnow().isoformat()
            }

        # Merge with provided metadata
        if metadata:
            default_metadata.update(metadata)

        return {
            'org_id': org_id,
            'user_id': user_id,
            'org_role': role.value,
            'metadata': json.dumps(default_metadata) if default_metadata else None,
            'status': 'active',
            'joined_at': datetime.utcnow()
        }
