"""
Social Feed API Endpoints

Feature Flag: feed_system (DISABLED by default)
All endpoints protected with @require_feature('feed_system')

Endpoints:
- GET /api/social/feed           - Get personalized feed
- GET /api/social/feed/following - Get chronological feed from followed users
- GET /api/social/feed/trending  - Get trending content
"""

from flask import Blueprint, request, jsonify, g
from app.core.feature_flags import require_feature
from app.middleware.auth import token_required

feed_bp = Blueprint('social_feed', __name__)


@feed_bp.route('/api/social/feed', methods=['GET'])
@token_required
@require_feature('feed_system')
def get_personalized_feed():
    """
    Get personalized algorithmic feed

    Feature Flag: feed_system (must be enabled)
    Auth: Required

    Query Params:
        page (int): Page number (default: 1)
        per_page (int): Posts per page (default: 20, max: 50)
        algorithm (str): 'personalized', 'chronological' (default: personalized)

    Returns:
        200: Feed with posts
        403: Feature not available
    """
    from app.social.feed.feed_generator import FeedGenerator

    user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 50)
    algorithm = request.args.get('algorithm', 'personalized')

    feed = FeedGenerator.generate_feed(
        user_id=user_id,
        algorithm=algorithm,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'success': True,
        'data': feed,
        'meta': {
            'algorithm': algorithm,
            'page': page,
            'per_page': per_page,
            'disclosure': 'This feed is ranked based on your interests and engagement.' if algorithm == 'personalized' else 'This feed shows posts in chronological order.'
        }
    }), 200


@feed_bp.route('/api/social/feed/following', methods=['GET'])
@token_required
@require_feature('feed_system')
def get_following_feed():
    """
    Get chronological feed from followed users

    Feature Flag: feed_system
    Auth: Required

    Query Params:
        page (int): Page number
        per_page (int): Posts per page

    Returns:
        200: Chronological feed
    """
    from app.social.feed.chronological_feed import ChronologicalFeed

    user_id = g.user_id
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 50)

    feed = ChronologicalFeed.generate(
        user_id=user_id,
        page=page,
        per_page=per_page
    )

    return jsonify({
        'success': True,
        'data': feed,
        'meta': {
            'algorithm': 'chronological',
            'page': page,
            'per_page': per_page
        }
    }), 200


@feed_bp.route('/api/social/feed/trending', methods=['GET'])
@token_required
@require_feature('trending_discovery')
def get_trending_feed():
    """
    Get trending content

    Feature Flag: trending_discovery (separate flag)
    Auth: Required

    Query Params:
        timeframe (str): '24h', '7d', '30d' (default: 24h)
        category (str): Optional category filter

    Returns:
        200: Trending posts
    """
    from app.social.discovery.trending import TrendingDiscovery

    user_id = g.user_id
    timeframe = request.args.get('timeframe', '24h')
    category = request.args.get('category')

    trending = TrendingDiscovery.get_trending(
        user_id=user_id,
        timeframe=timeframe,
        category=category
    )

    return jsonify({
        'success': True,
        'data': trending,
        'meta': {
            'timeframe': timeframe,
            'category': category
        }
    }), 200
