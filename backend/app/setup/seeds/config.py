"""
LernsystemX Setup - Seed Data - System Features

Seeds initial data for 25 system features across 10 categories:
- Audio (1): speech_to_text
- Collaboration (7): peer_instruction, peer_review, team_case, learning_journal,
    project_portfolio, project_based_learning, inverted_classroom
- Exam Systems (3): ihk_exam_system, practical_exam_engine, chapter_completion_system
- Gamification (3): adaptive_difficulty, xp_quest_system, daily_recall
- Interactive Tools (1): whiteboard_engine
- IT Environments (4): it_sandbox, code_sandbox, network_simulation, terminal_access
- Learning Paths (1): learning_path_generator
- Meta Features (1): timer_wrapper
- Tutor (3): npc_tutor, socratic_dialog, comprehension_checker
- Visualization (1): mindmap_generator

Source of Truth: backend/migrations/11_System/038_system_features.sql

For course categories, see: config_part2.py
For learning methods and user roles, see:
- seeds.py: Core seeding functions
- seeds_roles.py: User roles

ISO 9001:2015 compliant - Data standardization
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, execute_query, insert_returning


class SeedDataConfig:
    """
    Seed system configuration data - System Features

    Provides predefined data for 25 system features.
    Source of Truth: backend/migrations/11_System/038_system_features.sql

    For course categories, see SeedDataConfigCategories in config_part2.py.
    """

    @classmethod
    def seed_system_features(cls, skip_existing: bool = True) -> int:
        """
        Seed 25 system features across 10 categories

        Categories:
        - Audio (1 feature): speech_to_text
        - Collaboration (7 features): peer_instruction, peer_review, team_case,
          learning_journal, project_portfolio, project_based_learning, inverted_classroom
        - Exam Systems (3 features): ihk_exam_system, practical_exam_engine,
          chapter_completion_system
        - Gamification (3 features): adaptive_difficulty, xp_quest_system, daily_recall
        - Interactive Tools (1 feature): whiteboard_engine
        - IT Environments (4 features): it_sandbox, code_sandbox, network_simulation,
          terminal_access
        - Learning Paths (1 feature): learning_path_generator
        - Meta Features (1 feature): timer_wrapper
        - Tutor (3 features): npc_tutor, socratic_dialog, comprehension_checker
        - Visualization (1 feature): mindmap_generator

        Args:
            skip_existing: Skip if features already exist

        Returns:
            Number of features created

        Example:
            >>> count = SeedDataConfig.seed_system_features()
            >>> print(f"Created {count} system features")
        """
        # Check if features already exist
        if skip_existing:
            existing = fetch_one("SELECT COUNT(*) FROM support_systems.system_features")
            if existing and existing['count'] > 0:
                return 0

        system_features = [
            # Audio (1)
            {
                'feature_code': 'speech_to_text',
                'feature_name': 'Speech-to-Text Engine',
                'description': 'Sprachaufnahme mit KI-Transkription & Bewertung',
                'category': 'audio',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'microphone',
                'former_lm_id': 17
            },

            # Collaboration (7)
            {
                'feature_code': 'peer_instruction',
                'feature_name': 'Peer Instruction',
                'description': 'Peer Instruction Methode (Think-Pair-Share)',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'users',
                'former_lm_id': 26
            },
            {
                'feature_code': 'peer_review',
                'feature_name': 'Peer Review',
                'description': 'Gegenseitige Bewertung von Lösungen',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'users',
                'former_lm_id': None
            },
            {
                'feature_code': 'team_case',
                'feature_name': 'Team-Case',
                'description': 'Kollaborative Fallbearbeitung',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'people-carry',
                'former_lm_id': None
            },
            {
                'feature_code': 'learning_journal',
                'feature_name': 'Lerntagebuch',
                'description': 'Persönliche Reflexion und Dokumentation',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'book',
                'former_lm_id': None
            },
            {
                'feature_code': 'project_portfolio',
                'feature_name': 'Projekt-Portfolio',
                'description': 'Sammlung eigener Projekte',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'folder-open',
                'former_lm_id': None
            },
            {
                'feature_code': 'project_based_learning',
                'feature_name': 'Projektbasiertes Lernen',
                'description': 'Project-Based Learning Workflows',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'tasks',
                'former_lm_id': 31
            },
            {
                'feature_code': 'inverted_classroom',
                'feature_name': 'Inverted Classroom',
                'description': 'Flipped Classroom Unterstützung',
                'category': 'collaboration',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'chalkboard-teacher',
                'former_lm_id': None
            },

            # Exam Systems (3)
            {
                'feature_code': 'ihk_exam_system',
                'feature_name': 'IHK-Prüfungssystem',
                'description': 'Prüfungsaufgaben im IHK/Kammer-Format',
                'category': 'exam_systems',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'certificate',
                'former_lm_id': 10
            },
            {
                'feature_code': 'practical_exam_engine',
                'feature_name': 'Praxisprüfungs-Engine',
                'description': 'Mehrstufige praktische Prüfungsaufgaben',
                'category': 'exam_systems',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'clipboard-check',
                'former_lm_id': 11
            },
            {
                'feature_code': 'chapter_completion_system',
                'feature_name': 'Kapitelabschluss-System',
                'description': 'Umfassende Kapitelabschluss-Prüfung',
                'category': 'exam_systems',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'icon': 'trophy',
                'former_lm_id': 14
            },

            # Gamification (3)
            {
                'feature_code': 'adaptive_difficulty',
                'feature_name': 'Adaptive Schwierigkeit',
                'description': 'Passt Aufgabenschwierigkeit automatisch an Leistungsstand an',
                'category': 'gamification',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'chart-line',
                'former_lm_id': None
            },
            {
                'feature_code': 'xp_quest_system',
                'feature_name': 'XP & Quest System',
                'description': 'Erfahrungspunkte, Level, Achievements, Daily Quests',
                'category': 'gamification',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'trophy',
                'former_lm_id': None
            },
            {
                'feature_code': 'daily_recall',
                'feature_name': 'Daily Recall',
                'description': 'Tägliche Wiederholungslogik (Spaced Repetition)',
                'category': 'gamification',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'calendar-check',
                'former_lm_id': None
            },

            # Interactive Tools (1)
            {
                'feature_code': 'whiteboard_engine',
                'feature_name': 'Whiteboard-Engine',
                'description': 'Interaktive Whiteboard-Aufgaben mit KI-Erkennung (Formeln, Diagramme, Keywords)',
                'category': 'interactive_tools',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'pencil-ruler',
                'former_lm_id': 5
            },

            # IT Environments (4)
            {
                'feature_code': 'it_sandbox',
                'feature_name': 'IT-Sandbox',
                'description': 'Praktische Übungen in simulierten IT-Umgebungen (Code, Config, Netzwerk, Terminal)',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'laptop-code',
                'former_lm_id': 10
            },
            {
                'feature_code': 'code_sandbox',
                'feature_name': 'Code-Sandbox',
                'description': 'Isolierte Code-Ausführungsumgebung',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'code',
                'former_lm_id': None
            },
            {
                'feature_code': 'network_simulation',
                'feature_name': 'Netzwerk-Simulation',
                'description': 'Virtuelle Netzwerk-Topologien',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'network-wired',
                'former_lm_id': None
            },
            {
                'feature_code': 'terminal_access',
                'feature_name': 'Terminal-Zugriff',
                'description': 'Web-basierter Terminal-Zugang',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'terminal',
                'former_lm_id': None
            },

            # Learning Paths (1)
            {
                'feature_code': 'learning_path_generator',
                'feature_name': 'Lernpfad-Generator',
                'description': 'KI-gestützte Lernpfad-Erstellung und -Optimierung',
                'category': 'learning_paths',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'icon': 'route',
                'former_lm_id': None
            },

            # Meta Features (1)
            {
                'feature_code': 'timer_wrapper',
                'feature_name': 'Timer/Zeitlimit-Feature',
                'description': 'Zeitbegrenzung für beliebige Aufgaben (Meta-Feature)',
                'category': 'meta_features',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'clock',
                'former_lm_id': 14
            },

            # Tutor (3)
            {
                'feature_code': 'npc_tutor',
                'feature_name': 'NPC-/Persona-Tutor',
                'description': 'KI-basierter Tutor mit verschiedenen Rollen/Personas',
                'category': 'tutor',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'icon': 'user-graduate',
                'former_lm_id': None
            },
            {
                'feature_code': 'socratic_dialog',
                'feature_name': 'Sokratischer Dialog',
                'description': 'KI-geführter Dialog zur Wissensvermittlung',
                'category': 'tutor',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'icon': 'comments',
                'former_lm_id': None
            },
            {
                'feature_code': 'comprehension_checker',
                'feature_name': 'Verständnis-Checker',
                'description': 'Mikro-Checks basierend auf Bloom-Taxonomie',
                'category': 'tutor',
                'requires_infrastructure': False,
                'requires_external_service': True,
                'icon': 'check-circle',
                'former_lm_id': 13
            },

            # Visualization (1)
            {
                'feature_code': 'mindmap_generator',
                'feature_name': 'Mindmap-Generator',
                'description': 'Generiert kursweite Mindmaps aus Theorie-Inhalten',
                'category': 'visualization',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'sitemap',
                'former_lm_id': None
            }
        ]

        created = 0
        for feature in system_features:
            try:
                result = execute_query(
                    """
                    INSERT INTO support_systems.system_features (
                        feature_code, feature_name, description, category,
                        requires_infrastructure, requires_external_service, icon, former_lm_id,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
                        feature['icon'],
                        feature['former_lm_id']
                    ),
                    fetch_one=True
                )
                if result:
                    created += 1
            except Exception as e:
                print(f"Error creating system feature '{feature['feature_code']}': {str(e)}")

        return created


# Convenience function
def seed_system_features(**kwargs) -> int:
    """Quick function to seed system features"""
    return SeedDataConfig.seed_system_features(**kwargs)
