"""
LernsystemX Setup - Seed Data - System Configuration

Seeds initial data for:
- System features (25 features across 10 categories)
  - Audio (2): tts_engine, audio_recording
  - Collaboration (3): liveroom_collaboration, screen_sharing, collaborative_whiteboard
  - Exam Systems (3): ihk_exam_system, multi_step_practice_exam, certification_exam
  - Gamification (2): xp_system, badge_system
  - Interactive Tools (3): whiteboard_engine, code_sandbox, math_equation_solver
  - IT Environments (2): virtual_lab, terminal_emulator
  - Learning Paths (2): learning_path_engine, adaptive_learning
  - Meta Features (2): feature_flags, usage_analytics
  - Tutor (2): npc_tutor, ai_tutor_companion
  - Visualization (2): 3d_visualization, interactive_diagrams
- Course categories (8 categories)

For learning methods and user roles, see:
- seeds.py: Core seeding functions
- seeds_roles.py: User roles

ISO 9001:2015 compliant - Data standardization
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.database.connection import fetch_one, execute_query, insert_returning


class SeedDataConfig:
    """
    Seed system configuration data

    Provides predefined data for 25 system features and 8 course categories.
    """

    @classmethod
    def seed_system_features(cls, skip_existing: bool = True) -> int:
        """
        Seed 25 system features across 10 categories

        Categories:
        - Audio (2 features)
        - Collaboration (3 features)
        - Exam Systems (3 features)
        - Gamification (2 features)
        - Interactive Tools (3 features)
        - IT Environments (2 features)
        - Learning Paths (2 features)
        - Meta Features (2 features)
        - Tutor (2 features)
        - Visualization (2 features)

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
            # Audio (2)
            {
                'feature_code': 'tts_engine',
                'feature_name': 'Text-to-Speech Engine',
                'description': 'Converts text content to speech in multiple languages',
                'category': 'audio',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'volume-2',
                'former_lm_id': None
            },
            {
                'feature_code': 'audio_recording',
                'feature_name': 'Audio Recording',
                'description': 'Record and playback audio annotations',
                'category': 'audio',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'mic',
                'former_lm_id': None
            },

            # Collaboration (3)
            {
                'feature_code': 'liveroom_collaboration',
                'feature_name': 'LiveRoom Collaboration',
                'description': 'Real-time collaborative learning environment with video/audio',
                'category': 'collaboration',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'users',
                'former_lm_id': None
            },
            {
                'feature_code': 'screen_sharing',
                'feature_name': 'Screen Sharing',
                'description': 'Share screens during collaborative sessions',
                'category': 'collaboration',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'share-2',
                'former_lm_id': None
            },
            {
                'feature_code': 'collaborative_whiteboard',
                'feature_name': 'Collaborative Whiteboard',
                'description': 'Shared digital whiteboard for real-time drawing and annotation',
                'category': 'collaboration',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'edit-3',
                'former_lm_id': None
            },

            # Exam Systems (3)
            {
                'feature_code': 'ihk_exam_system',
                'feature_name': 'IHK Exam System',
                'description': 'Professional certification exams in IHK format',
                'category': 'exam_systems',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'award',
                'former_lm_id': None
            },
            {
                'feature_code': 'multi_step_practice_exam',
                'feature_name': 'Multi-Step Practice Exam',
                'description': 'Progressive practical exams with multiple steps',
                'category': 'exam_systems',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'checklist',
                'former_lm_id': None
            },
            {
                'feature_code': 'certification_exam',
                'feature_name': 'Certification Exam',
                'description': 'Official certification exams with credentials',
                'category': 'exam_systems',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'certificate',
                'former_lm_id': None
            },

            # Gamification (2)
            {
                'feature_code': 'xp_system',
                'feature_name': 'Experience Points System',
                'description': 'Track user progress through XP and level progression',
                'category': 'gamification',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'trending-up',
                'former_lm_id': None
            },
            {
                'feature_code': 'badge_system',
                'feature_name': 'Badge & Achievement System',
                'description': 'Earn badges and achievements for milestones',
                'category': 'gamification',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'star',
                'former_lm_id': None
            },

            # Interactive Tools (3)
            {
                'feature_code': 'whiteboard_engine',
                'feature_name': 'AI Whiteboard Engine',
                'description': 'Interactive whiteboard with formula recognition and diagram support',
                'category': 'interactive_tools',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'layers',
                'former_lm_id': None
            },
            {
                'feature_code': 'code_sandbox',
                'feature_name': 'Code Sandbox Environment',
                'description': 'Safe isolated environment for code execution and testing',
                'category': 'interactive_tools',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'terminal',
                'former_lm_id': None
            },
            {
                'feature_code': 'math_equation_solver',
                'feature_name': 'Math Equation Solver',
                'description': 'Step-by-step mathematical equation solving',
                'category': 'interactive_tools',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'equal',
                'former_lm_id': None
            },

            # IT Environments (2)
            {
                'feature_code': 'virtual_lab',
                'feature_name': 'Virtual Lab Environment',
                'description': 'Simulated IT laboratory for hands-on practice',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'flask',
                'former_lm_id': None
            },
            {
                'feature_code': 'terminal_emulator',
                'feature_name': 'Terminal Emulator',
                'description': 'Web-based terminal for command-line learning',
                'category': 'it_environments',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'terminal',
                'former_lm_id': None
            },

            # Learning Paths (2)
            {
                'feature_code': 'learning_path_engine',
                'feature_name': 'Learning Path Engine',
                'description': 'Structured learning paths with prerequisites and progression',
                'category': 'learning_paths',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'map',
                'former_lm_id': None
            },
            {
                'feature_code': 'adaptive_learning',
                'feature_name': 'Adaptive Learning System',
                'description': 'AI-powered content adaptation based on learner progress',
                'category': 'learning_paths',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'zap',
                'former_lm_id': None
            },

            # Meta Features (2)
            {
                'feature_code': 'feature_flags',
                'feature_name': 'Feature Flags System',
                'description': 'Progressive feature rollout and A/B testing',
                'category': 'meta_features',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'flag',
                'former_lm_id': None
            },
            {
                'feature_code': 'usage_analytics',
                'feature_name': 'Usage Analytics',
                'description': 'Comprehensive analytics on user engagement and learning patterns',
                'category': 'meta_features',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'bar-chart-2',
                'former_lm_id': None
            },

            # Tutor (2)
            {
                'feature_code': 'npc_tutor',
                'feature_name': 'NPC Tutor Companion',
                'description': 'AI-powered NPC tutor for personalized learning assistance',
                'category': 'tutor',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'user',
                'former_lm_id': None
            },
            {
                'feature_code': 'ai_tutor_companion',
                'feature_name': 'AI Tutor Companion',
                'description': '1:1 AI tutoring with real-time assistance and feedback',
                'category': 'tutor',
                'requires_infrastructure': True,
                'requires_external_service': True,
                'icon': 'user-check',
                'former_lm_id': None
            },

            # Visualization (2)
            {
                'feature_code': '3d_visualization',
                'feature_name': '3D Visualization',
                'description': 'Interactive 3D models and visualizations for spatial learning',
                'category': 'visualization',
                'requires_infrastructure': True,
                'requires_external_service': False,
                'icon': 'cube',
                'former_lm_id': None
            },
            {
                'feature_code': 'interactive_diagrams',
                'feature_name': 'Interactive Diagrams',
                'description': 'Interactive and animated diagrams for concept visualization',
                'category': 'visualization',
                'requires_infrastructure': False,
                'requires_external_service': False,
                'icon': 'gitgraph',
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

    @classmethod
    def seed_categories(cls, skip_existing: bool = True) -> int:
        """
        Seed 8 course categories

        Categories:
        - Programming
        - Languages
        - Business
        - Science
        - Mathematics
        - History
        - Art & Design
        - Technology

        Args:
            skip_existing: Skip if categories already exist

        Returns:
            Number of categories created

        Example:
            >>> count = SeedDataConfig.seed_categories()
            >>> print(f"Created {count} course categories")
        """
        # Check if categories already exist
        if skip_existing:
            existing = fetch_one("SELECT COUNT(*) FROM course_categories")
            if existing and existing['count'] > 0:
                return 0

        categories = [
            {
                'category_name': 'Programming',
                'description': 'Software development and programming languages',
                'icon': 'code',
                'color': '#FF6B6B',
                'display_order': 1,
                'is_active': True
            },
            {
                'category_name': 'Languages',
                'description': 'Foreign language learning and linguistics',
                'icon': 'globe',
                'color': '#4ECDC4',
                'display_order': 2,
                'is_active': True
            },
            {
                'category_name': 'Business',
                'description': 'Business management, economics, and entrepreneurship',
                'icon': 'briefcase',
                'color': '#45B7D1',
                'display_order': 3,
                'is_active': True
            },
            {
                'category_name': 'Science',
                'description': 'Natural sciences, physics, chemistry, and biology',
                'icon': 'flask',
                'color': '#96CEB4',
                'display_order': 4,
                'is_active': True
            },
            {
                'category_name': 'Mathematics',
                'description': 'Mathematics, calculus, algebra, and statistics',
                'icon': 'calculator',
                'color': '#FFEAA7',
                'display_order': 5,
                'is_active': True
            },
            {
                'category_name': 'History',
                'description': 'Historical events, cultures, and world history',
                'icon': 'book',
                'color': '#DDA15E',
                'display_order': 6,
                'is_active': True
            },
            {
                'category_name': 'Art & Design',
                'description': 'Visual arts, graphic design, and creative skills',
                'icon': 'palette',
                'color': '#BC6C25',
                'display_order': 7,
                'is_active': True
            },
            {
                'category_name': 'Technology',
                'description': 'IT infrastructure, networks, and emerging technologies',
                'icon': 'cpu',
                'color': '#6C63FF',
                'display_order': 8,
                'is_active': True
            }
        ]

        created = 0
        for category in categories:
            try:
                result = execute_query(
                    """
                    INSERT INTO course_categories (
                        category_name, description, icon, color, display_order,
                        is_active, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (category_name) DO NOTHING
                    RETURNING *
                    """,
                    (
                        category['category_name'],
                        category['description'],
                        category['icon'],
                        category['color'],
                        category['display_order'],
                        category['is_active']
                    ),
                    fetch_one=True
                )
                if result:
                    created += 1
            except Exception as e:
                print(f"Error creating category '{category['category_name']}': {str(e)}")

        return created


# Convenience functions
def seed_system_features(**kwargs) -> int:
    """Quick function to seed system features"""
    return SeedDataConfig.seed_system_features(**kwargs)


def seed_categories(**kwargs) -> int:
    """Quick function to seed course categories"""
    return SeedDataConfig.seed_categories(**kwargs)
