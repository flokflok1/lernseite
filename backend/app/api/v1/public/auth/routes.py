"""
LernsystemX Authentication API

Core authentication endpoints: registration, login, token management, user info.

Endpoints:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/verify-email - Verify email address
- POST /api/v1/auth/login - User login (with optional 2FA)
- POST /api/v1/auth/refresh - Refresh JWT token
- POST /api/v1/auth/logout - Logout (revoke token)
- GET /api/v1/auth/me - Get current user info

Password reset and 2FA endpoints are in routes_part2.py.

ISO 27001:2013 compliant - Authentication and access control
Refactored: 2026-01-12 - Consolidated from auth/ folder into flat file
Split: 2026-02-17 - Password reset + 2FA moved to routes_part2.py (Quality Gate G01)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from pydantic import ValidationError
from datetime import timedelta
import logging
import os

from app.infrastructure.i18n.error_codes import ErrorCode, error_response

logger = logging.getLogger(__name__)

from app.domain.models.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    EmailVerification
)
from app.infrastructure.persistence.repositories.user import UserRepository
from app.infrastructure.persistence.repositories.auth.authorization import AuthorizationRepository
from app.api.middleware.auth import token_required, get_current_user
from app.infrastructure.security import BruteForceProtection
from app.application.services.system.audit.service import AuditService
from app.application.services.system.auth.authorization import AuthorizationService
from app.setup.initialization.admin import AdminSetup


# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# =============================================================================
# REGISTRATION ENDPOINTS
# =============================================================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user (disabled during beta — invite code required in future)
    """
    # BETA: Registration disabled — users are created by admin via /panel/admin/users
    if not os.environ.get('REGISTRATION_ENABLED', '').lower() == 'true':
        return jsonify({
            'success': False,
            'error': 'Registration disabled',
            'message': 'Registrierung ist derzeit deaktiviert. Kontaktiere den Administrator.'
        }), 403

    """
    Register new user

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": "user" (optional),
            "organisation_id": 1 (optional)
        }

    Response:
        201: User created successfully
        400: Validation error or user already exists
        500: Server error
    """
    try:
        data = request.get_json()
        user_data = UserCreate(**data)

        user = UserRepository.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role or 'user',
            organisation_id=user_data.organisation_id
        )

        user_response = UserResponse(**user)

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user_response.model_dump(),
            'email_verification_required': True
        }), 201

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'fields': e.errors()})
    except ValueError as e:
        return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400, details={'error': str(e)})
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """
    Verify email address with token

    Request Body:
        {"token": "verification_token"}

    Response:
        200: Email verified successfully
        400: Invalid or expired token
    """
    try:
        data = request.get_json()
        verification_data = EmailVerification(**data)

        # TODO: Implement email verification token logic
        return jsonify({
            'success': False,
            'error': 'Not implemented',
            'message': 'Email verification not yet implemented'
        }), 501

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'fields': e.errors()})
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


# =============================================================================
# LOGIN ENDPOINTS
# =============================================================================

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login with optional 2FA

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "totp_code": "123456" (optional, required if 2FA enabled)
        }

    Response:
        200: Login successful with JWT tokens
        401: Invalid credentials or 2FA code
        403: Account locked or deactivated
    """
    try:
        data = request.get_json()
        login_data = UserLogin(**data)
        client_ip = request.remote_addr

        # Check brute-force protection
        is_blocked, error_message = BruteForceProtection.check_login_lockout(login_data.email, client_ip)
        if is_blocked:
            return error_response(ErrorCode.USER_ACCOUNT_LOCKED, 403, details={'message': error_message})

        # Authenticate user
        user = UserRepository.authenticate(email=login_data.email, password=login_data.password)
        if not user:
            BruteForceProtection.record_failed_attempt(login_data.email, client_ip)
            AuditService.log_login_failed(email=login_data.email, reason='Invalid credentials', metadata={'ip': client_ip})
            remaining = BruteForceProtection.get_remaining_attempts(login_data.email)
            return error_response(ErrorCode.AUTH_INVALID_CREDENTIALS, 401, details={'remaining_attempts': remaining})

        # Check 2FA
        if user.get('two_factor_enabled', False):
            if not login_data.totp_code:
                return error_response(ErrorCode.AUTH_2FA_REQUIRED, 401, details={'two_factor_required': True})

            is_valid = AdminSetup.verify_2fa_code(user.get('two_factor_secret'), login_data.totp_code)
            if not is_valid:
                BruteForceProtection.record_failed_attempt(login_data.email, client_ip)
                remaining = BruteForceProtection.get_remaining_attempts(login_data.email)
                return error_response(ErrorCode.AUTH_2FA_INVALID, 401, details={'remaining_attempts': remaining})

        # Get user's groups with hierarchy levels
        user_groups = AuthorizationService.get_user_groups_with_levels(user['user_id'])

        # Query user's effective permissions using SQL function
        user_permissions_result = AuthorizationRepository.get_user_effective_permissions(user['user_id'])
        permission_codes = [p['permission_code'] for p in user_permissions_result] if user_permissions_result else []

        # Successful login
        BruteForceProtection.record_successful_login(login_data.email, client_ip)

        # Get frontend role from primary group (first joined group)
        # Frontend role is now stored in database (core.groups.frontend_role)
        # Frontend expects: Free, Premium, Creator, Teacher, School, Company,
        #                   Support, Moderator, Admin, school_admin, company_admin, owner
        primary_group_name = user_groups[0]['name'] if user_groups else 'No Group'
        frontend_role = user_groups[0].get('frontend_role', 'Free') if user_groups else 'Free'

        AuditService.log_login_success(
            user_id=user['user_id'],
            user_email=user['email'],
            user_role=primary_group_name,  # Log full group name for audit
            metadata={
                '2fa_used': user.get('two_factor_enabled', False),
                'groups': [g['name'] for g in user_groups],
                'permission_count': len(permission_codes),
                'frontend_role': frontend_role  # Log mapped role
            }
        )

        # Create JWT tokens with group-based claims (GBA)
        additional_claims = {
            'groups': [
                {
                    'id': str(g['id']),
                    'name': g['name'],
                    'slug': g['slug'],
                    'type': g['group_type'],
                    'access_level': g['access_level']
                } for g in user_groups
            ],
            'permissions': permission_codes
        }
        access_token = create_access_token(
            identity=user['user_id'],
            expires_delta=timedelta(hours=1),
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(
            identity=user['user_id'],
            expires_delta=timedelta(days=30),
            additional_claims=additional_claims
        )

        if 'user_id' in user and user['user_id'] is not None:
            user['user_id'] = str(user['user_id'])

        # GBA: No role field - authorization is via groups and permissions only

        user_response = UserResponse(**user)
        token_response = TokenResponse(
            access_token=access_token,
            token_type='bearer',
            expires_in=3600,
            user=user_response
        )

        response_data = {
            'success': True,
            'message': 'Login successful',
            **token_response.model_dump(),
            'refresh_token': refresh_token,
            'groups': AuthorizationService.format_groups_response(user_groups),
            'permissions': permission_codes
        }

        return jsonify(response_data), 200

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'fields': e.errors()})
    except Exception as e:
        logger.error(f"Login error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token

    Headers:
        Authorization: Bearer <refresh_token>

    Response:
        200: New access token
        401: Invalid refresh token
    """
    try:
        user_id = get_jwt_identity()
        user = UserRepository.find_by_id(user_id)

        if not user or not user.get('is_active', True):
            return error_response(ErrorCode.USER_NOT_FOUND, 401)

        # Query user's active groups (Group-Based RBAC 3.0)
        # Consistent with login endpoint for token refresh
        user_groups = AuthorizationRepository.get_user_active_groups(user_id)

        # Query user's effective permissions using SQL function
        user_permissions_result = AuthorizationRepository.get_user_effective_permissions(user_id)
        permission_codes = [p['permission_code'] for p in user_permissions_result] if user_permissions_result else []

        # Create new access token with GBA claims
        # Consistent with login endpoint
        additional_claims = {
            'groups': [
                {
                    'id': str(g['id']),
                    'name': g['name'],
                    'slug': g['slug'],
                    'type': g['group_type'],
                    'access_level': g['access_level']
                } for g in user_groups
            ],
            'permissions': permission_codes
        }
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(hours=1),
            additional_claims=additional_claims
        )

        return jsonify({
            'success': True,
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': 3600
        }), 200

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 401, details={'error': str(e)})


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Logout user (revoke token)

    Headers:
        Authorization: Bearer <access_token> (must be valid)

    Response:
        200: Logout successful
        401: Token invalid/expired (use refresh endpoint first)
    """
    try:
        jti = get_jwt().get('jti')
        # TODO: Add token to blacklist in Redis

        return jsonify({'success': True, 'message': 'Logout successful'}), 200

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user_info():
    """
    Get current authenticated user information

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: User information with groups and hierarchy level
    """
    try:
        user = get_current_user()
        user_response = UserResponse(**user)

        # Get user's groups with hierarchy levels
        user_groups = AuthorizationService.get_user_groups_with_levels(user['user_id'])

        return jsonify({
            'success': True,
            'user': user_response.model_dump(),
            'groups': AuthorizationService.format_groups_response(user_groups)
        }), 200

    except Exception as e:
        logger.error(f"Get user info error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


# Export blueprint
__all__ = ['auth_bp']
