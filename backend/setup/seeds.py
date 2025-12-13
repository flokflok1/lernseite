"""
LernsystemX Setup - Seed Data

Seeds initial data for:
- Learning methods (21 methods: basic, premium, pro)
- User roles (9 roles with hierarchy)
- Categories/Domains (5-level categorization)
- Default system data

ISO 9001:2015 compliant - Data standardization
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.database.connection import fetch_one, execute_query, insert_returning


class SeedData:
    """
    Seed initial system data

    Provides predefined data for learning methods, roles, and categories.
    """

    @classmethod
    def seed_all(cls, skip_existing: bool = True) -> Dict:
        """
        Seed all initial data

        Args:
            skip_existing: Skip if data already exists (default: True)

        Returns:
            Dictionary with seeding results (shows ACTUAL database counts, not just insertions)

        Example:
            >>> results = SeedData.seed_all()
            >>> print(f"Database has {results['learning_methods']} learning methods")
        """
        results = {
            'learning_methods': 0,
            'roles': 0,
            'categories': 0,
            'errors': []
        }

        try:
            # Attempt to seed learning methods
            cls.seed_learning_methods(skip_existing)

            # Attempt to seed roles
            cls.seed_roles(skip_existing)

            # Attempt to seed categories
            cls.seed_categories(skip_existing)

            # Return ACTUAL database counts (not insertion counts)
            # This ensures the user sees the correct numbers even if data already exists
            methods_result = fetch_one("SELECT COUNT(*) as count FROM learning_method_types")
            results['learning_methods'] = methods_result['count'] if methods_result else 0

            roles_result = fetch_one("SELECT COUNT(*) as count FROM roles")
            results['roles'] = roles_result['count'] if roles_result else 0

            categories_result = fetch_one("SELECT COUNT(*) as count FROM course_categories")
            results['categories'] = categories_result['count'] if categories_result else 0

        except Exception as e:
            results['errors'].append(str(e))

        return results

    @classmethod
    def seed_learning_methods(cls, skip_existing: bool = True) -> int:
        """
        Seed 21 learning method TYPES (11 basic, 6 premium, 4 pro)

        Args:
            skip_existing: Skip if method types already exist

        Returns:
            Number of learning method types created

        Example:
            >>> count = SeedData.seed_learning_methods()
            >>> print(f"Created {count} learning method types")
        """
        # Check if method types already exist
        if skip_existing:
            existing = fetch_one("SELECT COUNT(*) FROM learning_method_types")
            if existing and existing['count'] > 0:
                return 0

        learning_methods = [
            # Basic Methods (11) - Free for all users
            {
                'name': 'Flashcards',
                'description': 'Klassische Lernkarten mit Frage und Antwort',
                'tier': 'basic',
                'active': True,
                'config': {
                    'supports_images': True,
                    'supports_audio': True,
                    'ai_enabled': False,
                    'max_cards_per_set': 500
                }
            },
            {
                'name': 'Quiz',
                'description': 'Multiple-Choice Quiz mit sofortigem Feedback',
                'tier': 'basic',
                'active': True,
                'config': {
                    'question_types': ['multiple_choice', 'true_false', 'fill_blank'],
                    'ai_enabled': False,
                    'max_questions': 100
                }
            },
            {
                'name': 'Lückentext',
                'description': 'Texte mit Lücken zum Ausfüllen',
                'tier': 'basic',
                'active': True,
                'config': {
                    'auto_generate': False,
                    'difficulty_levels': ['easy', 'medium', 'hard']
                }
            },
            {
                'name': 'Multiple Choice',
                'description': 'Fragen mit mehreren Antwortmöglichkeiten',
                'tier': 'basic',
                'active': True,
                'config': {
                    'min_options': 2,
                    'max_options': 6,
                    'shuffle_answers': True
                }
            },
            {
                'name': 'True/False',
                'description': 'Wahr oder Falsch Fragen',
                'tier': 'basic',
                'active': True,
                'config': {
                    'explanation_required': True
                }
            },
            {
                'name': 'Zuordnung',
                'description': 'Zuordnungsaufgaben (Matching)',
                'tier': 'basic',
                'active': True,
                'config': {
                    'max_pairs': 20,
                    'shuffle_items': True
                }
            },
            {
                'name': 'Sortierung',
                'description': 'Elemente in richtige Reihenfolge bringen',
                'tier': 'basic',
                'active': True,
                'config': {
                    'max_items': 15,
                    'show_hints': True
                }
            },
            {
                'name': 'Mindmap',
                'description': 'Visuelles Mindmapping Tool',
                'tier': 'basic',
                'active': True,
                'config': {
                    'max_nodes': 100,
                    'supports_images': True,
                    'export_formats': ['png', 'pdf', 'json']
                }
            },
            {
                'name': 'Video',
                'description': 'Video-basiertes Lernen mit Notizen',
                'tier': 'basic',
                'active': True,
                'config': {
                    'supports_youtube': True,
                    'supports_vimeo': True,
                    'supports_upload': True,
                    'max_duration_minutes': 120
                }
            },
            {
                'name': 'Audio',
                'description': 'Audio-Lernmaterial (Podcasts, Vorlesungen)',
                'tier': 'basic',
                'active': True,
                'config': {
                    'supports_upload': True,
                    'max_duration_minutes': 180,
                    'playback_speeds': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
                }
            },
            {
                'name': 'PDF',
                'description': 'PDF-Dokumente mit Annotation-Funktion',
                'tier': 'basic',
                'active': True,
                'config': {
                    'max_size_mb': 50,
                    'supports_annotations': True,
                    'supports_highlights': True
                }
            },

            # Premium Methods (6) - Requires Premium subscription
            {
                'name': 'KI-Tutor',
                'description': 'KI-gestützter persönlicher Tutor',
                'tier': 'premium',
                'active': True,
                'config': {
                    'ai_model': 'gpt-4',
                    'context_memory': True,
                    'adaptive_difficulty': True,
                    'max_conversation_turns': 50
                }
            },
            {
                'name': 'KI-Glossar',
                'description': 'Automatisch generiertes Glossar mit KI-Erklärungen',
                'tier': 'premium',
                'active': True,
                'config': {
                    'auto_extract_terms': True,
                    'multilingual': True,
                    'max_terms': 500
                }
            },
            {
                'name': 'Braindump',
                'description': 'Freies Schreiben mit KI-Feedback',
                'tier': 'premium',
                'active': True,
                'config': {
                    'ai_feedback': True,
                    'grammar_check': True,
                    'structure_suggestions': True
                }
            },
            {
                'name': 'Zertifikatsprüfung',
                'description': 'Offizielle Prüfung mit Zertifikat',
                'tier': 'premium',
                'active': True,
                'config': {
                    'time_limited': True,
                    'proctoring_available': True,
                    'certificate_template': 'default',
                    'min_pass_percentage': 70
                }
            },
            {
                'name': 'Lernpfad-KI',
                'description': 'KI-optimierte personalisierte Lernpfade',
                'tier': 'premium',
                'active': True,
                'config': {
                    'adaptive_sequencing': True,
                    'difficulty_adjustment': True,
                    'prerequisite_checking': True
                }
            },
            {
                'name': 'Live-Raum',
                'description': 'Virtuelle Live-Sessions mit Videokonferenz',
                'tier': 'premium',
                'active': True,
                'config': {
                    'max_participants': 50,
                    'screen_sharing': True,
                    'whiteboard': True,
                    'recording': True
                }
            },

            # Pro Methods (4) - Requires Pro subscription
            {
                'name': 'Deep Praxis',
                'description': 'Tiefgreifende Praxisübungen mit KI-Bewertung',
                'tier': 'pro',
                'active': True,
                'config': {
                    'ai_code_review': True,
                    'ai_essay_feedback': True,
                    'complexity_levels': ['beginner', 'intermediate', 'advanced', 'expert'],
                    'peer_review': True
                }
            },
            {
                'name': 'Deep Scenario',
                'description': 'Komplexe Szenario-basierte Simulationen',
                'tier': 'pro',
                'active': True,
                'config': {
                    'branching_scenarios': True,
                    'ai_npcs': True,
                    'consequence_tracking': True,
                    'max_decision_points': 100
                }
            },
            {
                'name': 'Projekt-Simulation',
                'description': 'Realistische Projekt-Simulationen',
                'tier': 'pro',
                'active': True,
                'config': {
                    'team_collaboration': True,
                    'ai_stakeholders': True,
                    'resource_management': True,
                    'timeline_simulation': True
                }
            },
            {
                'name': 'Echtzeit-Debugging',
                'description': 'Live-Code-Debugging mit KI-Unterstützung',
                'tier': 'pro',
                'active': True,
                'config': {
                    'supported_languages': ['python', 'javascript', 'java', 'cpp', 'csharp'],
                    'ai_hints': True,
                    'step_by_step_debugging': True,
                    'code_execution': True
                }
            }
        ]

        created = 0
        for idx, method in enumerate(learning_methods, start=1):
            try:
                import json
                result = execute_query(
                    """
                    INSERT INTO learning_method_types (
                        method_number, name, description, tier, active, config, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (name) DO NOTHING
                    RETURNING *
                    """,
                    (
                        idx,
                        method['name'],
                        method['description'],
                        method['tier'],
                        method['active'],
                        json.dumps(method['config'])
                    ),
                    fetch_one=True
                )
                if result:
                    created += 1
            except Exception as e:
                print(f"Error creating learning method type '{method['name']}': {str(e)}")

        return created

    @classmethod
    def seed_roles(cls, skip_existing: bool = True) -> int:
        """
        Seed 9 user roles with hierarchy

        Args:
            skip_existing: Skip if roles already exist

        Returns:
            Number of roles created

        Example:
            >>> count = SeedData.seed_roles()
        """
        # Check if roles already exist
        if skip_existing:
            existing = fetch_one("SELECT COUNT(*) FROM roles")
            if existing and existing['count'] > 0:
                return 0

        roles = [
            {
                'name': 'user',
                'display_name': 'User',
                'description': 'Standard user with basic access',
                'hierarchy_level': 1,
                'permissions': {
                    'courses': ['view_public', 'enroll'],
                    'learning_methods': ['basic'],
                    'max_courses': 5
                }
            },
            {
                'name': 'premium',
                'display_name': 'Premium User',
                'description': 'Premium subscriber with extended features',
                'hierarchy_level': 2,
                'permissions': {
                    'courses': ['view_public', 'view_premium', 'enroll'],
                    'learning_methods': ['basic', 'premium'],
                    'max_courses': 50,
                    'ai_features': True,
                    'certificates': True
                }
            },
            {
                'name': 'creator',
                'display_name': 'Content Creator',
                'description': 'Can create and publish courses',
                'hierarchy_level': 3,
                'permissions': {
                    'courses': ['view_all', 'create', 'edit_own', 'publish'],
                    'learning_methods': ['basic', 'premium'],
                    'max_courses': 100,
                    'analytics': True,
                    'revenue_share': True
                }
            },
            {
                'name': 'teacher',
                'display_name': 'Teacher',
                'description': 'Teacher in school organisation',
                'hierarchy_level': 4,
                'permissions': {
                    'courses': ['view_all', 'create', 'edit_own', 'publish'],
                    'students': ['create', 'manage', 'grade'],
                    'learning_methods': ['basic', 'premium'],
                    'classes': ['create', 'manage'],
                    'reports': True
                }
            },
            {
                'name': 'school_admin',
                'display_name': 'School Administrator',
                'description': 'Administrator of school organisation',
                'hierarchy_level': 5,
                'permissions': {
                    'courses': ['view_all', 'create', 'edit_all', 'delete'],
                    'users': ['create', 'manage', 'delete'],
                    'teachers': ['manage'],
                    'learning_methods': ['basic', 'premium', 'pro'],
                    'organisation': ['manage_settings', 'manage_branding'],
                    'billing': ['view', 'manage']
                }
            },
            {
                'name': 'company_admin',
                'display_name': 'Company Administrator',
                'description': 'Administrator of company organisation',
                'hierarchy_level': 5,
                'permissions': {
                    'courses': ['view_all', 'create', 'edit_all', 'delete'],
                    'users': ['create', 'manage', 'delete'],
                    'learning_methods': ['basic', 'premium', 'pro'],
                    'organisation': ['manage_settings', 'manage_branding'],
                    'billing': ['view', 'manage'],
                    'analytics': ['advanced']
                }
            },
            {
                'name': 'moderator',
                'display_name': 'Moderator',
                'description': 'Content moderator',
                'hierarchy_level': 6,
                'permissions': {
                    'courses': ['view_all', 'edit_all', 'moderate'],
                    'users': ['view_all', 'moderate'],
                    'comments': ['delete', 'moderate'],
                    'reports': ['view', 'resolve']
                }
            },
            {
                'name': 'support',
                'display_name': 'Support',
                'description': 'Customer support team',
                'hierarchy_level': 7,
                'permissions': {
                    'users': ['view_all', 'edit_profile', 'reset_password'],
                    'tickets': ['view', 'respond', 'close'],
                    'courses': ['view_all'],
                    'logs': ['view']
                }
            },
            {
                'name': 'admin',
                'display_name': 'Administrator',
                'description': 'System administrator',
                'hierarchy_level': 8,
                'permissions': {
                    'all': True,
                    'system': ['manage_settings', 'manage_users', 'manage_organisations'],
                    'billing': ['view_all', 'manage_all'],
                    'analytics': ['full_access']
                }
            },
            {
                'name': 'superadmin',
                'display_name': 'Super Administrator',
                'description': 'Full system access',
                'hierarchy_level': 9,
                'permissions': {
                    'all': True,
                    'system': ['full_access'],
                    'database': ['access'],
                    'security': ['manage']
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
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (role_name) DO NOTHING
                    RETURNING *
                    """,
                    (
                        role['name'],
                        role['display_name'],
                        role['description'],
                        role['hierarchy_level']
                    ),
                    fetch_one=True
                )
                if result:
                    created += 1
            except Exception as e:
                print(f"Error creating role '{role['name']}': {str(e)}")

        return created

    @classmethod
    def seed_categories(cls, skip_existing: bool = True) -> int:
        """
        Seed default categories (5-level system)

        Args:
            skip_existing: Skip if categories already exist

        Returns:
            Number of categories created

        Example:
            >>> count = SeedData.seed_categories()
        """
        # Check if categories already exist
        if skip_existing:
            existing = fetch_one("SELECT COUNT(*) FROM course_categories")
            if existing and existing['count'] > 0:
                return 0

        # Top-level categories (Domains)
        categories = [
            {
                'name': 'Informatik & IT',
                'slug': 'informatik-it',
                'description': 'Computer Science, Software Development, IT',
                'parent_id': None,
                'level': 1,
                'icon': 'code',
                'color': '#3b82f6'
            },
            {
                'name': 'Mathematik',
                'slug': 'mathematik',
                'description': 'Mathematics, Statistics, Data Science',
                'parent_id': None,
                'level': 1,
                'icon': 'calculator',
                'color': '#8b5cf6'
            },
            {
                'name': 'Naturwissenschaften',
                'slug': 'naturwissenschaften',
                'description': 'Physics, Chemistry, Biology',
                'parent_id': None,
                'level': 1,
                'icon': 'atom',
                'color': '#10b981'
            },
            {
                'name': 'Sprachen',
                'slug': 'sprachen',
                'description': 'Languages and Linguistics',
                'parent_id': None,
                'level': 1,
                'icon': 'language',
                'color': '#f59e0b'
            },
            {
                'name': 'Business & Management',
                'slug': 'business-management',
                'description': 'Business, Economics, Management',
                'parent_id': None,
                'level': 1,
                'icon': 'briefcase',
                'color': '#06b6d4'
            },
            {
                'name': 'Kunst & Design',
                'slug': 'kunst-design',
                'description': 'Art, Design, Creative',
                'parent_id': None,
                'level': 1,
                'icon': 'palette',
                'color': '#ec4899'
            },
            {
                'name': 'Gesundheit & Medizin',
                'slug': 'gesundheit-medizin',
                'description': 'Health, Medicine, Nursing',
                'parent_id': None,
                'level': 1,
                'icon': 'heart',
                'color': '#ef4444'
            },
            {
                'name': 'Sozialwissenschaften',
                'slug': 'sozialwissenschaften',
                'description': 'Psychology, Sociology, Philosophy',
                'parent_id': None,
                'level': 1,
                'icon': 'users',
                'color': '#a855f7'
            }
        ]

        created = 0
        for category in categories:
            try:
                result = execute_query(
                    """
                    INSERT INTO course_categories (
                        name, slug, description, parent_id, level,
                        icon, color, active, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, true, NOW())
                    ON CONFLICT (slug) DO NOTHING
                    RETURNING *
                    """,
                    (
                        category['name'],
                        category['slug'],
                        category['description'],
                        category['parent_id'],
                        category['level'],
                        category['icon'],
                        category['color']
                    ),
                    fetch_one=True
                )
                if result:
                    created += 1
            except Exception as e:
                print(f"Error creating category '{category['name']}': {str(e)}")

        return created

    @classmethod
    def get_seeding_status(cls) -> Dict:
        """
        Get current seeding status

        Returns:
            Dictionary with counts of seeded data

        Example:
            >>> status = SeedData.get_seeding_status()
            >>> print(f"Learning method types: {status['learning_methods']}")
        """
        try:
            methods_count = fetch_one("SELECT COUNT(*) FROM learning_method_types")
            roles_count = fetch_one("SELECT COUNT(*) FROM roles")
            categories_count = fetch_one("SELECT COUNT(*) FROM course_categories")

            return {
                'learning_methods': methods_count['count'] if methods_count else 0,
                'roles': roles_count['count'] if roles_count else 0,
                'categories': categories_count['count'] if categories_count else 0,
                'expected': {
                    'learning_methods': 21,
                    'roles': 10,
                    'categories': 8
                }
            }
        except Exception:
            return {
                'learning_methods': 0,
                'roles': 0,
                'categories': 0,
                'expected': {
                    'learning_methods': 21,
                    'roles': 10,
                    'categories': 8
                }
            }


# Convenience functions
def seed_all(**kwargs) -> Dict:
    """Quick function to seed all data"""
    return SeedData.seed_all(**kwargs)


def seed_learning_methods(**kwargs) -> int:
    """Quick function to seed learning methods"""
    return SeedData.seed_learning_methods(**kwargs)


def seed_roles(**kwargs) -> int:
    """Quick function to seed roles"""
    return SeedData.seed_roles(**kwargs)


def seed_categories(**kwargs) -> int:
    """Quick function to seed categories"""
    return SeedData.seed_categories(**kwargs)
