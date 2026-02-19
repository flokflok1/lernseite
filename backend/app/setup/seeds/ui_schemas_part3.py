"""
LernsystemX Setup - Seed Data - UI Schemas (Part 3)

System Features UI schema definitions for 25 features across 10 categories:
- Audio (2): TTS Engine, Audio Recording
- Collaboration (3): LiveRoom, Screen Sharing, Collaborative Whiteboard
- Exam Systems (3): IHK Exam, Multi-Step Practice, Certification
- Gamification (2): XP System, Badge System
- Interactive Tools (3): Whiteboard Engine, Code Sandbox, Math Equation Solver
- IT Environments (2): Virtual Lab, Terminal Emulator
- Learning Paths (2): Learning Path Engine, Adaptive Learning
- Meta Features (2): Feature Flags, Usage Analytics
- Tutor (2): NPC Tutor, AI Tutor Companion
- Visualization (2): 3D Visualization, Interactive Diagrams

Split from ui_schemas.py for Quality Gate G01 compliance (max 500 lines).
"""

from typing import Dict


def get_system_features_schemas() -> Dict[str, Dict]:
    """
    Get complete UI schemas for all 25 System Features.

    Returns:
        Dictionary mapping feature_code to its UI schema definition.
        Each schema includes form fields, validation rules, and UI config.
    """
    return {
        # Audio (2)
        'tts_engine': {
            'feature_code': 'tts_engine',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'voice_selection',
                    'type': 'select',
                    'label_fallback': 'Stimmauswahl',
                    'options': [
                        {'value': 'female_neutral', 'label_fallback': 'Frau (neutral)'},
                        {'value': 'male_neutral', 'label_fallback': 'Mann (neutral)'},
                        {'value': 'child', 'label_fallback': 'Kind'}
                    ]
                },
                {
                    'name': 'speech_rate',
                    'type': 'number',
                    'label_fallback': 'Sprechgeschwindigkeit',
                    'default': 1.0,
                    'validation': {'min': 0.5, 'max': 2.0}
                }
            ]
        },

        'audio_recording': {
            'feature_code': 'audio_recording',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'max_duration',
                    'type': 'number',
                    'label_fallback': 'Maximale Aufnahmedauer (Sekunden)',
                    'default': 300
                }
            ]
        },

        # Collaboration (3)
        'liveroom_collaboration': {
            'feature_code': 'liveroom_collaboration',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'max_participants',
                    'type': 'number',
                    'label_fallback': 'Maximale Teilnehmer',
                    'default': 50
                }
            ]
        },

        'screen_sharing': {
            'feature_code': 'screen_sharing',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'share_audio',
                    'type': 'checkbox',
                    'label_fallback': 'Audio teilen',
                    'default': True
                }
            ]
        },

        'collaborative_whiteboard': {
            'feature_code': 'collaborative_whiteboard',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'canvas_size',
                    'type': 'select',
                    'label_fallback': 'Canvas-Größe',
                    'options': [
                        {'value': 'small', 'label_fallback': 'Klein'},
                        {'value': 'medium', 'label_fallback': 'Mittel'},
                        {'value': 'large', 'label_fallback': 'Groß'}
                    ]
                }
            ]
        },

        # Exam Systems (3)
        'ihk_exam_system': {
            'feature_code': 'ihk_exam_system',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'exam_duration',
                    'type': 'number',
                    'label_fallback': 'Prüfungsdauer (Minuten)',
                    'default': 180
                }
            ]
        },

        'multi_step_practice_exam': {
            'feature_code': 'multi_step_practice_exam',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'number_of_steps',
                    'type': 'number',
                    'label_fallback': 'Anzahl der Schritte',
                    'validation': {'min': 2, 'max': 10}
                }
            ]
        },

        'certification_exam': {
            'feature_code': 'certification_exam',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'credential_issuer',
                    'type': 'text',
                    'label_fallback': 'Ausstellende Stelle'
                }
            ]
        },

        # Gamification (2)
        'xp_system': {
            'feature_code': 'xp_system',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'xp_per_activity',
                    'type': 'number',
                    'label_fallback': 'XP pro Aktivität',
                    'default': 10
                }
            ]
        },

        'badge_system': {
            'feature_code': 'badge_system',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'show_badges_public',
                    'type': 'checkbox',
                    'label_fallback': 'Badges öffentlich zeigen',
                    'default': True
                }
            ]
        },

        # Interactive Tools (3)
        'whiteboard_engine': {
            'feature_code': 'whiteboard_engine',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'enable_formula_recognition',
                    'type': 'checkbox',
                    'label_fallback': 'Formel-Erkennung aktivieren',
                    'default': True
                }
            ]
        },

        'code_sandbox': {
            'feature_code': 'code_sandbox',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'programming_languages',
                    'type': 'array',
                    'label_fallback': 'Programmiersprachen',
                    'item_schema': {
                        'type': 'object',
                        'fields': [
                            {
                                'name': 'language',
                                'type': 'select',
                                'options': [
                                    {'value': 'python', 'label_fallback': 'Python'},
                                    {'value': 'javascript', 'label_fallback': 'JavaScript'},
                                    {'value': 'java', 'label_fallback': 'Java'},
                                    {'value': 'cpp', 'label_fallback': 'C++'}
                                ]
                            }
                        ]
                    }
                }
            ]
        },

        'math_equation_solver': {
            'feature_code': 'math_equation_solver',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'show_steps',
                    'type': 'checkbox',
                    'label_fallback': 'Lösungsschritte zeigen',
                    'default': True
                }
            ]
        },

        # IT Environments (2)
        'virtual_lab': {
            'feature_code': 'virtual_lab',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'lab_templates',
                    'type': 'array',
                    'label_fallback': 'Laborvorlagen',
                    'item_schema': {
                        'type': 'object',
                        'fields': [
                            {
                                'name': 'template_name',
                                'type': 'text',
                                'label_fallback': 'Template-Name'
                            }
                        ]
                    }
                }
            ]
        },

        'terminal_emulator': {
            'feature_code': 'terminal_emulator',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'os_type',
                    'type': 'select',
                    'label_fallback': 'Betriebssystem',
                    'options': [
                        {'value': 'linux', 'label_fallback': 'Linux'},
                        {'value': 'windows', 'label_fallback': 'Windows'}
                    ]
                }
            ]
        },

        # Learning Paths (2)
        'learning_path_engine': {
            'feature_code': 'learning_path_engine',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'enable_prerequisites',
                    'type': 'checkbox',
                    'label_fallback': 'Voraussetzungen aktivieren',
                    'default': True
                }
            ]
        },

        'adaptive_learning': {
            'feature_code': 'adaptive_learning',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'adaptation_sensitivity',
                    'type': 'select',
                    'label_fallback': 'Anpassungsempfindlichkeit',
                    'options': [
                        {'value': 'low', 'label_fallback': 'Niedrig'},
                        {'value': 'medium', 'label_fallback': 'Mittel'},
                        {'value': 'high', 'label_fallback': 'Hoch'}
                    ]
                }
            ]
        },

        # Meta Features (2)
        'feature_flags': {
            'feature_code': 'feature_flags',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'rollout_percentage',
                    'type': 'number',
                    'label_fallback': 'Ausrollungs-Prozentsatz',
                    'default': 0,
                    'validation': {'min': 0, 'max': 100}
                }
            ]
        },

        'usage_analytics': {
            'feature_code': 'usage_analytics',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'retention_days',
                    'type': 'number',
                    'label_fallback': 'Aufbewahrungstage',
                    'default': 90
                }
            ]
        },

        # Tutor (2)
        'npc_tutor': {
            'feature_code': 'npc_tutor',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'tutor_personality',
                    'type': 'select',
                    'label_fallback': 'Tutoren-Persönlichkeit',
                    'options': [
                        {'value': 'friendly', 'label_fallback': 'Freundlich'},
                        {'value': 'professional', 'label_fallback': 'Professionell'},
                        {'value': 'motivating', 'label_fallback': 'Motivierend'}
                    ]
                }
            ]
        },

        'ai_tutor_companion': {
            'feature_code': 'ai_tutor_companion',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'response_style',
                    'type': 'select',
                    'label_fallback': 'Antwortstil',
                    'options': [
                        {'value': 'detailed', 'label_fallback': 'Detailliert'},
                        {'value': 'concise', 'label_fallback': 'Prägnant'},
                        {'value': 'socratic', 'label_fallback': 'Sokratisch'}
                    ]
                }
            ]
        },

        # Visualization (2)
        '3d_visualization': {
            'feature_code': '3d_visualization',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'enable_rotation',
                    'type': 'checkbox',
                    'label_fallback': 'Rotation aktivieren',
                    'default': True
                }
            ]
        },

        'interactive_diagrams': {
            'feature_code': 'interactive_diagrams',
            'form_type': 'dynamic',
            'language_support': ['de', 'en', 'pl'],
            'layout': 'vertical',
            'fields': [
                {
                    'name': 'animation_style',
                    'type': 'select',
                    'label_fallback': 'Animationsstil',
                    'options': [
                        {'value': 'smooth', 'label_fallback': 'Glatt'},
                        {'value': 'stepped', 'label_fallback': 'Schrittweise'},
                        {'value': 'bouncy', 'label_fallback': 'Federnd'}
                    ]
                }
            ]
        }
    }
