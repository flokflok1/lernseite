"""
LernsystemX Profile User Data API

User data query endpoints:
- GET /api/v1/profile/courses        - Get enrolled courses
- GET /api/v1/profile/activity       - Get activity history
- GET /api/v1/profile/stats          - Get profile statistics
- GET /api/v1/profile/subscription   - Get subscription info
- GET /api/v1/profile/tokens         - Get token balance

ISO 27001:2013 compliant
Split from: profile.py (Part 4/4 - User Data)
"""

from flask import Blueprint, request, jsonify

from app.infrastructure.persistence.repositories.user import UserRepository
from app.infrastructure.persistence.repositories.token import TokenRepository
from app.infrastructure.persistence.repositories.subscription import SubscriptionRepository
from app.services.system.billing.service import BillingService
from app.api.middleware.auth import token_required, get_current_user

user_data_bp = Blueprint('profile_user_data', __name__, url_prefix='/profile')


@user_data_bp.route('/courses', methods=['GET'])
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


@user_data_bp.route('/activity', methods=['GET'])
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


@user_data_bp.route('/stats', methods=['GET'])
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


@user_data_bp.route('/subscription', methods=['GET'])
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


@user_data_bp.route('/tokens', methods=['GET'])
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


__all__ = ['profile_user_data_bp']
