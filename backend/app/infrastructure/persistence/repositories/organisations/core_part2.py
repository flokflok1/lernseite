"""
LernsystemX Organisation Repository - Part 2

User-organisation membership management and token operations:
- User-organisation assignments (assign, remove, update role)
- User queries for organisations
- Token pool management (consume, add)

Split from core.py for Quality Gate G01 compliance (max 500 lines per file).
"""

from typing import Optional, Dict, Any
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning, update_returning
from app.infrastructure.cache.service import CacheService
import json


class OrganisationUsersMixin:
    """
    Mixin for user-organisation membership and token operations.

    Provides class methods for managing organisation memberships
    and token pool operations. Mixed into OrganisationRepository.
    """

    @classmethod
    def assign_user_to_organisation(
        cls,
        user_id: int,
        org_id: int,
        org_role: str = 'student'
    ) -> Optional[Dict]:
        """
        Assign user to organisation

        Args:
            user_id: User ID
            org_id: Organisation ID
            org_role: Role within organisation (org_admin, teacher, student, etc.)

        Returns:
            Created organisation_user record as dictionary

        Raises:
            ValueError: If user already assigned to organisation

        Example:
            >>> org_user = OrganisationRepository.assign_user_to_organisation(
            ...     user_id=123,
            ...     org_id=5,
            ...     org_role='teacher'
            ... )
        """
        # Check if user already assigned
        existing_query = """
            SELECT * FROM organisation_users
            WHERE org_id = %s AND user_id = %s
        """
        existing = fetch_one(existing_query, (org_id, user_id))

        if existing:
            raise ValueError(f"User {user_id} is already assigned to organisation {org_id}")

        # Insert into organisation_users
        insert_query = """
            INSERT INTO organisation_users (
                org_id, user_id, org_role, status, joined_at, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """
        params = (
            org_id,
            user_id,
            org_role,
            'active',
            datetime.utcnow(),
            datetime.utcnow()
        )

        return insert_returning(insert_query, params)

    @classmethod
    def get_users_for_organisation(
        cls,
        org_id: int,
        org_role: Optional[str] = None,
        status: str = 'active',
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """
        Get users for organisation with optional filtering

        Args:
            org_id: Organisation ID
            org_role: Filter by organisation role (optional)
            status: Filter by status (default: 'active')
            page: Page number
            per_page: Items per page

        Returns:
            Dictionary with items, total, page, per_page, total_pages

        Example:
            >>> result = OrganisationRepository.get_users_for_organisation(
            ...     org_id=5,
            ...     org_role='teacher',
            ...     page=1
            ... )
        """
        # Build WHERE clause
        conditions = ['ou.org_id = %s']
        params = [org_id]

        if org_role:
            conditions.append('ou.org_role = %s')
            params.append(org_role)

        if status:
            conditions.append('ou.status = %s')
            params.append(status)

        where_clause = ' AND '.join(conditions)

        # Count total
        count_query = f"""
            SELECT COUNT(*) as total
            FROM organisation_users ou
            WHERE {where_clause}
        """
        count_result = fetch_one(count_query, tuple(params))
        total = count_result['total'] if count_result else 0

        # Fetch items with user details
        offset = (page - 1) * per_page
        items_query = f"""
            SELECT
                ou.*,
                u.firstname,
                u.lastname,
                u.email,
                u.role as user_role
            FROM organisation_users ou
            JOIN core.users u ON ou.user_id = u.user_id
            WHERE {where_clause}
            ORDER BY ou.joined_at DESC
            LIMIT %s OFFSET %s
        """
        items = fetch_all(items_query, tuple(params + [per_page, offset]))

        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page if total > 0 else 0

        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }

    @classmethod
    def remove_user_from_organisation(cls, org_id: int, user_id: int) -> bool:
        """
        Remove user from organisation

        Args:
            org_id: Organisation ID
            user_id: User ID

        Returns:
            True if successful, False otherwise

        Example:
            >>> success = OrganisationRepository.remove_user_from_organisation(5, 123)
        """
        query = """
            DELETE FROM organisation_users
            WHERE org_id = %s AND user_id = %s
        """
        result = execute_query(query, (org_id, user_id))
        return result > 0

    @classmethod
    def update_user_role(cls, org_id: int, user_id: int, org_role: str) -> Optional[Dict]:
        """
        Update user's role within organisation

        Args:
            org_id: Organisation ID
            user_id: User ID
            org_role: New organisation role

        Returns:
            Updated organisation_user record

        Example:
            >>> org_user = OrganisationRepository.update_user_role(5, 123, 'org_admin')
        """
        query = """
            UPDATE organisation_users
            SET org_role = %s
            WHERE org_id = %s AND user_id = %s
            RETURNING *
        """
        return update_returning(query, (org_role, org_id, user_id))

    @classmethod
    def consume_tokens(cls, org_id: int, amount: int) -> bool:
        """
        Consume tokens from organisation token pool

        Args:
            org_id: Organisation ID
            amount: Number of tokens to consume

        Returns:
            True if successful, False if insufficient tokens

        Example:
            >>> success = OrganisationRepository.consume_tokens(5, 1000)
        """
        # Check available tokens
        org = cls.get_organisation_by_id(org_id)
        if not org:
            return False

        available = org['token_pool'] - org['token_used']
        if available < amount:
            return False

        # Update token_used
        query = """
            UPDATE organisations.organisations
            SET token_used = token_used + %s, updated_at = %s
            WHERE org_id = %s
        """
        result = execute_query(query, (amount, datetime.utcnow(), org_id))
        return result > 0

    @staticmethod
    def get_org_user_role(org_id: int, user_id) -> Optional[Dict]:
        """
        Get user's role within an organisation.

        Args:
            org_id: Organisation ID
            user_id: User ID

        Returns:
            Dict with 'org_role' key if found, None otherwise
        """
        return fetch_one(
            """
            SELECT org_role FROM organisation_users
            WHERE org_id = %s AND user_id = %s AND status = 'active'
            """,
            (org_id, user_id)
        )

    @classmethod
    def add_tokens(cls, org_id: int, amount: int) -> Optional[Dict]:
        """
        Add tokens to organisation token pool

        Args:
            org_id: Organisation ID
            amount: Number of tokens to add

        Returns:
            Updated organisation

        Example:
            >>> org = OrganisationRepository.add_tokens(5, 50000)
        """
        query = """
            UPDATE organisations.organisations
            SET token_pool = token_pool + %s, updated_at = %s
            WHERE org_id = %s
            RETURNING *
        """
        org = update_returning(query, (amount, datetime.utcnow(), org_id))

        # Parse JSONB fields
        if org:
            if org.get('branding'):
                org['branding'] = json.loads(org['branding']) if isinstance(org['branding'], str) else org['branding']
            if org.get('settings'):
                org['settings'] = json.loads(org['settings']) if isinstance(org['settings'], str) else org['settings']

        return org
