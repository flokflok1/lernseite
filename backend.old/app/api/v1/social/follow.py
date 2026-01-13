"""
Social Follow API Endpoints

Feature Flag: follow_system (DISABLED by default)
All endpoints protected with @require_feature('follow_system')

Endpoints:
- POST   /api/social/follow/:user_id     - Follow user
- DELETE /api/social/follow/:user_id     - Unfollow user
- GET    /api/social/followers/:user_id  - Get followers
- GET    /api/social/following/:user_id  - Get following
- GET    /api/social/suggestions          - Get follow suggestions
"""

from flask import Blueprint, request, jsonify, g
from app.core.feature_flags import require_feature
from app.middleware.auth import token_required

follow_bp = Blueprint('social_follow', __name__, url_prefix='/social/follow')


@follow_bp.route('/api/social/follow/<target_user_id>', methods=['POST'])
@token_required
@require_feature('follow_system')
def follow_user(target_user_id: str):
    """
    Follow a user

    Feature Flag: follow_system
    Auth: Required

    Returns:
        201: Follow created
        400: Cannot follow yourself or already following
        404: User not found
    """
    from app.social.follow.follow_manager import FollowManager

    follower_user_id = g.user_id

    if follower_user_id == target_user_id:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_ACTION',
                'message': 'Cannot follow yourself'
            }
        }), 400

    result = FollowManager.follow_user(
        follower_user_id=follower_user_id,
        followed_user_id=target_user_id
    )

    if not result['success']:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 400

    return jsonify({
        'success': True,
        'data': result['data'],
        'message': result.get('message', 'Following successfully')
    }), 201


@follow_bp.route('/api/social/follow/<target_user_id>', methods=['DELETE'])
@token_required
@require_feature('follow_system')
def unfollow_user(target_user_id: str):
    """
    Unfollow a user

    Feature Flag: follow_system
    Auth: Required

    Returns:
        200: Unfollowed successfully
        404: Not following this user
    """
    from app.social.follow.follow_manager import FollowManager

    follower_user_id = g.user_id

    success = FollowManager.unfollow_user(
        follower_user_id=follower_user_id,
        followed_user_id=target_user_id
    )

    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'You are not following this user'
            }
        }), 404

    return jsonify({
        'success': True,
        'message': 'Unfollowed successfully'
    }), 200


@follow_bp.route('/api/social/followers/<target_user_id>', methods=['GET'])
@token_required
@require_feature('follow_system')
def get_followers(target_user_id: str):
    """
    Get user's followers list

    Feature Flag: follow_system
    Auth: Required

    Query Params:
        page (int): Page number
        per_page (int): Items per page (max: 100)

    Returns:
        200: List of followers
    """
    from app.social.follow.followers_service import FollowersService

    viewer_user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)

    followers = FollowersService.get_followers(
        user_id=target_user_id,
        viewer_user_id=viewer_user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'success': True,
        'data': followers,
        'meta': {
            'page': page,
            'per_page': per_page
        }
    }), 200


@follow_bp.route('/api/social/following/<target_user_id>', methods=['GET'])
@token_required
@require_feature('follow_system')
def get_following(target_user_id: str):
    """
    Get users that this user is following

    Feature Flag: follow_system
    Auth: Required

    Query Params:
        page (int): Page number
        per_page (int): Items per page

    Returns:
        200: List of following
    """
    from app.social.follow.following_service import FollowingService

    viewer_user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)

    following = FollowingService.get_following(
        user_id=target_user_id,
        viewer_user_id=viewer_user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'success': True,
        'data': following,
        'meta': {
            'page': page,
            'per_page': per_page
        }
    }), 200


@follow_bp.route('/api/social/suggestions', methods=['GET'])
@token_required
@require_feature('follow_system')
def get_follow_suggestions():
    """
    Get AI-powered follow suggestions

    Feature Flag: follow_system
    Auth: Required

    Query Params:
        limit (int): Number of suggestions (default: 10, max: 50)

    Returns:
        200: List of suggested users with reasons
    """
    from app.social.follow.suggestions import FollowSuggestions

    user_id = g.user_id
    limit = min(int(request.args.get('limit', 10)), 50)

    suggestions = FollowSuggestions.get_suggestions(
        user_id=user_id,
        limit=limit
    )

    return jsonify({
        'success': True,
        'data': suggestions,
        'meta': {
            'limit': limit
        }
    }), 200
