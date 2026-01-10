"""
Organisations Domain - CRUD Routes (Admin Journey)

Admin-only endpoints for organisation management:
- GET    /organisations         - List organisations (admin only)
- POST   /organisations         - Create organisation (admin only)
- GET    /organisations/<id>    - Get organisation details
- PUT    /organisations/<id>    - Update organisation

Architecture: Journey-Based DDD
Database: PostgreSQL via OrganisationRepository (direct SQL)
ISO 27001:2013 compliant - Multi-tenant organisation management
"""

from flask import Blueprint

from ._helpers import (
    request, jsonify,
    ValidationError,
    OrganisationCreate, OrganisationUpdate,
    OrganisationResponse, OrganisationListResponse,
    OrganisationRepository,
    token_required, admin_required, get_current_user,
    can_manage_organisation
)


organisations_core_bp = Blueprint(
    'organisations_core',
    __name__,
    url_prefix='/organisations'
)


@organisations_core_bp.route('', methods=['GET'])
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


@organisations_core_bp.route('', methods=['POST'])
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

        # Create organisation via OrganisationService (includes EventBus)
        org = OrganisationService.create_organisation(
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


@organisations_core_bp.route('/<int:org_id>', methods=['GET'])
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

        # Check permissions
        if current_user['role'] not in ['admin', 'superadmin']:
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


@organisations_core_bp.route('/<int:org_id>', methods=['PUT'])
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

        # Update organisation via OrganisationService (includes EventBus)
        org = OrganisationService.update_organisation(org_id, update_dict)

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
