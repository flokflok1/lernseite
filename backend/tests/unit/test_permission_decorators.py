"""
Unit Tests for GBA Permission Decorators (Compatibility Wrapper)

Tests the GBA compatibility wrapper decorators:
- @require_system_admin - System admin access (GBA via PermissionService)
- @require_org_admin - Organisation admin access (GBA via PermissionService)
- @require_org_member - Organisation membership check (resource-based)

Tests verify:
- Correct access granted to authorized users
- Access denied (403) to unauthorized users
- PermissionService.check_permission() integration
- Fail-secure behavior on service errors
- Proper error responses

Architecture Note:
- Decorators use _get_token_required() for lazy import of @token_required
- PermissionService.check_permission(current_user, permission_code) is imported
  lazily inside each wrapper function
- g.current_user provides the authenticated user dict from JWT
"""

import pytest
from unittest.mock import patch, MagicMock
import types

import app.infrastructure.security.gba.permissions_compat as compat_module

# Module path constants for patching
COMPAT_MODULE = 'app.infrastructure.security.gba.permissions_compat'
PERMISSION_SERVICE = (
    'app.application.services.system.auth.permission.PermissionService'
)


def _make_mock_g(user_dict):
    """Create a mock g object with current_user attribute.

    We cannot use patch() on Flask's g proxy because it triggers
    application context checks. Instead, we replace the module-level
    reference to g with a simple namespace object.
    """
    mock_g = types.SimpleNamespace(current_user=user_dict)
    return mock_g


# ==============================================
# FIXTURES
# ==============================================

@pytest.fixture
def system_admin_user():
    """Create mock system admin user."""
    return {
        'user_id': '550e8400-e29b-41d4-a716-446655440000',
        'role': 'admin',
        'organisation_id': None,
    }


@pytest.fixture
def org_admin_user():
    """Create mock organisation admin user."""
    return {
        'user_id': '550e8400-e29b-41d4-a716-446655440001',
        'role': 'school_admin',
        'organisation_id': '550e8400-e29b-41d4-a716-446655440100',
    }


@pytest.fixture
def regular_user():
    """Create mock regular user."""
    return {
        'user_id': '550e8400-e29b-41d4-a716-446655440002',
        'role': 'user',
        'organisation_id': '550e8400-e29b-41d4-a716-446655440100',
    }


@pytest.fixture
def other_org_user():
    """Create mock user from different organisation."""
    return {
        'user_id': '550e8400-e29b-41d4-a716-446655440003',
        'role': 'user',
        'organisation_id': '550e8400-e29b-41d4-a716-446655440200',
    }


# ==============================================
# TESTS: @require_system_admin
# ==============================================

class TestRequireSystemAdmin:
    """Test @require_system_admin decorator."""

    def test_system_admin_access_granted(self, system_admin_user):
        """Test system admin access when PermissionService grants it."""
        mock_g = _make_mock_g(system_admin_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check:

            mock_token.return_value = lambda f: f
            mock_check.return_value = True
            compat_module.g = mock_g

            try:
                @compat_module.require_system_admin
                def protected_view():
                    return {'status': 'ok'}, 200

                result = protected_view()
            finally:
                compat_module.g = original_g

            assert result == ({'status': 'ok'}, 200)
            mock_check.assert_called_once_with(
                system_admin_user, 'view_any_resource'
            )

    def test_system_admin_access_denied(self, regular_user):
        """Test 403 response when user lacks system admin permission."""
        mock_g = _make_mock_g(regular_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check, \
             patch(f'{COMPAT_MODULE}.jsonify') as mock_jsonify:

            mock_token.return_value = lambda f: f
            mock_check.return_value = False
            mock_jsonify.return_value = MagicMock()
            compat_module.g = mock_g

            try:
                @compat_module.require_system_admin
                def protected_view():
                    return {'status': 'ok'}, 200

                result = protected_view()
            finally:
                compat_module.g = original_g

            assert result[1] == 403
            mock_check.assert_called_once_with(
                regular_user, 'view_any_resource'
            )

    def test_system_admin_service_error_fail_secure(self, regular_user):
        """Test fail-secure: exception from PermissionService propagates."""
        mock_g = _make_mock_g(regular_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check:

            mock_token.return_value = lambda f: f
            mock_check.side_effect = Exception("Service Error")
            compat_module.g = mock_g

            try:
                @compat_module.require_system_admin
                def protected_view():
                    return {'status': 'ok'}, 200

                with pytest.raises(Exception, match="Service Error"):
                    protected_view()
            finally:
                compat_module.g = original_g


# ==============================================
# TESTS: @require_org_admin
# ==============================================

class TestRequireOrgAdmin:
    """Test @require_org_admin decorator."""

    def test_org_admin_with_users_manage_permission(self, org_admin_user):
        """Test org admin access via users.manage permission."""
        mock_g = _make_mock_g(org_admin_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check:

            mock_token.return_value = lambda f: f
            mock_check.return_value = True
            compat_module.g = mock_g

            try:
                @compat_module.require_org_admin
                def protected_view():
                    return {'status': 'ok'}, 200

                result = protected_view()
            finally:
                compat_module.g = original_g

            assert result == ({'status': 'ok'}, 200)
            mock_check.assert_any_call(org_admin_user, 'users.manage')

    def test_org_admin_with_system_admin_bypass(self, system_admin_user):
        """Test system admin bypasses org admin via view_any_resource."""
        mock_g = _make_mock_g(system_admin_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check:

            mock_token.return_value = lambda f: f

            def side_effect(user, perm):
                if perm == 'view_any_resource':
                    return True
                return False

            mock_check.side_effect = side_effect
            compat_module.g = mock_g

            try:
                @compat_module.require_org_admin
                def protected_view():
                    return {'status': 'ok'}, 200

                result = protected_view()
            finally:
                compat_module.g = original_g

            assert result == ({'status': 'ok'}, 200)

    def test_org_admin_denied_no_permission(self, regular_user):
        """Test 403 when user has neither users.manage nor view_any_resource."""
        mock_g = _make_mock_g(regular_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check, \
             patch(f'{COMPAT_MODULE}.jsonify') as mock_jsonify:

            mock_token.return_value = lambda f: f
            mock_check.return_value = False
            mock_jsonify.return_value = MagicMock()
            compat_module.g = mock_g

            try:
                @compat_module.require_org_admin
                def protected_view():
                    return {'status': 'ok'}, 200

                result = protected_view()
            finally:
                compat_module.g = original_g

            assert result[1] == 403


# ==============================================
# TESTS: @require_org_member
# ==============================================

class TestRequireOrgMember:
    """Test @require_org_member decorator (resource-based access)."""

    def test_org_member_system_admin_bypass(self, system_admin_user):
        """Test system admin can access any org via view_any_resource."""
        mock_g = _make_mock_g(system_admin_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check:

            mock_token.return_value = lambda f: f
            mock_check.return_value = True
            compat_module.g = mock_g

            try:
                @compat_module.require_org_member
                def protected_view(org_id):
                    return {'org': org_id}, 200

                result = protected_view(org_id='some-other-org-id')
            finally:
                compat_module.g = original_g

            assert result[1] == 200
            mock_check.assert_called_with(
                system_admin_user, 'view_any_resource'
            )

    def test_org_member_belongs_to_org(self, regular_user):
        """Test user can access organisation they belong to."""
        org_id = regular_user['organisation_id']
        mock_g = _make_mock_g(regular_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check:

            mock_token.return_value = lambda f: f
            mock_check.return_value = False  # Not a system admin
            compat_module.g = mock_g

            try:
                @compat_module.require_org_member
                def protected_view(org_id):
                    return {'org': org_id}, 200

                result = protected_view(org_id=org_id)
            finally:
                compat_module.g = original_g

            assert result == ({'org': org_id}, 200)

    def test_org_member_not_belongs_to_org(self, regular_user):
        """Test user cannot access organisation they do not belong to."""
        mock_g = _make_mock_g(regular_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check, \
             patch(f'{COMPAT_MODULE}.jsonify') as mock_jsonify:

            mock_token.return_value = lambda f: f
            mock_check.return_value = False
            mock_jsonify.return_value = MagicMock()
            compat_module.g = mock_g

            try:
                @compat_module.require_org_member
                def protected_view(org_id):
                    return {'org': org_id}, 200

                result = protected_view(
                    org_id='550e8400-e29b-41d4-a716-446655440200'
                )
            finally:
                compat_module.g = original_g

            assert result[1] == 403

    def test_org_member_missing_org_id(self, regular_user):
        """Test 400 Bad Request when org_id not in kwargs."""
        mock_g = _make_mock_g(regular_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check, \
             patch(f'{COMPAT_MODULE}.jsonify') as mock_jsonify:

            mock_token.return_value = lambda f: f
            mock_check.return_value = False
            mock_jsonify.return_value = MagicMock()
            compat_module.g = mock_g

            try:
                @compat_module.require_org_member
                def protected_view():
                    return {'org': 'unknown'}, 200

                result = protected_view()
            finally:
                compat_module.g = original_g

            assert result[1] == 400


# ==============================================
# INTEGRATION TESTS
# ==============================================

class TestPermissionDecoratorIntegration:
    """Integration tests for permission decorators."""

    def test_system_admin_has_more_power_than_org_admin(
        self, system_admin_user
    ):
        """Test system admin bypasses org membership checks."""
        mock_g = _make_mock_g(system_admin_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check:

            mock_token.return_value = lambda f: f
            mock_check.return_value = True
            compat_module.g = mock_g

            try:
                inner = compat_module.require_org_member(
                    lambda org_id: ({'status': 'ok'}, 200)
                )
                decorated = compat_module.require_system_admin(inner)
                result = decorated(org_id='different-org')
            finally:
                compat_module.g = original_g

            assert result[1] == 200

    def test_regular_user_denied_system_admin_route(self, regular_user):
        """Test regular user cannot access system admin protected route."""
        mock_g = _make_mock_g(regular_user)
        original_g = compat_module.g

        with patch(f'{COMPAT_MODULE}._get_token_required') as mock_token, \
             patch(f'{PERMISSION_SERVICE}.check_permission') as mock_check, \
             patch(f'{COMPAT_MODULE}.jsonify') as mock_jsonify:

            mock_token.return_value = lambda f: f
            mock_check.return_value = False
            mock_jsonify.return_value = MagicMock()
            compat_module.g = mock_g

            try:
                @compat_module.require_system_admin
                def admin_only_view():
                    return {'status': 'ok'}, 200

                result = admin_only_view()
            finally:
                compat_module.g = original_g

            assert result[1] == 403


# ==============================================
# DOCSTRING TESTS
# ==============================================

class TestDecoratorDocumentation:
    """Verify decorators have proper documentation."""

    def test_require_system_admin_has_docstring(self):
        """Verify @require_system_admin has GBA-related docstring."""
        assert compat_module.require_system_admin.__doc__ is not None
        doc = compat_module.require_system_admin.__doc__
        assert 'GBA' in doc or 'compatibility wrapper' in doc.lower()

    def test_require_org_admin_has_docstring(self):
        """Verify @require_org_admin has GBA-related docstring."""
        assert compat_module.require_org_admin.__doc__ is not None
        doc = compat_module.require_org_admin.__doc__
        assert 'GBA' in doc or 'compatibility wrapper' in doc.lower()

    def test_require_org_member_has_docstring(self):
        """Verify @require_org_member has organisation-related docstring."""
        assert compat_module.require_org_member.__doc__ is not None
        doc = compat_module.require_org_member.__doc__
        assert 'organisation' in doc.lower() or 'organization' in doc.lower()
