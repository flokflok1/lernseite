"""
Unit Tests for Feature-Based Authorization System

Tests:
- FeatureService core methods
- Feature metadata retrieval and caching
- User feature availability calculation
- Feature access control (has_access_feature)
- Granular feature permissions
- Context-filtered features
- Cache invalidation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.application.services.system.features.service import FeatureService
from app.infrastructure.cache.service import CacheService


class TestFeatureServiceMetadata:
    """Tests for feature metadata retrieval."""

    @patch('app.application.services.system.features.service.FeatureRepository')
    @patch('app.application.services.system.features.service.CacheService')
    def test_get_feature_metadata_found(self, mock_cache, mock_repo):
        """Test retrieving metadata for existing feature."""
        # Setup
        mock_cache.cache_get.return_value = None
        mock_repo.find_by_code.return_value = {
            'feature_code': 'code_sandbox',
            'feature_name': 'Code Sandbox',
            'description': 'Isolated code execution',
            'category': 'it_environments',
            'icon': 'code',
            'requires_infrastructure': True,
            'requires_external_service': False
        }

        # Execute
        result = FeatureService.get_feature_metadata('code_sandbox')

        # Assert
        assert result is not None
        assert result['feature_code'] == 'code_sandbox'
        assert result['feature_name'] == 'Code Sandbox'
        assert result['category'] == 'it_environments'

        # Verify cache was checked and set
        mock_cache.cache_get.assert_called_once()
        mock_cache.cache_set.assert_called_once()

    @patch('app.application.services.system.features.service.FeatureRepository')
    @patch('app.application.services.system.features.service.CacheService')
    def test_get_feature_metadata_not_found(self, mock_cache, mock_repo):
        """Test retrieving metadata for nonexistent feature."""
        # Setup
        mock_cache.cache_get.return_value = None
        mock_repo.find_by_code.return_value = None

        # Execute
        result = FeatureService.get_feature_metadata('nonexistent_feature')

        # Assert
        assert result is None
        mock_cache.cache_set.assert_not_called()

    @patch('app.application.services.system.features.service.FeatureRepository')
    @patch('app.application.services.system.features.service.CacheService')
    def test_get_feature_metadata_from_cache(self, mock_cache, mock_repo):
        """Test retrieving feature metadata from cache."""
        # Setup
        cached_metadata = {
            'feature_code': 'ai_studio',
            'feature_name': 'AI Studio',
            'category': 'ai'
        }
        mock_cache.cache_get.return_value = cached_metadata

        # Execute
        result = FeatureService.get_feature_metadata('ai_studio')

        # Assert
        assert result == cached_metadata
        mock_repo.find_by_code.assert_not_called()  # Should not query DB
        mock_cache.cache_set.assert_not_called()    # Should not set (already in cache)

    @patch('app.application.services.system.features.service.FeatureRepository')
    @patch('app.application.services.system.features.service.CacheService')
    def test_get_feature_metadata_error_handling(self, mock_cache, mock_repo):
        """Test error handling in metadata retrieval."""
        # Setup
        mock_cache.cache_get.return_value = None
        mock_repo.find_by_code.side_effect = Exception("Database error")

        # Execute
        result = FeatureService.get_feature_metadata('code_sandbox')

        # Assert
        assert result is None  # Should return None on error


class TestFeatureServiceAvailableFeatures:
    """Tests for getting available features for user."""

    @patch('app.application.services.system.features.service.get_connection')
    @patch('app.application.services.system.features.service.FeatureRepository')
    @patch('app.application.services.system.features.service.CacheService')
    @patch('app.application.services.system.features.service.UserRepository')
    def test_get_available_features_success(self, mock_user_repo, mock_cache, mock_feature_repo, mock_get_connection):
        """Test getting available features for user."""
        # Setup
        user_id = 'user-123'
        mock_cache.cache_get.return_value = None

        # Setup context manager mock for database connection
        mock_conn = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        # Mock UserRepository.find_by_id as an instance method
        mock_user_instance = mock_user_repo.return_value
        mock_user_instance.find_by_id.return_value = {
            'user_id': user_id,
            'role_id': 1,
            'organisation_id': 'org-456'
        }

        role_features = [
            {'feature_code': 'code_sandbox', 'access_level': 'execute'},
            {'feature_code': 'learning_journal', 'access_level': 'view'}
        ]
        org_features = [
            {'feature_code': 'ai_studio', 'access_level': 'execute'}
        ]

        mock_feature_instance = mock_feature_repo.return_value
        mock_feature_instance.get_user_group_features.return_value = role_features
        mock_feature_instance.get_org_subscribed_features.return_value = org_features

        # Execute
        result = FeatureService.get_available_features(user_id)

        # Assert
        assert len(result) == 3
        feature_codes = {f['feature_code'] for f in result}
        assert feature_codes == {'code_sandbox', 'learning_journal', 'ai_studio'}
        mock_cache.cache_set.assert_called_once()

    @patch('app.application.services.system.features.service.get_connection')
    @patch('app.application.services.system.features.service.FeatureRepository')
    @patch('app.application.services.system.features.service.CacheService')
    @patch('app.application.services.system.features.service.UserRepository')
    def test_get_available_features_deduplication(self, mock_user_repo, mock_cache, mock_feature_repo, mock_get_connection):
        """Test that duplicate features are deduplicated."""
        # Setup
        user_id = 'user-789'
        mock_cache.cache_get.return_value = None

        # Setup context manager mock for database connection
        mock_conn = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        mock_user_instance = mock_user_repo.return_value
        mock_user_instance.find_by_id.return_value = {
            'user_id': user_id,
            'role_id': 2,
            'organisation_id': 'org-789'
        }

        # Both role and org have same feature
        role_features = [
            {'feature_code': 'code_sandbox', 'access_level': 'execute', 'from': 'role'}
        ]
        org_features = [
            {'feature_code': 'code_sandbox', 'access_level': 'execute', 'from': 'org'}
        ]

        mock_feature_instance = mock_feature_repo.return_value
        mock_feature_instance.get_user_group_features.return_value = role_features
        mock_feature_instance.get_org_subscribed_features.return_value = org_features

        # Execute
        result = FeatureService.get_available_features(user_id)

        # Assert
        assert len(result) == 1  # Deduplicated
        assert result[0]['feature_code'] == 'code_sandbox'

    @patch('app.application.services.system.features.service.get_connection')
    @patch('app.application.services.system.features.service.CacheService')
    @patch('app.application.services.system.features.service.UserRepository')
    def test_get_available_features_user_not_found(self, mock_user_repo, mock_cache, mock_get_connection):
        """Test handling when user not found."""
        # Setup
        mock_cache.cache_get.return_value = None

        # Setup context manager mock for database connection
        mock_conn = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__exit__.return_value = None

        mock_user_instance = mock_user_repo.return_value
        mock_user_instance.find_by_id.return_value = None

        # Execute
        result = FeatureService.get_available_features('nonexistent-user')

        # Assert
        assert result == []

    @patch('app.application.services.system.features.service.CacheService')
    def test_get_available_features_from_cache(self, mock_cache):
        """Test retrieving available features from cache."""
        # Setup
        user_id = 'user-999'
        cached_features = [
            {'feature_code': 'code_sandbox', 'access_level': 'execute'}
        ]
        mock_cache.cache_get.return_value = cached_features

        # Execute
        result = FeatureService.get_available_features(user_id)

        # Assert
        assert result == cached_features
        # Cache hit means no DB calls should be made


class TestFeatureServiceCanAccessFeature:
    """Tests for feature access control."""

    @patch('app.application.services.system.features.service.CacheService')
    @patch.object(FeatureService, 'get_available_features')
    def test_can_access_feature_allowed(self, mock_get_available, mock_cache):
        """Test user can access feature."""
        # Setup
        mock_cache.cache_get.return_value = None
        features = [
            {'feature_code': 'code_sandbox'},
            {'feature_code': 'learning_journal'}
        ]
        mock_get_available.return_value = features

        # Execute
        result = FeatureService.can_access_feature('user-123', 'code_sandbox')

        # Assert
        assert result is True
        mock_cache.cache_set.assert_called_once()

    @patch('app.application.services.system.features.service.CacheService')
    @patch.object(FeatureService, 'get_available_features')
    def test_can_access_feature_denied(self, mock_get_available, mock_cache):
        """Test user cannot access feature."""
        # Setup
        mock_cache.cache_get.return_value = None
        features = [{'feature_code': 'learning_journal'}]
        mock_get_available.return_value = features

        # Execute
        result = FeatureService.can_access_feature('user-456', 'code_sandbox')

        # Assert
        assert result is False
        mock_cache.cache_set.assert_called_once()

    @patch('app.application.services.system.features.service.CacheService')
    def test_can_access_feature_from_cache(self, mock_cache):
        """Test feature access from cache."""
        # Setup
        mock_cache.cache_get.return_value = True

        # Execute
        from app.application.services.system.features.service import FeatureService
        result = FeatureService.can_access_feature('user-789', 'ai_studio')

        # Assert
        assert result is True


class TestFeatureServiceContextFiltering:
    """Tests for context-filtered features."""

    @patch.object(FeatureService, 'get_available_features')
    def test_get_user_context_features(self, mock_get_available):
        """Test filtering features by user context."""
        # Setup
        all_features = [
            {'feature_code': 'code_sandbox', 'category': 'it_environments'},
            {'feature_code': 'ai_studio', 'category': 'ai'},
            {'feature_code': 'learning_journal', 'category': 'learning_paths'},
            {'feature_code': 'whiteboard', 'category': 'collaboration'}
        ]
        mock_get_available.return_value = all_features

        # Execute
        result = FeatureService.get_user_context_features('user-123', context='user')

        # Assert - should include learning_paths, collaboration, audio, gamification, tutor, visualization
        feature_categories = {f.get('category') for f in result}
        assert 'learning_paths' in feature_categories
        assert 'collaboration' in feature_categories

    @patch.object(FeatureService, 'get_available_features')
    def test_get_admin_context_features(self, mock_get_available):
        """Test filtering features by admin context."""
        # Setup
        all_features = [
            {'feature_code': 'course_management', 'category': 'learning_paths'},
            {'feature_code': 'user_management', 'category': 'collaboration'},
            {'feature_code': 'learning_journal', 'category': 'learning_paths'}
        ]
        mock_get_available.return_value = all_features

        # Execute
        result = FeatureService.get_user_context_features('user-456', context='admin')

        # Assert
        assert len(result) > 0

    @patch.object(FeatureService, 'get_available_features')
    def test_get_community_context_features(self, mock_get_available):
        """Test filtering features by community context."""
        # Setup
        all_features = [
            {'feature_code': 'posts', 'category': 'collaboration'},
            {'feature_code': 'messages', 'category': 'collaboration'},
            {'feature_code': 'charts', 'category': 'visualization'},
            {'feature_code': 'ai_studio', 'category': 'ai'}
        ]
        mock_get_available.return_value = all_features

        # Execute
        result = FeatureService.get_user_context_features('user-789', context='community')

        # Assert
        feature_categories = {f.get('category') for f in result}
        assert 'collaboration' in feature_categories
        assert 'visualization' in feature_categories


class TestFeatureServiceCacheInvalidation:
    """Tests for cache invalidation."""

    @patch('app.application.services.system.features.service.CacheService')
    def test_invalidate_user_cache(self, mock_cache):
        """Test cache invalidation for user."""
        # Execute
        FeatureService.invalidate_user_cache('user-123')

        # Assert
        mock_cache.cache_delete_pattern.assert_called_once()
        call_args = mock_cache.cache_delete_pattern.call_args[0][0]
        assert 'user-123' in call_args


class TestFeatureServiceSummary:
    """Tests for feature summary."""

    @patch('app.application.services.system.features.service.FeatureRepository')
    def test_get_all_features_summary(self, mock_repo):
        """Test getting summary of all features."""
        # Setup
        features = [
            {'feature_code': 'code_sandbox', 'feature_name': 'Code Sandbox', 'category': 'it_environments'},
            {'feature_code': 'ai_studio', 'feature_name': 'AI Studio', 'category': 'ai'},
            {'feature_code': 'learning_journal', 'feature_name': 'Learning Journal', 'category': 'learning_paths'},
            {'feature_code': 'whiteboard', 'feature_name': 'Whiteboard', 'category': 'collaboration'}
        ]
        mock_repo.list_all_features.return_value = features

        # Execute
        result = FeatureService.get_all_features_summary()

        # Assert
        assert result['total_features'] == 4
        assert result['by_category']['it_environments'] == 1
        assert result['by_category']['ai'] == 1
        assert result['by_category']['learning_paths'] == 1
        assert result['by_category']['collaboration'] == 1
        assert len(result['features']) == 4

    @patch('app.application.services.system.features.service.FeatureRepository')
    def test_get_all_features_summary_error_handling(self, mock_repo):
        """Test error handling in features summary."""
        # Setup
        mock_repo.list_all_features.side_effect = Exception("Database error")

        # Execute
        result = FeatureService.get_all_features_summary()

        # Assert
        assert result['total_features'] == 0
        assert result['by_category'] == {}
        assert result['features'] == []
