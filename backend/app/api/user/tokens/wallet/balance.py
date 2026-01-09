"""
LernsystemX Tokens Wallet API

Token wallet balance endpoints for users and organisations.

Endpoints:
- GET /api/v1/tokens/me - Get current user's token balance
- GET /api/v1/tokens/organisation/:id - Get organisation token balance (org admin only)
"""

from flask import Blueprint, jsonify

from app.models.token import (
    TokenWalletResponse,
    TokenBalanceResponse
)
from app.repositories.token import TokenRepository
from app.services.billing_service import BillingService
from app.middleware.auth import token_required, get_current_user


tokens_wallet_bp = Blueprint(
    'tokens_wallet',
    __name__,
    url_prefix='/tokens'
)


# ============================================================================
# WALLET ENDPOINTS
# ============================================================================

@tokens_wallet_bp.route('/me', methods=['GET'])
@token_required
def get_my_token_balance():
    """
    Get current user's token balance

    Returns user's personal wallet or organisation wallet if user belongs to org.

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Token balance information
        {
            "success": true,
            "wallet": {
                "wallet_id": 1,
                "balance": 8500,
                "reserved": 1500,
                "available": 7000,
                "total_purchased": 20000,
                "total_granted": 10000,
                "total_consumed": 21500,
                "monthly_grant_amount": 10000,
                "last_grant_date": "2025-01-01",
                "source": "user"
            }
        }
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

        # Convert to response model
        wallet_response = TokenWalletResponse(**wallet)

        # Calculate available tokens
        available = wallet['balance'] - wallet.get('reserved', 0)

        # Build balance response
        balance = TokenBalanceResponse(
            wallet_id=wallet['wallet_id'],
            balance=wallet['balance'],
            reserved=wallet.get('reserved', 0),
            available=available,
            source=source,
            monthly_grant=wallet.get('monthly_grant_amount'),
            next_grant_date=wallet.get('last_grant_date')
        )

        return jsonify({
            'success': True,
            'wallet': wallet_response.model_dump(),
            'balance': balance.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get token balance',
            'details': str(e)
        }), 500


@tokens_wallet_bp.route('/organisation/<int:organization_id>', methods=['GET'])
@token_required
def get_organisation_tokens(organization_id: int):
    """
    Get organisation token balance (org admin only)

    Only accessible by users who are admins of the specified organisation.

    Headers:
        Authorization: Bearer <access_token>

    Path Parameters:
        organization_id: Organisation ID

    Response:
        200: Organisation token balance
        403: Not an admin of this organisation
        404: Organisation not found
    """
    try:
        user = get_current_user()

        # Verify user is admin of this organisation
        if user.get('organization_id') != organization_id:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You do not have access to this organisation'
            }), 403

        # Check if user has org_admin role
        if user.get('role') not in ['org_admin', 'admin']:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Only organisation admins can view organisation token balance'
            }), 403

        # Get organisation wallet
        wallet = TokenRepository.get_wallet_for_organisation(organization_id)

        if not wallet:
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': 'Organisation wallet not found'
            }), 404

        # Convert to response model
        wallet_response = TokenWalletResponse(**wallet)

        # Get usage statistics
        stats = TokenRepository.get_org_token_stats(
            organization_id=organization_id,
            period_days=30
        )

        return jsonify({
            'success': True,
            'wallet': wallet_response.model_dump(),
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get organisation tokens',
            'details': str(e)
        }), 500
