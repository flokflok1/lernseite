"""
LernsystemX Setup - Seed Data

Seeds initial data for:
- Learning methods (12 Content-Lernmethoden: lm00-lm11)
  - Gruppe A (Erklärend): lm00-lm04 (5 methods)
  - Gruppe B (Praxis): lm05-lm08 (4 methods)
  - Gruppe C (Prüfung): lm09-lm11 (3 methods)
- System features (25 features across 9 categories)
  - Interactive Tools (3), Exam & Assessment (4), Meta Features (1)
  - Visualization (1), Tutor & Coaching (2), Gamification (3)
  - Learning Paths (1), Collaboration (7), IT Environments (3)
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
            'system_features': 0,
            'roles': 0,
            'categories': 0,
            'errors': []
        }

        try:
            # Attempt to seed learning methods
            cls.seed_learning_methods(skip_existing)

            # Attempt to seed system features
            cls.seed_system_features(skip_existing)

            # Attempt to seed roles
            cls.seed_roles(skip_existing)

            # Attempt to seed categories
            cls.seed_categories(skip_existing)

            # Return ACTUAL database counts (not insertion counts)
            # This ensures the user sees the correct numbers even if data already exists
            methods_result = fetch_one("SELECT COUNT(*) as count FROM learning_method_types")
            results['learning_methods'] = methods_result['count'] if methods_result else 0

            features_result = fetch_one("SELECT COUNT(*) as count FROM support_systems.system_features")
            results['system_features'] = features_result['count'] if features_result else 0

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
    def seed_system_features(cls, skip_existing: bool = True) -> int:
        """
        Seed 25 System-Features

        Categories:
        - Interactive Tools (3)
        - Exam & Assessment (4)
        - Meta Features (1)
        - Visualization (1)
        - Tutor & Coaching (2)
        - Gamification (3)
        - Learning Paths (1)
        - Collaboration (7)
        - IT Environments (3)

        Args:
            skip_existing: Skip if features already exist

        Returns:
            Number of system features created

        Example:
            >>> count = SeedData.seed_system_features()
            >>> print(f"Created {count} system features")
        """
        # Check if features already exist
        if skip_existing:
            existing = fetch_one("SELECT COUNT(*) FROM support_systems.system_features")
            if existing and existing['count'] > 0:
                return 0

        system_features = [
            # Interactive Tools (3)
            {
                'feature_code': 'whiteboard_engine',
                'feature_name': 'Whiteboard-Engine',
                'description': 'Interaktive Whiteboard-Aufgaben mit KI-Erkennung',
                'category': 'interactive_tools',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': 5,
                'icon': 'pencil',
                'config': {
                    'recognition_types': ['formula', 'diagram', 'network', 'keywords'],
                    'ai_feedback': True,
                    'save_history': True
                }
            },
            {
                'feature_code': 'it_sandbox',
                'feature_name': 'IT-Sandbox',
                'description': 'Praktische Übungen in simulierten IT-Umgebungen',
                'category': 'interactive_tools',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': 10,
                'icon': 'terminal',
                'config': {
                    'sandbox_types': ['code', 'config', 'network', 'terminal'],
                    'max_duration': 3600,
                    'auto_cleanup': True
                }
            },
            {
                'feature_code': 'speech_to_text',
                'feature_name': 'Speech-to-Text Engine',
                'description': 'Sprachaufnahme mit KI-Transkription & Bewertung',
                'category': 'interactive_tools',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': 17,
                'icon': 'microphone',
                'config': {
                    'max_duration': 600,
                    'language': 'de-DE',
                    'ai_grading': True,
                    'provider': 'whisper'
                }
            },

            # Exam & Assessment (4)
            {
                'feature_code': 'ihk_exam_system',
                'feature_name': 'IHK-Prüfungssystem',
                'description': 'Prüfungsaufgaben im IHK/Kammer-Format',
                'category': 'exam_systems',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': 10,
                'icon': 'certificate',
                'config': {
                    'exam_format': 'ihk_it',
                    'time_limit': 180,
                    'passing_score': 50
                }
            },
            {
                'feature_code': 'practical_exam_engine',
                'feature_name': 'Praxisprüfungs-Engine',
                'description': 'Mehrstufige praktische Prüfungsaufgaben',
                'category': 'exam_systems',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 11,
                'icon': 'clipboard-check',
                'config': {
                    'max_steps': 10,
                    'allow_skip': False,
                    'partial_credit': True,
                    'dependency_mode': 'strict'
                }
            },
            {
                'feature_code': 'comprehension_checker',
                'feature_name': 'Verständnis-Checker',
                'description': 'Mikro-Checks basierend auf Bloom-Taxonomie',
                'category': 'tutor',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': 13,
                'icon': 'check-circle',
                'config': {
                    'bloom_levels': ['recall', 'understand', 'apply', 'analyze', 'evaluate', 'create'],
                    'min_questions_per_level': 2,
                    'adaptive': True,
                    'immediate_feedback': True
                }
            },
            {
                'feature_code': 'chapter_completion_system',
                'feature_name': 'Kapitelabschluss-System',
                'description': 'Umfassende Kapitelabschluss-Prüfung',
                'category': 'exam_systems',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': 14,
                'icon': 'trophy',
                'config': {
                    'pass_threshold': 70,
                    'certificate_on_pass': True,
                    'show_correct_answers': True
                }
            },

            # Meta Features (1)
            {
                'feature_code': 'timer_wrapper',
                'feature_name': 'Timer/Zeitlimit',
                'description': 'Zeitbegrenzung für beliebige Aufgaben',
                'category': 'meta_features',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 14,
                'icon': 'clock',
                'config': {
                    'default_time_limit': 60,
                    'show_remaining_time': True,
                    'auto_submit': True
                }
            },

            # Visualization (1)
            {
                'feature_code': 'mindmap_generator',
                'feature_name': 'Mindmap-Generator',
                'description': 'Generiert kursweite Mindmaps aus Theorie-Inhalten',
                'category': 'visualization',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': 5,
                'icon': 'sitemap',
                'config': {
                    'auto_generate': True,
                    'max_depth': 3,
                    'style': 'hierarchical'
                }
            },

            # Tutor & Coaching (2)
            {
                'feature_code': 'npc_tutor',
                'feature_name': 'NPC-/Persona-Tutor',
                'description': 'KI-basierter Tutor mit verschiedenen Rollen/Personas',
                'category': 'tutor',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': None,
                'icon': 'user-tie',
                'config': {
                    'personas': ['professor', 'peer', 'mentor', 'coach'],
                    'conversation_style': 'adaptive',
                    'remember_context': True
                }
            },
            {
                'feature_code': 'socratic_dialog',
                'feature_name': 'Sokratischer Dialog',
                'description': 'KI-geführter Dialog zur Wissensvermittlung durch Fragen',
                'category': 'tutor',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': None,
                'icon': 'comments',
                'config': {
                    'max_questions': 10,
                    'difficulty_adaptation': True
                }
            },

            # Gamification (3)
            {
                'feature_code': 'adaptive_difficulty',
                'feature_name': 'Adaptive Schwierigkeit',
                'description': 'Passt Aufgabenschwierigkeit automatisch an',
                'category': 'gamification',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': None,
                'icon': 'chart-line',
                'config': {
                    'adjustment_algorithm': 'elo',
                    'min_attempts': 3
                }
            },
            {
                'feature_code': 'xp_quest_system',
                'feature_name': 'XP & Quest System',
                'description': 'Erfahrungspunkte, Level, Achievements, Daily Quests',
                'category': 'gamification',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': None,
                'icon': 'star',
                'config': {
                    'xp_per_task': 100,
                    'daily_quests_count': 3
                }
            },
            {
                'feature_code': 'daily_recall',
                'feature_name': 'Daily Recall',
                'description': 'Tägliche Wiederholungslogik (Spaced Repetition)',
                'category': 'gamification',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': None,
                'icon': 'calendar-check',
                'config': {
                    'algorithm': 'sm2',
                    'daily_limit': 20
                }
            },

            # Learning Paths (1)
            {
                'feature_code': 'learning_path_generator',
                'feature_name': 'Lernpfad-Generator',
                'description': 'KI-gestützte Lernpfad-Erstellung und -Optimierung',
                'category': 'learning_paths',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': None,
                'icon': 'route',
                'config': {
                    'personalized': True,
                    'adapt_to_performance': True
                }
            },

            # Collaboration (7)
            {
                'feature_code': 'peer_instruction',
                'feature_name': 'Peer Instruction',
                'description': 'Peer Instruction Methode (Think-Pair-Share)',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 26,
                'icon': 'users',
                'config': {
                    'phases': ['think', 'pair', 'share'],
                    'time_per_phase': 300
                }
            },
            {
                'feature_code': 'team_case',
                'feature_name': 'Team-Case',
                'description': 'Kollaborative Fallbearbeitung',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 27,
                'icon': 'briefcase',
                'config': {
                    'max_team_size': 5,
                    'collaborative_editing': True
                }
            },
            {
                'feature_code': 'peer_review',
                'feature_name': 'Peer Review',
                'description': 'Gegenseitige Bewertung von Lösungen',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 28,
                'icon': 'user-check',
                'config': {
                    'anonymous': True,
                    'min_reviews': 2
                }
            },
            {
                'feature_code': 'learning_journal',
                'feature_name': 'Lerntagebuch',
                'description': 'Persönliche Reflexion und Dokumentation',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 29,
                'icon': 'book',
                'config': {
                    'prompts_enabled': True,
                    'private': True
                }
            },
            {
                'feature_code': 'project_portfolio',
                'feature_name': 'Projekt-Portfolio',
                'description': 'Sammlung eigener Projekte',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 30,
                'icon': 'folder-open',
                'config': {
                    'max_projects': 50,
                    'public_sharing': True
                }
            },
            {
                'feature_code': 'project_based_learning',
                'feature_name': 'Projektbasiertes Lernen',
                'description': 'Project-Based Learning Workflows',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 31,
                'icon': 'tasks',
                'config': {
                    'phases': ['planning', 'execution', 'presentation'],
                    'team_based': True
                }
            },
            {
                'feature_code': 'inverted_classroom',
                'feature_name': 'Inverted Classroom',
                'description': 'Flipped Classroom Unterstützung',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'active': True,
                'former_lm_id': 32,
                'icon': 'sync-alt',
                'config': {
                    'pre_class_materials': True,
                    'in_class_activities': True
                }
            },

            # IT Environments (3)
            {
                'feature_code': 'code_sandbox',
                'feature_name': 'Code-Sandbox',
                'description': 'Isolierte Code-Ausführungsumgebung',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': None,
                'icon': 'code',
                'config': {
                    'languages': ['python', 'javascript', 'java', 'go'],
                    'max_execution_time': 30
                }
            },
            {
                'feature_code': 'network_simulation',
                'feature_name': 'Netzwerk-Simulation',
                'description': 'Virtuelle Netzwerk-Topologien',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': None,
                'icon': 'network-wired',
                'config': {
                    'max_nodes': 20,
                    'protocols': ['tcp', 'udp', 'icmp']
                }
            },
            {
                'feature_code': 'terminal_access',
                'feature_name': 'Terminal-Zugriff',
                'description': 'Web-basierter Terminal-Zugang',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'active': True,
                'former_lm_id': None,
                'icon': 'terminal',
                'config': {
                    'shell': 'bash',
                    'max_session_time': 1800
                }
            }
        ]

        created = 0
        for feature in system_features:
            try:
                import json
                result = execute_query(
                    """
                    INSERT INTO support_systems.system_features (
                        feature_code, feature_name, description, category,
                        requires_infrastructure, requires_external_service,
                        active, config, icon, former_lm_id, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (feature_code) DO NOTHING
                    RETURNING *
                    """,
                    (
                        feature['feature_code'],
                        feature['feature_name'],
                        feature['description'],
                        feature['category'],
                        feature['requires_infrastructure'],
                        feature['requires_external_service'],
                        feature['active'],
                        json.dumps(feature['config']),
                        feature['icon'],
                        feature['former_lm_id']
                    ),
                    fetch_one=True
                )
                if result:
                    created += 1
            except Exception as e:
                print(f"Error creating system feature '{feature['feature_name']}': {str(e)}")

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
            features_count = fetch_one("SELECT COUNT(*) FROM support_systems.system_features")
            roles_count = fetch_one("SELECT COUNT(*) FROM roles")
            categories_count = fetch_one("SELECT COUNT(*) FROM course_categories")

            return {
                'learning_methods': methods_count['count'] if methods_count else 0,
                'system_features': features_count['count'] if features_count else 0,
                'roles': roles_count['count'] if roles_count else 0,
                'categories': categories_count['count'] if categories_count else 0,
                'expected': {
                    'learning_methods': 12,
                    'system_features': 25,
                    'roles': 9,
                    'categories': 8
                }
            }
        except Exception:
            return {
                'learning_methods': 0,
                'system_features': 0,
                'roles': 0,
                'categories': 0,
                'expected': {
                    'learning_methods': 12,
                    'system_features': 25,
                    'roles': 9,
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


def seed_system_features(**kwargs) -> int:
    """Quick function to seed system features"""
    return SeedData.seed_system_features(**kwargs)


def seed_roles(**kwargs) -> int:
    """Quick function to seed roles"""
    return SeedData.seed_roles(**kwargs)


def seed_categories(**kwargs) -> int:
    """Quick function to seed categories"""
    return SeedData.seed_categories(**kwargs)
