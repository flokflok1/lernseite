"""
Social Comments API Endpoints

Feature Flag: comments (ENABLED for courses, extending to posts)
All endpoints protected with @require_feature('comments')

Endpoints:
- POST   /api/social/comments/post/:post_id       - Add comment to post
- GET    /api/social/comments/post/:post_id       - Get post comments
- PUT    /api/social/comments/:comment_id         - Update comment
- DELETE /api/social/comments/:comment_id         - Delete comment
- POST   /api/social/comments/:comment_id/reply   - Reply to comment
"""

from flask import Blueprint, request, jsonify, g
from app.core.feature_flags import require_feature
from app.middleware.auth import token_required

comments_bp = Blueprint('social_comments', __name__)


@comments_bp.route('/api/social/comments/post/<post_id>', methods=['POST'])
@token_required
@require_feature('comments')
def add_comment(post_id: str):
    """
    Add comment to a post

    Feature Flag: comments (enabled)
    Auth: Required

    Body:
        content (str): Comment text

    Returns:
        201: Comment created
        400: Invalid input
        404: Post not found
    """
    from app.social.engagement.comments import CommentsService

    user_id = g.user_id
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_INPUT',
                'message': 'Comment content cannot be empty'
            }
        }), 400

    result = CommentsService.add_comment(
        user_id=user_id,
        post_id=post_id,
        content=content
    )

    if not result['success']:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 404

    return jsonify({
        'success': True,
        'data': result['data'],
        'message': 'Comment added'
    }), 201


@comments_bp.route('/api/social/comments/post/<post_id>', methods=['GET'])
@token_required
@require_feature('comments')
def get_post_comments(post_id: str):
    """
    Get comments for a post

    Feature Flag: comments
    Auth: Required

    Query Params:
        page (int): Page number
        per_page (int): Items per page (max: 100)
        sort (str): 'newest', 'oldest', 'most_liked' (default: newest)

    Returns:
        200: List of comments with threading
    """
    from app.social.engagement.comments import CommentsService

    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    sort = request.args.get('sort', 'newest')

    comments = CommentsService.get_post_comments(
        post_id=post_id,
        page=page,
        per_page=per_page,
        sort=sort
    )

    return jsonify({
        'success': True,
        'data': comments,
        'meta': {
            'page': page,
            'per_page': per_page,
            'sort': sort
        }
    }), 200


@comments_bp.route('/api/social/comments/<comment_id>', methods=['PUT'])
@token_required
@require_feature('comments')
def update_comment(comment_id: str):
    """
    Update comment

    Feature Flag: comments
    Auth: Required (must be comment owner)

    Body:
        content (str): Updated content

    Returns:
        200: Comment updated
        403: Not comment owner
        404: Comment not found
    """
    from app.social.engagement.comments import CommentsService

    user_id = g.user_id
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_INPUT',
                'message': 'Comment content cannot be empty'
            }
        }), 400

    result = CommentsService.update_comment(
        comment_id=comment_id,
        user_id=user_id,
        content=content
    )

    if not result['success']:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 404

    return jsonify({
        'success': True,
        'data': result['data'],
        'message': 'Comment updated'
    }), 200


@comments_bp.route('/api/social/comments/<comment_id>', methods=['DELETE'])
@token_required
@require_feature('comments')
def delete_comment(comment_id: str):
    """
    Delete comment (soft delete)

    Feature Flag: comments
    Auth: Required (must be comment owner)

    Returns:
        200: Comment deleted
        403: Not comment owner
        404: Comment not found
    """
    from app.social.engagement.comments import CommentsService

    user_id = g.user_id

    success = CommentsService.delete_comment(
        comment_id=comment_id,
        user_id=user_id
    )

    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Comment not found or no permission'
            }
        }), 404

    return jsonify({
        'success': True,
        'message': 'Comment deleted'
    }), 200


@comments_bp.route('/api/social/comments/<parent_comment_id>/reply', methods=['POST'])
@token_required
@require_feature('comments')
def reply_to_comment(parent_comment_id: str):
    """
    Reply to a comment (max depth: 2)

    Feature Flag: comments
    Auth: Required

    Body:
        content (str): Reply text

    Returns:
        201: Reply created
        400: Max thread depth reached or invalid input
        404: Parent comment not found
    """
    from app.social.engagement.comments import CommentsService

    user_id = g.user_id
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_INPUT',
                'message': 'Reply content cannot be empty'
            }
        }), 400

    result = CommentsService.reply_to_comment(
        user_id=user_id,
        parent_comment_id=parent_comment_id,
        content=content
    )

    if not result['success']:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 400 if result['error']['code'] == 'MAX_DEPTH_REACHED' else 404

    return jsonify({
        'success': True,
        'data': result['data'],
        'message': 'Reply added'
    }), 201
