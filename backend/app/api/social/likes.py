"""
Social Likes & Reactions API Endpoints

Feature Flag: likes_reactions (DISABLED by default)
All endpoints protected with @require_feature('likes_reactions')

Endpoints:
- POST   /api/social/likes/post/:post_id       - Like/Unlike post
- POST   /api/social/reactions/post/:post_id   - React to post (extended)
- GET    /api/social/likes/post/:post_id       - Get post likes
- POST   /api/social/likes/comment/:comment_id - Like/Unlike comment
"""

from flask import Blueprint, request, jsonify, g
from app.core.feature_flags import require_feature
from app.middleware.auth import token_required

likes_bp = Blueprint('social_likes', __name__)


@likes_bp.route('/api/social/likes/post/<post_id>', methods=['POST'])
@token_required
@require_feature('likes_reactions')
def toggle_post_like(post_id: str):
    """
    Like or unlike a post (toggle)

    Feature Flag: likes_reactions
    Auth: Required

    Returns:
        200: Like toggled
        404: Post not found
    """
    from app.social.engagement.likes import LikesService

    user_id = g.user_id

    result = LikesService.toggle_like(
        user_id=user_id,
        post_id=post_id
    )

    if not result['success']:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 404

    return jsonify({
        'success': True,
        'data': result['data'],
        'message': result['message']  # 'Liked' or 'Unliked'
    }), 200


@likes_bp.route('/api/social/reactions/post/<post_id>', methods=['POST'])
@token_required
@require_feature('likes_reactions')
def react_to_post(post_id: str):
    """
    React to a post with extended reactions

    Feature Flag: likes_reactions
    Auth: Required

    Body:
        reaction_type (str): 'like', 'love', 'haha', 'wow', 'sad', 'angry', 'thinking', 'celebrate'

    Returns:
        200: Reaction added/updated
        400: Invalid reaction type
        404: Post not found
    """
    from app.social.engagement.reactions import ReactionsService

    user_id = g.user_id
    data = request.get_json()
    reaction_type = data.get('reaction_type')

    valid_reactions = ['like', 'love', 'haha', 'wow', 'sad', 'angry', 'thinking', 'celebrate']
    if reaction_type not in valid_reactions:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_REACTION',
                'message': f'Invalid reaction type. Must be one of: {", ".join(valid_reactions)}'
            }
        }), 400

    result = ReactionsService.add_reaction(
        user_id=user_id,
        post_id=post_id,
        reaction_type=reaction_type
    )

    if not result['success']:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 404

    return jsonify({
        'success': True,
        'data': result['data'],
        'message': 'Reaction added'
    }), 200


@likes_bp.route('/api/social/likes/post/<post_id>', methods=['GET'])
@token_required
@require_feature('likes_reactions')
def get_post_likes(post_id: str):
    """
    Get users who liked a post

    Feature Flag: likes_reactions
    Auth: Required

    Query Params:
        page (int): Page number
        per_page (int): Items per page (max: 100)

    Returns:
        200: List of users who liked the post
    """
    from app.social.engagement.likes import LikesService

    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)

    likes = LikesService.get_post_likes(
        post_id=post_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'success': True,
        'data': likes,
        'meta': {
            'page': page,
            'per_page': per_page
        }
    }), 200


@likes_bp.route('/api/social/likes/comment/<comment_id>', methods=['POST'])
@token_required
@require_feature('likes_reactions')
def toggle_comment_like(comment_id: str):
    """
    Like or unlike a comment (toggle)

    Feature Flag: likes_reactions
    Auth: Required

    Returns:
        200: Like toggled
        404: Comment not found
    """
    from app.social.engagement.likes import LikesService

    user_id = g.user_id

    result = LikesService.toggle_comment_like(
        user_id=user_id,
        comment_id=comment_id
    )

    if not result['success']:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 404

    return jsonify({
        'success': True,
        'data': result['data'],
        'message': result['message']
    }), 200


@likes_bp.route('/api/social/reactions/post/<post_id>', methods=['DELETE'])
@token_required
@require_feature('likes_reactions')
def remove_reaction(post_id: str):
    """
    Remove reaction from post

    Feature Flag: likes_reactions
    Auth: Required

    Returns:
        200: Reaction removed
        404: No reaction found
    """
    from app.social.engagement.reactions import ReactionsService

    user_id = g.user_id

    success = ReactionsService.remove_reaction(
        user_id=user_id,
        post_id=post_id
    )

    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'No reaction found'
            }
        }), 404

    return jsonify({
        'success': True,
        'message': 'Reaction removed'
    }), 200
