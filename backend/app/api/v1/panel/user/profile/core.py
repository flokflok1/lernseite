"""
LernsystemX Profile Core API

Core profile management endpoints:
- GET    /api/v1/profile                     - Get current user profile
- PUT    /api/v1/profile                     - Update profile
- DELETE /api/v1/profile                     - Delete account (soft delete)

ISO 27001:2013 compliant
Split from: profile.py (Part 1/4 - Core)
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.domain.models.schemas.user import (
    UserUpdate, UserProfile, PasswordChange
)
from app.infrastructure.persistence.repositories.user import UserRepository
from app.infrastructure.persistence.repositories.token import TokenRepository
from app.application.services.system.billing.service import BillingService
from app.application.services.system.auth.authorization import AuthorizationService
from app.api.middleware.auth import token_required, get_current_user

core_bp = Blueprint('profile_core', __name__, url_prefix='')


@core_bp.route('', methods=['GET'])
@token_required
def get_profile():
    """
    Get current user's profile

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: User profile with extended information
        - User data
        - Subscription info
        - Token balance
        - Course counts
    """
    try:
        user = get_current_user()

        # Get user's groups with hierarchy levels
        user_groups = AuthorizationService.get_user_groups_with_levels(user['user_id'])

        # Fetch subscription info
        plan_info = BillingService.get_effective_plan_for_user(user['user_id'])
        subscription_plan = plan_info.get('plan_name', 'free')
        subscription_status = 'active' if plan_info['source'] != 'default' else 'none'

        # Fetch token balance
        if plan_info['source'] == 'organisation' and user.get('organisation_id'):
            wallet = TokenRepository.get_or_create_organisation_wallet(user['organisation_id'])
        else:
            wallet = TokenRepository.get_or_create_user_wallet(user['user_id'])

        token_balance = wallet['balance'] if wallet else 0

        # TODO: Fetch course counts
        courses_enrolled = 0
        courses_created = 0

        # Create extended profile
        profile = UserProfile(
            **user,
            subscription_plan=subscription_plan,
            subscription_status=subscription_status,
            token_balance=token_balance,
            courses_enrolled=courses_enrolled,
            courses_created=courses_created
        )

        return jsonify({
            'success': True,
            'profile': profile.model_dump(),
            'groups': AuthorizationService.format_groups_response(user_groups)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get profile',
            'details': str(e)
        }), 500


@core_bp.route('', methods=['PUT'])
@token_required
def update_profile():
    """
    Update current user's profile

    Headers:
        Authorization: Bearer <access_token>

    Request Body (all fields optional):
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com"
        }

    Note: Users cannot change their own role

    Response:
        200: Profile updated successfully
        400: Validation error
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate with Pydantic
        update_data = UserUpdate(**data)

        # Prevent changing own role
        if update_data.role:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You cannot change your own role'
            }), 403

        # Prevent self-deactivation
        if update_data.is_active is False:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You cannot deactivate your own account'
            }), 403

        # Update user (only include non-None fields)
        update_dict = {
            k: v for k, v in update_data.model_dump().items()
            if v is not None and k not in ['role', 'is_active', 'organisation_id']
        }

        if not update_dict:
            return jsonify({
                'success': False,
                'error': 'No fields to update',
                'message': 'Please provide at least one field to update'
            }), 400

        updated_user = UserRepository.update(user['user_id'], update_dict)

        # Convert to profile
        profile = UserProfile(**updated_user)

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': profile.model_dump()
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
            'error': 'Profile update failed',
            'details': str(e)
        }), 500


@core_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """
    Change current user's password

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "current_password": "OldPass123!",
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!"
        }

    Response:
        200: Password changed successfully
        400: Validation error or incorrect current password
        401: Current password is incorrect
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate with Pydantic
        password_data = PasswordChange(**data)

        # Verify current password
        authenticated = UserRepository.authenticate(
            user['email'],
            password_data.current_password
        )

        if not authenticated:
            return jsonify({
                'success': False,
                'error': 'Incorrect password',
                'message': 'The current password you entered is incorrect'
            }), 401

        # Update password
        success = UserRepository.update_password(
            user['user_id'],
            password_data.new_password
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Password update failed',
                'message': 'Failed to update password'
            }), 500

        # TODO: Send email notification about password change
        # send_password_changed_email(user['email'])

        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
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
            'error': 'Password change failed',
            'details': str(e)
        }), 500


@core_bp.route('', methods=['DELETE'])
@token_required
def delete_profile():
    """
    Delete own account (soft delete - deactivate)

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "password": "CurrentPass123!",
            "confirmation": "DELETE MY ACCOUNT"
        }

    Response:
        200: Account deleted successfully
        400: Invalid confirmation
        401: Incorrect password
    """
    try:
        user = get_current_user()
        data = request.get_json()

        password = data.get('password')
        confirmation = data.get('confirmation')

        # Verify password
        if not password:
            return jsonify({
                'success': False,
                'error': 'Password required',
                'message': 'Please provide your password to confirm account deletion'
            }), 400

        authenticated = UserRepository.authenticate(user['email'], password)

        if not authenticated:
            return jsonify({
                'success': False,
                'error': 'Incorrect password',
                'message': 'The password you entered is incorrect'
            }), 401

        # Verify confirmation text
        if confirmation != 'DELETE MY ACCOUNT':
            return jsonify({
                'success': False,
                'error': 'Invalid confirmation',
                'message': 'Please type "DELETE MY ACCOUNT" to confirm'
            }), 400

        # Deactivate account
        UserRepository.deactivate_user(user['user_id'])

        # TODO: Schedule data deletion after 30 days
        # TODO: Send account deletion confirmation email

        return jsonify({
            'success': True,
            'message': 'Your account has been deactivated. You have 30 days to reactivate before permanent deletion.'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Account deletion failed',
            'details': str(e)
        }), 500


__all__ = ['profile_core_bp']
