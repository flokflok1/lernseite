"""
Tutor Knowledge Service Package

Lädt Tutor-Wissen aus DB/Kurs-Inhalten für den KI-Tutor:
- Kurs-Inhalte (Titel, Beschreibungen, Lernziele)
- Kapitel-Struktur
- Lektions-Inhalte
- Lernmethoden-Daten
- Kurs-Dateien (PDFs, Skripte)
- Lernfortschritt des Users

Der Tutor kann damit kontextbezogene Erklärungen geben,
basierend auf dem aktuellen Lernstand des Schülers.
"""

from typing import Dict, Any, Optional, List
import logging

# Import sub-modules
from . import context_loader, method_loader, file_loader, progress_loader, prompt_builder

logger = logging.getLogger(__name__)


class TutorKnowledgeService:
    """
    Service zum Laden von Tutor-Wissen aus der Datenbank.

    Der Tutor verwendet dieses Wissen um:
    - Kontextbezogene Erklärungen zu geben
    - Aufgaben basierend auf Kurs-Inhalten zu generieren
    - Verweise auf relevante Materialien zu machen
    - Den Lernfortschritt zu berücksichtigen
    """

    # =========================================================================
    # KURS-KONTEXT LADEN
    # =========================================================================

    @classmethod
    def get_course_context(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Lädt den vollständigen Kurs-Kontext für den Tutor.

        Args:
            course_id: UUID des Kurses

        Returns:
            Dict mit Kurs-Informationen für den Tutor
        """
        return context_loader.get_course_context(course_id)

    @classmethod
    def get_chapter_context(cls, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Lädt den Kapitel-Kontext mit allen Lektionen und Lernmethoden.

        Args:
            chapter_id: UUID des Kapitels

        Returns:
            Dict mit Kapitel-Details für den Tutor
        """
        return context_loader.get_chapter_context(chapter_id)

    @classmethod
    def get_lesson_content(cls, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Lädt den vollständigen Inhalt einer Lektion für den Tutor.

        Args:
            lesson_id: ID der Lektion

        Returns:
            Dict mit Lektions-Inhalt
        """
        return context_loader.get_lesson_content(lesson_id)

    # =========================================================================
    # LERNMETHODEN-WISSEN
    # =========================================================================

    @classmethod
    def get_learning_method_data(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """
        Lädt die vollständigen Daten einer Lernmethode.

        Args:
            method_id: UUID der Lernmethode

        Returns:
            Dict mit Lernmethoden-Daten inkl. JSONB-Content
        """
        return method_loader.get_learning_method_data(method_id)

    # =========================================================================
    # KURS-DATEIEN (SKRIPTE, MATERIALIEN)
    # =========================================================================

    @classmethod
    def get_course_files(
        cls,
        course_id: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lädt Kurs-Dateien (PDFs, Skripte, Materialien).

        Args:
            course_id: UUID des Kurses
            category: Optional: 'script', 'material', 'exercise', etc.

        Returns:
            Liste der Dateien mit Metadaten
        """
        return file_loader.get_course_files(course_id, category)

    # =========================================================================
    # USER PROGRESS (Lernfortschritt)
    # =========================================================================

    @classmethod
    def get_user_progress(
        cls,
        user_id: str,
        course_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Lädt den Lernfortschritt eines Users in einem Kurs.

        Args:
            user_id: UUID des Users
            course_id: UUID des Kurses

        Returns:
            Dict mit Fortschrittsdaten
        """
        return progress_loader.get_user_progress(user_id, course_id)

    # =========================================================================
    # TUTOR-PROMPT BUILDER
    # =========================================================================

    @classmethod
    def build_tutor_context_prompt(
        cls,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        lesson_id: Optional[int] = None,
        method_id: Optional[str] = None,
        user_id: Optional[str] = None,
        include_files: bool = True,
        include_progress: bool = True
    ) -> str:
        """
        Baut einen Kontext-Prompt für den KI-Tutor basierend auf DB-Inhalten.

        Args:
            course_id: Kurs-ID für Kurs-Kontext
            chapter_id: Kapitel-ID für detaillierten Kapitel-Kontext
            lesson_id: Lektions-ID für Lektions-Inhalt
            method_id: Lernmethoden-ID für spezifische Aufgaben
            user_id: User-ID für Fortschrittsdaten
            include_files: Kurs-Dateien einbeziehen
            include_progress: Lernfortschritt einbeziehen

        Returns:
            Formatierter Kontext-String für den Tutor-Prompt
        """
        return prompt_builder.build_tutor_context_prompt(
            course_id=course_id,
            chapter_id=chapter_id,
            lesson_id=lesson_id,
            method_id=method_id,
            user_id=user_id,
            include_files=include_files,
            include_progress=include_progress
        )


__all__ = ['TutorKnowledgeService']
