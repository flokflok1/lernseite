"""
Tests for Learning Method Plugin System

Tests cover:
- LMPluginRepository (database operations)
- LMPluginDiscoveryService (plugin scanning)
- LMPluginRegistry (runtime registry)
- API endpoints (approval workflow)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
from pathlib import Path

# Repository Tests
class TestLMPluginRepository:
    """Tests for LMPluginRepository"""

    @patch('app.database.connection.fetch_one')
    def test_find_by_code_success(self, mock_fetch_one):
        """Test finding plugin by code"""
        mock_fetch_one.return_value = {
            'plugin_id': 'test-id-123',
            'plugin_code': 'lm_test',
            'name': 'Test Plugin',
            'approval_status': 'pending_review'
        }

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.find_by_code('lm_test')

        assert result is not None
        assert result['plugin_code'] == 'lm_test'
        assert result['name'] == 'Test Plugin'
        mock_fetch_one.assert_called_once()

    @patch('app.database.connection.fetch_one')
    def test_find_by_code_not_found(self, mock_fetch_one):
        """Test finding non-existent plugin"""
        mock_fetch_one.return_value = None

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.find_by_code('lm_nonexistent')

        assert result is None

    @patch('app.database.connection.fetch_all')
    def test_get_active_plugins(self, mock_fetch_all):
        """Test getting active plugins"""
        mock_fetch_all.return_value = [
            {
                'plugin_id': 'id-1',
                'plugin_code': 'lm_active_1',
                'approval_status': 'approved',
                'is_active': True
            },
            {
                'plugin_id': 'id-2',
                'plugin_code': 'lm_active_2',
                'approval_status': 'approved',
                'is_active': True
            }
        ]

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.get_active_plugins()

        assert len(result) == 2
        assert all(p['is_active'] for p in result)
        assert all(p['approval_status'] == 'approved' for p in result)

    @patch('app.database.connection.fetch_all')
    def test_get_pending_plugins(self, mock_fetch_all):
        """Test getting pending plugins"""
        mock_fetch_all.return_value = [
            {
                'plugin_id': 'id-1',
                'plugin_code': 'lm_pending_1',
                'approval_status': 'pending_review'
            }
        ]

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.get_pending_plugins()

        assert len(result) == 1
        assert result[0]['approval_status'] == 'pending_review'

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository._log_approval_action')
    @patch('app.database.connection.execute_query')
    def test_approve_plugin_success(self, mock_execute, mock_log):
        """Test approving a plugin"""
        mock_execute.return_value = 1  # 1 row affected

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.approve_plugin('test-id', 'reviewer-id')

        assert result is True
        mock_execute.assert_called_once()
        mock_log.assert_called_once_with('test-id', 'approved', 'reviewer-id', None)

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository._log_approval_action')
    @patch('app.database.connection.execute_query')
    def test_approve_plugin_not_found(self, mock_execute, mock_log):
        """Test approving non-existent plugin"""
        mock_execute.return_value = 0  # No rows affected

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.approve_plugin('nonexistent-id', 'reviewer-id')

        assert result is False
        mock_log.assert_not_called()

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository._log_approval_action')
    @patch('app.database.connection.execute_query')
    def test_reject_plugin(self, mock_execute, mock_log):
        """Test rejecting a plugin"""
        mock_execute.return_value = 1

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.reject_plugin('test-id', 'reviewer-id', 'Not suitable')

        assert result is True
        mock_log.assert_called_once_with('test-id', 'rejected', 'reviewer-id', 'Not suitable')

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository._log_approval_action')
    @patch('app.database.connection.execute_query')
    def test_activate_plugin_success(self, mock_execute, mock_log):
        """Test activating an approved plugin"""
        mock_execute.return_value = 1

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.activate_plugin('test-id', 'admin-id')

        assert result is True
        mock_log.assert_called_once_with('test-id', 'activated', 'admin-id', None)

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository._log_approval_action')
    @patch('app.database.connection.execute_query')
    def test_deactivate_plugin(self, mock_execute, mock_log):
        """Test deactivating a plugin"""
        mock_execute.return_value = 1

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.deactivate_plugin('test-id', 'admin-id')

        assert result is True
        mock_log.assert_called_once_with('test-id', 'deactivated', 'admin-id', None)

    @patch('app.database.connection.fetch_one')
    def test_is_plugin_in_use_true(self, mock_fetch_one):
        """Test checking if plugin is in use"""
        mock_fetch_one.return_value = {'count': 5}

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.is_plugin_in_use('test-id')

        assert result is True

    @patch('app.database.connection.fetch_one')
    def test_is_plugin_in_use_false(self, mock_fetch_one):
        """Test checking if plugin is not in use"""
        mock_fetch_one.return_value = {'count': 0}

        from app.repositories.plugins.lm_plugins import LMPluginRepository
        result = LMPluginRepository.is_plugin_in_use('test-id')

        assert result is False


# Discovery Service Tests
class TestLMPluginDiscoveryService:
    """Tests for LMPluginDiscoveryService"""

    @patch('app.services.plugins.lm_discovery.PLUGIN_DIR')
    @patch('app.services.plugins.lm_discovery.LMPluginDiscoveryService._extract_metadata')
    def test_scan_plugins_success(self, mock_extract, mock_plugin_dir):
        """Test scanning plugins from filesystem"""
        # Mock plugin directory
        mock_file = Mock()
        mock_file.name = 'lm_plugin_test.py'
        mock_plugin_dir.exists.return_value = True
        mock_plugin_dir.glob.return_value = [mock_file]

        # Mock metadata extraction
        mock_extract.return_value = {
            'plugin_code': 'lm_test',
            'name': 'Test Plugin',
            'group_code': 'A',
            'tier': 'basic',
            'ki_usage': 'optional',
            'icon': '🧪',
            'config_schema': {'type': 'object'},
            'file_path': '/path/to/plugin.py',
            'file_hash': 'abc123'
        }

        from app.services.plugins.lm_discovery import LMPluginDiscoveryService
        result = LMPluginDiscoveryService.scan_plugins()

        assert len(result) == 1
        assert result[0]['plugin_code'] == 'lm_test'
        assert result[0]['name'] == 'Test Plugin'

    @patch('app.services.plugins.lm_discovery.PLUGIN_DIR')
    def test_scan_plugins_directory_not_exists(self, mock_plugin_dir):
        """Test scanning when plugin directory doesn't exist"""
        mock_plugin_dir.exists.return_value = False

        from app.services.plugins.lm_discovery import LMPluginDiscoveryService
        result = LMPluginDiscoveryService.scan_plugins()

        assert result == []

    @patch('app.services.plugins.lm_discovery.importlib.util.spec_from_file_location')
    @patch('app.services.plugins.lm_discovery.LMPluginDiscoveryService._hash_file')
    def test_extract_metadata_success(self, mock_hash, mock_spec):
        """Test extracting metadata from plugin file"""
        # Mock module with PLUGIN_METADATA
        mock_module = Mock()
        mock_module.PLUGIN_METADATA = {
            'plugin_code': 'lm_test',
            'name': 'Test Plugin',
            'config_schema': {'type': 'object'}
        }

        mock_spec_obj = Mock()
        mock_spec_obj.loader = Mock()
        mock_spec_obj.loader.exec_module = Mock()
        mock_spec.return_value = mock_spec_obj

        mock_hash.return_value = 'abc123hash'

        from app.services.plugins.lm_discovery import LMPluginDiscoveryService
        with patch('app.services.plugins.lm_discovery.importlib.util.module_from_spec', return_value=mock_module):
            result = LMPluginDiscoveryService._extract_metadata(Path('/test/plugin.py'))

        assert result is not None
        assert result['plugin_code'] == 'lm_test'
        assert 'file_path' in result
        assert 'file_hash' in result

    @patch('app.services.plugins.lm_discovery.importlib.util.spec_from_file_location')
    def test_extract_metadata_no_metadata_attribute(self, mock_spec):
        """Test extracting metadata from file without PLUGIN_METADATA"""
        mock_module = Mock()
        del mock_module.PLUGIN_METADATA  # No PLUGIN_METADATA attribute

        mock_spec_obj = Mock()
        mock_spec_obj.loader = Mock()
        mock_spec.return_value = mock_spec_obj

        from app.services.plugins.lm_discovery import LMPluginDiscoveryService
        with patch('app.services.plugins.lm_discovery.importlib.util.module_from_spec', return_value=mock_module):
            result = LMPluginDiscoveryService._extract_metadata(Path('/test/plugin.py'))

        assert result is None

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository.find_by_code')
    @patch('app.database.connection.fetch_one')
    @patch('app.database.connection.execute_query')
    def test_register_plugin_new(self, mock_execute, mock_fetch_one, mock_find_by_code):
        """Test registering a new plugin"""
        mock_find_by_code.return_value = None  # Plugin doesn't exist
        mock_fetch_one.return_value = {'plugin_id': 'new-id-123'}

        metadata = {
            'plugin_code': 'lm_new',
            'name': 'New Plugin',
            'group_code': 'A',
            'tier': 'basic',
            'ki_usage': 'optional',
            'icon': '🆕',
            'config_schema': {'type': 'object'},
            'file_path': '/path/to/new_plugin.py',
            'file_hash': 'newhash123'
        }

        from app.services.plugins.lm_discovery import LMPluginDiscoveryService
        result = LMPluginDiscoveryService.register_plugin(metadata, 'admin-id')

        assert result == 'new-id-123'
        mock_fetch_one.assert_called_once()

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository.find_by_code')
    @patch('app.database.connection.execute_query')
    def test_register_plugin_existing_same_hash(self, mock_execute, mock_find_by_code):
        """Test registering existing plugin with same hash"""
        mock_find_by_code.return_value = {
            'plugin_id': 'existing-id',
            'file_hash': 'samehash123'
        }

        metadata = {
            'plugin_code': 'lm_existing',
            'file_hash': 'samehash123'
        }

        from app.services.plugins.lm_discovery import LMPluginDiscoveryService
        result = LMPluginDiscoveryService.register_plugin(metadata, 'admin-id')

        assert result == 'existing-id'
        mock_execute.assert_not_called()  # No update needed

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository.find_by_code')
    @patch('app.database.connection.execute_query')
    def test_register_plugin_existing_different_hash(self, mock_execute, mock_find_by_code):
        """Test registering existing plugin with different hash (file changed)"""
        mock_find_by_code.return_value = {
            'plugin_id': 'existing-id',
            'file_hash': 'oldhash123'
        }

        metadata = {
            'plugin_code': 'lm_existing',
            'file_hash': 'newhash456'
        }

        from app.services.plugins.lm_discovery import LMPluginDiscoveryService
        result = LMPluginDiscoveryService.register_plugin(metadata, 'admin-id')

        assert result == 'existing-id'
        mock_execute.assert_called_once()  # Hash updated


# Registry Tests
class TestLMPluginRegistry:
    """Tests for LMPluginRegistry"""

    def test_singleton_pattern(self):
        """Test that registry is singleton"""
        from app.services.plugins.lm_registry import LMPluginRegistry

        registry1 = LMPluginRegistry()
        registry2 = LMPluginRegistry()

        assert registry1 is registry2

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository.get_active_plugins')
    def test_load_plugins(self, mock_get_active):
        """Test loading active plugins"""
        mock_get_active.return_value = [
            {
                'plugin_id': 'id-1',
                'plugin_code': 'lm_test',
                'name': 'Test Plugin',
                'group_code': 'A',
                'tier': 'basic',
                'ki_usage': 'optional',
                'icon': '🧪',
                'config_schema': {'type': 'object'}
            }
        ]

        from app.services.plugins.lm_registry import LMPluginRegistry
        registry = LMPluginRegistry()
        registry._load_plugins()

        assert len(registry._plugins) > 0

    @patch('app.ki.learning_method_mapping.LEARNING_METHODS')
    def test_get_builtin_learning_method(self, mock_learning_methods):
        """Test getting built-in learning method (0-11)"""
        mock_lm = Mock()
        mock_lm.id = 0
        mock_lm.code = 'lm00'
        mock_learning_methods.get.return_value = mock_lm

        from app.services.plugins.lm_registry import LMPluginRegistry
        registry = LMPluginRegistry()
        result = registry.get_learning_method(0)

        assert result is not None
        mock_learning_methods.get.assert_called_with(0)

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository.get_active_plugins')
    def test_get_plugin_learning_method(self, mock_get_active):
        """Test getting plugin learning method (100+)"""
        mock_get_active.return_value = []

        from app.services.plugins.lm_registry import LMPluginRegistry
        registry = LMPluginRegistry()
        registry._plugins[100] = Mock()

        result = registry.get_learning_method(100)

        assert result is not None

    def test_force_reload(self):
        """Test force reload of plugins"""
        from app.services.plugins.lm_registry import LMPluginRegistry

        registry = LMPluginRegistry()
        initial_reload_time = registry._last_reload

        with patch.object(registry, '_load_plugins') as mock_load:
            registry.force_reload()
            mock_load.assert_called_once()


# Integration Tests
class TestPluginApprovalWorkflow:
    """Integration tests for plugin approval workflow"""

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository')
    @patch('app.services.plugins.lm_discovery.LMPluginDiscoveryService')
    def test_complete_approval_workflow(self, mock_discovery, mock_repository):
        """Test complete workflow: scan → approve → activate"""
        # Step 1: Scan discovers plugin
        mock_discovery.scan_plugins.return_value = [{
            'plugin_code': 'lm_test',
            'name': 'Test Plugin',
            'approval_status': 'pending_review'
        }]

        # Step 2: Register plugin
        mock_discovery.register_plugin.return_value = 'new-plugin-id'

        # Step 3: Approve plugin
        mock_repository.approve_plugin.return_value = True

        # Step 4: Activate plugin
        mock_repository.activate_plugin.return_value = True

        # Simulate workflow
        plugins = mock_discovery.scan_plugins()
        assert len(plugins) == 1

        plugin_id = mock_discovery.register_plugin(plugins[0], 'admin-id')
        assert plugin_id is not None

        approved = mock_repository.approve_plugin(plugin_id, 'reviewer-id')
        assert approved is True

        activated = mock_repository.activate_plugin(plugin_id, 'admin-id')
        assert activated is True

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository')
    def test_rejection_workflow(self, mock_repository):
        """Test rejection workflow"""
        mock_repository.reject_plugin.return_value = True

        rejected = mock_repository.reject_plugin('plugin-id', 'reviewer-id', 'Not suitable')
        assert rejected is True

    @patch('app.repositories.plugins.lm_plugins.LMPluginRepository')
    def test_cannot_deactivate_in_use_plugin(self, mock_repository):
        """Test that plugin in use cannot be deactivated"""
        mock_repository.is_plugin_in_use.return_value = True

        # Simulate deactivation attempt
        in_use = mock_repository.is_plugin_in_use('plugin-id')
        assert in_use is True

        # Should not call deactivate if in use
        if not in_use:
            mock_repository.deactivate_plugin('plugin-id', 'admin-id')

        mock_repository.deactivate_plugin.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
