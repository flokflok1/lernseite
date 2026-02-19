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

Schema data is split across three files for Quality Gate G01 compliance:
- ui_schemas.py: Class, public methods, Gruppe A schemas (lm00-lm04)
- ui_schemas_part2.py: Gruppe B+C schemas (lm05-lm11)
- ui_schemas_part3.py: System Features schemas (25 features)

ISO 9001:2015 compliant - Data standardization
ISO/IEC/IEEE 26515:2018 compliant - Schema design
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

from app.infrastructure.persistence.database.connection import fetch_one, execute_query, insert_returning

from app.setup.seeds.ui_schemas_part2 import get_learning_methods_schemas_group_b_c
from app.setup.seeds.ui_schemas_part3 import get_system_features_schemas


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
        if skip_existing:
            existing = fetch_one(
                "SELECT COUNT(*) FROM learning_methods.learning_method_types WHERE ui_schema IS NOT NULL"
            )
            if existing and existing['count'] >= 12:
                return 0

        ui_schemas = cls._get_learning_methods_schemas()

        updated = 0
        for method_type, schema in ui_schemas.items():
            try:
                result = execute_query(
                    """
                    UPDATE learning_methods.learning_method_types
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

        NOTE: Currently skipped because support_systems.system_features table
        does not have a ui_schema column. UI schemas for features are stored
        in the config jsonb column instead.

        Args:
            skip_existing: Skip if schemas already seeded

        Returns:
            Number of schemas updated (always 0 for now)
        """
        return 0

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
        schemas = _get_learning_methods_schemas_group_a()
        schemas.update(get_learning_methods_schemas_group_b_c())
        return schemas

    @classmethod
    def _get_system_features_schemas(cls) -> Dict[str, Dict]:
        """
        Get complete UI schemas for all 25 System Features

        Returns minimal but complete schemas for each feature.
        Data defined in ui_schemas_part3.py for file size compliance.
        """
        return get_system_features_schemas()


def _get_learning_methods_schemas_group_a() -> Dict[int, Dict]:
    """
    UI schemas for Gruppe A - Erklaerend (5 Methoden: lm00-lm04)

    Returns:
        Dictionary mapping method_type (0-4) to UI schema definitions.
    """
    return {
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
    }


# Convenience functions
def seed_learning_methods_ui_schemas(**kwargs) -> int:
    """Quick function to seed learning methods UI schemas"""
    return SeedDataUISchemas.seed_learning_methods_ui_schemas(**kwargs)


def seed_system_features_ui_schemas(**kwargs) -> int:
    """Quick function to seed system features UI schemas"""
    return SeedDataUISchemas.seed_system_features_ui_schemas(**kwargs)
