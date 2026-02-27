"""
Structure patch operations for course authoring.
"""

import logging
import uuid
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class StructureOperations:
    """Handles draft structure patch operations."""

    @staticmethod
    def apply_operations(
        structure: Dict, operations: List[Dict]
    ) -> Tuple[Dict, List[str], List[Dict]]:
        """
        Wendet Operationen auf draft_structure an.

        Args:
            structure: Aktuelle draft_structure
            operations: Liste der Operationen

        Returns:
            Tuple of (updated structure, list of applied op names, list of failed ops with errors)
        """
        applied: List[str] = []
        failed: List[Dict] = []

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
                elif op_type == 'reorder_chapters':
                    StructureOperations._reorder_chapters(structure, data)
                elif op_type == 'reorder_lessons':
                    StructureOperations._reorder_lessons(structure, op, data)
                elif op_type == 'set_meta':
                    StructureOperations._set_meta(structure, data)
                else:
                    logger.warning(f"Unknown operation type: {op_type}")
                    failed.append({'op': op_type, 'error': f'Unknown operation type: {op_type}'})
                    continue

                structure['meta']['last_operation'] = op_type
                applied.append(op_type)

            except Exception as e:
                logger.error(f"Error applying operation {op_type}: {e}", exc_info=True)
                failed.append({'op': op_type, 'error': str(e)})

        return structure, applied, failed

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
                ch.update({k: v for k, v in data.items() if k not in ('id', 'existing_id')})
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
        # Preserve content if AI generated it
        if data.get('content'):
            lesson['content'] = data['content']
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
                    lesson.update({k: v for k, v in data.items() if k not in ('id', 'existing_id')})
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
                        method.update({k: v for k, v in data.items() if k not in ('id', 'existing_id')})
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

    @staticmethod
    def _reorder_chapters(structure: Dict, data: Dict) -> None:
        """Reorder chapters by ID list."""
        order = data.get('order', [])
        if not order:
            return
        chapters_by_id = {ch['id']: ch for ch in structure['chapters']}
        reordered = [chapters_by_id[cid] for cid in order if cid in chapters_by_id]
        # Append any chapters not in the order list at the end
        remaining = [ch for ch in structure['chapters'] if ch['id'] not in set(order)]
        structure['chapters'] = reordered + remaining

    @staticmethod
    def _reorder_lessons(structure: Dict, op: Dict, data: Dict) -> None:
        """Reorder lessons within a chapter by ID list."""
        chapter_id = op.get('chapter_id') or data.get('chapter_id')
        order = data.get('order', [])
        if not order or not chapter_id:
            return
        for ch in structure['chapters']:
            if ch['id'] == chapter_id:
                lessons_by_id = {l['id']: l for l in ch['lessons']}
                reordered = [lessons_by_id[lid] for lid in order if lid in lessons_by_id]
                remaining = [l for l in ch['lessons'] if l['id'] not in set(order)]
                ch['lessons'] = reordered + remaining
                break

    @staticmethod
    def _set_meta(structure: Dict, data: Dict) -> None:
        """Set metadata on the draft structure."""
        if 'meta' not in structure:
            structure['meta'] = {}
        for key, value in data.items():
            structure['meta'][key] = value
