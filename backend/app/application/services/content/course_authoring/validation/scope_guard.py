"""
Scope Guard — Security-Layer für AI Editor Operationen.

Prüft ob KI-generierte Operationen im erlaubten Scope liegen.
Blockiert Out-of-Scope Operationen und loggt sie.

DDD-Layer: Application (Orchestrierung zwischen Domain-Scope und Operations)
"""

import logging
from typing import Dict, List, Tuple

from app.domain.ai.scope import (
    OperationScope,
    DESTRUCTIVE_OPS,
    SCOPE_LESSON,
    SCOPE_CHAPTER,
)

logger = logging.getLogger(__name__)


class ScopeGuard:
    """Prüft Operationen gegen den definierten Scope."""

    @staticmethod
    def check(
        operations: List[Dict],
        scope: OperationScope,
        draft_structure: Dict
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Filtert Operationen nach Scope.

        Args:
            operations: Liste der KI-generierten Operationen
            scope: Erlaubter Änderungs-Bereich
            draft_structure: Aktuelle Kursstruktur (für ID-Lookups)

        Returns:
            (allowed_ops, blocked_ops) — blocked_ops haben extra 'block_reason'
        """
        allowed = []
        blocked = []

        # Max-Operations-Limit prüfen
        if len(operations) > scope.max_operations:
            logger.warning(
                f"Scope Guard: {len(operations)} operations exceed limit "
                f"of {scope.max_operations} for scope '{scope.scope_type}'. "
                f"Truncating to limit."
            )
            excess = operations[scope.max_operations:]
            for op in excess:
                blocked.append({
                    **op,
                    'block_reason': 'max_operations_exceeded'
                })
            operations = operations[:scope.max_operations]

        # Kurs-weiter Scope: Alles erlaubt (Plan-Tab, Struktur-Modus)
        if scope.is_course_wide:
            return operations, blocked

        for op in operations:
            op_type = op.get('op', '')
            reason = ScopeGuard._check_single(op, op_type, scope, draft_structure)

            if reason:
                blocked.append({**op, 'block_reason': reason})
            else:
                allowed.append(op)

        if blocked:
            blocked_summary = [
                f"{b['op']}({b.get('block_reason')})"
                for b in blocked
            ]
            logger.warning(
                f"Scope Guard blocked {len(blocked)} operations: {blocked_summary}"
            )

        return allowed, blocked

    @staticmethod
    def _check_single(
        op: Dict,
        op_type: str,
        scope: OperationScope,
        draft_structure: Dict
    ) -> str:
        """
        Prüft eine einzelne Operation.

        Returns:
            Block-Grund als String, oder '' wenn erlaubt.
        """
        # 1. Operation-Typ im Scope erlaubt?
        if op_type not in scope.allowed_ops:
            return f'op_not_allowed_in_{scope.scope_type}_scope'

        # 2. Ziel-Element im Scope?
        if scope.scope_type == SCOPE_LESSON:
            return ScopeGuard._check_lesson_scope(op, op_type, scope, draft_structure)
        elif scope.scope_type == SCOPE_CHAPTER:
            return ScopeGuard._check_chapter_scope(op, op_type, scope, draft_structure)

        return ''

    @staticmethod
    def _check_lesson_scope(
        op: Dict,
        op_type: str,
        scope: OperationScope,
        draft_structure: Dict
    ) -> str:
        """Prüft ob Operation innerhalb des Lesson-Scopes liegt."""
        # update_lesson: lesson_id muss im Scope sein
        if op_type == 'update_lesson':
            lesson_id = op.get('lesson_id') or op.get('data', {}).get('lesson_id')
            if lesson_id and lesson_id not in scope.lesson_ids:
                return 'lesson_out_of_scope'

        # add/update/delete_method: lesson_id muss im Scope sein
        if op_type in ('add_method', 'update_method', 'delete_method'):
            lesson_id = op.get('lesson_id') or op.get('data', {}).get('lesson_id')
            if lesson_id and lesson_id not in scope.lesson_ids:
                return 'method_lesson_out_of_scope'

            # delete_method: Methode muss zur erlaubten Lektion gehören
            if op_type == 'delete_method':
                method_id = op.get('data', {}).get('id') or op.get('method_id')
                if method_id:
                    owner_lesson = ScopeGuard._find_method_lesson(
                        method_id, draft_structure
                    )
                    if owner_lesson and owner_lesson not in scope.lesson_ids:
                        return 'method_belongs_to_other_lesson'

        return ''

    @staticmethod
    def _check_chapter_scope(
        op: Dict,
        op_type: str,
        scope: OperationScope,
        draft_structure: Dict
    ) -> str:
        """Prüft ob Operation innerhalb des Chapter-Scopes liegt."""
        # update_chapter: chapter_id muss im Scope sein
        if op_type == 'update_chapter':
            chapter_id = op.get('chapter_id') or op.get('data', {}).get('chapter_id')
            if chapter_id and chapter_id not in scope.chapter_ids:
                return 'chapter_out_of_scope'

        # add/update/delete_lesson: Lektion muss im erlaubten Kapitel sein
        if op_type in ('add_lesson', 'update_lesson', 'delete_lesson'):
            chapter_id = op.get('chapter_id')
            if chapter_id and chapter_id not in scope.chapter_ids:
                return 'lesson_chapter_out_of_scope'

            # Für update/delete: Lektion via Draft prüfen
            if op_type in ('update_lesson', 'delete_lesson'):
                lesson_id = op.get('lesson_id') or op.get('data', {}).get('id')
                if lesson_id:
                    owner_chapter = ScopeGuard._find_lesson_chapter(
                        lesson_id, draft_structure
                    )
                    if owner_chapter and owner_chapter not in scope.chapter_ids:
                        return 'lesson_in_other_chapter'

        # Methods: zugehörige Lektion muss im Kapitel-Scope sein
        if op_type in ('add_method', 'update_method', 'delete_method'):
            lesson_id = op.get('lesson_id') or op.get('data', {}).get('lesson_id')
            if lesson_id:
                owner_chapter = ScopeGuard._find_lesson_chapter(
                    lesson_id, draft_structure
                )
                if owner_chapter and owner_chapter not in scope.chapter_ids:
                    return 'method_lesson_in_other_chapter'

        # reorder_lessons: chapter_id muss im Scope sein
        if op_type == 'reorder_lessons':
            chapter_id = op.get('chapter_id') or op.get('data', {}).get('chapter_id')
            if chapter_id and chapter_id not in scope.chapter_ids:
                return 'reorder_chapter_out_of_scope'

        return ''

    @staticmethod
    def _find_lesson_chapter(lesson_id: str, draft: Dict) -> str:
        """Findet das Kapitel einer Lektion in der draft_structure."""
        for ch in draft.get('chapters', []):
            for lesson in ch.get('lessons', []):
                if lesson.get('id') == lesson_id:
                    return ch.get('id', '')
        return ''

    @staticmethod
    def _find_method_lesson(method_id: str, draft: Dict) -> str:
        """Findet die Lektion einer Methode in der draft_structure."""
        for ch in draft.get('chapters', []):
            for lesson in ch.get('lessons', []):
                for method in lesson.get('methods', []):
                    if method.get('id') == method_id:
                        return lesson.get('id', '')
        return ''
