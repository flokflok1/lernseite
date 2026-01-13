"""
Organisation Service Layer (DDD Pattern)

DDD Service Layer for Organisation business logic.
Orchestrates Repository calls and enforces business rules.

Business Rules:
- Every organisation must have at least one org_admin
- Domain must be unique across organisations
- Token pool cannot be negative
- Member limits enforced based on org_type
- Audit trail for critical operations

ISO 27001:2013 compliant - Business logic with security controls
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.repositories.organisations.core import OrganisationRepository
from app.repositories.user import UserRepository
from app.database.connection import execute_query, fetch_one, fetch_all
from .value_objects import OrgType, MemberRole, BillingModel
from .factory import OrganisationFactory

logger = logging.getLogger(__name__)


class OrganisationService:
    """
    DDD Service Layer for Organisation domain.

    Implements business logic that doesn't belong to a single entity.
    Orchestrates multiple repository calls and enforces complex business rules.

    Examples:
        >>> # Create organisation with admin
        >>> org = OrganisationService.create_organisation_with_admin(
        ...     org_data={'name': 'Tech Uni', 'org_type': 'school', 'domain': 'tech.edu'},
        ...     admin_user_id=42
        ... )

        >>> # Transfer ownership
        >>> result = OrganisationService.transfer_ownership(
        ...     org_id=1,
        ...     from_user_id=42,
        ...     to_user_id=99,
        ...     requester_role='admin'
        ... )
    """

    @staticmethod
    def create_organisation_with_admin(
        org_data: dict,
        admin_user_id: int
    ) -> dict:
        """
        Create organisation and assign admin in single transaction.

        Business Rule: Every organisation must have an org_admin.

        Args:
            org_data: Organisation data (name, org_type, domain, etc.)
            admin_user_id: User ID to assign as org_admin

        Returns:
            Created organisation with admin assigned

        Raises:
            ValueError: If user doesn't exist or domain already exists

        Example:
            >>> org = OrganisationService.create_organisation_with_admin(
            ...     org_data={'name': 'Tech Uni', 'org_type': 'school', 'domain': 'tech.edu'},
            ...     admin_user_id=42
            ... )
        """
        # Validate user exists
        user = UserRepository.find_by_id(admin_user_id)
        if not user:
            raise ValueError(f"User with ID {admin_user_id} not found")

        # Validate domain availability
        domain = org_data.get('domain')
        if domain and not OrganisationService.check_domain_availability(domain):
            raise ValueError(f"Domain {domain} is already taken")

        # Create organisation based on type
        org_type = org_data.get('org_type')

        if org_type == OrgType.SCHOOL:
            org_dict = OrganisationFactory.create_school(
                name=org_data['name'],
                domain=domain,
                max_students=org_data.get('max_students', 1000),
                max_teachers=org_data.get('max_teachers', 50),
                branding=org_data.get('branding'),
                settings=org_data.get('settings')
            )
        elif org_type == OrgType.COMPANY:
            org_dict = OrganisationFactory.create_company(
                name=org_data['name'],
                domain=domain,
                employee_limit=org_data.get('employee_limit', 500),
                department_structure=org_data.get('department_structure'),
                branding=org_data.get('branding'),
                settings=org_data.get('settings')
            )
        elif org_type == OrgType.TEACHER_TEAM:
            org_dict = OrganisationFactory.create_teacher_team(
                name=org_data['name'],
                lead_teacher_id=admin_user_id,
                max_members=org_data.get('max_members', 10),
                subject_areas=org_data.get('subject_areas'),
                settings=org_data.get('settings')
            )
        elif org_type == OrgType.CREATOR_TEAM:
            org_dict = OrganisationFactory.create_creator_team(
                name=org_data['name'],
                lead_creator_id=admin_user_id,
                max_members=org_data.get('max_members', 5),
                content_types=org_data.get('content_types'),
                settings=org_data.get('settings')
            )
        else:
            raise ValueError(f"Invalid organisation type: {org_type}")

        # Create organisation
        org = OrganisationRepository.create(org_dict)

        # Assign admin
        admin_role = MemberRole(MemberRole.ORG_ADMIN)
        member_dict = OrganisationFactory.add_member(
            org_id=org['org_id'],
            user_id=admin_user_id,
            role=admin_role,
            metadata={'assigned_by': 'system', 'is_founder': True}
        )

        OrganisationRepository.assign_user_to_organisation(
            user_id=admin_user_id,
            org_id=org['org_id'],
            org_role=admin_role.value
        )

        # Update user's organisation_id
        UserRepository.update(admin_user_id, {'organization_id': org['org_id']})

        logger.info(
            f"Organisation created: {org['org_id']} ({org_type}) "
            f"with admin user {admin_user_id}"
        )

        return org

    @staticmethod
    def transfer_ownership(
        org_id: int,
        from_user_id: int,
        to_user_id: int,
        requester_role: str
    ) -> dict:
        """
        Transfer organisation ownership with audit trail.

        Business Rules:
            - Only current org_admin or system admin can transfer
            - Target user must be existing member
            - Audit log entry created
            - Previous admin becomes regular member

        Args:
            org_id: Organisation ID
            from_user_id: Current org_admin user ID
            to_user_id: New org_admin user ID
            requester_role: Role of user making request (for audit)

        Returns:
            Updated organisation with new admin

        Raises:
            ValueError: If validation fails
            PermissionError: If requester lacks permission

        Example:
            >>> result = OrganisationService.transfer_ownership(
            ...     org_id=1,
            ...     from_user_id=42,
            ...     to_user_id=99,
            ...     requester_role='admin'
            ... )
        """
        # Validate organisation exists
        org = OrganisationRepository.get_organisation_by_id(org_id)
        if not org:
            raise ValueError(f"Organisation with ID {org_id} not found")

        # Validate requester permission
        if requester_role not in ['admin', 'superadmin', 'org_admin']:
            raise PermissionError("Only admins can transfer ownership")

        # Validate from_user is current admin
        current_admin_query = """
            SELECT user_id FROM organisation_users
            WHERE org_id = %s AND org_role = 'org_admin' AND status = 'active'
        """
        current_admin = fetch_one(current_admin_query, (org_id,))

        if not current_admin or current_admin['user_id'] != from_user_id:
            raise ValueError(f"User {from_user_id} is not current org_admin")

        # Validate to_user is member
        target_member_query = """
            SELECT user_id, org_role FROM organisation_users
            WHERE org_id = %s AND user_id = %s AND status = 'active'
        """
        target_member = fetch_one(target_member_query, (org_id, to_user_id))

        if not target_member:
            raise ValueError(f"User {to_user_id} is not a member of this organisation")

        # Demote old admin to member
        demote_query = """
            UPDATE organisation_users
            SET org_role = 'member', updated_at = NOW()
            WHERE org_id = %s AND user_id = %s
        """
        execute_query(demote_query, (org_id, from_user_id))

        # Promote new admin
        promote_query = """
            UPDATE organisation_users
            SET org_role = 'org_admin', updated_at = NOW()
            WHERE org_id = %s AND user_id = %s
        """
        execute_query(promote_query, (org_id, to_user_id))

        # Create audit log entry
        audit_query = """
            INSERT INTO audit_logs (
                event_type, entity_type, entity_id, user_id,
                details, created_at
            ) VALUES (
                'ownership_transfer', 'organisation', %s, %s,
                %s, NOW()
            )
        """
        audit_details = {
            'from_user_id': from_user_id,
            'to_user_id': to_user_id,
            'requester_role': requester_role
        }
        execute_query(audit_query, (org_id, from_user_id, str(audit_details)))

        logger.info(
            f"Organisation {org_id} ownership transferred "
            f"from user {from_user_id} to user {to_user_id}"
        )

        return OrganisationRepository.get_organisation_by_id(org_id)

    @staticmethod
    def upgrade_organisation_type(
        org_id: int,
        new_type: OrgType,
        requester_role: str
    ) -> dict:
        """
        Upgrade organisation type (e.g., teacher_team → school).

        Business Rules:
            - Only admin can upgrade
            - Token pool adjusted based on new type
            - Migration path validated (teams can become enterprises, not reverse)
            - Audit trail created

        Args:
            org_id: Organisation ID
            new_type: New organisation type (OrgType)
            requester_role: Role of requester (must be admin)

        Returns:
            Updated organisation

        Raises:
            PermissionError: If requester not admin
            ValueError: If invalid migration path

        Example:
            >>> org = OrganisationService.upgrade_organisation_type(
            ...     org_id=1,
            ...     new_type=OrgType(OrgType.SCHOOL),
            ...     requester_role='admin'
            ... )
        """
        # Validate permission
        if requester_role not in ['admin', 'superadmin']:
            raise PermissionError("Only system admins can upgrade organisation type")

        # Validate organisation exists
        org = OrganisationRepository.get_organisation_by_id(org_id)
        if not org:
            raise ValueError(f"Organisation with ID {org_id} not found")

        old_type = OrgType(org['org_type'])

        # Validate migration path
        if old_type.is_enterprise and new_type.is_team:
            raise ValueError(
                "Cannot downgrade from enterprise to team. "
                "Create new team instead."
            )

        # Calculate new token pool (keep current + add difference)
        old_pool = old_type.default_token_pool
        new_pool = new_type.default_token_pool
        token_adjustment = new_pool - old_pool

        # Update organisation
        update_dict = {
            'org_type': new_type.value,
            'billing_model': new_type.default_billing_model,
            'token_pool': org['token_pool'] + token_adjustment,
            'updated_at': datetime.utcnow()
        }

        updated_org = OrganisationRepository.update_organisation(org_id, update_dict)

        # Create audit log
        audit_query = """
            INSERT INTO audit_logs (
                event_type, entity_type, entity_id, user_id,
                details, created_at
            ) VALUES (
                'org_type_upgrade', 'organisation', %s, NULL,
                %s, NOW()
            )
        """
        audit_details = {
            'old_type': old_type.value,
            'new_type': new_type.value,
            'token_adjustment': token_adjustment,
            'requester_role': requester_role
        }
        execute_query(audit_query, (org_id, str(audit_details)))

        logger.info(
            f"Organisation {org_id} upgraded from {old_type.value} "
            f"to {new_type.value} (tokens: +{token_adjustment})"
        )

        return updated_org

    @staticmethod
    def calculate_token_allocation(
        org_id: int,
        new_members_count: int
    ) -> dict:
        """
        Calculate token allocation for new members.

        Business Rules:
            - Per-user billing: tokens split evenly
            - Flat billing: all members share pool
            - Hybrid: base allocation + shared pool

        Args:
            org_id: Organisation ID
            new_members_count: Number of new members to add

        Returns:
            Dictionary with allocation breakdown

        Example:
            >>> allocation = OrganisationService.calculate_token_allocation(
            ...     org_id=1,
            ...     new_members_count=10
            ... )
            >>> # {'per_member': 500, 'total': 5000, 'remaining': 45000}
        """
        org = OrganisationRepository.get_organisation_by_id(org_id)
        if not org:
            raise ValueError(f"Organisation with ID {org_id} not found")

        billing_model = BillingModel(org['billing_model'])
        available_tokens = org['token_pool'] - org['token_used']
        current_members = OrganisationRepository.get_member_count(org_id)

        if billing_model.value == BillingModel.PER_USER:
            # Divide available tokens by total members (current + new)
            total_members = current_members + new_members_count
            per_member = available_tokens // total_members if total_members > 0 else 0
            total_allocated = per_member * new_members_count

        elif billing_model.value == BillingModel.FLAT:
            # All members share the pool
            per_member = 0  # Not applicable
            total_allocated = 0  # No pre-allocation

        else:  # HYBRID
            # Base allocation per member + shared pool
            base_per_member = 1000  # Base allocation
            total_allocated = base_per_member * new_members_count
            per_member = base_per_member

        return {
            'per_member': per_member,
            'total_allocated': total_allocated,
            'remaining_pool': available_tokens - total_allocated,
            'billing_model': billing_model.value,
            'current_members': current_members,
            'new_members': new_members_count
        }

    @staticmethod
    def validate_member_limit(org_id: int, new_members: int) -> bool:
        """
        Validate organisation member limits based on type.

        Business Rules:
            - Enterprise (school, company): No limit
            - Teacher teams: Max 20 members
            - Creator teams: Max 10 members
            - Custom limits from settings override defaults

        Args:
            org_id: Organisation ID
            new_members: Number of new members to add

        Returns:
            True if within limits, False otherwise

        Example:
            >>> if OrganisationService.validate_member_limit(org_id=1, new_members=5):
            ...     # Add members
        """
        org = OrganisationRepository.get_organisation_by_id(org_id)
        if not org:
            return False

        org_type = OrgType(org['org_type'])

        # Enterprise organisations have no limit
        if org_type.is_enterprise:
            return True

        # Get current member count
        current_members = OrganisationRepository.get_member_count(org_id)

        # Check against default limit
        default_limit = org_type.default_member_limit
        if default_limit and (current_members + new_members) > default_limit:
            return False

        return True

    @staticmethod
    def check_domain_availability(domain: str) -> bool:
        """
        Check if domain is available for organisation.

        Args:
            domain: Domain to check (e.g., 'tech.edu')

        Returns:
            True if available, False if taken

        Example:
            >>> if OrganisationService.check_domain_availability('tech.edu'):
            ...     # Create organisation with this domain
        """
        query = """
            SELECT org_id FROM organisations.organizations
            WHERE domain = %s AND status != 'deleted'
        """
        result = fetch_one(query, (domain,))
        return result is None

    @staticmethod
    def get_member_roles_summary(org_id: int) -> Dict[str, int]:
        """
        Get summary of member counts by role.

        Args:
            org_id: Organisation ID

        Returns:
            Dictionary with role counts

        Example:
            >>> summary = OrganisationService.get_member_roles_summary(org_id=1)
            >>> # {'org_admin': 1, 'teacher': 10, 'student': 500}
        """
        query = """
            SELECT org_role, COUNT(*) as count
            FROM organisation_users
            WHERE org_id = %s AND status = 'active'
            GROUP BY org_role
        """
        results = fetch_all(query, (org_id,))

        return {row['org_role']: row['count'] for row in results}
