"""
Social Posts API Endpoints

Feature Flag: user_posts (DISABLED by default)
All endpoints protected with @require_feature('user_posts')

Endpoints:
- POST   /api/social/posts          - Create post
- GET    /api/social/posts/:id      - Get post by ID
- PUT    /api/social/posts/:id      - Update post
- DELETE /api/social/posts/:id      - Delete post (soft delete)
- GET    /api/social/posts/user/:id - Get user's posts
- POST   /api/social/posts/:id/pin  - Pin post to profile
"""

from flask import Blueprint, request, jsonify, g
from app.core.feature_flags import require_feature
from app.middleware.auth import token_required
from typing import Optional

posts_bp = Blueprint('social_posts', __name__, url_prefix='/social/posts')


@posts_bp.route('/api/social/posts', methods=['POST'])
@token_required
@require_feature('user_posts')
def create_post():
    """
    Create a new social post

    Feature Flag: user_posts (must be enabled)
    Auth: Required

    Body:
        content (str): Post text content
        content_type (str): 'text', 'media', 'course_portfolio', 'achievement'
        visibility (str): 'public', 'followers', 'private', 'unlisted'
        media_urls (list): Optional list of media URLs
        mentions (list): Optional list of user IDs to mention
        hashtags (list): Optional list of hashtags

    Returns:
        201: Post created successfully
        400: Invalid input
        403: Feature not available
    """
    from app.social.posts.post_manager import PostManager

    data = request.get_json()
    user_id = g.user_id

    # Validate required fields
    if not data.get('content') and not data.get('media_urls'):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_INPUT',
                'message': 'Post must have either content or media'
            }
        }), 400

    # Create post
    post = PostManager.create_post(
        user_id=user_id,
        content=data.get('content'),
        content_type=data.get('content_type', 'text'),
        visibility=data.get('visibility', 'public'),
        media_urls=data.get('media_urls', []),
        mentions=data.get('mentions', []),
        hashtags=data.get('hashtags', [])
    )

    return jsonify({
        'success': True,
        'data': post
    }), 201


@posts_bp.route('/api/social/posts/<post_id>', methods=['GET'])
@token_required
@require_feature('user_posts')
def get_post(post_id: str):
    """
    Get post by ID

    Feature Flag: user_posts
    Auth: Required

    Returns:
        200: Post data
        404: Post not found
        403: No access to private post
    """
    from app.social.posts.post_manager import PostManager

    user_id = g.user_id
    post = PostManager.get_post(post_id, viewer_user_id=user_id)

    if not post:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Post not found'
            }
        }), 404

    return jsonify({
        'success': True,
        'data': post
    }), 200


@posts_bp.route('/api/social/posts/<post_id>', methods=['PUT'])
@token_required
@require_feature('user_posts')
def update_post(post_id: str):
    """
    Update post

    Feature Flag: user_posts
    Auth: Required (must be post owner)

    Body:
        content (str): Updated content
        visibility (str): Updated visibility

    Returns:
        200: Post updated
        403: Not post owner
        404: Post not found
    """
    from app.social.posts.post_manager import PostManager

    data = request.get_json()
    user_id = g.user_id

    post = PostManager.update_post(
        post_id=post_id,
        user_id=user_id,
        content=data.get('content'),
        visibility=data.get('visibility')
    )

    if not post:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Post not found or no permission'
            }
        }), 404

    return jsonify({
        'success': True,
        'data': post
    }), 200


@posts_bp.route('/api/social/posts/<post_id>', methods=['DELETE'])
@token_required
@require_feature('user_posts')
def delete_post(post_id: str):
    """
    Delete post (soft delete)

    Feature Flag: user_posts
    Auth: Required (must be post owner)

    Returns:
        200: Post deleted
        403: Not post owner
        404: Post not found
    """
    from app.social.posts.post_manager import PostManager

    user_id = g.user_id
    success = PostManager.delete_post(post_id, user_id)

    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Post not found or no permission'
            }
        }), 404

    return jsonify({
        'success': True,
        'message': 'Post deleted successfully'
    }), 200


@posts_bp.route('/api/social/posts/user/<target_user_id>', methods=['GET'])
@token_required
@require_feature('user_posts')
def get_user_posts(target_user_id: str):
    """
    Get user's posts

    Feature Flag: user_posts
    Auth: Required

    Query Params:
        page (int): Page number (default: 1)
        per_page (int): Posts per page (default: 20, max: 100)

    Returns:
        200: List of posts with pagination
    """
    from app.social.posts.post_manager import PostManager

    viewer_user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)

    posts = PostManager.get_user_posts(
        target_user_id=target_user_id,
        viewer_user_id=viewer_user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'success': True,
        'data': posts,
        'meta': {
            'page': page,
            'per_page': per_page
        }
    }), 200


@posts_bp.route('/api/social/posts/<post_id>/pin', methods=['POST'])
@token_required
@require_feature('user_posts')
def pin_post(post_id: str):
    """
    Pin post to profile top

    Feature Flag: user_posts
    Auth: Required (must be post owner)

    Returns:
        200: Post pinned
        403: Not post owner or already have pinned post
        404: Post not found
    """
    from app.social.posts.post_manager import PostManager

    user_id = g.user_id
    success = PostManager.pin_post(post_id, user_id)

    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PIN_FAILED',
                'message': 'Could not pin post. Either not found, not owner, or already have pinned post.'
            }
        }), 400

    return jsonify({
        'success': True,
        'message': 'Post pinned successfully'
    }), 200
