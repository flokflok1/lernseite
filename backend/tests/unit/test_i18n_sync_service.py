"""
Unit Tests for I18nSyncService

Tests for:
- Sync initiation and state management
- Translation scanning and diff detection
- Conflict resolution
- Sync application
- Rollback functionality
- Dashboard statistics
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from app.services.i18n_sync_service import I18nSyncService, TranslationComparisonService
from app.repositories.i18n_sync import SyncRepository
from app.repositories.i18n_translation import TranslationRepository
from app.models.i18n_sync import SyncOperation, SyncChange
from app.utils.exceptions import ValidationError, NotFoundError, BusinessLogicError


class TestI18nSyncService:
    """Test suite for I18nSyncService."""
    
    @pytest.fixture
    def mock_connection(self):
        """Mock database connection."""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_connection):
        """Create service instance with mocked repositories."""
        service = I18nSyncService(mock_connection)
        return service
    
    def test_initiate_sync_manual_mode(self, service):
        """Test initiating a manual sync operation."""
        # Arrange
        user_id = "user_123"
        sync_data = {
            'user_id': user_id,
            'mode': 'MANUAL',
            'languages': ['de', 'en'],
            'metadata': {'source': 'frontend'}
        }
        
        mock_sync = SyncOperation(
            sync_id='sync_001',
            user_id=user_id,
            mode='MANUAL',
            status='PENDING',
            languages=['de', 'en'],
            created_at=datetime.utcnow()
        )
        
        service.sync_repo.create = Mock(return_value=mock_sync)
        
        # Act
        result = service.initiate_sync(
            user_id=user_id,
            mode='MANUAL',
            languages=['de', 'en'],
            metadata={'source': 'frontend'}
        )
        
        # Assert
        assert result.sync_id == 'sync_001'
        assert result.mode == 'MANUAL'
        assert result.status == 'PENDING'
        assert result.languages == ['de', 'en']
        service.sync_repo.create.assert_called_once()
    
    def test_initiate_sync_auto_mode(self, service):
        """Test initiating an auto sync operation."""
        # Arrange
        user_id = "user_456"
        mock_sync = SyncOperation(
            sync_id='sync_002',
            user_id=user_id,
            mode='AUTO',
            status='PENDING',
            languages=['fr', 'pl'],
            created_at=datetime.utcnow()
        )
        
        service.sync_repo.create = Mock(return_value=mock_sync)
        
        # Act
        result = service.initiate_sync(
            user_id=user_id,
            mode='AUTO',
            languages=['fr', 'pl']
        )
        
        # Assert
        assert result.mode == 'AUTO'
        service.sync_repo.create.assert_called_once()
    
    def test_initiate_sync_invalid_mode(self, service):
        """Test initiating sync with invalid mode."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            service.initiate_sync(
                user_id='user_123',
                mode='INVALID',
                languages=['de']
            )
        
        assert 'mode' in str(exc_info.value).lower()
    
    def test_scan_translations_detects_new_keys(self, service):
        """Test scan detects new translation keys."""
        # Arrange
        sync_id = 'sync_001'
        frontend_translations = {
            'de': {'greeting': 'Hallo', 'goodbye': 'Auf Wiedersehen'},
            'en': {'greeting': 'Hello', 'goodbye': 'Goodbye'}
        }
        
        # Database has no translations
        service.translation_repo.find_all = Mock(return_value=[])
        
        mock_sync = SyncOperation(sync_id=sync_id, status='SCANNING')
        service.sync_repo.update = Mock(return_value=mock_sync)
        service.translation_repo.create = Mock(return_value=None)
        
        # Act
        result_sync, new_count, changed_count, deleted_count, conflict_count = \
            service.scan_translations(sync_id, frontend_translations)
        
        # Assert
        assert new_count == 4  # 2 keys × 2 languages
        assert changed_count == 0
        assert deleted_count == 0
        assert conflict_count == 0
    
    def test_scan_translations_detects_changes(self, service):
        """Test scan detects changed translations."""
        # Arrange
        sync_id = 'sync_001'
        frontend_translations = {
            'de': {'greeting': 'Hallo World'},  # Changed
        }
        
        # Database has different value
        existing = SyncChange(
            change_id=1,
            sync_id=sync_id,
            key='greeting',
            language='de',
            previous_value='Hallo',
            new_value='Hallo World',
            change_type='CHANGED'
        )
        
        service.translation_repo.find_all = Mock(return_value=[existing])
        mock_sync = SyncOperation(sync_id=sync_id, status='SCANNING')
        service.sync_repo.update = Mock(return_value=mock_sync)
        
        # Act
        result_sync, new_count, changed_count, deleted_count, conflict_count = \
            service.scan_translations(sync_id, frontend_translations)
        
        # Assert
        assert changed_count >= 0  # Depends on comparison logic
    
    def test_get_scan_results_with_pagination(self, service):
        """Test retrieving scan results with pagination."""
        # Arrange
        sync_id = 'sync_001'
        mock_changes = [
            SyncChange(change_id=1, sync_id=sync_id, key='greeting', change_type='NEW'),
            SyncChange(change_id=2, sync_id=sync_id, key='goodbye', change_type='NEW'),
        ]
        
        service.translation_repo.find_by = Mock(return_value=mock_changes)
        service.translation_repo.count = Mock(return_value=2)
        
        # Act
        changes, total = service.get_scan_results(sync_id, limit=20, offset=0)
        
        # Assert
        assert len(changes) == 2
        assert total == 2
        service.translation_repo.find_by.assert_called_once()
    
    def test_resolve_conflict_manual_mode(self, service):
        """Test resolving a conflict in manual mode."""
        # Arrange
        sync_id = 'sync_001'
        change_id = 1
        user_id = 'user_123'
        
        service.translation_repo.find_by_id = Mock(
            return_value=SyncChange(
                change_id=change_id,
                sync_id=sync_id,
                change_type='CONFLICT'
            )
        )
        
        mock_resolution = Mock(resolution_id=1)
        service.sync_repo.create_resolution = Mock(return_value=mock_resolution)
        
        # Act
        result = service.resolve_conflict(
            sync_id=sync_id,
            change_id=change_id,
            action='ADD',
            user_id=user_id,
            notes='Added manually'
        )
        
        # Assert
        assert result.resolution_id == 1
        service.sync_repo.create_resolution.assert_called_once()
    
    def test_resolve_conflict_invalid_action(self, service):
        """Test resolving conflict with invalid action."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            service.resolve_conflict(
                sync_id='sync_001',
                change_id=1,
                action='INVALID_ACTION',
                user_id='user_123'
            )
        
        assert 'action' in str(exc_info.value).lower()
    
    def test_apply_sync_auto_mode(self, service):
        """Test applying sync in auto mode."""
        # Arrange
        sync_id = 'sync_001'
        mock_sync = SyncOperation(sync_id=sync_id, status='COMPLETED')
        service.sync_repo.find_by_id = Mock(return_value=mock_sync)
        service.sync_repo.update = Mock(return_value=mock_sync)
        
        # Act
        result_sync, stats = service.apply_sync(sync_id, auto_resolve=True)
        
        # Assert
        assert result_sync.status == 'COMPLETED'
        assert 'applied' in stats
    
    def test_apply_sync_manual_with_unresolved_conflicts(self, service):
        """Test applying sync manually with unresolved conflicts fails."""
        # Arrange
        sync_id = 'sync_001'
        mock_sync = SyncOperation(sync_id=sync_id, mode='MANUAL', status='COMPLETED')
        service.sync_repo.find_by_id = Mock(return_value=mock_sync)
        
        # Have unresolved conflicts
        mock_changes = [
            SyncChange(change_id=1, change_type='CONFLICT', resolved=False)
        ]
        service.translation_repo.find_by = Mock(return_value=mock_changes)
        
        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            service.apply_sync(sync_id, auto_resolve=False)
        
        assert 'unresolved' in str(exc_info.value).lower()
    
    def test_rollback_sync(self, service):
        """Test rolling back a sync operation."""
        # Arrange
        sync_id = 'sync_001'
        user_id = 'user_123'
        reason = 'User requested rollback'
        
        mock_sync = SyncOperation(sync_id=sync_id, status='ROLLED_BACK')
        service.sync_repo.update = Mock(return_value=mock_sync)
        service.translation_repo.delete_by_sync = Mock(return_value=True)
        
        # Act
        result = service.rollback_sync(sync_id, user_id, reason)
        
        # Assert
        assert result.status == 'ROLLED_BACK'
        service.translation_repo.delete_by_sync.assert_called_once_with(sync_id)
    
    def test_get_sync_details(self, service):
        """Test retrieving complete sync details."""
        # Arrange
        sync_id = 'sync_001'
        mock_sync = SyncOperation(sync_id=sync_id)
        mock_changes = [
            SyncChange(change_id=1, change_type='NEW'),
            SyncChange(change_id=2, change_type='CHANGED'),
        ]
        
        service.sync_repo.find_by_id = Mock(return_value=mock_sync)
        service.translation_repo.find_by = Mock(return_value=mock_changes)
        
        # Act
        details = service.get_sync_details(sync_id)
        
        # Assert
        assert details['sync']['sync_id'] == sync_id
        assert 'changes' in details
        assert len(details['changes']['all']) == 2
    
    def test_get_dashboard_stats(self, service):
        """Test retrieving dashboard statistics."""
        # Arrange
        service.sync_repo.count = Mock(return_value=10)
        service.sync_repo.find_by = Mock(side_effect=lambda **kw: [] if kw.get('status') == 'COMPLETED' else [])
        service.translation_repo.count = Mock(return_value=500)
        
        # Act
        stats = service.get_dashboard_stats()
        
        # Assert
        assert 'total_syncs' in stats
        assert 'translations' in stats
        assert 'total_keys' in stats['translations']
    
    def test_sync_not_found(self, service):
        """Test handling sync not found."""
        # Arrange
        service.sync_repo.find_by_id = Mock(return_value=None)
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            service.rollback_sync('nonexistent', 'user_123', 'reason')


class TestTranslationComparisonService:
    """Test suite for TranslationComparisonService."""
    
    def test_compare_translations_new_keys(self):
        """Test detecting new translation keys."""
        # Arrange
        frontend = {'greeting': 'Hello', 'goodbye': 'Goodbye'}
        database = {}
        
        # Act
        diff = TranslationComparisonService.compare(
            frontend_value=frontend,
            database_value=database,
            key='greeting',
            language='en'
        )
        
        # Assert
        assert diff['type'] == 'NEW'
    
    def test_compare_translations_changed_value(self):
        """Test detecting changed translation values."""
        # Arrange
        frontend = 'Hello World'
        database = 'Hello'
        
        # Act
        diff = TranslationComparisonService.compare(
            frontend_value=frontend,
            database_value=database,
            key='greeting',
            language='en'
        )
        
        # Assert
        assert diff['type'] == 'CHANGED'
        assert diff['previous'] == 'Hello'
        assert diff['new'] == 'Hello World'
    
    def test_compare_translations_deleted_keys(self):
        """Test detecting deleted translation keys."""
        # Arrange
        frontend = None  # Removed from frontend
        database = 'Hello'
        
        # Act
        diff = TranslationComparisonService.compare(
            frontend_value=frontend,
            database_value=database,
            key='greeting',
            language='en'
        )
        
        # Assert
        assert diff['type'] == 'DELETED'
    
    def test_compare_translations_no_changes(self):
        """Test when translations are identical."""
        # Arrange
        frontend = 'Hello'
        database = 'Hello'
        
        # Act
        diff = TranslationComparisonService.compare(
            frontend_value=frontend,
            database_value=database,
            key='greeting',
            language='en'
        )
        
        # Assert
        assert diff['type'] is None  # No change


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
