"""
LernsystemX Auth API - Login Module

Endpoints:
- POST /api/v1/auth/login - User login (with optional 2FA)
- POST /api/v1/auth/refresh - Refresh JWT token
- POST /api/v1/auth/logout - Logout (revoke token)
- GET /api/v1/auth/me - Get current user info

ISO 27001:2013 compliant - Authentication and access control
"""

from flask import Blueprint

from ._helpers import (
    request, jsonify,
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    ValidationError, timedelta,
    UserLogin, UserResponse, TokenResponse,
    UserRepository,
    token_required, get_current_user,
    BruteForceProtection, AuditService, AdminSetup
)


auth_login_bp = Blueprint('auth_login', __name__, url_prefix='/auth')


@auth_login_bp.route('/login', methods=['POST'])
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


@auth_login_bp.route('/refresh', methods=['POST'])
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


@auth_login_bp.route('/logout', methods=['POST'])
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


@auth_login_bp.route('/me', methods=['GET'])
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
