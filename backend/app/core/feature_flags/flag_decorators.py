"""
Feature Flag Decorators

Provides @require_feature decorator for protecting endpoints
with feature flag checks.

Usage:
    from app.core.feature_flags.flag_decorators import require_feature

    @require_feature('user_posts')
    def create_post():
        '''Only available if user_posts feature is enabled'''
        ...

    @require_feature('feed_system', user_segment='beta')
    def get_feed():
        '''Beta users only'''
        ...
"""

from functools import wraps
from flask import jsonify, g
from app.core.feature_flags.flag_manager import FeatureFlagManager


def require_feature(feature_name: str, user_segment: str = None, organisation: bool = False):
    """
    Decorator to check if feature is enabled

    Args:
        feature_name: Name of feature flag (e.g., 'user_posts')
        user_segment: Optional segment requirement (e.g., 'beta', 'premium')
        organisation: If True, check organisation-level flag

    Returns:
        Function decorator that returns 403 if feature is disabled

    Example:
        @require_feature('user_posts')
        def create_post():
            '''Create a post - only if enabled'''
            data = request.get_json()
            post = PostService.create_post(...)
            return jsonify(post), 201

        @require_feature('feed_system', user_segment='beta')
        def get_feed():
            '''Get feed - beta users only'''
            feed = FeedService.generate_feed(...)
            return jsonify(feed), 200
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get flag manager
            flag_manager = FeatureFlagManager()

            # Get context from Flask g object
            user_id = g.get('user_id')
            organisation_id = g.get('organisation_id') if organisation else None

            # Check if feature is enabled
            is_enabled = flag_manager.is_enabled(
                feature_name,
                user_id=user_id,
                organisation_id=organisation_id,
                user_segment=user_segment
            )

            if not is_enabled:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'FEATURE_NOT_AVAILABLE',
                        'message': f'The feature "{feature_name}" is not yet available for your account.',
                        'feature': feature_name
                    }
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def optional_feature(feature_name: str, fallback_function=None):
    """
    Decorator for optional features with fallback

    If feature is disabled, calls fallback_function instead

    Args:
        feature_name: Name of feature flag
        fallback_function: Function to call if feature is disabled

    Example:
        def get_basic_feed():
            return jsonify({'feed': [], 'type': 'basic'})

        @optional_feature('feed_system', fallback_function=get_basic_feed)
        def get_advanced_feed():
            '''Returns advanced feed if enabled, basic feed otherwise'''
            feed = FeedService.generate_advanced_feed(...)
            return jsonify({'feed': feed, 'type': 'advanced'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            flag_manager = FeatureFlagManager()

            user_id = g.get('user_id')
            organisation_id = g.get('organisation_id')

            is_enabled = flag_manager.is_enabled(
                feature_name,
                user_id=user_id,
                organisation_id=organisation_id
            )

            if is_enabled:
                return f(*args, **kwargs)
            elif fallback_function:
                return fallback_function(*args, **kwargs)
            else:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'FEATURE_NOT_AVAILABLE',
                        'message': f'The feature "{feature_name}" is not available.',
                        'feature': feature_name
                    }
                }), 403

        return decorated_function
    return decorator


def feature_gate(feature_name: str):
    """
    Decorator that adds feature flag info to response

    Does NOT block request, just adds metadata

    Args:
        feature_name: Name of feature flag

    Example:
        @feature_gate('analytics')
        def get_analytics():
            '''Returns analytics with feature flag info in response'''
            data = AnalyticsService.get_data()
            return jsonify(data)

        # Response includes: {'data': {...}, 'feature_flags': {'analytics': true}}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            flag_manager = FeatureFlagManager()

            user_id = g.get('user_id')
            organisation_id = g.get('organisation_id')

            is_enabled = flag_manager.is_enabled(
                feature_name,
                user_id=user_id,
                organisation_id=organisation_id
            )

            # Call original function
            response = f(*args, **kwargs)

            # Add feature flag metadata to response
            if isinstance(response, tuple):
                data, status_code = response
                if hasattr(data, 'json'):
                    json_data = data.json
                    if not json_data.get('feature_flags'):
                        json_data['feature_flags'] = {}
                    json_data['feature_flags'][feature_name] = is_enabled
                return data, status_code
            else:
                if hasattr(response, 'json'):
                    json_data = response.json
                    if not json_data.get('feature_flags'):
                        json_data['feature_flags'] = {}
                    json_data['feature_flags'][feature_name] = is_enabled

            return response

        return decorated_function
    return decorator
