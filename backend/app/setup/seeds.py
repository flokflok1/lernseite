"""
LernsystemX Setup - Seed Data - Core

Seeds initial data for:
- Learning methods (12 Content-Lernmethoden: lm00-lm11)
  - Gruppe A (Erklärend): lm00-lm04 (5 methods)
  - Gruppe B (Praxis): lm05-lm08 (4 methods)
  - Gruppe C (Prüfung): lm09-lm11 (3 methods)

For system features, user roles, and categories, see:
- seeds_config.py: System features & categories
- seeds_roles.py: User roles

ISO 9001:2015 compliant - Data standardization
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, execute_query, insert_returning


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
            'learning_methods_with_ui_schemas': 0,
            'system_features': 0,
            'system_features_with_ui_schemas': 0,
            'categories': 0,
            'errors': []
        }

        try:
            # Attempt to seed learning methods
            cls.seed_learning_methods(skip_existing)

            # Attempt to seed system features (from seeds_config)
            from app.setup.seeds_config import SeedDataConfig
            SeedDataConfig.seed_system_features(skip_existing)

            # Note: Roles have been replaced by Groups (PHASE B migration)
            # Groups are seeded in migrations: 020_groups_table.sql onwards

            # Attempt to seed categories (from seeds_config)
            SeedDataConfig.seed_categories(skip_existing)

            # Seed UI schemas for learning methods and system features (NEW - Phase 5)
            from app.setup.seeds_ui_schemas import SeedDataUISchemas
            SeedDataUISchemas.seed_learning_methods_ui_schemas(skip_existing)
            SeedDataUISchemas.seed_system_features_ui_schemas(skip_existing)

            # Return ACTUAL database counts (not insertion counts)
            # This ensures the user sees the correct numbers even if data already exists
            methods_result = fetch_one("SELECT COUNT(*) as count FROM learning_method_types")
            results['learning_methods'] = methods_result['count'] if methods_result else 0

            methods_with_schemas = fetch_one(
                "SELECT COUNT(*) as count FROM learning_method_types WHERE ui_schema IS NOT NULL"
            )
            results['learning_methods_with_ui_schemas'] = methods_with_schemas['count'] if methods_with_schemas else 0

            features_result = fetch_one("SELECT COUNT(*) as count FROM support_systems.system_features")
            results['system_features'] = features_result['count'] if features_result else 0

            features_with_schemas = fetch_one(
                "SELECT COUNT(*) as count FROM support_systems.system_features WHERE ui_schema IS NOT NULL"
            )
            results['system_features_with_ui_schemas'] = features_with_schemas['count'] if features_with_schemas else 0

            # Note: Roles replaced by Groups - count groups instead
            groups_result = fetch_one("SELECT COUNT(*) as count FROM core.groups")
            results['groups'] = groups_result['count'] if groups_result else 0

            categories_result = fetch_one("SELECT COUNT(*) as count FROM course_categories")
            results['categories'] = categories_result['count'] if categories_result else 0

        except Exception as e:
            results['errors'].append(str(e))

        return results

    @classmethod
    def seed_learning_methods(cls, skip_existing: bool = True) -> int:
        """
        Seed 12 Content-Lernmethoden (lm00-lm11)

        Gruppe A (Erklärend): lm00-lm04
        Gruppe B (Praxis): lm05-lm08
        Gruppe C (Prüfung): lm09-lm11

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
            # Gruppe A - Erklärend (5 Methoden)
            {
                'method_type': 0,
                'name': 'Tiefgehende Erklärung',
                'description': 'Ausführliche KI-gestützte Erklärung von Konzepten',
                'group_code': 'A',
                'tier': 'basic',
                'ki_usage': 'intensiv',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'supports_examples': True,
                    'supports_diagrams': True
                }
            },
            {
                'method_type': 1,
                'name': 'Schritt-für-Schritt',
                'description': 'Schrittweise Anleitung durch komplexe Themen',
                'group_code': 'A',
                'tier': 'basic',
                'ki_usage': 'mittel',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'numbered_steps': True,
                    'interactive': True
                }
            },
            {
                'method_type': 2,
                'name': 'Interaktive Theorie',
                'description': 'Interaktive Theorievermittlung mit Fragen',
                'group_code': 'A',
                'tier': 'basic',
                'ki_usage': 'mittel',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'inline_questions': True,
                    'adaptive_content': True
                }
            },
            {
                'method_type': 3,
                'name': 'Diagramm/Visualisierung',
                'description': 'Visuelle Darstellung von Konzepten',
                'group_code': 'A',
                'tier': 'basic',
                'ki_usage': 'mittel',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'diagram_types': ['flowchart', 'mindmap', 'timeline', 'network'],
                    'export_formats': ['png', 'svg', 'pdf']
                }
            },
            {
                'method_type': 4,
                'name': 'Beispiel-Szenario',
                'description': 'Praxisnahe Beispiele und Szenarien',
                'group_code': 'A',
                'tier': 'basic',
                'ki_usage': 'mittel',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'context_adaptable': True,
                    'real_world_examples': True
                }
            },

            # Gruppe B - Praxis (4 Methoden)
            {
                'method_type': 5,
                'name': 'Mathe-Interaktiv',
                'description': 'Interaktive Mathematik-Aufgaben',
                'group_code': 'B',
                'tier': 'basic',
                'ki_usage': 'mittel',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'step_by_step_solution': True,
                    'latex_support': True,
                    'formula_editor': True
                }
            },
            {
                'method_type': 6,
                'name': 'Flashcards',
                'description': 'Klassische Lernkarten mit Frage und Antwort',
                'group_code': 'B',
                'tier': 'basic',
                'ki_usage': 'optional',
                'active': True,
                'config': {
                    'supports_images': True,
                    'supports_audio': True,
                    'ai_enabled': False,
                    'max_cards_per_set': 500,
                    'spaced_repetition': True
                }
            },
            {
                'method_type': 7,
                'name': 'Drag & Drop',
                'description': 'Zuordnungs- und Sortieraufgaben',
                'group_code': 'B',
                'tier': 'basic',
                'ki_usage': 'optional',
                'active': True,
                'config': {
                    'ai_enabled': False,
                    'max_items': 20,
                    'shuffle_items': True,
                    'supports_images': True
                }
            },
            {
                'method_type': 8,
                'name': 'Lückentext',
                'description': 'Texte mit Lücken zum Ausfüllen',
                'group_code': 'B',
                'tier': 'basic',
                'ki_usage': 'optional',
                'active': True,
                'config': {
                    'ai_enabled': False,
                    'auto_generate': True,
                    'difficulty_levels': ['easy', 'medium', 'hard'],
                    'hint_system': True
                }
            },

            # Gruppe C - Prüfung (3 Methoden)
            {
                'method_type': 9,
                'name': 'Freitext-Langantwort',
                'description': 'Lange Textantworten mit KI-Bewertung',
                'group_code': 'C',
                'tier': 'premium',
                'ki_usage': 'mittel',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'ai_grading': True,
                    'min_words': 50,
                    'max_words': 1000,
                    'rubric_support': True
                }
            },
            {
                'method_type': 10,
                'name': 'IHK-Stil Aufgaben',
                'description': 'Prüfungsaufgaben im IHK-Format',
                'group_code': 'C',
                'tier': 'premium',
                'ki_usage': 'intensiv',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'question_types': ['gebunden', 'ungebunden', 'handlungssituation'],
                    'points_based_grading': True,
                    'time_tracking': True
                }
            },
            {
                'method_type': 11,
                'name': 'Multi-Step Praxisprüfung',
                'description': 'Mehrstufige praktische Prüfung',
                'group_code': 'C',
                'tier': 'premium',
                'ki_usage': 'intensiv',
                'active': True,
                'config': {
                    'ai_enabled': True,
                    'min_steps': 2,
                    'max_steps': 10,
                    'progressive_unlock': True,
                    'partial_grading': True
                }
            }
        ]

        created = 0
        for method in learning_methods:
            try:
                import json
                result = execute_query(
                    """
                    INSERT INTO learning_method_types (
                        method_type, name, description, group_code, tier,
                        ki_usage, active, config, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (method_type) DO NOTHING
                    RETURNING *
                    """,
                    (
                        method['method_type'],
                        method['name'],
                        method['description'],
                        method['group_code'],
                        method['tier'],
                        method['ki_usage'],
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
            features_count = fetch_one("SELECT COUNT(*) FROM support_systems.system_features")
            groups_count = fetch_one("SELECT COUNT(*) FROM core.groups")
            categories_count = fetch_one("SELECT COUNT(*) FROM course_categories")

            return {
                'learning_methods': methods_count['count'] if methods_count else 0,
                'system_features': features_count['count'] if features_count else 0,
                'groups': groups_count['count'] if groups_count else 0,
                'categories': categories_count['count'] if categories_count else 0,
                'expected': {
                    'learning_methods': 12,
                    'system_features': 25,
                    'groups': 9,
                    'categories': 8
                }
            }
        except Exception:
            return {
                'learning_methods': 0,
                'system_features': 0,
                'groups': 0,
                'categories': 0,
                'expected': {
                    'learning_methods': 12,
                    'system_features': 25,
                    'groups': 9,
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
