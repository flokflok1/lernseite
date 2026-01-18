"""
LernsystemX Organisations API - Consolidated

Organisation CRUD:
- GET /organisations - List organisations (admin only)
- POST /organisations - Create organisation (admin only)
- GET /organisations/<id> - Get organisation details
- PUT /organisations/<id> - Update organisation

Organisation Members:
- GET /organisations/<id>/users - List organisation users
- POST /organisations/<id>/assign-user - Assign user to organisation

All routes: /api/v1/organisations/*
ISO 27001:2013 compliant - Multi-tenant organisation management
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from typing import Optional
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.domain.models.organisation import (
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationResponse,
    OrganisationListResponse,
    OrganisationAssignUserRequest,
    OrganisationUserResponse
)
from app.infrastructure.persistence.repositories.organisations.core import OrganisationRepository
from app.infrastructure.persistence.database.connection import fetch_one
from app.api.middleware.auth import (
    token_required,
    admin_required,
    get_current_user
)

organisations_bp = Blueprint('organisations', __name__, url_prefix='/organisations')

__all__ = ['organisations_bp']


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def can_manage_organisation(user: dict, org_id: int) -> bool:
    """
    Check if user can manage organisation

    Args:
        user: Current user dictionary
        org_id: Organisation ID

    Returns:
        True if user can manage this organisation
    """
    # Admins can manage all organisations (RBAC 2.0: dynamic from DB)
    from app.application.services.permission_service import PermissionService
    if PermissionService.check_threshold(user, 'organisations.manage_any'):
        return True

    # Organisation admins can only manage their own organisation
    if user.get('organization_id') == org_id:
        # Check if user has org_admin role
        org_user_query = """
            SELECT org_role FROM organisation_users
            WHERE org_id = %s AND user_id = %s AND status = 'active'
        """
        org_user = fetch_one(org_user_query, (org_id, user['user_id']))

        if org_user and org_user['org_role'] == 'org_admin':
            return True

    return False


def check_org_membership(user: dict, org_id: int, required_roles: Optional[list] = None) -> bool:
    """
    Check if user is a member of organisation with optional role check

    Args:
        user: Current user dictionary
        org_id: Organisation ID
        required_roles: Optional list of required org roles (e.g., ['org_admin', 'teacher'])

    Returns:
        True if user is member (and has required role if specified)
    """
    # Admins always have access (RBAC 2.0: dynamic from DB)
    from app.application.services.permission_service import PermissionService
    if PermissionService.check_threshold(user, 'organisations.view_any'):
        return True

    # Check basic membership
    if user.get('organization_id') != org_id:
        return False

    # If no specific role required, membership is enough
    if not required_roles:
        return True

    # Check org role
    org_user_query = """
        SELECT org_role FROM organisation_users
        WHERE org_id = %s AND user_id = %s AND status = 'active'
    """
    org_user = fetch_one(org_user_query, (org_id, user['user_id']))

    if org_user and org_user['org_role'] in required_roles:
        return True

    return False


# =============================================================================
# ORGANISATION CRUD
# =============================================================================

@organisations_bp.route('', methods=['GET'])
@admin_required
def list_organisations():
    """
    List all organisations with pagination

    Headers:
        Authorization: Bearer <access_token> (admin required)

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 10, max: 100)
        org_type: Filter by organisation type (school, company, teacher_team, creator_team)
        status: Filter by status (active, suspended, deleted)

    Response:
        200: Paginated list of organisations
        403: Insufficient permissions (admin required)
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        org_type = request.args.get('org_type')
        status = request.args.get('status', 'active')

        # Get organisations
        result = OrganisationRepository.get_organisations(
            org_type=org_type,
            status=status,
            page=page,
            per_page=per_page
        )

        # Convert to Pydantic models
        org_responses = [OrganisationResponse(**org) for org in result['items']]

        # Create paginated response
        org_list = OrganisationListResponse(
            items=org_responses,
            total=result['total'],
            page=result['page'],
            per_page=result['per_page'],
            total_pages=result['total_pages'],
            has_prev=result['has_prev'],
            has_next=result['has_next']
        )

        return jsonify({
            'success': True,
            **org_list.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list organisations',
            'details': str(e)
        }), 500


@organisations_bp.route('', methods=['POST'])
@admin_required
def create_organisation():
    """
    Create new organisation

    Headers:
        Authorization: Bearer <access_token> (admin required)

    Request Body:
        {
            "name": "Tech University",
            "org_type": "school",
            "domain": "tech.edu",
            "billing_model": "per_user",
            "token_pool": 100000,
            "branding": {...},
            "settings": {...}
        }

    Response:
        201: Organisation created successfully
        400: Validation error
        403: Insufficient permissions
    """
    try:
        data = request.get_json()

        # Validate with Pydantic
        org_data = OrganisationCreate(**data)

        # Create organisation
        org = OrganisationRepository.create_organisation(
            name=org_data.name,
            org_type=org_data.org_type,
            domain=org_data.domain,
            billing_model=org_data.billing_model,
            token_pool=org_data.token_pool,
            branding=org_data.branding.model_dump() if org_data.branding else None,
            settings=org_data.settings.model_dump() if org_data.settings else None
        )

        # Convert to response model
        org_response = OrganisationResponse(**org)

        return jsonify({
            'success': True,
            'message': 'Organisation created successfully',
            'organisation': org_response.model_dump()
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Organisation creation failed',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Organisation creation failed',
            'details': str(e)
        }), 500


@organisations_bp.route('/<int:org_id>', methods=['GET'])
@token_required
def get_organisation(org_id: int):
    """
    Get organisation details

    Headers:
        Authorization: Bearer <access_token>

    Path Parameters:
        org_id: Organisation ID

    Response:
        200: Organisation details
        403: Insufficient permissions (admin or org member required)
        404: Organisation not found

    Permissions:
        - Admins can view all organisations
        - Organisation members can view their own organisation
    """
    try:
        current_user = get_current_user()

        # Check permissions (RBAC 2.0: dynamic from DB)
        from app.application.services.permission_service import PermissionService
        if not PermissionService.check_threshold(current_user, 'organisations.view_any'):
            # Check if user is member of this organisation
            if current_user.get('organization_id') != org_id:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'You do not have permission to view this organisation'
                }), 403

        # Get organisation
        org = OrganisationRepository.get_organisation_by_id(org_id)

        if not org:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': f'Organisation with ID {org_id} not found'
            }), 404

        # Convert to response model
        org_response = OrganisationResponse(**org)

        return jsonify({
            'success': True,
            'organisation': org_response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get organisation',
            'details': str(e)
        }), 500


@organisations_bp.route('/<int:org_id>', methods=['PUT'])
@token_required
def update_organisation(org_id: int):
    """
    Update organisation

    Headers:
        Authorization: Bearer <access_token>

    Path Parameters:
        org_id: Organisation ID

    Request Body (all fields optional):
        {
            "name": "New Name",
            "domain": "newdomain.com",
            "billing_model": "flat",
            "branding": {...},
            "settings": {...},
            "status": "active"
        }

    Response:
        200: Organisation updated successfully
        400: Validation error
        403: Insufficient permissions (admin or org_admin required)
        404: Organisation not found

    Permissions:
        - Admins can update all organisations
        - org_admin can update their own organisation
    """
    try:
        current_user = get_current_user()

        # Check permissions
        if not can_manage_organisation(current_user, org_id):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You do not have permission to update this organisation'
            }), 403

        data = request.get_json()

        # Validate with Pydantic
        update_data = OrganisationUpdate(**data)

        # Build update dictionary (only non-None fields)
        update_dict = {
            k: v for k, v in update_data.model_dump().items()
            if v is not None
        }

        # Convert nested models to dicts
        if 'branding' in update_dict and update_dict['branding']:
            update_dict['branding'] = update_dict['branding']
        if 'settings' in update_dict and update_dict['settings']:
            update_dict['settings'] = update_dict['settings']

        if not update_dict:
            return jsonify({
                'success': False,
                'error': 'No fields to update',
                'message': 'Please provide at least one field to update'
            }), 400

        # Update organisation
        org = OrganisationRepository.update_organisation(org_id, update_dict)

        if not org:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': f'Organisation with ID {org_id} not found'
            }), 404

        # Convert to response model
        org_response = OrganisationResponse(**org)

        return jsonify({
            'success': True,
            'message': 'Organisation updated successfully',
            'organisation': org_response.model_dump()
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Organisation update failed',
            'details': str(e)
        }), 500


# =============================================================================
# ORGANISATION MEMBERS
# =============================================================================

@organisations_bp.route('/<int:org_id>/users', methods=['GET'])
@token_required
def list_organisation_users(org_id: int):
    """
    List users for organisation

    Headers:
        Authorization: Bearer <access_token>

    Path Parameters:
        org_id: Organisation ID

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 50, max: 100)
        org_role: Filter by organisation role
        status: Filter by status (default: active)

    Response:
        200: Paginated list of organisation users
        403: Insufficient permissions (org_admin, teacher, or admin required)

    Permissions:
        - Admins can view users of all organisations
        - org_admin can view users in their organisation
        - teacher can view students in their organisation
    """
    try:
        current_user = get_current_user()

        # Check permissions - need org_admin, teacher, or trainer role
        if not check_org_membership(
            current_user,
            org_id,
            required_roles=['org_admin', 'teacher', 'trainer']
        ):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You do not have permission to view users of this organisation'
            }), 403

        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        org_role = request.args.get('org_role')
        status = request.args.get('status', 'active')

        # Get users
        result = OrganisationRepository.get_users_for_organisation(
            org_id=org_id,
            org_role=org_role,
            status=status,
            page=page,
            per_page=per_page
        )

        # Convert to Pydantic models
        user_responses = [OrganisationUserResponse(**user) for user in result['items']]

        return jsonify({
            'success': True,
            'items': [u.model_dump() for u in user_responses],
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'total_pages': result['total_pages'],
            'has_prev': result['has_prev'],
            'has_next': result['has_next']
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list organisation users',
            'details': str(e)
        }), 500


@organisations_bp.route('/<int:org_id>/assign-user', methods=['POST'])
@token_required
def assign_user_to_organisation(org_id: int):
    """
    Assign user to organisation

    Headers:
        Authorization: Bearer <access_token>

    Path Parameters:
        org_id: Organisation ID

    Request Body:
        {
            "user_id": 123,
            "org_role": "student"
        }

    Response:
        201: User assigned successfully
        400: Validation error or user already assigned
        403: Insufficient permissions (org_admin or admin required)
        404: Organisation or user not found

    Permissions:
        - Admins can assign users to any organisation
        - org_admin can assign users to their organisation
    """
    try:
        current_user = get_current_user()

        # Check permissions
        if not can_manage_organisation(current_user, org_id):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You do not have permission to assign users to this organisation'
            }), 403

        data = request.get_json()

        # Validate with Pydantic
        assign_data = OrganisationAssignUserRequest(**data)

        # Check if organisation exists
        org = OrganisationRepository.get_organisation_by_id(org_id)
        if not org:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': f'Organisation with ID {org_id} not found'
            }), 404

        # Assign user
        org_user = OrganisationRepository.assign_user_to_organisation(
            user_id=assign_data.user_id,
            org_id=org_id,
            org_role=assign_data.org_role
        )

        # Convert to response model
        org_user_response = OrganisationUserResponse(**org_user)

        return jsonify({
            'success': True,
            'message': 'User assigned to organisation successfully',
            'organisation_user': org_user_response.model_dump()
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Assignment failed',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to assign user to organisation',
            'details': str(e)
        }), 500
