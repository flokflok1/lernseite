"""
LernsystemX Authentication API

Authentication endpoints:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login (with optional 2FA)
- POST /api/v1/auth/refresh - Refresh JWT token
- POST /api/v1/auth/logout - Logout (revoke token)
- POST /api/v1/auth/verify-email - Verify email address
- POST /api/v1/auth/forgot-password - Request password reset
- POST /api/v1/auth/reset-password - Reset password with token
- POST /api/v1/auth/2fa/setup - Setup 2FA
- POST /api/v1/auth/2fa/verify - Verify 2FA code
- POST /api/v1/auth/2fa/disable - Disable 2FA

ISO 27001:2013 compliant - Authentication and access control
"""

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from pydantic import ValidationError
from datetime import timedelta

from app.api import api_v1
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
from app.repositories.user_repository import UserRepository
from app.middleware.auth import token_required, get_current_user
from app.security import BruteForceProtection
from app.services.audit_service import AuditService
from setup.admin_setup import AdminSetup


@api_v1.route('/auth/register', methods=['POST'])
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
            "organisation_id": 1 (optional)
        }

    Response:
        201: User created successfully
        400: Validation error or user already exists
        500: Server error
    """
    try:
        # Get request data
        data = request.get_json()

        # Validate with Pydantic
        user_data = UserCreate(**data)

        # Create user via repository
        user = UserRepository.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role or 'user',
            organisation_id=user_data.organisation_id
        )

        # Convert to response model
        user_response = UserResponse(**user)

        # TODO: Send verification email
        # send_verification_email(user['email'], user['user_id'])

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user_response.model_dump(),
            'email_verification_required': True
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
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Registration failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/login', methods=['POST'])
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
        500: Server error
    """
    try:
        # Get request data
        data = request.get_json()

        # Validate with Pydantic
        login_data = UserLogin(**data)

        # Get client IP
        client_ip = request.remote_addr

        # Check for brute-force / account lockout
        is_blocked, error_message = BruteForceProtection.check_login_lockout(
            login_data.email,
            client_ip
        )

        if is_blocked:
            return jsonify({
                'success': False,
                'error': 'Account locked',
                'message': error_message
            }), 403

        # Authenticate user
        user = UserRepository.authenticate(
            email=login_data.email,
            password=login_data.password
        )

        if not user:
            # Record failed login attempt
            BruteForceProtection.record_failed_attempt(login_data.email, client_ip)

            # Audit log: failed login
            AuditService.log_login_failed(
                email=login_data.email,
                reason='Invalid credentials',
                metadata={'ip': client_ip}
            )

            # Get remaining attempts for user feedback
            remaining = BruteForceProtection.get_remaining_attempts(login_data.email)

            return jsonify({
                'success': False,
                'error': 'Invalid credentials',
                'message': 'Email or password is incorrect',
                'remaining_attempts': remaining
            }), 401

        # Check if 2FA is enabled
        if user.get('two_factor_enabled', False):
            if not login_data.totp_code:
                return jsonify({
                    'success': False,
                    'error': '2FA code required',
                    'message': 'Please provide your 6-digit 2FA code',
                    'two_factor_required': True
                }), 401

            # Verify TOTP code
            is_valid = AdminSetup.verify_2fa_code(
                user.get('two_factor_secret'),
                login_data.totp_code
            )

            if not is_valid:
                # Record failed 2FA attempt
                BruteForceProtection.record_failed_attempt(login_data.email, client_ip)
                remaining = BruteForceProtection.get_remaining_attempts(login_data.email)

                return jsonify({
                    'success': False,
                    'error': 'Invalid 2FA code',
                    'message': 'The 2FA code you entered is incorrect',
                    'remaining_attempts': remaining
                }), 401

        # Record successful login (reset counters)
        BruteForceProtection.record_successful_login(login_data.email, client_ip)

        # Audit log: successful login
        AuditService.log_login_success(
            user_id=user['user_id'],
            user_email=user['email'],
            user_role=user['role'],
            metadata={'2fa_used': user.get('two_factor_enabled', False)}
        )

        # Create JWT tokens
        access_token = create_access_token(
            identity=user['user_id'],
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            identity=user['user_id'],
            expires_delta=timedelta(days=30)
        )

        # Convert UUID to string for Pydantic validation
        if 'user_id' in user and user['user_id'] is not None:
            user['user_id'] = str(user['user_id'])

        # Convert to response model
        user_response = UserResponse(**user)

        # Create token response
        token_response = TokenResponse(
            access_token=access_token,
            token_type='bearer',
            expires_in=3600,  # 1 hour
            user=user_response
        )

        return jsonify({
            'success': True,
            'message': 'Login successful',
            **token_response.model_dump(),
            'refresh_token': refresh_token
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
            'error': 'Login failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/refresh', methods=['POST'])
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
        # Get user ID from refresh token
        user_id = get_jwt_identity()

        # Fetch user to ensure they still exist and are active
        user = UserRepository.find_by_id(user_id)
        if not user or not user.get('is_active', True):
            return jsonify({
                'success': False,
                'error': 'User not found or inactive'
            }), 401

        # Create new access token
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(hours=1)
        )

        return jsonify({
            'success': True,
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': 3600
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Token refresh failed',
            'details': str(e)
        }), 401


@api_v1.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    """
    Logout user (revoke token)

    Note: In production, implement token blacklist using Redis

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Logout successful
    """
    try:
        # Get JWT ID for blacklisting
        jti = get_jwt().get('jti')

        # TODO: Add token to blacklist in Redis
        # redis_client.setex(f"blacklist:{jti}", timedelta(hours=2), "true")

        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Logout failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/verify-email', methods=['POST'])
def verify_email():
    """
    Verify email address with token

    Request Body:
        {
            "token": "verification_token"
        }

    Response:
        200: Email verified successfully
        400: Invalid or expired token
    """
    try:
        # Get request data
        data = request.get_json()

        # Validate with Pydantic
        verification_data = EmailVerification(**data)

        # TODO: Implement email verification token logic
        # 1. Decode token
        # 2. Get user_id from token
        # 3. Verify email

        # For now, placeholder response
        return jsonify({
            'success': False,
            'error': 'Not implemented',
            'message': 'Email verification not yet implemented'
        }), 501

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Email verification failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset

    Request Body:
        {
            "email": "user@example.com"
        }

    Response:
        200: Password reset email sent (even if email doesn't exist - security)
    """
    try:
        # Get request data
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400

        # Check if user exists (don't reveal if email exists)
        user = UserRepository.find_by_email(email)

        if user:
            # TODO: Generate password reset token and send email
            # 1. Generate secure token
            # 2. Store token in database with expiry
            # 3. Send email with reset link
            pass

        # Always return success to prevent email enumeration
        return jsonify({
            'success': True,
            'message': 'If an account exists with this email, a password reset link has been sent'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Password reset request failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/reset-password', methods=['POST'])
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
        # Get request data
        data = request.get_json()

        # Validate with Pydantic
        reset_data = PasswordReset(**data)

        # TODO: Implement password reset logic
        # 1. Verify token
        # 2. Get user_id from token
        # 3. Update password
        # 4. Invalidate token

        return jsonify({
            'success': False,
            'error': 'Not implemented',
            'message': 'Password reset not yet implemented'
        }), 501

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Password reset failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/2fa/setup', methods=['POST'])
@token_required
def setup_2fa():
    """
    Setup two-factor authentication

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: 2FA setup initiated
        - totp_secret: TOTP secret for authenticator app
        - qr_code: Base64-encoded QR code
        - recovery_codes: List of recovery codes
    """
    try:
        user = get_current_user()

        # Check if 2FA is already enabled
        if user.get('two_factor_enabled', False):
            return jsonify({
                'success': False,
                'error': '2FA already enabled',
                'message': 'Two-factor authentication is already enabled for your account'
            }), 400

        # Generate TOTP secret
        totp_secret = AdminSetup._generate_totp_secret()

        # Generate QR code
        qr_code = AdminSetup.generate_qr_code(user['email'], totp_secret)

        # Generate recovery codes
        recovery_codes = AdminSetup._generate_recovery_codes(count=10)

        # Store TOTP secret (but don't enable 2FA yet)
        # User must verify with a code first
        from app.database.connection import execute_query
        execute_query(
            """
            UPDATE users
            SET two_factor_secret = %s
            WHERE user_id = %s
            """,
            (totp_secret, user['user_id'])
        )

        # Store recovery codes
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
        return jsonify({
            'success': False,
            'error': '2FA setup failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/2fa/verify', methods=['POST'])
@token_required
def verify_2fa():
    """
    Verify and enable 2FA with TOTP code

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "totp_code": "123456"
        }

    Response:
        200: 2FA enabled successfully
        400: Invalid code
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate with Pydantic
        verify_data = TwoFactorSetup(**data)

        # Get TOTP secret
        totp_secret = user.get('two_factor_secret')
        if not totp_secret:
            return jsonify({
                'success': False,
                'error': '2FA not set up',
                'message': 'Please set up 2FA first at /api/v1/auth/2fa/setup'
            }), 400

        # Verify TOTP code
        is_valid = AdminSetup.verify_2fa_code(totp_secret, verify_data.totp_code)

        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid 2FA code',
                'message': 'The code you entered is incorrect. Please try again.'
            }), 400

        # Enable 2FA
        from app.database.connection import execute_query
        execute_query(
            """
            UPDATE users
            SET two_factor_enabled = true
            WHERE user_id = %s
            """,
            (user['user_id'],)
        )

        # Audit log: 2FA enabled
        AuditService.log_2fa_enabled(
            user_id=user['user_id'],
            user_email=user['email']
        )

        return jsonify({
            'success': True,
            'message': 'Two-factor authentication enabled successfully',
            'two_factor_enabled': True
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
            'error': '2FA verification failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/2fa/disable', methods=['POST'])
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

        # Validate with Pydantic
        disable_data = TwoFactorDisable(**data)

        # Check if 2FA is enabled
        if not user.get('two_factor_enabled', False):
            return jsonify({
                'success': False,
                'error': '2FA not enabled',
                'message': 'Two-factor authentication is not enabled for your account'
            }), 400

        # Verify password
        authenticated = UserRepository.authenticate(
            user['email'],
            disable_data.password
        )

        if not authenticated:
            return jsonify({
                'success': False,
                'error': 'Invalid password',
                'message': 'The password you entered is incorrect'
            }), 401

        # Verify TOTP code
        totp_secret = user.get('two_factor_secret')
        is_valid = AdminSetup.verify_2fa_code(totp_secret, disable_data.totp_code)

        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid 2FA code',
                'message': 'The 2FA code you entered is incorrect'
            }), 400

        # Disable 2FA
        from app.database.connection import execute_query
        execute_query(
            """
            UPDATE users
            SET two_factor_enabled = false,
                two_factor_secret = NULL
            WHERE user_id = %s
            """,
            (user['user_id'],)
        )

        # Audit log: 2FA disabled
        AuditService.log_2fa_disabled(
            user_id=user['user_id'],
            user_email=user['email']
        )

        return jsonify({
            'success': True,
            'message': 'Two-factor authentication disabled successfully',
            'two_factor_enabled': False
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
            'error': '2FA disable failed',
            'details': str(e)
        }), 500


@api_v1.route('/auth/me', methods=['GET'])
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

        return jsonify({
            'success': True,
            'user': user_response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get user info',
            'details': str(e)
        }), 500
