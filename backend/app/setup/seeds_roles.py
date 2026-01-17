"""
LernsystemX Setup - Seed Data - User Roles

Seeds initial data for:
- User roles (9 roles with hierarchy: 1-9)
  - Hierarchy level 1: Guest (Community)
  - Hierarchy level 2: Free user (Student)
  - Hierarchy level 3: Premium (Learner)
  - Hierarchy level 4: Creator
  - Hierarchy level 5: Teacher
  - Hierarchy level 6: School Admin
  - Hierarchy level 7: Company Admin
  - Hierarchy level 8: Support/Moderator
  - Hierarchy level 9: System Admin

ISO 9001:2015 compliant - Data standardization

For learning methods, see:
- seeds.py: Core seeding functions
- seeds_config.py: System features & categories
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.database.connection import fetch_one, execute_query, insert_returning


class SeedDataRoles:
    """
    Seed user roles

    Provides predefined data for 9-level role hierarchy.
    """

    @classmethod
    def seed_roles(cls, skip_existing: bool = True) -> int:
        """
        Seed 9 user roles with hierarchy

        Hierarchy:
        - Level 1: Guest (read-only community access)
        - Level 2: Free/Student (basic learning)
        - Level 3: Premium (advanced features, tokens)
        - Level 4: Creator (can create content)
        - Level 5: Teacher (manage classes, students)
        - Level 6: School Admin (manage organization)
        - Level 7: Company Admin (manage enterprise)
        - Level 8: Support/Moderator (content moderation)
        - Level 9: System Admin (full system access)

        Args:
            skip_existing: Skip if roles already exist

        Returns:
            Number of roles created

        Example:
            >>> count = SeedDataRoles.seed_roles()
            >>> print(f"Created {count} roles")
        """
        # Check if roles already exist
        if skip_existing:
            existing = fetch_one("SELECT COUNT(*) FROM roles")
            if existing and existing['count'] > 0:
                return 0

        roles = [
            {
                'role_name': 'guest',
                'display_name': 'Gast',
                'description': 'Schreibgeschützter Community-Zugriff',
                'hierarchy_level': 1,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0000000001,  # Read-only
                'config': {
                    'can_read': True,
                    'can_create': False,
                    'can_edit': False,
                    'can_delete': False,
                    'can_access_premium': False,
                    'can_manage_users': False,
                    'max_courses': 0,
                    'max_lessons_per_course': 0
                }
            },
            {
                'role_name': 'free',
                'display_name': 'Kostenlos',
                'description': 'Grundlegende Lernfunktionen',
                'hierarchy_level': 2,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0000000011,  # Read + Write
                'config': {
                    'can_read': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': False,
                    'can_access_premium': False,
                    'can_manage_users': False,
                    'max_courses': 5,
                    'max_lessons_per_course': 50,
                    'monthly_tokens': 1000
                }
            },
            {
                'role_name': 'premium',
                'display_name': 'Premium',
                'description': 'Erweiterte Lernfunktionen mit KI-Features',
                'hierarchy_level': 3,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0000000111,  # Read + Write + Premium
                'config': {
                    'can_read': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_access_premium': True,
                    'can_manage_users': False,
                    'max_courses': 20,
                    'max_lessons_per_course': 500,
                    'monthly_tokens': 10000,
                    'ai_features_enabled': True,
                    'advanced_analytics': True
                }
            },
            {
                'role_name': 'creator',
                'display_name': 'Inhaltsersteller',
                'description': 'Kann Kurse und Inhalte erstellen',
                'hierarchy_level': 4,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0000001111,  # All basic + creator
                'config': {
                    'can_read': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_access_premium': True,
                    'can_manage_users': False,
                    'can_publish_content': True,
                    'max_courses': 100,
                    'max_lessons_per_course': 5000,
                    'monthly_tokens': 20000,
                    'ai_features_enabled': True,
                    'advanced_analytics': True,
                    'content_library_access': True
                }
            },
            {
                'role_name': 'teacher',
                'display_name': 'Lehrer',
                'description': 'Verwaltet Klassen und Schüler',
                'hierarchy_level': 5,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0000011111,  # Creator + teacher
                'config': {
                    'can_read': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_access_premium': True,
                    'can_manage_users': True,
                    'can_manage_organization': False,
                    'can_publish_content': True,
                    'max_courses': 200,
                    'max_lessons_per_course': 10000,
                    'monthly_tokens': 50000,
                    'ai_features_enabled': True,
                    'advanced_analytics': True,
                    'content_library_access': True,
                    'classroom_management': True,
                    'student_progress_tracking': True,
                    'assignment_grading': True
                }
            },
            {
                'role_name': 'school_admin',
                'display_name': 'Schul-Administrator',
                'description': 'Verwaltet Schulorganisation',
                'hierarchy_level': 6,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0000111111,  # Teacher + school admin
                'config': {
                    'can_read': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_access_premium': True,
                    'can_manage_users': True,
                    'can_manage_organization': True,
                    'can_manage_school': True,
                    'can_publish_content': True,
                    'organization_level': 'school',
                    'unlimited_courses': True,
                    'monthly_tokens': 100000,
                    'ai_features_enabled': True,
                    'advanced_analytics': True,
                    'content_library_access': True,
                    'classroom_management': True,
                    'student_progress_tracking': True,
                    'assignment_grading': True,
                    'bulk_operations': True,
                    'sso_integration': True
                }
            },
            {
                'role_name': 'company_admin',
                'display_name': 'Unternehmens-Administrator',
                'description': 'Verwaltet Unternehmensorganisation',
                'hierarchy_level': 7,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0001111111,  # School admin + company
                'config': {
                    'can_read': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_access_premium': True,
                    'can_manage_users': True,
                    'can_manage_organization': True,
                    'can_manage_enterprise': True,
                    'can_publish_content': True,
                    'organization_level': 'enterprise',
                    'unlimited_courses': True,
                    'unlimited_users': True,
                    'monthly_tokens': 500000,
                    'ai_features_enabled': True,
                    'advanced_analytics': True,
                    'content_library_access': True,
                    'classroom_management': True,
                    'student_progress_tracking': True,
                    'assignment_grading': True,
                    'bulk_operations': True,
                    'sso_integration': True,
                    'api_access': True,
                    'white_label_options': True,
                    'custom_branding': True,
                    'advanced_security': True
                }
            },
            {
                'role_name': 'moderator',
                'display_name': 'Moderator',
                'description': 'Moderiert Inhalte und Community',
                'hierarchy_level': 8,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0011111111,  # Company admin + moderation
                'config': {
                    'can_read': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_access_premium': True,
                    'can_manage_users': True,
                    'can_moderate_content': True,
                    'can_moderate_community': True,
                    'can_suspend_users': True,
                    'unlimited_courses': True,
                    'unlimited_users': True,
                    'monthly_tokens': 100000,
                    'ai_features_enabled': True,
                    'advanced_analytics': True,
                    'content_library_access': True,
                    'moderation_tools': True,
                    'user_suspension': True,
                    'content_removal': True,
                    'report_handling': True,
                    'audit_logs': True
                }
            },
            {
                'role_name': 'admin',
                'display_name': 'System-Administrator',
                'description': 'Vollständiger Systemzugriff',
                'hierarchy_level': 9,
                'is_system_role': True,
                'active': True,
                'permissions_mask': 0b0111111111,  # All permissions
                'config': {
                    'can_read': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_access_premium': True,
                    'can_manage_users': True,
                    'can_manage_system': True,
                    'can_manage_infrastructure': True,
                    'can_access_logs': True,
                    'can_access_database': True,
                    'unlimited_courses': True,
                    'unlimited_users': True,
                    'unlimited_tokens': True,
                    'ai_features_enabled': True,
                    'advanced_analytics': True,
                    'content_library_access': True,
                    'moderation_tools': True,
                    'user_suspension': True,
                    'system_monitoring': True,
                    'security_settings': True,
                    'api_access': True,
                    'white_label_options': True,
                    'custom_branding': True,
                    'advanced_security': True,
                    'backup_restore': True,
                    'audit_logs': True,
                    'full_system_access': True
                }
            }
        ]

        created = 0
        for role in roles:
            try:
                import json
                result = execute_query(
                    """
                    INSERT INTO roles (
                        role_name, display_name, description, hierarchy_level,
                        is_system_role, active, permissions_mask, config, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (role_name) DO NOTHING
                    RETURNING *
                    """,
                    (
                        role['role_name'],
                        role['display_name'],
                        role['description'],
                        role['hierarchy_level'],
                        role['is_system_role'],
                        role['active'],
                        role['permissions_mask'],
                        json.dumps(role['config'])
                    ),
                    fetch_one=True
                )
                if result:
                    created += 1
            except Exception as e:
                print(f"Error creating role '{role['role_name']}': {str(e)}")

        return created


# Convenience function
def seed_roles(**kwargs) -> int:
    """Quick function to seed roles"""
    return SeedDataRoles.seed_roles(**kwargs)
