"""
LernsystemX Setup - Seed Data - UI Schemas (Part 2)

Learning Methods UI schemas for Gruppe B (Praxis) and Gruppe C (Pruefung):
- Gruppe B - Praxis (4 Methoden: lm05-lm08)
  - lm05: Mathe-Interaktiv
  - lm06: Flashcards
  - lm07: Drag & Drop
  - lm08: Lückentext

- Gruppe C - Pruefung (3 Methoden: lm09-lm11)
  - lm09: Freitext-Langantwort
  - lm10: IHK-Stil Aufgaben
  - lm11: Multi-Step Praxisprüfung

Split from ui_schemas.py for Quality Gate G01 compliance (max 500 lines).
"""

from typing import Dict


def get_learning_methods_schemas_group_b_c() -> Dict[int, Dict]:
    """
    UI schemas for Gruppe B - Praxis (lm05-lm08) and Gruppe C - Pruefung (lm09-lm11)

    Returns:
        Dictionary mapping method_type (5-11) to UI schema definitions.
    """
    return {
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

        # Gruppe C - Pruefung (3 Methoden)
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
