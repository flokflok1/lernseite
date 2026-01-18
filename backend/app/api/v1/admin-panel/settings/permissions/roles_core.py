"""
RBAC 2.0 - Roles Core Components

Shared templates, models, and utilities for role management.

Phase 5.3 - Owner-Admin & Dynamic Roles System
"""

from app.domain.models.admin_roles import RoleTemplate

# ============================================================================
# Role Templates Configuration
# ============================================================================

ROLE_TEMPLATES = {
    RoleTemplate.PARENT: {
        'display_name': 'Parent',
        'description': 'Parental control account for child activity monitoring',
        'recommended_hierarchy': 2,
        'default_features': ['content_approval', 'activity_reports'],
        'default_color': '#10b981',
        'default_icon': '👪'
    },
    RoleTemplate.ENTERPRISE_ADMIN: {
        'display_name': 'Enterprise Admin',
        'description': 'Enterprise administrator with bulk management features',
        'recommended_hierarchy': 6,
        'default_features': ['bulk_import', 'sso_config', 'advanced_analytics'],
        'default_color': '#3b82f6',
        'default_icon': '🏢'
    },
    RoleTemplate.AUDITOR: {
        'display_name': 'Auditor',
        'description': 'Compliance auditor with read-only access to logs and reports',
        'recommended_hierarchy': 7,
        'default_features': ['audit_logs', 'compliance_reports', 'export_data'],
        'default_color': '#8b5cf6',
        'default_icon': '🔍'
    },
    RoleTemplate.LIBRARIAN: {
        'display_name': 'Librarian',
        'description': 'Content curator for managing course catalog',
        'recommended_hierarchy': 5,
        'default_features': ['content_moderation', 'category_management'],
        'default_color': '#f59e0b',
        'default_icon': '📚'
    },
    RoleTemplate.COURSE_MANAGER: {
        'display_name': 'Course Manager',
        'description': 'Course management without full admin access',
        'recommended_hierarchy': 4,
        'default_features': ['course_crud', 'course_publishing', 'course_analytics'],
        'default_color': '#06b6d4',
        'default_icon': '🎓'
    }
}


# ============================================================================
# Helper Functions
# ============================================================================

def format_role_response(role: dict, include_counts: bool = False) -> dict:
    """
    Format role data for API response.

    Args:
        role: Role dictionary from repository
        include_counts: Whether to include feature/permission/user counts

    Returns:
        Formatted role data dictionary
    """
    formatted = {
        'role_id': role['role_id'],
        'role_name': role['role_name'],
        'display_name': role['display_name'],
        'description': role['description'],
        'hierarchy_level': role['hierarchy_level'],
        'color': role['color'],
        'icon': role['icon'],
        'is_builtin': role['is_builtin'],
        'is_administrator': role['is_administrator'],
        'created_at': role['created_at'].isoformat() if role['created_at'] else None,
        'updated_at': role['updated_at'].isoformat() if role['updated_at'] else None,
        'created_by': str(role['created_by']) if role.get('created_by') else None,
    }

    if include_counts:
        formatted.update({
            'feature_count': role.get('feature_count', 0),
            'permission_count': role.get('permission_count', 0),
            'user_count': role.get('user_count', 0)
        })

    return formatted


def format_feature_response(feature: dict) -> dict:
    """
    Format feature data for API response.

    Args:
        feature: Feature dictionary from repository

    Returns:
        Formatted feature data dictionary
    """
    return {
        'feature_id': feature['feature_id'],
        'feature_code': feature['feature_code'],
        'feature_name': feature['feature_name'],
        'category': feature['category'],
        'active': feature['active'],
        'enabled_for_role': feature['enabled_for_role']
    }


def format_permission_response(permission: dict) -> dict:
    """
    Format permission data for API response.

    Args:
        permission: Permission dictionary from repository

    Returns:
        Formatted permission data dictionary
    """
    return {
        'permission_id': permission['permission_id'],
        'permission_key': permission['permission_key'],
        'display_name': permission.get('display_name'),
        'description': permission.get('description'),
        'module': permission.get('module'),
        'category': permission.get('category')
    }


__all__ = [
    'ROLE_TEMPLATES',
    'format_role_response',
    'format_feature_response',
    'format_permission_response'
]
