"""
Organisations Domain - Statistics Routes (Analytics Journey)

Organisation statistics endpoints:
- GET /organisations/<id>/stats - Get organisation statistics

Architecture: Journey-Based DDD
Database: PostgreSQL via OrganisationRepository (direct SQL)
ISO 27001:2013 compliant - Organisation analytics and reporting
"""

from flask import Blueprint

from ._helpers import (
    jsonify,
    OrganisationRepository,
    SubscriptionRepository,
    OrganisationStatsResponse,
    token_required, get_current_user,
    check_org_membership
)


organisations_stats_bp = Blueprint(
    'organisations_stats',
    __name__,
    url_prefix='/organisations'
)


@organisations_stats_bp.route('/<int:org_id>/stats', methods=['GET'])
@token_required
def get_organisation_stats(org_id: int):
    """
    Get organisation statistics

    Headers:
        Authorization: Bearer <access_token>

    Path Parameters:
        org_id: Organisation ID

    Response:
        200: Organisation statistics
        - User counts (total, active, by role)
        - Course counts (total, active)
        - Class counts (for schools)
        - Token usage
        - Subscription info
        403: Insufficient permissions (org_admin or admin required)
        404: Organisation not found

    Permissions:
        - Admins can view stats of all organisations
        - org_admin can view stats of their organisation
    """
    try:
        current_user = get_current_user()

        # Check permissions - only org_admin can view stats
        if not check_org_membership(current_user, org_id, required_roles=['org_admin']):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Only organisation administrators can view statistics'
            }), 403

        # Check if organisation exists
        org = OrganisationRepository.get_organisation_by_id(org_id)
        if not org:
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': f'Organisation with ID {org_id} not found'
            }), 404

        # Get base stats from repository
        stats = OrganisationRepository.get_organisation_stats(org_id)

        # Get subscription info (integration with SubscriptionRepository)
        try:
            subscription = SubscriptionRepository.get_subscription_for_organisation(org_id)
            if subscription:
                stats['subscription_plan'] = subscription.get('plan_name')
                stats['subscription_status'] = subscription.get('status')
                stats['subscription_expires_at'] = subscription.get('expires_at')
        except Exception:
            # Subscription repository may not be available yet
            pass

        # Convert to response model
        stats_response = OrganisationStatsResponse(**stats)

        return jsonify({
            'success': True,
            'stats': stats_response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get organisation statistics',
            'details': str(e)
        }), 500
