"""
LernsystemX Tokens Transactions API

Token transaction history endpoints.

Endpoints:
- GET /api/v1/tokens/transactions - Get current user's token transaction history
"""

from flask import Blueprint, request, jsonify

from app.models.token import TokenTransactionResponse
from app.repositories.token import TokenRepository
from app.middleware.auth import token_required, get_current_user


tokens_transactions_bp = Blueprint(
    'tokens_transactions',
    __name__,
    url_prefix='/tokens'
)


# ============================================================================
# TRANSACTION ENDPOINTS
# ============================================================================

@tokens_transactions_bp.route('/transactions', methods=['GET'])
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
