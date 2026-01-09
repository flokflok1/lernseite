"""
LernsystemX Setup - Organisation Management

Handles organisation creation and configuration during setup:
- LSX Academy (default system organisation)
- Custom organisations (schools, companies, creators)
- Domain binding and branding
- Organisation settings and token pools

ISO 9001:2015 compliant - Organisation management
"""

from typing import Dict, Optional
from datetime import datetime

from app.database.connection import (
    fetch_one,
    fetch_all,
    execute_query,
    insert_returning
)


class OrganisationSetup:
    """
    Setup and manage organisations during installation

    Implements multi-tenancy foundation for LernsystemX.
    """

    VALID_TYPES = ['system', 'school', 'company', 'academy', 'creator_org', 'community']

    @classmethod
    def create_organisation(
        cls,
        name: str,
        org_type: str,
        domain: Optional[str] = None,
        branding: Optional[Dict] = None,
        settings: Optional[Dict] = None
    ) -> Dict:
        """
        Create new organisation

        Args:
            name: Organisation name
            org_type: Type (system, school, company, creator_org, community)
            domain: Custom domain (optional, must be unique)
            branding: Branding configuration (logo, colors, etc.)
            settings: Organisation settings

        Returns:
            Created organisation data

        Raises:
            ValueError: If validation fails

        Example:
            >>> org = OrganisationSetup.create_organisation(
            ...     name='Example School',
            ...     org_type='school',
            ...     domain='school.example.com'
            ... )
        """
        # Validate organisation type
        if org_type not in cls.VALID_TYPES:
            raise ValueError(
                f"Invalid organisation type. Must be one of: {', '.join(cls.VALID_TYPES)}"
            )

        # Check domain uniqueness
        if domain:
            existing = fetch_one(
                "SELECT organization_id FROM organisations.organisations WHERE domain = %s",
                (domain,)
            )
            if existing:
                raise ValueError(f"Domain '{domain}' is already in use")

        # Create organisation
        import json

        # Extract logo_url from branding if provided
        logo_url = None
        if branding:
            logo_url = branding.get('logo_url')

        org = insert_returning(
            'organisations.organisations',
            {
                'name': name,
                'type': org_type,
                'domain': domain,
                'logo_url': logo_url,
                'status': 'active',
                'created_at': datetime.utcnow()
            }
        )

        if not org:
            raise RuntimeError("Failed to create organisation")

        # Create default settings
        cls._create_default_settings(org['organization_id'], org_type, settings)

        # Create token pool for schools and companies
        if org_type in ['school', 'company']:
            cls._create_token_pool(org['organization_id'])

        return org

    @classmethod
    def create_lsx_academy(cls) -> Dict:
        """
        Create default LSX Academy organisation

        This is the system organisation that manages:
        - System courses
        - Global content
        - Default admin account

        Returns:
            Created LSX Academy organisation

        Example:
            >>> lsx_academy = OrganisationSetup.create_lsx_academy()
            >>> print(f"LSX Academy ID: {lsx_academy['organisation_id']}")
        """
        # Check if LSX Academy already exists
        existing = fetch_one(
            "SELECT * FROM organisations.organisations WHERE name = %s OR domain = %s",
            ('LSX Academy', 'lsx.de')
        )

        if existing:
            return existing

        # Create LSX Academy (using 'academy' type for the main platform)
        return cls.create_organisation(
            name='LSX Academy',
            org_type='academy',
            domain='lsx.de',
            branding={
                'primary_color': '#2563eb',
                'secondary_color': '#1e40af',
                'logo_url': '/static/logo.png'
            },
            settings={
                'allow_public_courses': True,
                'allow_user_creation': True,
                'require_email_verification': True
            }
        )

    @staticmethod
    def _create_default_settings(
        organisation_id: int,
        org_type: str,
        custom_settings: Optional[Dict] = None
    ) -> None:
        """
        Create default organisation settings

        Args:
            organisation_id: Organisation ID
            org_type: Organisation type
            custom_settings: Custom settings to override defaults
        """
        # Default settings based on organisation type
        default_settings = {
            'system': {
                'allow_public_courses': True,
                'allow_user_creation': True,
                'require_email_verification': True,
                'max_users': None,
                'max_courses': None
            },
            'school': {
                'allow_public_courses': False,
                'allow_user_creation': False,  # Teachers create students
                'require_email_verification': True,
                'max_users': 1000,
                'max_courses': None
            },
            'company': {
                'allow_public_courses': False,
                'allow_user_creation': False,
                'require_email_verification': True,
                'max_users': 500,
                'max_courses': None
            },
            'creator_org': {
                'allow_public_courses': True,
                'allow_user_creation': False,
                'require_email_verification': True,
                'max_users': 50,
                'max_courses': None
            },
            'community': {
                'allow_public_courses': True,
                'allow_user_creation': True,
                'require_email_verification': False,
                'max_users': None,
                'max_courses': None
            }
        }

        settings = default_settings.get(org_type, default_settings['community'])

        # Override with custom settings
        if custom_settings:
            settings.update(custom_settings)

        # Store settings (we could create an organisation_settings table,
        # or store in JSONB column, or just skip for now)
        # For simplicity, we'll skip detailed settings table for Phase 5
        pass

    @staticmethod
    def _create_token_pool(organisation_id: int, initial_tokens: int = 10000) -> None:
        """
        Create token pool for organisation

        Args:
            organisation_id: Organisation ID
            initial_tokens: Initial token balance (default: 10000)

        Note:
            Token pools are used for schools and companies
            to allocate AI tokens to their users.
        """
        # Create organization-level token wallet
        execute_query(
            """
            INSERT INTO token_wallets (
                user_id, organization_id, balance, total_granted,
                total_purchased, total_consumed, created_at
            )
            VALUES (NULL, %s, %s, %s, 0, 0, NOW())
            ON CONFLICT DO NOTHING
            """,
            (organisation_id, initial_tokens, initial_tokens)
        )

    @classmethod
    def get_organisation(cls, organisation_id: int) -> Optional[Dict]:
        """
        Get organisation by ID

        Args:
            organisation_id: Organisation ID

        Returns:
            Organisation data or None

        Example:
            >>> org = OrganisationSetup.get_organisation(1)
        """
        return fetch_one(
            "SELECT * FROM organisations.organisations WHERE organization_id = %s",
            (organisation_id,)
        )

    @classmethod
    def get_organisation_by_domain(cls, domain: str) -> Optional[Dict]:
        """
        Get organisation by domain

        Args:
            domain: Organisation domain

        Returns:
            Organisation data or None

        Example:
            >>> org = OrganisationSetup.get_organisation_by_domain('school.example.com')
        """
        return fetch_one(
            "SELECT * FROM organisations.organisations WHERE domain = %s",
            (domain,)
        )

    @classmethod
    def list_organisations(cls, org_type: Optional[str] = None) -> list:
        """
        List all organisations

        Args:
            org_type: Filter by organisation type (optional)

        Returns:
            List of organisations

        Example:
            >>> schools = OrganisationSetup.list_organisations(org_type='school')
        """
        if org_type:
            return fetch_all(
                "SELECT * FROM organisations.organisations WHERE type = %s ORDER BY created_at DESC",
                (org_type,)
            )
        else:
            return fetch_all(
                "SELECT * FROM organisations.organisations ORDER BY created_at DESC"
            )

    @classmethod
    def update_branding(
        cls,
        organisation_id: int,
        branding: Dict
    ) -> Optional[Dict]:
        """
        Update organisation branding

        Args:
            organisation_id: Organisation ID
            branding: Branding configuration (must include logo_url)

        Returns:
            Updated organisation

        Example:
            >>> org = OrganisationSetup.update_branding(
            ...     1,
            ...     {
            ...         'logo_url': '/uploads/logo.png'
            ...     }
            ... )
        """
        logo_url = branding.get('logo_url')

        execute_query(
            """
            UPDATE organisations.organisations
            SET logo_url = %s, updated_at = NOW()
            WHERE organization_id = %s
            """,
            (logo_url, organisation_id)
        )

        return cls.get_organisation(organisation_id)

    @classmethod
    def activate_organisation(cls, organisation_id: int) -> bool:
        """
        Activate organisation

        Args:
            organisation_id: Organisation ID

        Returns:
            bool: True if activated successfully

        Example:
            >>> OrganisationSetup.activate_organisation(5)
        """
        execute_query(
            "UPDATE organisations.organisations SET status = 'active' WHERE organization_id = %s",
            (organisation_id,)
        )
        return True

    @classmethod
    def deactivate_organisation(cls, organisation_id: int) -> bool:
        """
        Deactivate organisation

        Args:
            organisation_id: Organisation ID

        Returns:
            bool: True if deactivated successfully

        Example:
            >>> OrganisationSetup.deactivate_organisation(5)
        """
        execute_query(
            "UPDATE organisations.organisations SET status = 'inactive' WHERE organization_id = %s",
            (organisation_id,)
        )
        return True

    @classmethod
    def get_organisation_stats(cls) -> Dict:
        """
        Get organisation statistics

        Returns:
            Dictionary with organisation counts by type

        Example:
            >>> stats = OrganisationSetup.get_organisation_stats()
            >>> print(f"Total organisations: {stats['total']}")
            >>> print(f"Schools: {stats['by_type']['school']}")
        """
        # Total organisations
        total_result = fetch_one("SELECT COUNT(*) FROM organisations.organisations")
        total = total_result['count'] if total_result else 0

        # Active organisations
        active_result = fetch_one(
            "SELECT COUNT(*) FROM organisations.organisations WHERE status = 'active'"
        )
        active = active_result['count'] if active_result else 0

        # By type
        by_type_results = fetch_all("""
            SELECT type, COUNT(*) as count
            FROM organisations.organisations
            WHERE status = 'active'
            GROUP BY type
        """)

        by_type = {row['type']: row['count'] for row in by_type_results}

        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_type': by_type
        }


# Convenience functions
def create_lsx_academy() -> Dict:
    """Quick function to create LSX Academy"""
    return OrganisationSetup.create_lsx_academy()


def create_organisation(**kwargs) -> Dict:
    """Quick function to create organisation"""
    return OrganisationSetup.create_organisation(**kwargs)
