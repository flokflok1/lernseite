"""
LernsystemX Auth API - Registration Module

Endpoints:
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/verify-email - Verify email address

ISO 27001:2013 compliant - Authentication and access control
"""

from flask import Blueprint

from app.api.v1.auth._helpers import (
    request, jsonify,
    ValidationError,
    UserCreate, UserResponse, EmailVerification,
    UserRepository
)


auth_register_bp = Blueprint('auth_register', __name__, url_prefix='/auth')


@auth_register_bp.route('/register', methods=['POST'])
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
            organization_id=user_data.organization_id
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


@auth_register_bp.route('/verify-email', methods=['POST'])
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
