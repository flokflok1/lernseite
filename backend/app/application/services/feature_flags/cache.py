"""
LernsystemX Feature Configuration Cache Service

Cache layer for Enterprise Feature Configuration System:
- Redis cache management
- Cache invalidation triggers
- Real-time updates via Pub/Sub
- Cache status tracking

Phase 2 - Core Service Layer (Part 2)
Handles all caching and real-time synchronization for feature configs.

For core permission logic, see: feature_configuration_service.py
For rollout operations, see: feature_configuration_rollout.py
For A/B test operations, see: feature_configuration_ab_test.py
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import redis
from functools import wraps

from app.core.bootstrap.config import Config
from app.infrastructure.persistence.database.connection import get_db_connection
from app.infrastructure.persistence.repositories.feature_configuration_part2 import FeatureCacheStatusRepository

logger = logging.getLogger(__name__)


class FeatureConfigurationCacheService:
    """
    Cache service for feature configurations.

    Manages Redis caching with:
    - Automatic cache invalidation on config changes
    - Pub/Sub real-time updates
    - Cache health monitoring
    - TTL-based expiration
    """

    # Cache TTL constants (in seconds)
    FEATURE_CACHE_TTL = 300  # 5 minutes
    FEATURE_LIST_CACHE_TTL = 600  # 10 minutes
    USER_FEATURES_CACHE_TTL = 120  # 2 minutes

    # Redis key prefixes
    FEATURE_KEY_PREFIX = "feature:"
    USER_FEATURES_KEY_PREFIX = "user_features:"
    ROLLOUT_KEY_PREFIX = "rollout:"
    AB_TEST_KEY_PREFIX = "ab_test:"

    # Pub/Sub channels
    FEATURE_UPDATE_CHANNEL = "feature_updates"
    CACHE_INVALIDATION_CHANNEL = "cache_invalidation"

    _redis_client: Optional[redis.Redis] = None

    @classmethod
    def init_redis(cls, config: Config) -> None:
        """
        Initialize Redis connection.

        Args:
            config: Application configuration
        """
        cls._redis_client = redis.from_url(
            config.REDIS_URL,
            decode_responses=True
        )
        logger.info("Redis cache initialized for feature configurations")

    @classmethod
    def _get_redis(cls) -> redis.Redis:
        """Get Redis client."""
        if cls._redis_client is None:
            raise RuntimeError("Redis client not initialized. Call init_redis() first.")
        return cls._redis_client

    # ==================== CACHE OPERATIONS ====================

    @staticmethod
    def get_feature(feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Get feature configuration from cache.

        Args:
            feature_name: Feature name

        Returns:
            Feature config dict or None if not cached

        Example:
            feature = FeatureConfigurationCacheService.get_feature("ai_tutor")
            if feature:
                logger.info(f"Cache hit for {feature_name}")
        """
        redis_client = FeatureConfigurationCacheService._get_redis()
        cache_key = f"{FeatureConfigurationCacheService.FEATURE_KEY_PREFIX}{feature_name}"

        try:
            cached_value = redis_client.get(cache_key)
            if cached_value:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached_value)
        except Exception as e:
            logger.error(f"Error retrieving cache for {cache_key}: {e}")

        return None

    @staticmethod
    def set_feature(
        feature_name: str,
        feature_data: Dict[str, Any],
        ttl: int = FEATURE_CACHE_TTL
    ) -> None:
        """
        Set feature configuration in cache.

        Args:
            feature_name: Feature name
            feature_data: Feature configuration data
            ttl: Time to live in seconds (default: 5 minutes)

        Example:
            FeatureConfigurationCacheService.set_feature(
                "ai_tutor",
                {'id': 1, 'is_enabled': True, ...},
                ttl=300
            )
        """
        redis_client = FeatureConfigurationCacheService._get_redis()
        cache_key = f"{FeatureConfigurationCacheService.FEATURE_KEY_PREFIX}{feature_name}"

        try:
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(feature_data)
            )
            logger.debug(f"Cache set: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Error setting cache for {cache_key}: {e}")

    @staticmethod
    def delete_feature(feature_name: str) -> None:
        """
        Delete feature configuration from cache.

        Args:
            feature_name: Feature name
        """
        redis_client = FeatureConfigurationCacheService._get_redis()
        cache_key = f"{FeatureConfigurationCacheService.FEATURE_KEY_PREFIX}{feature_name}"

        try:
            redis_client.delete(cache_key)
            logger.debug(f"Cache deleted: {cache_key}")
        except Exception as e:
            logger.error(f"Error deleting cache for {cache_key}: {e}")

    @staticmethod
    def invalidate_feature(feature_name: str) -> None:
        """
        Invalidate feature cache and publish update event.

        Args:
            feature_name: Feature name to invalidate
        """
        # Delete from cache
        FeatureConfigurationCacheService.delete_feature(feature_name)

        # Update cache status in database
        with get_db_connection() as conn:
            cache_repo = FeatureCacheStatusRepository()
            cache_repo.update_status(feature_name)

        # Publish Pub/Sub event for real-time updates
        FeatureConfigurationCacheService.publish_update(
            feature_name,
            event_type="invalidated"
        )

        logger.info(f"Feature cache invalidated: {feature_name}")

    @staticmethod
    def invalidate_user_features(user_id: str) -> None:
        """
        Invalidate user's feature list cache.

        Args:
            user_id: User ID
        """
        redis_client = FeatureConfigurationCacheService._get_redis()

        # Delete all user features caches for this user
        # Pattern: user_features:{user_id}:*
        pattern = f"{FeatureConfigurationCacheService.USER_FEATURES_KEY_PREFIX}{user_id}:*"

        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.debug(f"Deleted {len(keys)} user feature caches for user {user_id}")
        except Exception as e:
            logger.error(f"Error invalidating user features for {user_id}: {e}")

    # ==================== PUB/SUB OPERATIONS ====================

    @staticmethod
    def publish_update(
        feature_name: str,
        event_type: str = "updated",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Publish feature update event via Redis Pub/Sub.

        Args:
            feature_name: Feature name
            event_type: Type of event (updated, enabled, disabled, invalidated)
            details: Optional event details

        Example:
            FeatureConfigurationCacheService.publish_update(
                "ai_tutor",
                event_type="enabled",
                details={'timestamp': datetime.utcnow().isoformat()}
            )
        """
        redis_client = FeatureConfigurationCacheService._get_redis()

        message = {
            'feature_name': feature_name,
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }

        try:
            redis_client.publish(
                FeatureConfigurationCacheService.FEATURE_UPDATE_CHANNEL,
                json.dumps(message)
            )
            logger.debug(f"Published feature update: {feature_name} ({event_type})")
        except Exception as e:
            logger.error(f"Error publishing update for {feature_name}: {e}")

    @staticmethod
    def subscribe_to_updates(callback) -> None:
        """
        Subscribe to feature update events (for background workers).

        Args:
            callback: Function to call when update received
                     Signature: callback(message: Dict[str, Any]) -> None

        Example:
            def handle_update(message):
                logger.info(f"Received update: {message['feature_name']}")

            FeatureConfigurationCacheService.subscribe_to_updates(handle_update)
        """
        redis_client = FeatureConfigurationCacheService._get_redis()
        pubsub = redis_client.pubsub()

        pubsub.subscribe(FeatureConfigurationCacheService.FEATURE_UPDATE_CHANNEL)

        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        callback(data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in Pub/Sub message: {message['data']}")
        except Exception as e:
            logger.error(f"Error in Pub/Sub subscription: {e}")
        finally:
            pubsub.close()

    # ==================== CACHE DECORATORS ====================

    @staticmethod
    def cached_feature(ttl: int = FEATURE_CACHE_TTL):
        """
        Decorator to cache function result by feature name.

        Args:
            ttl: Cache TTL in seconds

        Example:
            @FeatureConfigurationCacheService.cached_feature(ttl=300)
            def get_feature_config(feature_name: str) -> Dict:
                # Load from database
                return feature_repo.find_by_name(feature_name)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(feature_name: str, *args, **kwargs):
                # Try cache first
                cached = FeatureConfigurationCacheService.get_feature(feature_name)
                if cached:
                    return cached

                # Call function
                result = func(feature_name, *args, **kwargs)

                # Store in cache
                if result:
                    FeatureConfigurationCacheService.set_feature(
                        feature_name,
                        result,
                        ttl=ttl
                    )

                return result
            return wrapper
        return decorator

    # ==================== CACHE HEALTH ====================

    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache stats including hit rates, size, memory usage
        """
        redis_client = FeatureConfigurationCacheService._get_redis()

        try:
            info = redis_client.info('memory')
            feature_keys = redis_client.keys(
                f"{FeatureConfigurationCacheService.FEATURE_KEY_PREFIX}*"
            )
            user_keys = redis_client.keys(
                f"{FeatureConfigurationCacheService.USER_FEATURES_KEY_PREFIX}*"
            )

            return {
                'status': 'healthy',
                'memory_used_mb': info.get('used_memory_mb', 0),
                'memory_peak_mb': info.get('used_memory_peak_mb', 0),
                'feature_cache_keys': len(feature_keys),
                'user_cache_keys': len(user_keys),
                'total_keys': len(feature_keys) + len(user_keys)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    @staticmethod
    def clear_all_caches() -> None:
        """
        Clear all feature configuration caches.

        WARNING: This is destructive and should only be used in emergencies.
        Use with caution in production!
        """
        redis_client = FeatureConfigurationCacheService._get_redis()

        patterns = [
            f"{FeatureConfigurationCacheService.FEATURE_KEY_PREFIX}*",
            f"{FeatureConfigurationCacheService.USER_FEATURES_KEY_PREFIX}*",
            f"{FeatureConfigurationCacheService.ROLLOUT_KEY_PREFIX}*",
            f"{FeatureConfigurationCacheService.AB_TEST_KEY_PREFIX}*"
        ]

        total_deleted = 0
        for pattern in patterns:
            try:
                keys = redis_client.keys(pattern)
                if keys:
                    deleted = redis_client.delete(*keys)
                    total_deleted += deleted
                    logger.info(f"Deleted {deleted} keys matching pattern {pattern}")
            except Exception as e:
                logger.error(f"Error clearing cache pattern {pattern}: {e}")

        logger.warning(f"Total cache keys cleared: {total_deleted}")
