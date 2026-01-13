"""
LernsystemX Profile API

User profile management endpoints.

Core Endpoints:
- GET    /api/v1/profile                     - Get current user profile
- PUT    /api/v1/profile                     - Update profile
- POST   /api/v1/profile/change-password     - Change password
- DELETE /api/v1/profile                     - Delete account
- GET    /api/v1/profile/courses             - Get enrolled courses
- GET    /api/v1/profile/activity            - Get activity history
- GET    /api/v1/profile/stats               - Get statistics
- GET    /api/v1/profile/theme               - Get theme preference
- PATCH  /api/v1/profile/theme               - Update theme
- GET    /api/v1/profile/preferences         - Get preferences
- PUT    /api/v1/profile/preferences/window-sizes  - Update window sizes
- GET    /api/v1/profile/subscription        - Get subscription info
- GET    /api/v1/profile/tokens              - Get token balance

ISO 27001:2013 compliant
Refactored: 2026-01-12 - Consolidated from profile/ folder
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.user import (
    UserUpdate, UserProfile, PasswordChange,
    ThemePreferenceResponse, ThemePreferenceUpdateRequest
)
from app.repositories.user import UserRepository
from app.repositories.token import TokenRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.settings.user_preferences import UserPreferencesRepository
from app.services.billing_service import BillingService
from app.services.audit_service import AuditService, Severity
from app.middleware.auth import token_required, get_current_user

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

# Import all endpoints from original files
profile_core_bp = Blueprint('profile_core', __name__, url_prefix='/profile')


@profile_bp.route('', methods=['GET'])
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

        # Fetch subscription info
        plan_info = BillingService.get_effective_plan_for_user(user['user_id'])
        subscription_plan = plan_info.get('plan_name', 'free')
        subscription_status = 'active' if plan_info['source'] != 'default' else 'none'

        # Fetch token balance
        if plan_info['source'] == 'organisation' and user.get('organization_id'):
            wallet = TokenRepository.get_or_create_organisation_wallet(user['organization_id'])
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
            'profile': profile.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get profile',
            'details': str(e)
        }), 500


@profile_bp.route('', methods=['PUT'])
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
            if v is not None and k not in ['role', 'is_active', 'organization_id']
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


@profile_bp.route('/change-password', methods=['POST'])
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


@profile_bp.route('', methods=['DELETE'])
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


@profile_bp.route('/courses', methods=['GET'])
@token_required
def get_user_courses():
    """
    Get courses enrolled by current user

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 10)

    Response:
        200: List of enrolled courses
    """
    try:
        user = get_current_user()

        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)

        # TODO: Fetch enrolled courses from enrollments table
        # For now, return placeholder
        courses = {
            'items': [],
            'total': 0,
            'page': page,
            'per_page': per_page,
            'total_pages': 0
        }

        return jsonify({
            'success': True,
            'courses': courses
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get courses',
            'details': str(e)
        }), 500


@profile_bp.route('/activity', methods=['GET'])
@token_required
def get_activity():
    """
    Get current user's activity history

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        limit: Max activities to return (default: 20, max: 100)

    Response:
        200: List of recent activities
    """
    try:
        user = get_current_user()

        # Get query parameters
        limit = min(int(request.args.get('limit', 20)), 100)

        # TODO: Fetch activity from audit_logs table
        # For now, return placeholder
        activities = []

        return jsonify({
            'success': True,
            'activities': activities,
            'total': len(activities)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get activity',
            'details': str(e)
        }), 500


@profile_bp.route('/stats', methods=['GET'])
@token_required
def get_profile_stats():
    """
    Get current user's profile statistics

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Profile statistics
        - courses_enrolled: Number of enrolled courses
        - courses_completed: Number of completed courses
        - total_learning_time: Total time spent learning (minutes)
        - achievements_count: Number of achievements earned
    """
    try:
        user = get_current_user()

        # TODO: Calculate real statistics
        stats = {
            'courses_enrolled': 0,
            'courses_completed': 0,
            'total_learning_time': 0,
            'achievements_count': 0,
            'tokens_used': 0,
            'tokens_remaining': 0
        }

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get stats',
            'details': str(e)
        }), 500
@profile_bp.route('/theme', methods=['GET'])
@token_required
def get_theme_preference():
    """
    Get current user's theme preference

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Theme preference
            {
                "theme": "dark" | "light" | "system"
            }
        500: Server error

    Example:
        >>> GET /api/v1/profile/theme
        >>> Headers: Authorization: Bearer <token>
        >>> Response: {"theme": "dark"}
    """
    try:
        user = get_current_user()

        # Get theme preference from repository
        theme = UserRepository.get_theme_preference(user['user_id'])

        # Create response
        response = ThemePreferenceResponse(theme=theme)

        return jsonify(response.model_dump()), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get theme preference',
            'details': str(e)
        }), 500


@profile_bp.route('/theme', methods=['PATCH'])
@token_required
def update_theme_preference():
    """
    Update current user's theme preference

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "theme": "dark" | "light" | "system"
        }

    Response:
        200: Theme updated successfully
            {
                "theme": "dark" | "light" | "system"
            }
        400: Validation error (invalid theme value)
        401: Not authenticated
        500: Server error

    Example:
        >>> PATCH /api/v1/profile/theme
        >>> Headers: Authorization: Bearer <token>
        >>> Body: {"theme": "light"}
        >>> Response: {"theme": "light"}
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate with Pydantic
        theme_request = ThemePreferenceUpdateRequest(**data)

        # Get current theme for audit log
        old_theme = UserRepository.get_theme_preference(user['user_id'])

        # Update theme preference
        new_theme = UserRepository.update_theme_preference(
            user['user_id'],
            theme_request.theme
        )

        # Audit log: Theme preference changed
        AuditService.log_event(
            event_type='preferences',
            event_category='data_modification',
            action='change_theme',
            severity=Severity.INFO,
            user_id=user.get('user_id'),
            user_email=user.get('email'),
            user_role=user.get('role'),
            resource_type='user_preferences',
            resource_id=str(user['user_id']),
            description=f"User changed theme from '{old_theme}' to '{new_theme}'",
            metadata={
                'old_theme': old_theme,
                'new_theme': new_theme
            },
            success=True
        )

        # Create response
        response = ThemePreferenceResponse(theme=new_theme)

        return jsonify(response.model_dump()), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update theme preference',
            'details': str(e)
        }), 500

@profile_bp.route('/preferences', methods=['GET'])
@token_required
def get_user_preferences():
    """
    Get current user's preferences (window sizes, UI settings, etc.)

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: User preferences
            {
                "success": true,
                "preferences": {
                    "window_sizes": {"admin-model-selector": {"width": 800, "height": 600}},
                    "ui_settings": {},
                    "general_settings": {}
                }
            }
        500: Server error
    """
    try:
        user = get_current_user()
        prefs = UserPreferencesRepository.get_by_user_id(user['user_id'])

        if prefs:
            return jsonify({
                'success': True,
                'preferences': {
                    'window_sizes': prefs.get('window_sizes', {}),
                    'ui_settings': prefs.get('ui_settings', {}),
                    'general_settings': prefs.get('general_settings', {})
                }
            }), 200
        else:
            # Return empty preferences
            return jsonify({
                'success': True,
                'preferences': {
                    'window_sizes': {},
                    'ui_settings': {},
                    'general_settings': {}
                }
            }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get preferences',
            'details': str(e)
        }), 500


@profile_bp.route('/preferences/window-sizes', methods=['GET'])
@token_required
def get_window_sizes():
    """
    Get current user's window size preferences

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Window sizes
            {
                "success": true,
                "window_sizes": {
                    "admin-model-selector": {"width": 800, "height": 600},
                    "admin-course-editor": {"width": 1200, "height": 800}
                }
            }
    """
    try:
        user = get_current_user()
        window_sizes = UserPreferencesRepository.get_window_sizes(user['user_id'])

        return jsonify({
            'success': True,
            'window_sizes': window_sizes
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get window sizes',
            'details': str(e)
        }), 500


@profile_bp.route('/preferences/window-sizes', methods=['PUT'])
@token_required
def update_window_sizes():
    """
    Update window size for a specific window type

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "window_type": "admin-model-selector",
            "width": 900,
            "height": 700
        }

    Response:
        200: Window size updated
            {
                "success": true,
                "message": "Window size updated",
                "window_sizes": {...}
            }
        400: Invalid request
    """
    try:
        user = get_current_user()
        data = request.get_json()

        # Validate required fields
        window_type = data.get('window_type')
        width = data.get('width')
        height = data.get('height')

        if not window_type:
            return jsonify({
                'success': False,
                'error': 'window_type is required'
            }), 400

        if not isinstance(width, int) or not isinstance(height, int):
            return jsonify({
                'success': False,
                'error': 'width and height must be integers'
            }), 400

        # Validate minimum sizes
        if width < 400 or height < 300:
            return jsonify({
                'success': False,
                'error': 'Minimum window size is 400x300'
            }), 400

        # Update window size
        prefs = UserPreferencesRepository.update_window_size(
            user['user_id'],
            window_type,
            width,
            height
        )

        return jsonify({
            'success': True,
            'message': f'Window size for {window_type} updated',
            'window_sizes': prefs.get('window_sizes', {})
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update window size',
            'details': str(e)
        }), 500


@profile_bp.route('/preferences/window-sizes/<window_type>', methods=['DELETE'])
@token_required
def delete_window_size(window_type: str):
    """
    Delete a specific window size preference

    Headers:
        Authorization: Bearer <access_token>

    URL Parameters:
        window_type: The window type to delete (e.g. admin-model-selector)

    Response:
        200: Window size deleted
        404: Window type not found in preferences
    """
    try:
        user = get_current_user()

        prefs = UserPreferencesRepository.delete_window_size(user['user_id'], window_type)

        if prefs:
            return jsonify({
                'success': True,
                'message': f'Window size for {window_type} deleted',
                'window_sizes': prefs.get('window_sizes', {})
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No preferences found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete window size',
            'details': str(e)
        }), 500


@profile_bp.route('/preferences/reset', methods=['POST'])
@token_required
def reset_user_preferences():
    """
    Reset all user preferences to defaults

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Preferences reset
    """
    try:
        user = get_current_user()

        prefs = UserPreferencesRepository.reset_preferences(user['user_id'])

        return jsonify({
            'success': True,
            'message': 'Preferences reset to defaults',
            'preferences': {
                'window_sizes': prefs.get('window_sizes', {}) if prefs else {},
                'ui_settings': prefs.get('ui_settings', {}) if prefs else {},
                'general_settings': prefs.get('general_settings', {}) if prefs else {}
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to reset preferences',
            'details': str(e)
        }), 500


@profile_bp.route('/subscription', methods=['GET'])
@token_required
def get_subscription():
    """
    Get current user's subscription information

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Subscription information
        - plan: Subscription plan (free, premium, pro)
        - tier: Subscription tier
        - status: Subscription status (active, cancelled, expired)
        - features: Plan features
        - expires_at: Subscription end date
        - auto_renew: Whether subscription will auto-renew
        - source: Subscription source (user, organisation, default)
    """
    try:
        user = get_current_user()

        # Get effective plan
        plan_info = BillingService.get_effective_plan_for_user(user['user_id'])

        # Get detailed subscription if exists
        subscription_data = None

        if plan_info['source'] == 'user':
            subscription_data = SubscriptionRepository.get_subscription_for_user(user['user_id'])
        elif plan_info['source'] == 'organisation':
            subscription_data = SubscriptionRepository.get_subscription_for_organisation(
                user['organization_id']
            )

        # Build response
        response = {
            'plan': plan_info['plan_name'],
            'tier': plan_info['tier'],
            'features': plan_info['features'],
            'source': plan_info['source']
        }

        if subscription_data:
            response['status'] = subscription_data['status']
            response['expires_at'] = (
                subscription_data['expires_at'].isoformat()
                if subscription_data.get('expires_at') else None
            )
            response['auto_renew'] = subscription_data.get('auto_renew', False)
            response['billing_cycle'] = subscription_data.get('billing_cycle')
            response['started_at'] = (
                subscription_data['started_at'].isoformat()
                if subscription_data.get('started_at') else None
            )
        else:
            response['status'] = 'none'
            response['expires_at'] = None
            response['auto_renew'] = False

        return jsonify({
            'success': True,
            'subscription': response
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get subscription',
            'details': str(e)
        }), 500


@profile_bp.route('/tokens', methods=['GET'])
@token_required
def get_token_balance():
    """
    Get current user's AI token balance

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Token balance information
        - balance: Current token balance
        - total_purchased: Total tokens purchased
        - total_granted: Total tokens granted (subscriptions, promos)
        - total_consumed: Total tokens consumed
        - monthly_grant: Monthly subscription token grant
        - source: Wallet source (user, organisation)
    """
    try:
        user = get_current_user()

        # Get effective plan to determine wallet source
        plan_info = BillingService.get_effective_plan_for_user(user['user_id'])

        # Determine which wallet to return
        if plan_info['source'] == 'organisation' and user.get('organization_id'):
            # Organisation wallet
            wallet = TokenRepository.get_or_create_organisation_wallet(user['organization_id'])
            source = 'organisation'
        else:
            # User wallet
            wallet = TokenRepository.get_or_create_user_wallet(user['user_id'])
            source = 'user'

        token_balance = {
            'balance': wallet['balance'],
            'reserved': wallet.get('reserved', 0),
            'available': wallet['balance'] - wallet.get('reserved', 0),
            'total_purchased': wallet['total_purchased'],
            'total_granted': wallet['total_granted'],
            'total_consumed': wallet['total_consumed'],
            'monthly_grant': wallet.get('monthly_grant_amount'),
            'last_grant_date': (
                wallet.get('last_grant_date').isoformat()
                if wallet.get('last_grant_date') else None
            ),
            'source': source
        }

        return jsonify({
            'success': True,
            'tokens': token_balance
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get token balance',
            'details': str(e)
        }), 500

__all__ = ['profile_bp']
