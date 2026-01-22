"""
Unit Tests for Owner Group Creation Service

Tests the new GroupManagementService methods:
- create_owner_group_for_organization()
- _assign_owner_permissions()

These tests verify that:
1. Owner group is created with correct properties
2. Owner user is added to the group
3. Admin permissions are assigned
4. Audit logging works
5. Error handling is proper
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, Dict

from app.application.services.system.group_management import GroupManagementService
from app.utils.exceptions import ValidationError


class TestCreateOwnerGroupForOrganization:
    """Test suite for create_owner_group_for_organization() method."""

    @pytest.fixture
    def mock_db(self):
        """Mock database connection."""
        return Mock()

    @pytest.fixture
    def org_id(self):
        """Sample organization ID."""
        return str(uuid4())

    @pytest.fixture
    def user_id(self):
        """Sample user ID."""
        return str(uuid4())

    @pytest.fixture
    def admin_user_id(self):
        """Sample admin user ID."""
        return str(uuid4())

    # ========================================================================
    # Success Cases
    # ========================================================================

    def test_create_owner_group_success(self, org_id, user_id, admin_user_id, mock_db):
        """Test successful owner group creation."""

        # Mock the service method
        with patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group') as mock_add_user, \
             patch.object(GroupManagementService, '_assign_owner_permissions') as mock_assign_perms, \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch_org, \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch_user, \
             patch('app.application.services.system.group_management.execute_query') as mock_execute:

            # Setup mocks
            mock_fetch_org.side_effect = [
                {'id': org_id},  # Organization exists
                {'id': user_id}  # User exists
            ]

            expected_group = {
                'id': str(uuid4()),
                'name': 'Owner',
                'slug': f'{org_id}-owner',
                'organisation_id': org_id,
                'group_type': 'org_admin',
                'is_system_group': False,
                'is_protected': False
            }

            mock_create_group.return_value = expected_group
            mock_assign_perms.return_value = True

            # Call the method
            result = GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id,
                created_by=admin_user_id
            )

            # Assertions
            assert result is not None
            assert result['id'] == expected_group['id']
            assert result['name'] == 'Owner'
            assert result['slug'] == f'{org_id}-owner'
            assert result['group_type'] == 'org_admin'

            # Verify method calls
            mock_create_group.assert_called_once()
            mock_add_user.assert_called_once()
            mock_assign_perms.assert_called_once()

    def test_owner_group_properties(self, org_id, user_id):
        """Test that owner group has correct properties."""

        with patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group'), \
             patch.object(GroupManagementService, '_assign_owner_permissions'), \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch:

            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]

            owner_group = {
                'id': str(uuid4()),
                'name': 'Owner',
                'slug': f'{org_id}-owner',
                'group_type': 'org_admin'
            }
            mock_create_group.return_value = owner_group

            result = GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id
            )

            # Verify group type is org_admin
            assert result['group_type'] == 'org_admin'
            # Verify slug contains org_id
            assert org_id in result['slug']
            # Verify name is 'Owner'
            assert result['name'] == 'Owner'

    def test_user_added_to_group(self, org_id, user_id):
        """Test that owner user is added to group."""

        with patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group') as mock_add_user, \
             patch.object(GroupManagementService, '_assign_owner_permissions'), \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch:

            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]

            group_id = str(uuid4())
            mock_create_group.return_value = {'id': group_id, 'name': 'Owner'}

            GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id
            )

            # Verify add_user_to_group was called with correct parameters
            mock_add_user.assert_called_once()
            call_args = mock_add_user.call_args
            assert call_args[1]['group_id'] == group_id
            assert call_args[1]['user_id'] == user_id

    def test_permissions_assigned_to_group(self, org_id, user_id):
        """Test that admin permissions are assigned to owner group."""

        with patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group'), \
             patch.object(GroupManagementService, '_assign_owner_permissions') as mock_assign, \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch:

            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]

            group_id = str(uuid4())
            mock_create_group.return_value = {'id': group_id}
            mock_assign.return_value = True

            GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id
            )

            # Verify _assign_owner_permissions was called
            mock_assign.assert_called_once()
            call_args = mock_assign.call_args
            assert call_args[1]['group_id'] == group_id

    def test_audit_log_created(self, org_id, user_id, admin_user_id):
        """Test that audit log entry is created."""

        with patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group'), \
             patch.object(GroupManagementService, '_assign_owner_permissions'), \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch, \
             patch('app.application.services.system.group_management.execute_query') as mock_execute:

            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]
            mock_create_group.return_value = {'id': str(uuid4())}

            GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id,
                created_by=admin_user_id
            )

            # Verify audit log was created
            mock_execute.assert_called()
            call_args = mock_execute.call_args
            # Check that audit_logs insert was executed
            assert 'audit_logs' in str(call_args)

    # ========================================================================
    # Error Cases
    # ========================================================================

    def test_organization_not_found(self, org_id, user_id):
        """Test error when organization doesn't exist."""

        with patch('app.application.services.system.group_management.fetch_one') as mock_fetch:
            mock_fetch.return_value = None  # Organization not found

            with pytest.raises(ValueError) as exc_info:
                GroupManagementService.create_owner_group_for_organization(
                    organization_id=org_id,
                    owner_user_id=user_id
                )

            assert 'Organization' in str(exc_info.value)
            assert org_id in str(exc_info.value)

    def test_user_not_found(self, org_id, user_id):
        """Test error when user doesn't exist."""

        with patch('app.application.services.system.group_management.fetch_one') as mock_fetch:
            # First call (org check) succeeds, second (user check) fails
            mock_fetch.side_effect = [
                {'id': org_id},  # Organization found
                None  # User not found
            ]

            with pytest.raises(ValueError) as exc_info:
                GroupManagementService.create_owner_group_for_organization(
                    organization_id=org_id,
                    owner_user_id=user_id
                )

            assert 'User' in str(exc_info.value)
            assert user_id in str(exc_info.value)

    def test_group_creation_fails(self, org_id, user_id):
        """Test handling when group creation fails."""

        with patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch:

            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]
            mock_create_group.return_value = None  # Creation failed

            result = GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id
            )

            # Should return None on failure
            assert result is None

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_with_no_audit_context(self, org_id, user_id):
        """Test creation without audit context (created_by=None)."""

        with patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group'), \
             patch.object(GroupManagementService, '_assign_owner_permissions'), \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch:

            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]
            mock_create_group.return_value = {'id': str(uuid4())}

            # Should work without created_by parameter
            result = GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id,
                created_by=None
            )

            assert result is not None

    def test_idempotency(self, org_id, user_id):
        """Test that creating owner group multiple times is idempotent."""

        with patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group') as mock_add_user, \
             patch.object(GroupManagementService, '_assign_owner_permissions'), \
             patch('app.application.services.system.group_management.fetch_one') as mock_fetch:

            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]
            group_id = str(uuid4())
            mock_create_group.return_value = {'id': group_id}
            # Simulate ON CONFLICT DO NOTHING behavior
            mock_add_user.return_value = None  # Second call doesn't add duplicate

            # First call
            result1 = GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id
            )

            # Second call (should not fail)
            result2 = GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id
            )

            # Both should succeed
            assert result1 is not None
            assert result2 is not None


class TestAssignOwnerPermissions:
    """Test suite for _assign_owner_permissions() helper method."""

    @pytest.fixture
    def group_id(self):
        """Sample group ID."""
        return str(uuid4())

    @pytest.fixture
    def admin_user_id(self):
        """Sample admin user ID."""
        return str(uuid4())

    def test_assign_permissions_success(self, group_id, admin_user_id):
        """Test successful permission assignment."""

        with patch('app.application.services.system.group_management.fetch_one') as mock_fetch, \
             patch('app.application.services.system.group_management.execute_query') as mock_execute:

            # Mock returning some admin permissions
            mock_fetch.return_value = [
                {'id': 1, 'code': 'org.manage_users'},
                {'id': 2, 'code': 'org.manage_content'},
                {'id': 3, 'code': 'org.manage_settings'}
            ]

            result = GroupManagementService._assign_owner_permissions(
                group_id=group_id,
                assigned_by=admin_user_id
            )

            assert result is True
            mock_execute.assert_called_once()

    def test_no_permissions_found(self, group_id):
        """Test handling when no admin permissions exist."""

        with patch('app.application.services.system.group_management.fetch_one') as mock_fetch:
            mock_fetch.return_value = []  # No permissions found

            result = GroupManagementService._assign_owner_permissions(
                group_id=group_id
            )

            # Should return False when no permissions available
            assert result is False

    def test_permission_query_includes_hierarchy_level(self, group_id):
        """Test that permission query filters by hierarchy level."""

        with patch('app.application.services.system.group_management.fetch_one') as mock_fetch, \
             patch('app.application.services.system.group_management.execute_query'):

            mock_fetch.return_value = []

            GroupManagementService._assign_owner_permissions(group_id=group_id)

            # Verify query includes required_hierarchy_level >= 3
            call_args = mock_fetch.call_args
            query = call_args[0][0] if call_args[0] else ''
            assert 'required_hierarchy_level' in query
            assert '>= 3' in query

    def test_bulk_insert_with_on_conflict(self, group_id):
        """Test that permissions use ON CONFLICT for idempotency."""

        with patch('app.application.services.system.group_management.fetch_one') as mock_fetch, \
             patch('app.application.services.system.group_management.execute_query') as mock_execute:

            mock_fetch.return_value = [{'id': 1}]

            GroupManagementService._assign_owner_permissions(group_id=group_id)

            # Verify ON CONFLICT is used
            call_args = mock_execute.call_args
            query = call_args[0][0] if call_args[0] else ''
            assert 'ON CONFLICT' in query
            assert 'DO NOTHING' in query


class TestB2BIntegration:
    """Integration tests for B2B account creation with owner group."""

    def test_complete_b2b_setup_flow(self):
        """Test complete B2B account creation flow."""

        org_id = str(uuid4())
        user_id = str(uuid4())

        # Simulate the complete flow
        with patch('app.application.services.system.group_management.fetch_one') as mock_fetch, \
             patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group') as mock_add_user, \
             patch.object(GroupManagementService, '_assign_owner_permissions') as mock_assign:

            # Setup mocks
            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]
            mock_create_group.return_value = {'id': str(uuid4()), 'name': 'Owner'}
            mock_assign.return_value = True

            # Execute B2B signup
            owner_group = GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id
            )

            # Verify entire flow succeeded
            assert owner_group is not None
            mock_create_group.assert_called_once()
            mock_add_user.assert_called_once()
            mock_assign.assert_called_once()

    def test_partial_failure_handling(self):
        """Test that non-critical failures don't break signup."""

        org_id = str(uuid4())
        user_id = str(uuid4())

        # Simulate permission assignment failure
        with patch('app.application.services.system.group_management.fetch_one') as mock_fetch, \
             patch.object(GroupManagementService, 'create_group') as mock_create_group, \
             patch.object(GroupManagementService, 'add_user_to_group'), \
             patch.object(GroupManagementService, '_assign_owner_permissions') as mock_assign:

            mock_fetch.side_effect = [{'id': org_id}, {'id': user_id}]
            mock_create_group.return_value = {'id': str(uuid4())}
            mock_assign.return_value = False  # Permission assignment fails

            # Should still return group (permissions can be assigned later)
            result = GroupManagementService.create_owner_group_for_organization(
                organization_id=org_id,
                owner_user_id=user_id
            )

            # Group should be created even if permissions fail
            assert result is not None
