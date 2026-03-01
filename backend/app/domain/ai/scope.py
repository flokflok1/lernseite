"""
Operation Scope — Value Object für AI Editor Security.

Definiert den Änderungs-Bereich einer KI-Operation.
Der Scope wird vom Frontend bestimmt (was hat der User ausgewählt?)
und vom ScopeGuard durchgesetzt.
"""

from dataclasses import dataclass, field
from typing import Set, Optional


# Scope-Typen: Von restriktiv zu offen
SCOPE_LESSON = 'lesson'      # Nur eine Lektion + ihre Methoden
SCOPE_CHAPTER = 'chapter'    # Ein Kapitel + alle Lektionen darin
SCOPE_COURSE = 'course'      # Ganzer Kurs (Struktur-Modus / Plan-Tab)

# Welche Operationen pro Scope erlaubt sind
SCOPE_ALLOWED_OPS = {
    SCOPE_LESSON: {
        'update_lesson',
        'add_method', 'update_method', 'delete_method',
    },
    SCOPE_CHAPTER: {
        'update_chapter',
        'add_lesson', 'update_lesson', 'delete_lesson',
        'add_method', 'update_method', 'delete_method',
        'reorder_lessons',
    },
    SCOPE_COURSE: {
        'add_chapter', 'update_chapter', 'delete_chapter',
        'add_lesson', 'update_lesson', 'delete_lesson',
        'add_method', 'update_method', 'delete_method',
        'reorder_chapters', 'reorder_lessons',
    },
}

# Max. Operationen pro Scope (Halluzinations-Schutz)
SCOPE_MAX_OPS = {
    SCOPE_LESSON: 10,
    SCOPE_CHAPTER: 25,
    SCOPE_COURSE: 50,
}

# Destruktive Operationen die extra Prüfung brauchen
DESTRUCTIVE_OPS = {'delete_chapter', 'delete_lesson', 'delete_method'}


@dataclass(frozen=True)
class OperationScope:
    """
    Definiert was die KI ändern darf.

    Wird aus dem Frontend-Kontext abgeleitet:
    - User klickt auf Lektion → scope_type='lesson'
    - User klickt auf Kapitel → scope_type='chapter'
    - User ist im Plan-Tab / Kurs-Übersicht → scope_type='course'
    """
    scope_type: str
    course_id: str
    chapter_ids: Set[str] = field(default_factory=set)
    lesson_ids: Set[str] = field(default_factory=set)

    @property
    def allowed_ops(self) -> Set[str]:
        return SCOPE_ALLOWED_OPS.get(self.scope_type, set())

    @property
    def max_operations(self) -> int:
        return SCOPE_MAX_OPS.get(self.scope_type, 10)

    @property
    def is_course_wide(self) -> bool:
        return self.scope_type == SCOPE_COURSE

    @classmethod
    def for_lesson(cls, course_id: str, chapter_id: str, lesson_id: str) -> 'OperationScope':
        """Scope für eine einzelne Lektion."""
        return cls(
            scope_type=SCOPE_LESSON,
            course_id=course_id,
            chapter_ids={chapter_id},
            lesson_ids={lesson_id}
        )

    @classmethod
    def for_chapter(cls, course_id: str, chapter_id: str) -> 'OperationScope':
        """Scope für ein Kapitel mit allen Lektionen."""
        return cls(
            scope_type=SCOPE_CHAPTER,
            course_id=course_id,
            chapter_ids={chapter_id}
        )

    @classmethod
    def for_course(cls, course_id: str) -> 'OperationScope':
        """Scope für den gesamten Kurs (Plan-Tab, Struktur-Modus)."""
        return cls(
            scope_type=SCOPE_COURSE,
            course_id=course_id
        )
