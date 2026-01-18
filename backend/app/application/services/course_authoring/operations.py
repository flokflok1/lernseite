"""
Structure patch operations for course authoring.
"""

import logging
import uuid
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class StructureOperations:
    """Handles draft structure patch operations."""

    @staticmethod
    def apply_operations(structure: Dict, operations: List[Dict]) -> Dict:
        """
        Wendet Operationen auf draft_structure an.

        Args:
            structure: Aktuelle draft_structure
            operations: Liste der Operationen

        Returns:
            Aktualisierte structure
        """
        for op in operations:
            op_type = op.get('op')
            data = op.get('data', {})

            try:
                if op_type == 'add_chapter':
                    StructureOperations._add_chapter(structure, data)
                elif op_type == 'update_chapter':
                    StructureOperations._update_chapter(structure, op, data)
                elif op_type == 'delete_chapter':
                    StructureOperations._delete_chapter(structure, op, data)
                elif op_type == 'add_lesson':
                    StructureOperations._add_lesson(structure, op, data)
                elif op_type == 'update_lesson':
                    StructureOperations._update_lesson(structure, op, data)
                elif op_type == 'delete_lesson':
                    StructureOperations._delete_lesson(structure, op, data)
                elif op_type == 'add_method':
                    StructureOperations._add_method(structure, op, data)
                elif op_type == 'update_method':
                    StructureOperations._update_method(structure, op, data)
                elif op_type == 'delete_method':
                    StructureOperations._delete_method(structure, op, data)

                structure['meta']['last_operation'] = op_type

            except Exception as e:
                logger.error(f"Error applying operation {op_type}: {e}")

        return structure

    @staticmethod
    def _add_chapter(structure: Dict, data: Dict) -> None:
        """Add chapter to structure."""
        chapter = {
            'id': data.get('id', str(uuid.uuid4())),
            'title': data.get('title', 'Neues Kapitel'),
            'description': data.get('description', ''),
            'existing_id': None,
            'lessons': []
        }
        structure['chapters'].append(chapter)

    @staticmethod
    def _update_chapter(structure: Dict, op: Dict, data: Dict) -> None:
        """Update chapter in structure."""
        chapter_id = op.get('chapter_id') or data.get('id')
        for ch in structure['chapters']:
            if ch['id'] == chapter_id:
                ch.update({k: v for k, v in data.items() if k != 'id'})
                break

    @staticmethod
    def _delete_chapter(structure: Dict, op: Dict, data: Dict) -> None:
        """Delete chapter from structure."""
        chapter_id = op.get('chapter_id') or data.get('id')
        structure['chapters'] = [
            ch for ch in structure['chapters'] if ch['id'] != chapter_id
        ]

    @staticmethod
    def _add_lesson(structure: Dict, op: Dict, data: Dict) -> None:
        """Add lesson to structure."""
        chapter_id = op.get('chapter_id') or data.get('chapter_id')
        lesson = {
            'id': data.get('id', str(uuid.uuid4())),
            'title': data.get('title', 'Neue Lektion'),
            'type': data.get('type', 'text'),
            'existing_id': None,
            'methods': []
        }
        for ch in structure['chapters']:
            if ch['id'] == chapter_id:
                ch['lessons'].append(lesson)
                break

    @staticmethod
    def _update_lesson(structure: Dict, op: Dict, data: Dict) -> None:
        """Update lesson in structure."""
        lesson_id = op.get('lesson_id') or data.get('id')
        for ch in structure['chapters']:
            for lesson in ch['lessons']:
                if lesson['id'] == lesson_id:
                    lesson.update({k: v for k, v in data.items() if k != 'id'})
                    break

    @staticmethod
    def _delete_lesson(structure: Dict, op: Dict, data: Dict) -> None:
        """Delete lesson from structure."""
        lesson_id = op.get('lesson_id') or data.get('id')
        for ch in structure['chapters']:
            ch['lessons'] = [
                l for l in ch['lessons'] if l['id'] != lesson_id
            ]

    @staticmethod
    def _add_method(structure: Dict, op: Dict, data: Dict) -> None:
        """Add method to structure."""
        lesson_id = op.get('lesson_id') or data.get('lesson_id')
        method = {
            'id': data.get('id', str(uuid.uuid4())),
            'type': data.get('type', 'theory'),
            'title': data.get('title', 'Neue Methode'),
            'content': data.get('content', {})
        }
        for ch in structure['chapters']:
            for lesson in ch['lessons']:
                if lesson['id'] == lesson_id:
                    lesson['methods'].append(method)
                    break

    @staticmethod
    def _update_method(structure: Dict, op: Dict, data: Dict) -> None:
        """Update method in structure."""
        method_id = op.get('method_id') or data.get('id')
        for ch in structure['chapters']:
            for lesson in ch['lessons']:
                for method in lesson['methods']:
                    if method['id'] == method_id:
                        method.update({k: v for k, v in data.items() if k != 'id'})
                        break

    @staticmethod
    def _delete_method(structure: Dict, op: Dict, data: Dict) -> None:
        """Delete method from structure."""
        method_id = op.get('method_id') or data.get('id')
        for ch in structure['chapters']:
            for lesson in ch['lessons']:
                lesson['methods'] = [
                    m for m in lesson['methods'] if m['id'] != method_id
                ]
