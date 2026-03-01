"""
Validation utilities for course authoring operations.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class OperationValidator:
    """Validates patch operations and method types."""

    # Erlaubte Patch-Operationen
    VALID_OPERATIONS = {
        'add_chapter', 'update_chapter', 'delete_chapter',
        'add_lesson', 'update_lesson', 'delete_lesson',
        'add_method', 'update_method', 'delete_method',
        'reorder_chapters', 'reorder_lessons',
        'set_meta'
    }

    # Erlaubte Lernmethoden-Typen
    VALID_METHOD_TYPES = {
        'calculator_tutorial',  # Taschenrechner-Anleitung
        'tool_tutorial',        # Software/CLI-Tutorial
        'step_by_step',         # Prozess-Anleitung
        'theory',               # Theorieblatt
        'quiz',                 # Quiz
        'flashcards',           # Karteikarten
        'exam',                 # Prüfungssimulation
        'exercise',             # Übungsaufgabe
        'video',                # Video-Lektion
        'interactive'           # Interaktive Übung
    }

    @classmethod
    def validate_operations(cls, operations: List[Dict]) -> List[Dict]:
        """
        Validiert Patch-Operationen.

        Args:
            operations: Liste der zu validierenden Operationen

        Returns:
            Liste der validierten Operationen
        """
        validated = []
        for op in operations:
            op_type = op.get('op')
            if op_type not in cls.VALID_OPERATIONS:
                logger.warning(f"Invalid operation type: {op_type}")
                continue

            # Methoden-Typ validieren falls vorhanden
            if 'method' in op_type and op.get('data', {}).get('type'):
                method_type = op['data']['type']
                if method_type not in cls.VALID_METHOD_TYPES:
                    logger.warning(f"Invalid method type: {method_type}")
                    continue

            validated.append(op)

        return validated
