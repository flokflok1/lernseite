"""
LernsystemX Setup - Seed Data - UI Schemas

Seeds UI schema definitions for:
- Learning Methods (12 Content-Lernmethoden: lm00-lm11)
  - Complete form field definitions
  - i18n keys for all labels (German, English, Polish)
  - German fallback labels (for graceful degradation)
  - UI configuration and validation rules

- System Features (25 features across 10 categories)
  - Consistent schema structure with LMs
  - Feature-specific form fields
  - German fallback labels (as per user feedback in Phase 5)
  - Metadata and configuration schemas

The hybrid i18n approach allows:
- Primary: i18n keys (labels from frontend i18n registry)
- Fallback: German labels (when translations unavailable)
- Future: Polish and English translations via i18n registry

ISO 9001:2015 compliant - Data standardization
ISO/IEC/IEEE 26515:2018 compliant - Schema design
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

from app.infrastructure.persistence.database.connection import fetch_one, execute_query, insert_returning


class SeedDataUISchemas:
    """
    Seed UI schema data for Content-Lernmethoden and System-Features

    Provides complete ui_schema definitions with:
    - Dynamic form rendering support
    - i18n integration (hybrid keys + fallbacks)
    - Field validation rules
    - UI configuration
    """

    @classmethod
    def seed_learning_methods_ui_schemas(cls, skip_existing: bool = True) -> int:
        """
        Seed UI schemas for all 12 Learning Methods (lm00-lm11)

        Args:
            skip_existing: Skip if schemas already seeded

        Returns:
            Number of schemas updated
        """
        # Check if already seeded
        if skip_existing:
            existing = fetch_one(
                "SELECT COUNT(*) FROM learning_method_types WHERE ui_schema IS NOT NULL"
            )
            if existing and existing['count'] >= 12:
                return 0

        ui_schemas = cls._get_learning_methods_schemas()

        updated = 0
        for method_type, schema in ui_schemas.items():
            try:
                result = execute_query(
                    """
                    UPDATE learning_method_types
                    SET ui_schema = %s, updated_at = NOW()
                    WHERE method_type = %s
                    RETURNING *
                    """,
                    (json.dumps(schema), method_type),
                    fetch_one=True
                )
                if result:
                    updated += 1
            except Exception as e:
                print(f"Error updating UI schema for learning method {method_type}: {str(e)}")

        return updated

    @classmethod
    def seed_system_features_ui_schemas(cls, skip_existing: bool = True) -> int:
        """
        Seed UI schemas for all 25 System Features

        Args:
            skip_existing: Skip if schemas already seeded

        Returns:
            Number of schemas updated
        """
        # Check if already seeded
        if skip_existing:
            existing = fetch_one(
                "SELECT COUNT(*) FROM support_systems.system_features WHERE ui_schema IS NOT NULL"
            )
            if existing and existing['count'] >= 25:
                return 0

        ui_schemas = cls._get_system_features_schemas()

        updated = 0
        for feature_code, schema in ui_schemas.items():
            try:
                result = execute_query(
                    """
                    UPDATE support_systems.system_features
                    SET ui_schema = %s, updated_at = NOW()
                    WHERE feature_code = %s
                    RETURNING *
                    """,
                    (json.dumps(schema), feature_code),
                    fetch_one=True
                )
                if result:
                    updated += 1
            except Exception as e:
                print(f"Error updating UI schema for system feature '{feature_code}': {str(e)}")

        return updated

    @classmethod
    def _get_learning_methods_schemas(cls) -> Dict[int, Dict]:
        """
        Get complete UI schemas for all 12 Learning Methods

        Structure: {method_type: ui_schema_dict}
        Each ui_schema includes:
        - feature_code: Unique identifier
        - form_type: Dynamic form type
        - language_support: Supported languages
        - layout: Form layout (vertical/horizontal/tabs)
        - fields: Form field definitions with validation
        - ui_config: Rendering configuration
        """
        return {
            # Gruppe A - Erklärend (5 Methoden)
            0: {
                'feature_code': 'lm00_deep_explanation',
                'feature_name_i18n': 'learning_methods.lm00.name',
                'feature_name_fallback': 'Tiefgehende Erklärung',
                'feature_name_de': 'Tiefgehende Erklärung',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'text',
                        'label_i18n': 'learning_methods.lm00.field.title',
                        'label_fallback': 'Titel',
                        'label_de': 'Titel',
                        'required': True,
                        'validation': {'minLength': 3, 'maxLength': 200},
                        'placeholder_i18n': 'learning_methods.lm00.field.title.placeholder',
                        'placeholder_fallback': 'Erklärungsthema eingeben',
                        'help_text_i18n': 'learning_methods.lm00.field.title.help'
                    },
                    {
                        'name': 'content',
                        'type': 'richtext',
                        'label_i18n': 'learning_methods.lm00.field.content',
                        'label_fallback': 'Erklärungstext',
                        'label_de': 'Erklärungstext',
                        'required': True,
                        'validation': {'minLength': 50, 'maxLength': 10000},
                        'placeholder_i18n': 'learning_methods.lm00.field.content.placeholder',
                        'placeholder_fallback': 'Detaillierte Erklärung eingeben...',
                        'editor_config': {
                            'formats': ['bold', 'italic', 'underline', 'list', 'link', 'code'],
                            'height': '400px'
                        }
                    },
                    {
                        'name': 'include_examples',
                        'type': 'checkbox',
                        'label_i18n': 'learning_methods.lm00.field.include_examples',
                        'label_fallback': 'Beispiele hinzufügen',
                        'label_de': 'Beispiele hinzufügen',
                        'default': True
                    },
                    {
                        'name': 'include_diagrams',
                        'type': 'checkbox',
                        'label_i18n': 'learning_methods.lm00.field.include_diagrams',
                        'label_fallback': 'Diagramme hinzufügen',
                        'label_de': 'Diagramme hinzufügen',
                        'default': True
                    },
                    {
                        'name': 'ai_enhancement_level',
                        'type': 'select',
                        'label_i18n': 'learning_methods.lm00.field.ai_level',
                        'label_fallback': 'KI-Unterstützung',
                        'label_de': 'KI-Unterstützung',
                        'default': 'medium',
                        'options': [
                            {'value': 'low', 'label_fallback': 'Niedrig'},
                            {'value': 'medium', 'label_fallback': 'Mittel'},
                            {'value': 'high', 'label_fallback': 'Hoch'}
                        ]
                    }
                ],
                'ui_config': {
                    'show_preview': True,
                    'auto_save': True,
                    'sections': [
                        {'name': 'content', 'label_fallback': 'Inhalte'},
                        {'name': 'options', 'label_fallback': 'Optionen'}
                    ]
                }
            },

            1: {
                'feature_code': 'lm01_step_by_step',
                'feature_name_i18n': 'learning_methods.lm01.name',
                'feature_name_fallback': 'Schritt-für-Schritt',
                'feature_name_de': 'Schritt-für-Schritt',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'title',
                        'type': 'text',
                        'label_fallback': 'Anleitung Titel',
                        'required': True,
                        'validation': {'minLength': 3, 'maxLength': 200}
                    },
                    {
                        'name': 'steps',
                        'type': 'array',
                        'label_fallback': 'Schritte',
                        'required': True,
                        'min_items': 2,
                        'max_items': 20,
                        'item_schema': {
                            'type': 'object',
                            'fields': [
                                {
                                    'name': 'step_number',
                                    'type': 'number',
                                    'label_fallback': 'Schrittnummer',
                                    'readonly': True
                                },
                                {
                                    'name': 'title',
                                    'type': 'text',
                                    'label_fallback': 'Schritt Titel',
                                    'required': True
                                },
                                {
                                    'name': 'description',
                                    'type': 'richtext',
                                    'label_fallback': 'Beschreibung',
                                    'required': True
                                },
                                {
                                    'name': 'tip',
                                    'type': 'text',
                                    'label_fallback': 'Tipp',
                                    'required': False
                                }
                            ]
                        }
                    }
                ],
                'ui_config': {
                    'step_editor': True,
                    'drag_reorder': True,
                    'show_preview': True
                }
            },

            2: {
                'feature_code': 'lm02_interactive_theory',
                'feature_name_i18n': 'learning_methods.lm02.name',
                'feature_name_fallback': 'Interaktive Theorie',
                'feature_name_de': 'Interaktive Theorie',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'content_sections',
                        'type': 'array',
                        'label_fallback': 'Inhaltsbereiche',
                        'required': True,
                        'item_schema': {
                            'type': 'object',
                            'fields': [
                                {
                                    'name': 'section_title',
                                    'type': 'text',
                                    'label_fallback': 'Abschnitt'
                                },
                                {
                                    'name': 'content',
                                    'type': 'richtext',
                                    'label_fallback': 'Inhalt'
                                },
                                {
                                    'name': 'inline_question',
                                    'type': 'text',
                                    'label_fallback': 'Inline-Frage'
                                }
                            ]
                        }
                    }
                ],
                'ui_config': {
                    'interactive_elements': True,
                    'question_marker': True
                }
            },

            3: {
                'feature_code': 'lm03_diagram_visualization',
                'feature_name_i18n': 'learning_methods.lm03.name',
                'feature_name_fallback': 'Diagramm/Visualisierung',
                'feature_name_de': 'Diagramm/Visualisierung',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'diagram_type',
                        'type': 'select',
                        'label_fallback': 'Diagrammtyp',
                        'required': True,
                        'options': [
                            {'value': 'flowchart', 'label_fallback': 'Flussdiagramm'},
                            {'value': 'mindmap', 'label_fallback': 'Gedankenkarte'},
                            {'value': 'timeline', 'label_fallback': 'Zeitstrahl'},
                            {'value': 'network', 'label_fallback': 'Netzwerkdiagramm'}
                        ]
                    },
                    {
                        'name': 'diagram_data',
                        'type': 'code',
                        'label_fallback': 'Diagramm-Daten (JSON)',
                        'language': 'json'
                    }
                ],
                'ui_config': {
                    'diagram_preview': True,
                    'export_formats': ['png', 'svg', 'pdf']
                }
            },

            4: {
                'feature_code': 'lm04_example_scenario',
                'feature_name_i18n': 'learning_methods.lm04.name',
                'feature_name_fallback': 'Beispiel-Szenario',
                'feature_name_de': 'Beispiel-Szenario',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'scenario_title',
                        'type': 'text',
                        'label_fallback': 'Szenario Titel',
                        'required': True
                    },
                    {
                        'name': 'context',
                        'type': 'richtext',
                        'label_fallback': 'Kontext/Hintergrund',
                        'required': True
                    },
                    {
                        'name': 'example_description',
                        'type': 'richtext',
                        'label_fallback': 'Beispielbeschreibung',
                        'required': True
                    },
                    {
                        'name': 'real_world_application',
                        'type': 'richtext',
                        'label_fallback': 'Anwendung in der Praxis',
                        'required': False
                    }
                ],
                'ui_config': {
                    'context_aware': True,
                    'applicability_rating': True
                }
            },

            # Gruppe B - Praxis (4 Methoden)
            5: {
                'feature_code': 'lm05_math_interactive',
                'feature_name_i18n': 'learning_methods.lm05.name',
                'feature_name_fallback': 'Mathe-Interaktiv',
                'feature_name_de': 'Mathe-Interaktiv',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'problems',
                        'type': 'array',
                        'label_fallback': 'Aufgaben',
                        'required': True,
                        'item_schema': {
                            'type': 'object',
                            'fields': [
                                {
                                    'name': 'problem_text',
                                    'type': 'text',
                                    'label_fallback': 'Aufgabentext'
                                },
                                {
                                    'name': 'formula',
                                    'type': 'text',
                                    'label_fallback': 'Formel (LaTeX)'
                                },
                                {
                                    'name': 'solution',
                                    'type': 'text',
                                    'label_fallback': 'Lösung'
                                }
                            ]
                        }
                    }
                ],
                'ui_config': {
                    'latex_renderer': True,
                    'formula_editor': True,
                    'step_by_step_solution': True
                }
            },

            6: {
                'feature_code': 'lm06_flashcards',
                'feature_name_i18n': 'learning_methods.lm06.name',
                'feature_name_fallback': 'Flashcards',
                'feature_name_de': 'Flashcards',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'cards',
                        'type': 'array',
                        'label_fallback': 'Lernkarten',
                        'required': True,
                        'max_items': 500,
                        'item_schema': {
                            'type': 'object',
                            'fields': [
                                {
                                    'name': 'question',
                                    'type': 'text',
                                    'label_fallback': 'Frage',
                                    'required': True
                                },
                                {
                                    'name': 'answer',
                                    'type': 'richtext',
                                    'label_fallback': 'Antwort',
                                    'required': True
                                },
                                {
                                    'name': 'difficulty',
                                    'type': 'select',
                                    'label_fallback': 'Schwierigkeit',
                                    'options': [
                                        {'value': 'easy', 'label_fallback': 'Leicht'},
                                        {'value': 'medium', 'label_fallback': 'Mittel'},
                                        {'value': 'hard', 'label_fallback': 'Schwer'}
                                    ]
                                }
                            ]
                        }
                    }
                ],
                'ui_config': {
                    'spaced_repetition': True,
                    'progress_tracking': True
                }
            },

            7: {
                'feature_code': 'lm07_drag_drop',
                'feature_name_i18n': 'learning_methods.lm07.name',
                'feature_name_fallback': 'Drag & Drop',
                'feature_name_de': 'Drag & Drop',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'source_items',
                        'type': 'array',
                        'label_fallback': 'Elemente zum Verschieben',
                        'required': True,
                        'max_items': 20,
                        'item_schema': {
                            'type': 'object',
                            'fields': [
                                {
                                    'name': 'text',
                                    'type': 'text',
                                    'label_fallback': 'Element Text'
                                }
                            ]
                        }
                    },
                    {
                        'name': 'target_groups',
                        'type': 'array',
                        'label_fallback': 'Zielgruppen',
                        'required': True,
                        'item_schema': {
                            'type': 'object',
                            'fields': [
                                {
                                    'name': 'label',
                                    'type': 'text',
                                    'label_fallback': 'Gruppenname'
                                }
                            ]
                        }
                    }
                ],
                'ui_config': {
                    'shuffle_items': True,
                    'drag_preview': True
                }
            },

            8: {
                'feature_code': 'lm08_cloze_test',
                'feature_name_i18n': 'learning_methods.lm08.name',
                'feature_name_fallback': 'Lückentext',
                'feature_name_de': 'Lückentext',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'text_with_blanks',
                        'type': 'text',
                        'label_fallback': 'Text mit Lücken',
                        'help_text_fallback': 'Verwende __blank__ als Platzhalter',
                        'required': True
                    },
                    {
                        'name': 'answers',
                        'type': 'array',
                        'label_fallback': 'Antworten für Lücken',
                        'required': True,
                        'item_schema': {
                            'type': 'object',
                            'fields': [
                                {
                                    'name': 'answer',
                                    'type': 'text',
                                    'label_fallback': 'Korrekte Antwort'
                                },
                                {
                                    'name': 'alternatives',
                                    'type': 'array',
                                    'label_fallback': 'Alternative Antworten'
                                }
                            ]
                        }
                    }
                ],
                'ui_config': {
                    'hint_system': True,
                    'auto_generate': True
                }
            },

            # Gruppe C - Prüfung (3 Methoden)
            9: {
                'feature_code': 'lm09_long_text_answer',
                'feature_name_i18n': 'learning_methods.lm09.name',
                'feature_name_fallback': 'Freitext-Langantwort',
                'feature_name_de': 'Freitext-Langantwort',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'question',
                        'type': 'text',
                        'label_fallback': 'Frage',
                        'required': True
                    },
                    {
                        'name': 'min_words',
                        'type': 'number',
                        'label_fallback': 'Mindestanzahl Wörter',
                        'default': 50,
                        'validation': {'min': 1, 'max': 10000}
                    },
                    {
                        'name': 'max_words',
                        'type': 'number',
                        'label_fallback': 'Maximalanzahl Wörter',
                        'default': 1000,
                        'validation': {'min': 1, 'max': 10000}
                    },
                    {
                        'name': 'grading_rubric',
                        'type': 'richtext',
                        'label_fallback': 'Bewertungsrubrik',
                        'required': False
                    }
                ],
                'ui_config': {
                    'ai_grading': True,
                    'word_count_display': True,
                    'rubric_display': True
                }
            },

            10: {
                'feature_code': 'lm10_ihk_exam',
                'feature_name_i18n': 'learning_methods.lm10.name',
                'feature_name_fallback': 'IHK-Stil Aufgaben',
                'feature_name_de': 'IHK-Stil Aufgaben',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'question_type',
                        'type': 'select',
                        'label_fallback': 'Fragetyp',
                        'required': True,
                        'options': [
                            {'value': 'gebunden', 'label_fallback': 'Gebundene Aufgabe'},
                            {'value': 'ungebunden', 'label_fallback': 'Ungebundene Aufgabe'},
                            {'value': 'handlungssituation', 'label_fallback': 'Handlungssituation'}
                        ]
                    },
                    {
                        'name': 'question_text',
                        'type': 'richtext',
                        'label_fallback': 'Aufgabentext',
                        'required': True
                    },
                    {
                        'name': 'max_points',
                        'type': 'number',
                        'label_fallback': 'Maximalpunkte',
                        'default': 10
                    }
                ],
                'ui_config': {
                    'ihk_format': True,
                    'points_based_grading': True,
                    'time_tracking': True
                }
            },

            11: {
                'feature_code': 'lm11_multi_step_exam',
                'feature_name_i18n': 'learning_methods.lm11.name',
                'feature_name_fallback': 'Multi-Step Praxisprüfung',
                'feature_name_de': 'Multi-Step Praxisprüfung',
                'form_type': 'dynamic',
                'language_support': ['de', 'en', 'pl'],
                'layout': 'vertical',
                'fields': [
                    {
                        'name': 'steps',
                        'type': 'array',
                        'label_fallback': 'Prüfungsschritte',
                        'required': True,
                        'min_items': 2,
                        'max_items': 10,
                        'item_schema': {
                            'type': 'object',
                            'fields': [
                                {
                                    'name': 'step_number',
                                    'type': 'number',
                                    'label_fallback': 'Schrittnummer',
                                    'readonly': True
                                },
                                {
                                    'name': 'description',
                                    'type': 'richtext',
                                    'label_fallback': 'Schrittesbeschreibung'
                                },
                                {
                                    'name': 'points',
                                    'type': 'number',
                                    'label_fallback': 'Punkte'
                                },
                                {
                                    'name': 'unlock_next_step',
                                    'type': 'checkbox',
                                    'label_fallback': 'Nächsten Schritt freischalten'
                                }
                            ]
                        }
                    }
                ],
                'ui_config': {
                    'progressive_unlock': True,
                    'partial_grading': True,
                    'step_summary': True
                }
            }
        }

    @classmethod
    def _get_system_features_schemas(cls) -> Dict[str, Dict]:
        """
        Get complete UI schemas for all 25 System Features

        Returns minimal but complete schemas for each feature
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


# Convenience functions
def seed_learning_methods_ui_schemas(**kwargs) -> int:
    """Quick function to seed learning methods UI schemas"""
    return SeedDataUISchemas.seed_learning_methods_ui_schemas(**kwargs)


def seed_system_features_ui_schemas(**kwargs) -> int:
    """Quick function to seed system features UI schemas"""
    return SeedDataUISchemas.seed_system_features_ui_schemas(**kwargs)
