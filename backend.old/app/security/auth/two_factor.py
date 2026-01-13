"""
LernsystemX Auth API - Two-Factor Authentication Module

Endpoints:
- POST /api/v1/auth/2fa/setup - Setup 2FA
- POST /api/v1/auth/2fa/verify - Verify 2FA code
- POST /api/v1/auth/2fa/disable - Disable 2FA

ISO 27001:2013 compliant - Authentication and access control
"""

from flask import Blueprint

from ._helpers import (
    request, jsonify,
    ValidationError,
    TwoFactorSetup, TwoFactorDisable,
    UserRepository,
    token_required, get_current_user,
    AuditService, AdminSetup
)


auth_2fa_bp = Blueprint('auth_2fa', __name__, url_prefix='/auth/2fa')


@auth_2fa_bp.route('/setup', methods=['POST'])
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


@auth_2fa_bp.route('/verify', methods=['POST'])
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


@auth_2fa_bp.route('/disable', methods=['POST'])
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
