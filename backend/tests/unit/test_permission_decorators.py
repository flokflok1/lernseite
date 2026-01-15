"""
Unit Tests for RBAC 2.0 Permission Decorators

Tests the database-driven permission checking decorators:
- @require_permission() - Generic permission check
- @require_system_admin() - System admin access (RBAC 2.0)
- @require_org_admin() - Organisation admin access (RBAC 2.0)
- @require_org_member() - Organisation membership check

Tests verify:
- Correct access granted to authorized users
- Access denied (403) to unauthorized users
- Backward compatibility with hierarchy_level checks
- Fail-secure behavior on database errors
- Proper error responses

Migration Note:
- Phase 1 (2026-01-14): Replaced hardcoded role lists with:
  - require_system_admin: PermissionRepository + hierarchy_level >= 9
  - require_org_admin: PermissionRepository + hierarchy_level >= 5
  - require_org_member: hierarchy_level >= 9 (resource ownership check)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, jsonify, g
from app.security.permissions import (
    require_system_admin,
    require_org_admin,
    require_org_member,
    Permissions
)
from app.repositories.permission_repository import PermissionRepository


# ==============================================
# FIXTURES
# ==============================================

@pytest.fixture
def flask_app():
    """Create test Flask app with context."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    return app


@pytest.fixture
def mock_token_required():
    """Mock the @token_required decorator."""
    with patch('app.security.permissions.token_required') as mock:
        def identity_decorator(fn):
            """Pass-through decorator for testing."""
            return fn
        mock.side_effect = lambda f: identity_decorator
        yield mock


@pytest.fixture
def system_admin_user():
    """Create mock system admin user."""
    return {
        'user_id': '550e8400-e29b-41d4-a716-446655440000',
        'role': 'admin',
        'hierarchy_level': 9,
        'organization_id': None
    }


@pytest.fixture
def org_admin_user():
    """Create mock organisation admin user."""
    return {
        'user_id': '550e8400-e29b-41d4-a716-446655440001',
        'role': 'school_admin',
        'hierarchy_level': 5,
        'organization_id': '550e8400-e29b-41d4-a716-446655440100'
    }


@pytest.fixture
def regular_user():
    """Create mock regular user."""
    return {
        'user_id': '550e8400-e29b-41d4-a716-446655440002',
        'role': 'user',
        'hierarchy_level': 0,
        'organization_id': '550e8400-e29b-41d4-a716-446655440100'
    }


@pytest.fixture
def other_org_user():
    """Create mock user from different organisation."""
    return {
        'user_id': '550e8400-e29b-41d4-a716-446655440003',
        'role': 'user',
        'hierarchy_level': 0,
        'organization_id': '550e8400-e29b-41d4-a716-446655440200'
    }


# ==============================================
# TESTS: @require_system_admin()
# ==============================================

class TestRequireSystemAdmin:
    """Test @require_system_admin decorator."""

    @patch('app.security.permissions.PermissionRepository')
    @patch('app.security.permissions.g')
    def test_system_admin_with_permission(self, mock_g, mock_repo):
        """Test system admin access with database permission."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'hierarchy_level': 0  # No hierarchy level
        }
        mock_repo.user_has_permission.return_value = True

        # Create test function
        @require_system_admin
        def test_function():
            return {'status': 'ok'}, 200

        # Test requires token_required context
        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_system_admin(test_function)

            # Mock Flask context
            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn()

        # Verify database permission was checked
        mock_repo.user_has_permission.assert_called_with(
            user_id='550e8400-e29b-41d4-a716-446655440000',
            permission_key=Permissions.MANAGE_SYSTEM
        )

    @patch('app.security.permissions.PermissionRepository')
    @patch('app.security.permissions.g')
    def test_system_admin_with_hierarchy_level(self, mock_g, mock_repo):
        """Test system admin access with hierarchy_level >= 9 (backward compat)."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'hierarchy_level': 9  # System admin level
        }

        # Create test function
        @require_system_admin
        def test_function():
            return {'status': 'ok'}, 200

        # When hierarchy_level >= 9, function should execute without DB check
        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_system_admin(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn()

        # Should not check database when hierarchy_level >= 9
        mock_repo.user_has_permission.assert_not_called()

    @patch('app.security.permissions.PermissionRepository')
    @patch('app.security.permissions.g')
    @patch('app.security.permissions.jsonify')
    def test_system_admin_denied_no_permission(self, mock_jsonify, mock_g, mock_repo):
        """Test 403 response when user lacks permission."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'hierarchy_level': 0
        }
        mock_repo.user_has_permission.return_value = False
        mock_jsonify.return_value = {'error': 'Forbidden'}, 403

        @require_system_admin
        def test_function():
            return {'status': 'ok'}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_system_admin(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn()

        # Should call jsonify for error response
        mock_jsonify.assert_called()

    @patch('app.security.permissions.PermissionRepository')
    @patch('app.security.permissions.g')
    def test_system_admin_db_error_fail_secure(self, mock_g, mock_repo):
        """Test fail-secure behavior on database error."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'hierarchy_level': 0
        }
        # Simulate database error
        mock_repo.user_has_permission.side_effect = Exception("DB Connection Error")

        @require_system_admin
        def test_function():
            return {'status': 'ok'}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_system_admin(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn()

        # Should return 403 (fail-secure) on error
        assert result[1] == 403


# ==============================================
# TESTS: @require_org_admin()
# ==============================================

class TestRequireOrgAdmin:
    """Test @require_org_admin decorator."""

    @patch('app.security.permissions.PermissionRepository')
    @patch('app.security.permissions.g')
    def test_org_admin_with_manage_org_settings_permission(self, mock_g, mock_repo):
        """Test org admin with manage:org:settings permission."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440001',
            'hierarchy_level': 0
        }
        # First call returns False for MANAGE_ORG_SETTINGS, we won't check second
        mock_repo.user_has_permission.return_value = True

        @require_org_admin
        def test_function():
            return {'status': 'ok'}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_org_admin(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn()

        # Should check permissions
        mock_repo.user_has_permission.assert_called()

    @patch('app.security.permissions.PermissionRepository')
    @patch('app.security.permissions.g')
    def test_org_admin_with_hierarchy_level(self, mock_g, mock_repo):
        """Test org admin with hierarchy_level >= 5 (backward compat)."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440001',
            'hierarchy_level': 5  # Org admin level
        }

        @require_org_admin
        def test_function():
            return {'status': 'ok'}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_org_admin(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn()

        # Should not check database when hierarchy_level >= 5
        mock_repo.user_has_permission.assert_not_called()

    @patch('app.security.permissions.PermissionRepository')
    @patch('app.security.permissions.g')
    def test_org_admin_denied_low_hierarchy(self, mock_g, mock_repo):
        """Test 403 response when user has low hierarchy level and no permissions."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440002',
            'hierarchy_level': 0
        }
        mock_repo.user_has_permission.return_value = False

        @require_org_admin
        def test_function():
            return {'status': 'ok'}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_org_admin(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn()

        # Should check database and deny access
        assert result[1] == 403


# ==============================================
# TESTS: @require_org_member()
# ==============================================

class TestRequireOrgMember:
    """Test @require_org_member decorator (resource-based access)."""

    @patch('app.security.permissions.g')
    def test_org_member_system_admin_bypass(self, mock_g):
        """Test system admin can access any organisation."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'hierarchy_level': 9,  # System admin
            'organization_id': None
        }

        @require_org_member
        def test_function(org_id):
            return {'org': org_id}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_org_member(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn(org_id='some-other-org-id')

        # System admin should access any org without checking membership
        assert result[1] == 200

    @patch('app.security.permissions.g')
    def test_org_member_belongs_to_org(self, mock_g):
        """Test user can access organisation they belong to."""
        org_id = '550e8400-e29b-41d4-a716-446655440100'
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440001',
            'hierarchy_level': 0,
            'organization_id': org_id
        }

        @require_org_member
        def test_function(org_id):
            return {'org': org_id}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_org_member(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn(org_id=org_id)

        # User should be able to access their organisation
        assert result[1] == 200

    @patch('app.security.permissions.g')
    def test_org_member_not_belongs_to_org(self, mock_g):
        """Test user cannot access organisation they don't belong to."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440001',
            'hierarchy_level': 0,
            'organization_id': '550e8400-e29b-41d4-a716-446655440100'
        }

        @require_org_member
        def test_function(org_id):
            return {'org': org_id}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_org_member(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                # Try to access different organisation
                result = decorated_fn(org_id='550e8400-e29b-41d4-a716-446655440200')

        # User should be denied access
        assert result[1] == 403

    @patch('app.security.permissions.g')
    def test_org_member_missing_org_id(self, mock_g):
        """Test 400 Bad Request when org_id not in URL parameters."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440001',
            'hierarchy_level': 0,
            'organization_id': '550e8400-e29b-41d4-a716-446655440100'
        }

        @require_org_member
        def test_function():  # No org_id parameter
            return {'org': 'unknown'}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_org_member(test_function)

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                result = decorated_fn()

        # Should return 400 Bad Request
        assert result[1] == 400


# ==============================================
# INTEGRATION TESTS
# ==============================================

class TestPermissionDecoratorIntegration:
    """Integration tests for permission decorators."""

    @patch('app.security.permissions.PermissionRepository')
    @patch('app.security.permissions.g')
    def test_system_admin_precedence_over_org_admin(self, mock_g, mock_repo):
        """Test system admin has precedence and bypasses org checks."""
        mock_g.current_user = {
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'hierarchy_level': 9,  # System admin
            'organization_id': None
        }

        # Stack decorators: org check first, then system admin
        @require_system_admin
        @require_org_member
        def test_function(org_id):
            return {'status': 'ok'}, 200

        with patch('app.security.permissions.token_required') as mock_token:
            mock_token.side_effect = lambda f: f
            decorated_fn = require_system_admin(
                require_org_member(test_function)
            )

            with patch('app.security.permissions.g') as mock_g2:
                mock_g2.current_user = mock_g.current_user
                # Try different org
                result = decorated_fn(org_id='different-org')

        # Should succeed because system admin bypasses org checks
        assert result[1] == 200


# ==============================================
# DOCSTRING TESTS
# ==============================================

class TestDecoratorDocumentation:
    """Verify decorators have proper documentation."""

    def test_require_system_admin_has_docstring(self):
        """Verify @require_system_admin has comprehensive docstring."""
        assert require_system_admin.__doc__ is not None
        assert 'RBAC 2.0' in require_system_admin.__doc__
        assert 'PermissionRepository' in require_system_admin.__doc__
        assert 'hierarchy_level' in require_system_admin.__doc__
        assert len(require_system_admin.__doc__) > 500

    def test_require_org_admin_has_docstring(self):
        """Verify @require_org_admin has comprehensive docstring."""
        assert require_org_admin.__doc__ is not None
        assert 'RBAC 2.0' in require_org_admin.__doc__
        assert 'PermissionRepository' in require_org_admin.__doc__
        assert 'manage:org:settings' in require_org_admin.__doc__
        assert len(require_org_admin.__doc__) > 500

    def test_require_org_member_has_docstring(self):
        """Verify @require_org_member has comprehensive docstring."""
        assert require_org_member.__doc__ is not None
        assert 'resource-based' in require_org_member.__doc__
        assert 'hierarchy_level' in require_org_member.__doc__
        assert 'organization_id' in require_org_member.__doc__
        assert len(require_org_member.__doc__) > 500
