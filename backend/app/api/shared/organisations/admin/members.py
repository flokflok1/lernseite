"""
Organisation Members Management

Endpoints:
- GET    /api/v1/organisations/<id>/users       - List organisation users
- POST   /api/v1/organisations/<id>/assign-user - Assign user to organisation

ISO 27001:2013 compliant - Organisation member management
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.organisation import (
    OrganisationAssignUserRequest,
    OrganisationUserResponse
)
from app.repositories.organisations.core import OrganisationRepository
from app.middleware.auth import (
    token_required,
    get_current_user
)
from ._helpers import can_manage_organisation, check_org_membership


# Blueprint for organisation member operations
organisations_members_bp = Blueprint(
    'organisations_members',
    __name__,
    url_prefix='/organisations'
)


@organisations_members_bp.route('/<int:org_id>/users', methods=['GET'])
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


@organisations_members_bp.route('/<int:org_id>/assign-user', methods=['POST'])
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
