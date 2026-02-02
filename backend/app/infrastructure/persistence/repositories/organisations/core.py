"""
LernsystemX Organisation Repository

Handles all organisation-related database operations including:
- Organisation CRUD operations
- User-organisation associations
- Organisation classes (schools)
- Organisation statistics
- Integration with subscription and token systems

ISO 27001 compliant - Multi-tenant data isolation
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import json

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning, update_returning
from app.infrastructure.cache.service import CacheService
from flask import current_app


class OrganisationRepository(BaseRepository):
    """
    Organisation repository for multi-tenant organisation management

    Implements all organisation operations following the repository pattern.
    """

    table_name = 'organisations.organisations'
    pk_column = 'org_id'

    @classmethod
    def create_organisation(
        cls,
        name: str,
        org_type: str,
        domain: Optional[str] = None,
        billing_model: str = 'per_user',
        token_pool: int = 0,
        branding: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict]:
        """
        Create new organisation

        Args:
            name: Organisation name
            org_type: Organisation type (school, company, teacher_team, creator_team)
            domain: Organisation domain (optional, must be unique)
            billing_model: Billing model (per_user, flat, hybrid)
            token_pool: Initial token pool
            branding: Branding configuration (JSONB)
            settings: Organisation settings (JSONB)

        Returns:
            Created organisation as dictionary

        Raises:
            ValueError: If domain already exists

        Example:
            >>> org = OrganisationRepository.create_organisation(
            ...     name='Tech University',
            ...     org_type='school',
            ...     domain='tech.edu',
            ...     token_pool=100000
            ... )
        """
        # Check if domain already exists (if provided)
        if domain and cls.exists(domain=domain):
            raise ValueError(f"Organisation with domain {domain} already exists")

        # Prepare data
        data = {
            'name': name,
            'org_type': org_type,
            'domain': domain,
            'billing_model': billing_model,
            'token_pool': token_pool,
            'token_used': 0,
            'branding': json.dumps(branding) if branding else None,
            'settings': json.dumps(settings) if settings else None,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        return cls.create(data)

    @classmethod
    def get_organisation_by_id(cls, org_id: int, use_cache: bool = True) -> Optional[Dict]:
        """
        Get organisation by ID

        Args:
            org_id: Organisation ID
            use_cache: Use cache (default: True)

        Returns:
            Organisation as dictionary or None

        Example:
            >>> org = OrganisationRepository.get_organisation_by_id(5)
        """
        # Try cache first
        if use_cache:
            cache_key = CacheService.make_key('ORG', str(org_id), 'settings')
            ttl = current_app.config.get('CACHE_ORGANISATION_TTL', 300)

            def load_org():
                org = cls.find_by_id(org_id)

                # Parse JSONB fields
                if org:
                    if org.get('branding'):
                        org['branding'] = json.loads(org['branding']) if isinstance(org['branding'], str) else org['branding']
                    if org.get('settings'):
                        org['settings'] = json.loads(org['settings']) if isinstance(org['settings'], str) else org['settings']

                return org

            return CacheService.cache_get_or_set(cache_key, ttl, load_org)

        # Bypass cache
        org = cls.find_by_id(org_id)

        # Parse JSONB fields
        if org:
            if org.get('branding'):
                org['branding'] = json.loads(org['branding']) if isinstance(org['branding'], str) else org['branding']
            if org.get('settings'):
                org['settings'] = json.loads(org['settings']) if isinstance(org['settings'], str) else org['settings']

        return org

    @classmethod
    def get_organisation_by_domain(cls, domain: str) -> Optional[Dict]:
        """
        Get organisation by domain

        Args:
            domain: Organisation domain

        Returns:
            Organisation as dictionary or None

        Example:
            >>> org = OrganisationRepository.get_organisation_by_domain('tech.edu')
        """
        org = cls.find_by(domain=domain)

        # Parse JSONB fields
        if org:
            if org.get('branding'):
                org['branding'] = json.loads(org['branding']) if isinstance(org['branding'], str) else org['branding']
            if org.get('settings'):
                org['settings'] = json.loads(org['settings']) if isinstance(org['settings'], str) else org['settings']

        return org

    @classmethod
    def update_organisation(cls, org_id: int, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update organisation

        Args:
            org_id: Organisation ID
            data: Dictionary of fields to update

        Returns:
            Updated organisation as dictionary

        Example:
            >>> org = OrganisationRepository.update_organisation(
            ...     org_id=5,
            ...     data={'name': 'New Name', 'status': 'suspended'}
            ... )
        """
        # Handle JSONB fields
        if 'branding' in data and data['branding'] is not None:
            data['branding'] = json.dumps(data['branding'])
        if 'settings' in data and data['settings'] is not None:
            data['settings'] = json.dumps(data['settings'])

        # Add updated_at
        data['updated_at'] = datetime.utcnow()

        org = cls.update(org_id, data)

        # Parse JSONB fields in response
        if org:
            if org.get('branding'):
                org['branding'] = json.loads(org['branding']) if isinstance(org['branding'], str) else org['branding']
            if org.get('settings'):
                org['settings'] = json.loads(org['settings']) if isinstance(org['settings'], str) else org['settings']

            # Invalidate organisation cache after update
            CacheService.invalidate_organisation_cache(org_id)

        return org

    @classmethod
    def get_organisations(
        cls,
        org_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
        order_by: str = 'created_at DESC'
    ) -> Dict[str, Any]:
        """
        Get organisations with pagination and filtering

        Args:
            org_type: Filter by organisation type (optional)
            status: Filter by status (optional)
            page: Page number (1-indexed)
            per_page: Items per page
            order_by: Order by clause

        Returns:
            Dictionary with items, total, page, per_page, total_pages

        Example:
            >>> result = OrganisationRepository.get_organisations(
            ...     org_type='school',
            ...     status='active',
            ...     page=1,
            ...     per_page=10
            ... )
        """
        # Build WHERE clause
        conditions = []
        params = []

        if org_type:
            conditions.append('org_type = %s')
            params.append(org_type)

        if status:
            conditions.append('status = %s')
            params.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''

        # Count total
        count_query = f"SELECT COUNT(*) as total FROM {cls.table_name} {where_clause}"
        count_result = fetch_one(count_query, tuple(params))
        total = count_result['total'] if count_result else 0

        # Fetch items
        offset = (page - 1) * per_page
        items_query = f"""
            SELECT * FROM {cls.table_name}
            {where_clause}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """
        items = fetch_all(items_query, tuple(params + [per_page, offset]))

        # Parse JSONB fields
        for item in items:
            if item.get('branding'):
                item['branding'] = json.loads(item['branding']) if isinstance(item['branding'], str) else item['branding']
            if item.get('settings'):
                item['settings'] = json.loads(item['settings']) if isinstance(item['settings'], str) else item['settings']

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
    def get_organisation_stats(cls, org_id: int) -> Dict[str, Any]:
        """
        Get comprehensive organisation statistics

        Includes:
        - User counts (total, active, by role)
        - Course counts (total, active)
        - Class counts (for schools)
        - Token usage
        - Subscription info (via SubscriptionRepository)

        Args:
            org_id: Organisation ID

        Returns:
            Dictionary with comprehensive statistics

        Example:
            >>> stats = OrganisationRepository.get_organisation_stats(5)
            >>> print(f"Total users: {stats['total_users']}")
        """
        stats = {'org_id': org_id}

        # User statistics
        user_count_query = """
            SELECT
                COUNT(*) as total_users,
                COUNT(*) FILTER (WHERE status = 'active') as active_users
            FROM organisation_users
            WHERE org_id = %s
        """
        user_counts = fetch_one(user_count_query, (org_id,))
        stats['total_users'] = user_counts['total_users'] if user_counts else 0
        stats['active_users'] = user_counts['active_users'] if user_counts else 0

        # Users by role
        users_by_role_query = """
            SELECT org_role, COUNT(*) as count
            FROM organisation_users
            WHERE org_id = %s AND status = 'active'
            GROUP BY org_role
        """
        users_by_role = fetch_all(users_by_role_query, (org_id,))
        stats['users_by_role'] = {row['org_role']: row['count'] for row in users_by_role}

        # Course statistics
        course_count_query = """
            SELECT
                COUNT(*) as total_courses,
                COUNT(*) FILTER (WHERE c.status = 'published') as active_courses
            FROM organisation_courses oc
            JOIN courses.courses c ON oc.course_id = c.course_id
            WHERE oc.org_id = %s
        """
        course_counts = fetch_one(course_count_query, (org_id,))
        stats['total_courses'] = course_counts['total_courses'] if course_counts else 0
        stats['active_courses'] = course_counts['active_courses'] if course_counts else 0

        # Enrollment statistics
        enrollment_query = """
            SELECT COUNT(*) as total_enrollments
            FROM courses.course_enrollments e
            JOIN organisation_users ou ON e.user_id = ou.user_id
            WHERE ou.org_id = %s
        """
        enrollment_result = fetch_one(enrollment_query, (org_id,))
        stats['total_enrollments'] = enrollment_result['total_enrollments'] if enrollment_result else 0

        # Class statistics (for schools)
        class_count_query = """
            SELECT COUNT(*) as total_classes
            FROM organisations.organisation_classes
            WHERE org_id = %s
        """
        class_result = fetch_one(class_count_query, (org_id,))
        stats['total_classes'] = class_result['total_classes'] if class_result else 0

        # Token wallet info (from organisations.organisations table)
        org = cls.get_organisation_by_id(org_id)
        if org:
            stats['token_wallet'] = {
                'balance': org.get('token_pool', 0),
                'used': org.get('token_used', 0),
                'available': org.get('token_pool', 0) - org.get('token_used', 0)
            }

        # Subscription info will be added by the service layer
        # (requires SubscriptionRepository integration)
        stats['subscription_plan'] = None
        stats['subscription_status'] = None
        stats['subscription_expires_at'] = None

        return stats

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
