"""
LernsystemX User Token Wallet API

User Token Operations:
- GET /tokens/me - Get current user's token balance
- GET /tokens/organisation/<id> - Get organisation token balance (org admin only)
- GET /tokens/transactions - Get current user's token transaction history
- GET /tokens/usage - Get current user's token usage analytics
- POST /tokens/estimate - Estimate AI token cost

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
)
from app.infrastructure.persistence.repositories.token import TokenRepository
from app.application.services.system.billing.service import BillingService
from app.api.middleware.auth import token_required, get_current_user

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
        if plan_info['source'] == 'organisation' and user.get('organisation_id'):
            # Organisation wallet
            wallet = TokenRepository.get_or_create_organisation_wallet(user['organisation_id'])
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


@tokens_bp.route('/organisation/<int:organisation_id>', methods=['GET'])
@token_required
def get_organisation_tokens(organisation_id: int):
    """
    Get organisation token balance (org admin only)

    Only accessible by users who are admins of the specified organisation.

    Headers:
        Authorization: Bearer <access_token>

    Path Parameters:
        organisation_id: Organisation ID

    Response:
        200: Organisation token balance
        403: Not an admin of this organisation
        404: Organisation not found
    """
    try:
        user = get_current_user()

        # Verify user is admin of this organisation
        if user.get('organisation_id') != organisation_id:
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
        wallet = TokenRepository.get_wallet_for_organisation(organisation_id)

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
            organisation_id=organisation_id,
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
