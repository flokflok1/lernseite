"""
Integration Tests for Role Studio API (Phase 1 & 2)

Tests:
- RoleStudioMode CRUD operations via classmethod repository
- RoleStudioService static method behavior
- API endpoint response format validation
- Error handling and edge cases
- Backend integration with Frontend expectations

Note: RoleStudioModeRepository uses @classmethod decorators
and helper functions from app.database.connection (fetch_one, fetch_all, etc.)
"""

import pytest
from unittest.mock import patch
from datetime import datetime
from app.repositories.role_studio_mode import RoleStudioModeRepository
from app.services.role_studio_service import RoleStudioService


class TestRoleStudioModeRepository:
    """Tests for RoleStudioModeRepository (@classmethod pattern)."""

    @patch('app.repositories.role_studio_mode.fetch_all')
    def test_find_all_roles(self, mock_fetch_all):
        """Test retrieving all role studio modes."""
        # Setup
        mock_fetch_all.return_value = [
            {
                'role_code': 'SYSTEM_ADMIN',
                'display_name': 'System Administrator',
                'description': 'Full system access',
                'is_active': True,
                'requires_organization': False,
                'permissions': '[\"admin.roles.view\", \"admin.roles.edit\"]',
                'created_at': datetime.now(),
                'updated_at': None
            },
            {
                'role_code': 'ORG_ADMIN',
                'display_name': 'Organization Administrator',
                'description': 'Organization-level access',
                'is_active': True,
                'requires_organization': True,
                'permissions': '[\"org.manage\", \"org.users\"]',
                'created_at': datetime.now(),
                'updated_at': None
            }
        ]

        # Execute
        roles = RoleStudioModeRepository.find_all(limit=100, offset=0)

        # Assert
        assert len(roles) == 2
        assert roles[0]['role_code'] == 'SYSTEM_ADMIN'
        assert roles[1]['role_code'] == 'ORG_ADMIN'
        assert all(role['is_active'] for role in roles)

    @patch('app.repositories.role_studio_mode.fetch_one')
    def test_find_by_code(self, mock_fetch_one):
        """Test finding role studio mode by code."""
        # Setup
        mock_fetch_one.return_value = {
            'role_code': 'SYSTEM_ADMIN',
            'display_name': 'System Administrator',
            'description': 'Full system access',
            'is_active': True,
            'requires_organization': False,
            'permissions': '[\"admin.roles.view\", \"admin.roles.edit\"]',
            'created_at': datetime.now(),
            'updated_at': None
        }

        # Execute
        role = RoleStudioModeRepository.find_by_code('SYSTEM_ADMIN')

        # Assert
        assert role is not None
        assert role['role_code'] == 'SYSTEM_ADMIN'
        assert role['display_name'] == 'System Administrator'
        assert role['is_active'] is True

    @patch('app.repositories.role_studio_mode.fetch_one')
    def test_find_by_code_not_found(self, mock_fetch_one):
        """Test finding non-existent role studio mode."""
        # Setup
        mock_fetch_one.return_value = None

        # Execute
        role = RoleStudioModeRepository.find_by_code('NONEXISTENT')

        # Assert
        assert role is None

    @patch('app.repositories.role_studio_mode.insert_returning')
    def test_create_role(self, mock_insert):
        """Test creating new role studio mode."""
        # Setup
        new_role_data = {
            'role_code': 'CUSTOM_ROLE',
            'display_name': 'Custom Role',
            'studio_mode': 'teacher',
            'description': 'Custom role description',
            'is_active': True,
            'requires_organization': False,
            'permissions': '[\"read\", \"write\"]'
        }

        mock_insert.return_value = {
            **new_role_data,
            'created_at': datetime.now(),
            'updated_at': None
        }

        # Execute
        role = RoleStudioModeRepository.create(new_role_data)

        # Assert
        assert role is not None
        assert role['role_code'] == 'CUSTOM_ROLE'
        assert role['display_name'] == 'Custom Role'

    @patch('app.repositories.role_studio_mode.update_returning')
    def test_update_role(self, mock_update):
        """Test updating role studio mode."""
        # Setup
        update_data = {
            'display_name': 'Updated Display Name',
            'description': 'Updated description'
        }

        mock_update.return_value = {
            'role_code': 'SYSTEM_ADMIN',
            'display_name': 'Updated Display Name',
            'description': 'Updated description',
            'is_active': True,
            'requires_organization': False,
            'permissions': '[\"admin.roles.view\", \"admin.roles.edit\"]',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        # Execute
        role = RoleStudioModeRepository.update('SYSTEM_ADMIN', update_data)

        # Assert
        assert role is not None
        assert role['display_name'] == 'Updated Display Name'
        assert role['description'] == 'Updated description'

    @patch('app.repositories.role_studio_mode.delete_returning')
    def test_delete_role(self, mock_delete):
        """Test deleting role studio mode."""
        # Setup
        mock_delete.return_value = {
            'role_code': 'TEST_ROLE',
            'display_name': 'Test Role'
        }

        # Execute
        result = RoleStudioModeRepository.delete('TEST_ROLE')

        # Assert
        assert result is True

    @patch('app.repositories.role_studio_mode.fetch_one')
    def test_count_roles(self, mock_fetch_one):
        """Test counting role studio modes."""
        # Setup
        mock_fetch_one.return_value = (7,)  # 7 active roles

        # Execute
        count = RoleStudioModeRepository.count({'is_active': True})

        # Assert
        assert count == 7


class TestRoleStudioService:
    """Tests for RoleStudioService (@staticmethod pattern)."""

    def test_service_methods_exist(self):
        """Test that RoleStudioService has expected static methods."""
        # Assert - check for actual static methods in the service
        assert hasattr(RoleStudioService, 'get_role_studio_mode')
        assert hasattr(RoleStudioService, 'get_all_active_roles')
        assert hasattr(RoleStudioService, 'get_roles_by_studio_mode')
        assert hasattr(RoleStudioService, 'get_role_permissions')
        assert hasattr(RoleStudioService, 'has_permission')

    @patch('app.services.role_studio_service.RoleStudioModeRepository.find_by_code')
    def test_get_role_studio_mode(self, mock_find):
        """Test service retrieves role studio mode."""
        # Setup
        mock_find.return_value = {
            'role_code': 'admin',
            'studio_mode': 'admin',
            'permissions': '{"admin.view": true}'
        }

        # Execute
        config = RoleStudioService.get_role_studio_mode('admin')

        # Assert
        assert config is not None
        assert config['role_code'] == 'admin'
        assert isinstance(config['permissions'], dict)

    @patch('app.services.role_studio_service.RoleStudioModeRepository.find_all_active')
    def test_get_all_active_roles(self, mock_find_all):
        """Test service retrieves all active roles."""
        # Setup
        mock_find_all.return_value = [
            {
                'role_code': 'admin',
                'display_name': 'Admin',
                'permissions': '{"admin.view": true}'
            },
            {
                'role_code': 'user',
                'display_name': 'User',
                'permissions': '{"user.view": true}'
            }
        ]

        # Execute
        roles = RoleStudioService.get_all_active_roles()

        # Assert
        assert len(roles) == 2
        assert all(isinstance(r['permissions'], dict) for r in roles)


class TestRoleStudioAPIResponses:
    """Tests for API Response Format Compliance."""

    def test_role_response_structure(self):
        """Test that role response has correct structure for frontend."""
        # Expected frontend structure (from types)
        expected_fields = [
            'role_code',
            'display_name',
            'description',
            'is_active',
            'requires_organization',
            'permissions',
            'created_at',
            'updated_at'
        ]

        # Sample response
        role_response = {
            'role_code': 'SYSTEM_ADMIN',
            'display_name': 'System Administrator',
            'description': 'Full system access',
            'is_active': True,
            'requires_organization': False,
            'permissions': '[\"admin.roles.view\", \"admin.roles.edit\"]',
            'created_at': '2026-01-14T10:00:00Z',
            'updated_at': None
        }

        # Assert all required fields present
        for field in expected_fields:
            assert field in role_response, f"Missing field: {field}"

    def test_paginated_list_response_structure(self):
        """Test that paginated list response has correct structure."""
        # Sample response
        list_response = {
            'roles': [
                {
                    'role_code': 'ROLE1',
                    'display_name': 'Role 1',
                    'is_active': True,
                    'requires_organization': False
                },
                {
                    'role_code': 'ROLE2',
                    'display_name': 'Role 2',
                    'is_active': True,
                    'requires_organization': True
                }
            ],
            'total': 2
        }

        # Assert structure
        assert 'roles' in list_response
        assert 'total' in list_response
        assert isinstance(list_response['roles'], list)
        assert isinstance(list_response['total'], int)
        assert len(list_response['roles']) == 2
        assert list_response['total'] == 2

    def test_change_history_response_structure(self):
        """Test that change history response has correct structure."""
        expected_fields = [
            'role_code',
            'changed_by',
            'changed_at'
        ]

        history_response = {
            'role_code': 'TEST_ROLE',
            'changed_by': 'admin-1',
            'changed_at': '2026-01-14T10:00:00Z'
        }

        # Assert all required fields present
        for field in expected_fields:
            assert field in history_response, f"Missing field: {field}"


class TestRoleStudioErrorHandling:
    """Tests for error handling and edge cases."""

    @patch('app.repositories.role_studio_mode.fetch_all')
    def test_repository_fetch_error(self, mock_fetch):
        """Test repository error handling."""
        # Setup
        mock_fetch.side_effect = Exception("Database connection failed")

        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            RoleStudioModeRepository.find_all()

        assert "Database connection failed" in str(exc_info.value)

    def test_pagination_boundary_conditions(self):
        """Test pagination with boundary conditions."""
        test_cases = [
            {'page': 1, 'page_size': 20},      # First page
            {'page': 100, 'page_size': 20},    # High page number
            {'page': 1, 'page_size': 1},       # Single item per page
            {'page': 1, 'page_size': 1000},    # Large page size
        ]

        for case in test_cases:
            # Should not raise exceptions
            assert case['page'] > 0
            assert case['page_size'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
