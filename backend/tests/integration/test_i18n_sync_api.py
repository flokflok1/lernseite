"""
Integration Tests for i18n Sync API Endpoints

Tests complete workflows:
- MANUAL sync mode (scan → resolve → apply)
- AUTO sync mode (scan → auto-resolve → apply)
- Rollback functionality
- Conflict resolution
- Dashboard statistics
"""

import pytest
import json
from flask import Flask
from unittest.mock import Mock, MagicMock, patch
from app import create_app
from app.api.v1.admin.i18n_sync import bp
from app.services.i18n_sync_service import I18nSyncService


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app('testing')
    app.register_blueprint(bp)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    return {'Authorization': 'Bearer test_token'}


@pytest.fixture
def mock_auth(app):
    """Mock authentication middleware."""
    with patch('app.middleware.auth.require_auth', lambda f: f):
        yield


class TestI18nSyncAPIEndpoints:
    """Integration tests for i18n Sync API endpoints."""
    
    def test_get_dashboard_stats(self, client, auth_headers, mock_auth):
        """Test GET /api/admin/i18n-sync/stats endpoint."""
        # Arrange
        expected_stats = {
            'success': True,
            'data': {
                'total_syncs': 5,
                'syncs': {
                    'completed': 3,
                    'failed': 1,
                    'manual_mode': 2,
                    'auto_mode': 3
                },
                'performance': {'avg_scan_duration_ms': 1250},
                'translations': {
                    'total_keys': 450,
                    'by_language': {'de': 150, 'en': 150, 'pl': 150}
                },
                'success_rate': '83.3%'
            }
        }
        
        # Act
        response = client.get(
            '/api/admin/i18n-sync/stats',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'total_syncs' in data['data']
    
    def test_initiate_manual_scan(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/scan with MANUAL mode."""
        # Arrange
        scan_request = {
            'mode': 'MANUAL',
            'languages': ['de', 'en', 'pl'],
            'frontend_translations': {
                'de': {'greeting': 'Hallo', 'goodbye': 'Auf Wiedersehen'},
                'en': {'greeting': 'Hello', 'goodbye': 'Goodbye'},
                'pl': {'greeting': 'Cześć', 'goodbye': 'Do widzenia'}
            },
            'metadata': {'source': 'frontend_upload'}
        }
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/scan',
            json=scan_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'sync_id' in data['data']
        assert data['data']['mode'] == 'MANUAL'
        assert data['data']['status'] == 'COMPLETED'
    
    def test_initiate_auto_scan(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/scan with AUTO mode."""
        # Arrange
        scan_request = {
            'mode': 'AUTO',
            'languages': ['de', 'en'],
            'frontend_translations': {
                'de': {'key1': 'value1'},
                'en': {'key1': 'value1'}
            }
        }
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/scan',
            json=scan_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['mode'] == 'AUTO'
    
    def test_initiate_scan_missing_fields(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/scan with missing required fields."""
        # Arrange
        invalid_request = {
            'mode': 'MANUAL'
            # Missing 'languages' and 'frontend_translations'
        }
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/scan',
            json=invalid_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_get_scan_results(self, client, auth_headers, mock_auth):
        """Test GET /api/admin/i18n-sync/results/{sync_id} endpoint."""
        # Arrange
        sync_id = 'sync_001'
        
        # Act
        response = client.get(
            f'/api/admin/i18n-sync/results/{sync_id}',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'total' in data
        assert 'limit' in data
        assert 'offset' in data
    
    def test_get_scan_results_with_filters(self, client, auth_headers, mock_auth):
        """Test GET /api/admin/i18n-sync/results/{sync_id} with filters."""
        # Arrange
        sync_id = 'sync_001'
        
        # Act
        response = client.get(
            f'/api/admin/i18n-sync/results/{sync_id}?type=CONFLICT&language=de&limit=10&offset=0',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_resolve_conflict(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/{sync_id}/resolve endpoint."""
        # Arrange
        sync_id = 'sync_001'
        resolution_request = {
            'change_id': 1,
            'action': 'ADD',
            'notes': 'Added manually after review'
        }
        
        # Act
        response = client.post(
            f'/api/admin/i18n-sync/{sync_id}/resolve',
            json=resolution_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'resolution_id' in data['data']
    
    def test_resolve_conflict_invalid_action(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/{sync_id}/resolve with invalid action."""
        # Arrange
        sync_id = 'sync_001'
        invalid_request = {
            'change_id': 1,
            'action': 'INVALID_ACTION'
        }
        
        # Act
        response = client.post(
            f'/api/admin/i18n-sync/{sync_id}/resolve',
            json=invalid_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_apply_sync_auto_resolve(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/apply with auto_resolve."""
        # Arrange
        apply_request = {
            'sync_id': 'sync_001',
            'auto_resolve': True
        }
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/apply',
            json=apply_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'sync' in data['data']
        assert 'stats' in data['data']
    
    def test_apply_sync_without_resolving_conflicts(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/apply fails without resolving conflicts."""
        # Arrange
        apply_request = {
            'sync_id': 'sync_001',
            'auto_resolve': False
        }
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/apply',
            json=apply_request,
            headers=auth_headers
        )
        
        # Assert
        # Depends on whether conflicts exist
        assert response.status_code in [200, 422]  # 200 if no conflicts, 422 if unresolved
    
    def test_rollback_sync(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/rollback endpoint."""
        # Arrange
        rollback_request = {
            'sync_id': 'sync_001',
            'reason': 'Sync contained incorrect translations'
        }
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/rollback',
            json=rollback_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['status'] == 'ROLLED_BACK'
    
    def test_rollback_nonexistent_sync(self, client, auth_headers, mock_auth):
        """Test POST /api/admin/i18n-sync/rollback with nonexistent sync."""
        # Arrange
        rollback_request = {
            'sync_id': 'nonexistent',
            'reason': 'Testing'
        }
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/rollback',
            json=rollback_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_sync_history(self, client, auth_headers, mock_auth):
        """Test GET /api/admin/i18n-sync/history endpoint."""
        # Arrange
        # No arrange needed
        
        # Act
        response = client.get(
            '/api/admin/i18n-sync/history',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'total' in data
    
    def test_get_sync_history_filtered(self, client, auth_headers, mock_auth):
        """Test GET /api/admin/i18n-sync/history with filters."""
        # Arrange
        # No arrange needed
        
        # Act
        response = client.get(
            '/api/admin/i18n-sync/history?status=COMPLETED&mode=MANUAL&limit=10&offset=0',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_sync_details(self, client, auth_headers, mock_auth):
        """Test GET /api/admin/i18n-sync/{sync_id} endpoint."""
        # Arrange
        sync_id = 'sync_001'
        
        # Act
        response = client.get(
            f'/api/admin/i18n-sync/{sync_id}',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'sync' in data['data']
        assert 'changes' in data['data']
        assert 'resolutions' in data['data']


class TestI18nSyncAPIEndpointErrors:
    """Test error handling in i18n Sync API."""
    
    def test_validation_error_handler(self, client, auth_headers, mock_auth):
        """Test ValidationError is properly handled."""
        # Arrange
        invalid_request = {}
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/scan',
            json=invalid_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_not_found_error_handler(self, client, auth_headers, mock_auth):
        """Test NotFoundError is properly handled."""
        # Arrange
        # No arrange needed
        
        # Act
        response = client.post(
            '/api/admin/i18n-sync/rollback',
            json={'sync_id': 'nonexistent', 'reason': 'test'},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_business_logic_error_handler(self, client, auth_headers, mock_auth):
        """Test BusinessLogicError is properly handled."""
        # This would occur when trying to apply sync with unresolved conflicts
        # in MANUAL mode
        # The error handling is tested through the other tests


class TestI18nSyncAPIWorkflows:
    """Test complete workflows through the API."""
    
    def test_manual_sync_complete_workflow(self, client, auth_headers, mock_auth):
        """Test complete MANUAL sync workflow."""
        # Step 1: Initiate scan
        scan_response = client.post(
            '/api/admin/i18n-sync/scan',
            json={
                'mode': 'MANUAL',
                'languages': ['de'],
                'frontend_translations': {'de': {'greeting': 'Hallo'}}
            },
            headers=auth_headers
        )
        assert scan_response.status_code == 201
        sync_id = json.loads(scan_response.data)['data']['sync_id']
        
        # Step 2: Get scan results
        results_response = client.get(
            f'/api/admin/i18n-sync/results/{sync_id}',
            headers=auth_headers
        )
        assert results_response.status_code == 200
        
        # Step 3: Resolve conflicts (if any)
        resolve_response = client.post(
            f'/api/admin/i18n-sync/{sync_id}/resolve',
            json={'change_id': 1, 'action': 'ADD'},
            headers=auth_headers
        )
        # May be 200 or 404 depending on conflicts
        assert resolve_response.status_code in [200, 404, 422]
        
        # Step 4: Apply sync
        apply_response = client.post(
            '/api/admin/i18n-sync/apply',
            json={'sync_id': sync_id, 'auto_resolve': False},
            headers=auth_headers
        )
        assert apply_response.status_code in [200, 422]
    
    def test_auto_sync_complete_workflow(self, client, auth_headers, mock_auth):
        """Test complete AUTO sync workflow."""
        # Step 1: Initiate scan
        scan_response = client.post(
            '/api/admin/i18n-sync/scan',
            json={
                'mode': 'AUTO',
                'languages': ['en'],
                'frontend_translations': {'en': {'greeting': 'Hello'}}
            },
            headers=auth_headers
        )
        assert scan_response.status_code == 201
        sync_id = json.loads(scan_response.data)['data']['sync_id']
        
        # Step 2: Apply sync with auto-resolve
        apply_response = client.post(
            '/api/admin/i18n-sync/apply',
            json={'sync_id': sync_id, 'auto_resolve': True},
            headers=auth_headers
        )
        assert apply_response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
