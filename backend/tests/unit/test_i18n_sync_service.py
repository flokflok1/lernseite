"""
Unit Tests for I18nSyncService

Tests for:
- Sync initiation and state management
- Translation scanning and diff detection
- Conflict resolution
- Scan results retrieval
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from app.application.services.i18n.legacy.sync_service import I18nSyncService
from app.infrastructure.persistence.repositories.i18n.sync_ops import SyncOperation, SyncStatus
from app.infrastructure.persistence.repositories.i18n.sync_changes import SyncChange, ChangeType
from app.infrastructure.persistence.repositories.i18n.sync_resolutions import SyncResolution
from app.infrastructure.error_handling.exceptions import ValidationError, NotFoundError, BusinessLogicError


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

        mock_sync = SyncOperation(
            sync_id='sync_001',
            mode='MANUAL',
            status='PENDING',
            languages_synced=['de', 'en'],
            initiated_by_user_id=user_id
        )

        service.translation_repo.get_supported_languages = Mock(return_value=['de', 'en', 'pl'])
        service.sync_repo.create_sync = Mock(return_value=mock_sync)

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
        assert result.languages_synced == ['de', 'en']
        service.sync_repo.create_sync.assert_called_once()

    def test_initiate_sync_auto_mode(self, service):
        """Test initiating an auto sync operation."""
        # Arrange
        user_id = "user_456"
        mock_sync = SyncOperation(
            sync_id='sync_002',
            mode='AUTO',
            status='PENDING',
            languages_synced=['fr', 'pl'],
            initiated_by_user_id=user_id
        )

        service.translation_repo.get_supported_languages = Mock(return_value=['de', 'en', 'fr', 'pl'])
        service.sync_repo.create_sync = Mock(return_value=mock_sync)

        # Act
        result = service.initiate_sync(
            user_id=user_id,
            mode='AUTO',
            languages=['fr', 'pl']
        )

        # Assert
        assert result.mode == 'AUTO'
        service.sync_repo.create_sync.assert_called_once()

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

        mock_sync = SyncOperation(
            sync_id=sync_id,
            mode='MANUAL',
            status='PENDING',
            languages_synced=['de', 'en']
        )

        service.sync_repo.get_sync = Mock(return_value=mock_sync)
        service.sync_repo.update_sync_status = Mock(return_value=None)
        service.sync_repo.create_change = Mock(return_value=None)

        # get_translations_for_language returns (list, count) — empty DB
        service.translation_repo.get_translations_for_language = Mock(return_value=([], 0))

        # detect_changes returns dict of change types
        service.translation_repo.detect_changes = Mock(return_value={
            'new': [
                {'key': 'greeting', 'frontend_value': 'Hallo'},
                {'key': 'goodbye', 'frontend_value': 'Auf Wiedersehen'}
            ],
            'changed': [],
            'deleted': [],
            'conflicts': []
        })

        completed_sync = SyncOperation(
            sync_id=sync_id,
            mode='MANUAL',
            status='COMPLETED',
            languages_synced=['de', 'en'],
            new_keys=4
        )
        service.sync_repo.complete_sync = Mock(return_value=completed_sync)

        # Act
        result_sync, new_count, changed_count, deleted_count, conflict_count = \
            service.scan_translations(sync_id, frontend_translations)

        # Assert
        assert new_count == 4  # 2 keys x 2 languages
        assert changed_count == 0
        assert deleted_count == 0
        assert conflict_count == 0

    def test_scan_translations_rejects_non_pending(self, service):
        """Test scan rejects sync not in PENDING state."""
        # Arrange
        sync_id = 'sync_001'
        mock_sync = SyncOperation(
            sync_id=sync_id,
            mode='MANUAL',
            status='COMPLETED',
            languages_synced=['de']
        )
        service.sync_repo.get_sync = Mock(return_value=mock_sync)

        # Act & Assert
        with pytest.raises(BusinessLogicError):
            service.scan_translations(sync_id, {'de': {'key': 'value'}})

    def test_scan_translations_not_found(self, service):
        """Test scan raises when sync not found."""
        # Arrange
        service.sync_repo.get_sync = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(NotFoundError):
            service.scan_translations('nonexistent', {'de': {}})

    def test_get_scan_results_with_pagination(self, service):
        """Test retrieving scan results with pagination."""
        # Arrange
        sync_id = 'sync_001'
        mock_changes = [
            SyncChange(
                change_id=1, sync_id=sync_id,
                translation_key='greeting', language_code='de',
                change_type='NEW'
            ),
            SyncChange(
                change_id=2, sync_id=sync_id,
                translation_key='goodbye', language_code='de',
                change_type='NEW'
            ),
        ]

        service.sync_repo.list_changes = Mock(return_value=(mock_changes, 2))

        # Act
        changes, total = service.get_scan_results(sync_id, limit=20, offset=0)

        # Assert
        assert len(changes) == 2
        assert total == 2
        service.sync_repo.list_changes.assert_called_once()

    def test_resolve_conflict_success(self, service):
        """Test resolving a conflict successfully."""
        # Arrange
        sync_id = 'sync_001'
        change_id = 1
        user_id = 'user_123'

        mock_change = SyncChange(
            change_id=change_id,
            sync_id=sync_id,
            translation_key='greeting',
            language_code='de',
            change_type='CONFLICT'
        )

        service.sync_repo.get_change = Mock(return_value=mock_change)

        mock_resolution = SyncResolution(
            resolution_id=1,
            sync_id=sync_id,
            change_id=change_id,
            translation_key='greeting',
            language_code='de',
            chosen_action='ADD',
            decided_by_user_id=user_id
        )
        service.sync_repo.create_resolution = Mock(return_value=mock_resolution)
        service.sync_repo.update_change_resolution = Mock(return_value=None)

        # Act
        result = service.resolve_conflict(
            sync_id=sync_id,
            change_id=change_id,
            chosen_action='ADD',
            user_id=user_id,
            notes='Added manually'
        )

        # Assert
        assert result.resolution_id == 1
        service.sync_repo.create_resolution.assert_called_once()
        service.sync_repo.update_change_resolution.assert_called_once()

    def test_resolve_conflict_change_not_found(self, service):
        """Test resolving conflict when change not found."""
        # Arrange
        service.sync_repo.get_change = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(NotFoundError):
            service.resolve_conflict(
                sync_id='sync_001',
                change_id=999,
                chosen_action='ADD',
                user_id='user_123'
            )

    def test_resolve_conflict_non_conflict_change(self, service):
        """Test resolving a non-CONFLICT change raises error."""
        # Arrange
        mock_change = SyncChange(
            change_id=1,
            sync_id='sync_001',
            translation_key='greeting',
            language_code='de',
            change_type='NEW'  # Not CONFLICT
        )
        service.sync_repo.get_change = Mock(return_value=mock_change)

        # Act & Assert
        with pytest.raises(BusinessLogicError):
            service.resolve_conflict(
                sync_id='sync_001',
                change_id=1,
                chosen_action='ADD',
                user_id='user_123'
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
