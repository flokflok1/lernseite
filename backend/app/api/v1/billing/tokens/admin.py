"""
LernsystemX Admin Token Management API

Admin Token Operations:
- POST /tokens/manual-topup - Manual token top-up (admin only)
- GET /tokens/stats - Get global token statistics (admin only)

All routes: /api/v1/tokens/*
ISO 27001:2013 compliant - Token wallet security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.domain.models.token import (
    TokenTransactionResponse,
    TokenManualTopupRequest
)
from app.infrastructure.persistence.repositories.token import TokenRepository
from app.infrastructure.persistence.repositories.user import UserRepository
from app.api.middleware.auth import token_required, admin_required, get_current_user

admin_tokens_bp = Blueprint('admin_tokens', __name__, url_prefix='/tokens')

__all__ = ['admin_tokens_bp']


# =============================================================================
# ADMIN - TOKEN MANAGEMENT
# =============================================================================

@admin_tokens_bp.route('/manual-topup', methods=['POST'])
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
            "user_id": 42,  // OR "organisation_id": 10
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
            wallet = TokenRepository.get_or_create_organisation_wallet(topup_request.organisation_id)
            target_type = 'organisation'
            target_id = topup_request.organisation_id

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


@admin_tokens_bp.route('/stats', methods=['GET'])
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
