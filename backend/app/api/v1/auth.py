"""
LernsystemX Authentication API

All authentication endpoints in a single flat file.

Endpoints:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/verify-email - Verify email address
- POST /api/v1/auth/login - User login (with optional 2FA)
- POST /api/v1/auth/refresh - Refresh JWT token
- POST /api/v1/auth/logout - Logout (revoke token)
- GET /api/v1/auth/me - Get current user info
- POST /api/v1/auth/forgot-password - Request password reset
- POST /api/v1/auth/reset-password - Reset password with token
- POST /api/v1/auth/2fa/setup - Setup 2FA
- POST /api/v1/auth/2fa/verify - Verify 2FA code
- POST /api/v1/auth/2fa/disable - Disable 2FA

ISO 27001:2013 compliant - Authentication and access control
Refactored: 2026-01-12 - Consolidated from auth/ folder into flat file
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

from app.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    EmailVerification,
    TwoFactorSetup,
    TwoFactorDisable,
    PasswordReset
)
from app.repositories.user import UserRepository
from app.repositories.role_studio_mode import RoleStudioModeRepository
from app.middleware.auth import token_required, get_current_user
from app.security import BruteForceProtection
from app.services.audit_service import AuditService
from app.services.role_studio_service import RoleStudioService
from app.setup.admin_setup import AdminSetup
from app.database.connection import execute_query


# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# =============================================================================
# REGISTRATION ENDPOINTS
# =============================================================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": "user" (optional),
            "organization_id": 1 (optional)
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
            organization_id=user_data.organization_id
        )

        user_response = UserResponse(**user)

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user_response.model_dump(),
            'email_verification_required': True
        }), 201

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Registration failed', 'details': str(e)}), 500


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
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Email verification failed', 'details': str(e)}), 500


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
            return jsonify({'success': False, 'error': 'Account locked', 'message': error_message}), 403

        # Authenticate user
        user = UserRepository.authenticate(email=login_data.email, password=login_data.password)
        if not user:
            BruteForceProtection.record_failed_attempt(login_data.email, client_ip)
            AuditService.log_login_failed(email=login_data.email, reason='Invalid credentials', metadata={'ip': client_ip})
            remaining = BruteForceProtection.get_remaining_attempts(login_data.email)
            return jsonify({
                'success': False,
                'error': 'Invalid credentials',
                'message': 'Email or password is incorrect',
                'remaining_attempts': remaining
            }), 401

        # Check 2FA
        if user.get('two_factor_enabled', False):
            if not login_data.totp_code:
                return jsonify({
                    'success': False,
                    'error': '2FA code required',
                    'message': 'Please provide your 6-digit 2FA code',
                    'two_factor_required': True
                }), 401

            is_valid = AdminSetup.verify_2fa_code(user.get('two_factor_secret'), login_data.totp_code)
            if not is_valid:
                BruteForceProtection.record_failed_attempt(login_data.email, client_ip)
                remaining = BruteForceProtection.get_remaining_attempts(login_data.email)
                return jsonify({
                    'success': False,
                    'error': 'Invalid 2FA code',
                    'message': 'The 2FA code you entered is incorrect',
                    'remaining_attempts': remaining
                }), 401

        # Successful login
        BruteForceProtection.record_successful_login(login_data.email, client_ip)
        AuditService.log_login_success(
            user_id=user['user_id'],
            user_email=user['email'],
            user_role=user['role'],
            metadata={'2fa_used': user.get('two_factor_enabled', False)}
        )

        # Fetch role studio configuration for immediate frontend use (Phase 1)
        studio_config = None
        try:
            role_config = RoleStudioService.get_role_studio_mode(user.get('role', 'user'))
            if role_config:
                studio_config = {
                    'role_code': role_config.get('role_code'),
                    'studio_mode': role_config.get('studio_mode'),
                    'display_name': role_config.get('display_name'),
                    'permissions': role_config.get('permissions', {}),
                    'requires_organization': role_config.get('requires_organization', False)
                }
        except Exception as e:
            # Log but don't fail login if studio config is missing
            logger.warning(f"Could not fetch studio config for role {user.get('role')}: {str(e)}")
            studio_config = None

        # Create JWT tokens with additional claims (RBAC 2.0)
        additional_claims = {
            'role': user.get('role', 'user'),
            'hierarchy_level': user.get('hierarchy_level', 1)
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
            'refresh_token': refresh_token
        }

        # Add studio configuration to response if available
        if studio_config:
            response_data['studio_config'] = studio_config

        return jsonify(response_data), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Login failed', 'details': str(e)}), 500


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
            return jsonify({'success': False, 'error': 'User not found or inactive'}), 401

        # Create new access token with additional claims (RBAC 2.0)
        additional_claims = {
            'role': user.get('role', 'user'),
            'hierarchy_level': user.get('hierarchy_level', 1)
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
        return jsonify({'success': False, 'error': 'Token refresh failed', 'details': str(e)}), 401


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
        return jsonify({'success': False, 'error': 'Logout failed', 'details': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user_info():
    """
    Get current authenticated user information

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: User information
    """
    try:
        user = get_current_user()
        user_response = UserResponse(**user)

        return jsonify({'success': True, 'user': user_response.model_dump()}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to get user info', 'details': str(e)}), 500


# =============================================================================
# PASSWORD RESET ENDPOINTS
# =============================================================================

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset

    Request Body:
        {"email": "user@example.com"}

    Response:
        200: Password reset email sent (even if email doesn't exist - security)
    """
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400

        user = UserRepository.find_by_email(email)
        if user:
            # TODO: Generate password reset token and send email
            pass

        # Always return success to prevent email enumeration
        return jsonify({
            'success': True,
            'message': 'If an account exists with this email, a password reset link has been sent'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'Password reset request failed', 'details': str(e)}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password with token

    Request Body:
        {
            "token": "reset_token",
            "new_password": "NewSecurePass456!",
            "confirm_password": "NewSecurePass456!"
        }

    Response:
        200: Password reset successful
        400: Validation error or invalid token
    """
    try:
        data = request.get_json()
        reset_data = PasswordReset(**data)

        # TODO: Implement password reset logic
        return jsonify({
            'success': False,
            'error': 'Not implemented',
            'message': 'Password reset not yet implemented'
        }), 501

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Password reset failed', 'details': str(e)}), 500


# =============================================================================
# TWO-FACTOR AUTHENTICATION ENDPOINTS
# =============================================================================

@auth_bp.route('/2fa/setup', methods=['POST'])
@token_required
def setup_2fa():
    """
    Setup two-factor authentication

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: 2FA setup initiated with QR code and recovery codes
    """
    try:
        user = get_current_user()

        if user.get('two_factor_enabled', False):
            return jsonify({
                'success': False,
                'error': '2FA already enabled',
                'message': 'Two-factor authentication is already enabled for your account'
            }), 400

        totp_secret = AdminSetup._generate_totp_secret()
        qr_code = AdminSetup.generate_qr_code(user['email'], totp_secret)
        recovery_codes = AdminSetup._generate_recovery_codes(count=10)

        execute_query("UPDATE users SET two_factor_secret = %s WHERE user_id = %s", (totp_secret, user['user_id']))
        AdminSetup._store_recovery_codes(user['user_id'], recovery_codes)

        return jsonify({
            'success': True,
            'message': '2FA setup initiated. Please scan the QR code with your authenticator app',
            'totp_secret': totp_secret,
            'qr_code': qr_code,
            'recovery_codes': recovery_codes,
            'next_step': 'Verify your 2FA code at /api/v1/auth/2fa/verify'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': '2FA setup failed', 'details': str(e)}), 500


@auth_bp.route('/2fa/verify', methods=['POST'])
@token_required
def verify_2fa():
    """
    Verify and enable 2FA with TOTP code

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {"totp_code": "123456"}

    Response:
        200: 2FA enabled successfully
        400: Invalid code
    """
    try:
        user = get_current_user()
        data = request.get_json()
        verify_data = TwoFactorSetup(**data)

        totp_secret = user.get('two_factor_secret')
        if not totp_secret:
            return jsonify({
                'success': False,
                'error': '2FA not set up',
                'message': 'Please set up 2FA first at /api/v1/auth/2fa/setup'
            }), 400

        is_valid = AdminSetup.verify_2fa_code(totp_secret, verify_data.totp_code)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid 2FA code',
                'message': 'The code you entered is incorrect. Please try again.'
            }), 400

        execute_query("UPDATE users SET two_factor_enabled = true WHERE user_id = %s", (user['user_id'],))
        AuditService.log_2fa_enabled(user_id=user['user_id'], user_email=user['email'])

        return jsonify({
            'success': True,
            'message': 'Two-factor authentication enabled successfully',
            'two_factor_enabled': True
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': '2FA verification failed', 'details': str(e)}), 500


@auth_bp.route('/2fa/disable', methods=['POST'])
@token_required
def disable_2fa():
    """
    Disable two-factor authentication

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "password": "CurrentPass123!",
            "totp_code": "123456"
        }

    Response:
        200: 2FA disabled successfully
        400: Invalid password or code
    """
    try:
        user = get_current_user()
        data = request.get_json()
        disable_data = TwoFactorDisable(**data)

        if not user.get('two_factor_enabled', False):
            return jsonify({
                'success': False,
                'error': '2FA not enabled',
                'message': 'Two-factor authentication is not enabled for your account'
            }), 400

        authenticated = UserRepository.authenticate(user['email'], disable_data.password)
        if not authenticated:
            return jsonify({
                'success': False,
                'error': 'Invalid password',
                'message': 'The password you entered is incorrect'
            }), 401

        totp_secret = user.get('two_factor_secret')
        is_valid = AdminSetup.verify_2fa_code(totp_secret, disable_data.totp_code)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid 2FA code',
                'message': 'The 2FA code you entered is incorrect'
            }), 400

        execute_query("UPDATE users SET two_factor_enabled = false, two_factor_secret = NULL WHERE user_id = %s", (user['user_id'],))
        AuditService.log_2fa_disabled(user_id=user['user_id'], user_email=user['email'])

        return jsonify({
            'success': True,
            'message': 'Two-factor authentication disabled successfully',
            'two_factor_enabled': False
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': '2FA disable failed', 'details': str(e)}), 500


# Export blueprint
__all__ = ['auth_bp']
