"""
LernsystemX Tokens API - Consolidated

User Token Wallet:
- GET /tokens/me - Get current user's token balance
- GET /tokens/transactions - Get current user's token transaction history
- GET /tokens/usage - Get current user's token usage analytics
- POST /tokens/estimate - Estimate AI token cost

Organisation Token Wallet:
- GET /tokens/organisation/<id> - Get organisation token balance (org admin only)

Admin Management:
- POST /tokens/manual-topup - Manual token top-up (admin only)
- GET /tokens/stats - Get global token statistics (admin only)

All routes: /api/v1/tokens/*
ISO 27001:2013 compliant - Token wallet security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.domain.models.token import (
    TokenWalletResponse,
    TokenBalanceResponse,
    TokenTransactionResponse,
    TokenUsageStats,
    TokenManualTopupRequest
)
from app.repositories.token import TokenRepository
from app.repositories.user import UserRepository
from app.services.system.billing.service import BillingService
from app.middleware.auth import token_required, admin_required, get_current_user

tokens_bp = Blueprint('tokens', __name__, url_prefix='/tokens')

__all__ = ['tokens_bp']


# =============================================================================
# USER - WALLET BALANCE
# =============================================================================

@tokens_bp.route('/me', methods=['GET'])
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


@tokens_bp.route('/organisation/<int:organization_id>', methods=['GET'])
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


# =============================================================================
# USER - TRANSACTION HISTORY
# =============================================================================

@tokens_bp.route('/transactions', methods=['GET'])
@token_required
def get_my_transactions():
    """
    Get current user's token transaction history

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        limit: Max transactions to return (default: 50, max: 100)
        offset: Pagination offset (default: 0)

    Response:
        200: List of token transactions
        {
            "success": true,
            "transactions": [
                {
                    "transaction_id": 12345,
                    "amount": -2000,
                    "balance_after": 8500,
                    "reason": "ai_execution",
                    "description": "KI-Tutor execution",
                    "created_at": "2025-01-15T10:30:00"
                }
            ],
            "total": 150,
            "limit": 50,
            "offset": 0
        }
    """
    try:
        user = get_current_user()

        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))

        # Get user's wallet
        wallet = TokenRepository.get_or_create_user_wallet(user['user_id'])

        # Get transactions
        transactions = TokenRepository.get_transactions(
            wallet_id=wallet['wallet_id'],
            limit=limit,
            offset=offset
        )

        # Convert to response models
        transaction_responses = [
            TokenTransactionResponse(**txn) for txn in transactions
        ]

        return jsonify({
            'success': True,
            'transactions': [t.model_dump() for t in transaction_responses],
            'total': len(transactions),
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get transactions',
            'details': str(e)
        }), 500


# =============================================================================
# USER - USAGE STATISTICS
# =============================================================================

@tokens_bp.route('/usage', methods=['GET'])
@token_required
def get_my_usage():
    """
    Get current user's token usage statistics

    Headers:
        Authorization: Bearer <access_token>

    Query Parameters:
        period_days: Statistics period in days (default: 30)

    Response:
        200: Token usage statistics
        {
            "success": true,
            "stats": {
                "user_id": 42,
                "current_balance": 8500,
                "total_tokens_used": 15000,
                "total_tokens_bought": 20000,
                "total_tokens_granted": 10000,
                "by_reason": {
                    "ai_execution": 15000
                },
                "by_method": {
                    "KI-Tutor": 8000,
                    "KI-Glossar": 7000
                },
                "period_start": "2024-12-16T00:00:00",
                "period_end": "2025-01-15T00:00:00"
            }
        }
    """
    try:
        user = get_current_user()

        # Get query parameters
        period_days = int(request.args.get('period_days', 30))

        # Get usage statistics
        stats = TokenRepository.get_user_token_stats(
            user_id=user['user_id'],
            period_days=period_days
        )

        # Convert to response model
        stats_response = TokenUsageStats(**stats)

        return jsonify({
            'success': True,
            'stats': stats_response.model_dump(),
            'period_days': period_days
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get usage statistics',
            'details': str(e)
        }), 500


@tokens_bp.route('/estimate', methods=['POST'])
@token_required
def estimate_ai_cost():
    """
    Estimate AI token cost for a method

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "method_name": "KI-Tutor",
            "complexity": "medium"  // simple, medium, complex
        }

    Response:
        200: Estimated token cost
        {
            "success": true,
            "estimate": {
                "method_name": "KI-Tutor",
                "complexity": "medium",
                "estimated_tokens": 500,
                "can_afford": true,
                "current_balance": 8500
            }
        }
    """
    try:
        user = get_current_user()
        data = request.get_json()

        method_name = data.get('method_name')
        complexity = data.get('complexity', 'medium')

        if not method_name:
            return jsonify({
                'success': False,
                'error': 'Missing method_name',
                'message': 'Please provide a method_name to estimate cost'
            }), 400

        # Estimate cost
        estimated_tokens = BillingService.estimate_ai_cost(method_name, complexity)

        # Check if user can afford
        can_afford = BillingService.can_user_afford(user['user_id'], estimated_tokens)

        # Get current balance
        wallet = TokenRepository.get_or_create_user_wallet(user['user_id'])

        return jsonify({
            'success': True,
            'estimate': {
                'method_name': method_name,
                'complexity': complexity,
                'estimated_tokens': estimated_tokens,
                'can_afford': can_afford,
                'current_balance': wallet['balance']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to estimate cost',
            'details': str(e)
        }), 500


# =============================================================================
# ADMIN - TOKEN MANAGEMENT
# =============================================================================

@tokens_bp.route('/manual-topup', methods=['POST'])
@token_required
@admin_required
def manual_topup():
    """
    Manual token top-up (admin only)

    Allows admins to manually add or deduct tokens from user or organisation wallets.

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "user_id": 42,  // OR "organization_id": 10
            "amount": 5000,  // Positive = grant, negative = deduct
            "reason": "Support compensation for service outage"
        }

    Response:
        200: Tokens added/deducted successfully
        400: Validation error
        404: User/Organisation not found
    """
    try:
        data = request.get_json()

        # Validate request
        topup_request = TokenManualTopupRequest(**data)

        # Get or create wallet
        if topup_request.user_id:
            # User wallet
            user = UserRepository.find_by_id(topup_request.user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found',
                    'message': f'User {topup_request.user_id} does not exist'
                }), 404

            wallet = TokenRepository.get_or_create_user_wallet(topup_request.user_id)
            target_type = 'user'
            target_id = topup_request.user_id

        else:
            # Organisation wallet
            wallet = TokenRepository.get_or_create_organisation_wallet(topup_request.organization_id)
            target_type = 'organisation'
            target_id = topup_request.organization_id

        # Change balance
        transaction = TokenRepository.change_balance(
            wallet_id=wallet['wallet_id'],
            amount=topup_request.amount,
            reason='admin_adjustment',
            meta={
                'admin_reason': topup_request.reason,
                'admin_user_id': get_current_user()['user_id']
            },
            reference_type='admin_topup',
            reference_id=None
        )

        # Convert to response model
        transaction_response = TokenTransactionResponse(**transaction)

        return jsonify({
            'success': True,
            'message': f'Successfully {"added" if topup_request.amount > 0 else "deducted"} {abs(topup_request.amount)} tokens',
            'transaction': transaction_response.model_dump(),
            'new_balance': transaction['balance_after'],
            'target_type': target_type,
            'target_id': target_id
        }), 200

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
            'error': 'Manual top-up failed',
            'details': str(e)
        }), 500


@tokens_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_token_stats():
    """
    Get global token statistics (admin only)

    Headers:
        Authorization: Bearer <access_token>

    Response:
        200: Global token statistics
        {
            "success": true,
            "stats": {
                "total_wallets": 1523,
                "total_balance": 15234567,
                "total_purchased": 25000000,
                "total_granted": 10000000,
                "total_consumed": 19765433
            }
        }
    """
    try:
        # Get global statistics
        stats = TokenRepository.get_global_token_stats()

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get token statistics',
            'details': str(e)
        }), 500
