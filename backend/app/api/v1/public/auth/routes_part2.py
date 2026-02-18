"""
LernsystemX Authentication API - Part 2

Password reset and two-factor authentication endpoints.

Endpoints:
- POST /api/v1/auth/forgot-password - Request password reset
- POST /api/v1/auth/reset-password - Reset password with token
- POST /api/v1/auth/2fa/setup - Setup 2FA
- POST /api/v1/auth/2fa/verify - Verify 2FA code
- POST /api/v1/auth/2fa/disable - Disable 2FA

ISO 27001:2013 compliant - Authentication and access control
Split from routes.py to comply with Quality Gate G01 (max 500 lines per file)
"""

from flask import request, jsonify
from pydantic import ValidationError
import logging

from app.infrastructure.i18n.error_codes import ErrorCode, error_response

logger = logging.getLogger(__name__)

from app.domain.models.schemas.user import (
    TwoFactorSetup,
    TwoFactorDisable,
    PasswordReset
)
from app.infrastructure.persistence.repositories.user import UserRepository
from app.api.middleware.auth import token_required, get_current_user
from app.application.services.system.audit.service import AuditService
from app.setup.initialization.admin import AdminSetup
from app.infrastructure.persistence.database.connection import execute_query

from app.api.v1.public.auth.routes import auth_bp


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
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400, details={'field': 'email'})

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
        logger.error(f"Forgot password error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


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
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'fields': e.errors()})
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


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
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400, details={'message': 'Two-factor authentication is already enabled for your account'})

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
        logger.error(f"2FA setup error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


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
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400, details={'message': 'Please set up 2FA first at /api/v1/auth/2fa/setup'})

        is_valid = AdminSetup.verify_2fa_code(totp_secret, verify_data.totp_code)
        if not is_valid:
            return error_response(ErrorCode.AUTH_2FA_INVALID, 400)

        execute_query("UPDATE users SET two_factor_enabled = true WHERE user_id = %s", (user['user_id'],))
        AuditService.log_2fa_enabled(user_id=user['user_id'], user_email=user['email'])

        return jsonify({
            'success': True,
            'message': 'Two-factor authentication enabled successfully',
            'two_factor_enabled': True
        }), 200

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'fields': e.errors()})
    except Exception as e:
        logger.error(f"2FA verification error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})


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
            return error_response(ErrorCode.BUSINESS_LOGIC_ERROR, 400, details={'message': 'Two-factor authentication is not enabled for your account'})

        authenticated = UserRepository.authenticate(user['email'], disable_data.password)
        if not authenticated:
            return error_response(ErrorCode.AUTH_INVALID_CREDENTIALS, 401, details={'message': 'The password you entered is incorrect'})

        totp_secret = user.get('two_factor_secret')
        is_valid = AdminSetup.verify_2fa_code(totp_secret, disable_data.totp_code)
        if not is_valid:
            return error_response(ErrorCode.AUTH_2FA_INVALID, 400)

        execute_query("UPDATE users SET two_factor_enabled = false, two_factor_secret = NULL WHERE user_id = %s", (user['user_id'],))
        AuditService.log_2fa_disabled(user_id=user['user_id'], user_email=user['email'])

        return jsonify({
            'success': True,
            'message': 'Two-factor authentication disabled successfully',
            'two_factor_enabled': False
        }), 200

    except ValidationError as e:
        return error_response(ErrorCode.VALIDATION_ERROR, 400, details={'fields': e.errors()})
    except Exception as e:
        logger.error(f"2FA disable error: {e}")
        return error_response(ErrorCode.AUTH_FAILED, 500, details={'error': str(e)})
