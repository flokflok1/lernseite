"""
Learning Method Repository - AI Execution (Part 2: Prompt Building)

Method-specific prompt construction for AI-powered learning methods:
- _build_method_prompt: Route to correct prompt template by method type
- _extract_content_text: Parse lesson content (dict or string)
- _prompt_*: Individual prompt templates for each learning method type

Split from ai_execution.py for Quality Gate G01 compliance (<500 lines).
"""

from typing import Any, Optional
import json


class LearningMethodAIPromptsMixin:
    """
    Prompt building methods for AI-powered learning methods.

    Mixin class used by LearningMethodAIRepository.
    """

    @classmethod
    def _build_method_prompt(
        cls,
        method_type: Optional[int],
        method_name: str,
        method_description: str,
        lesson_title: Optional[str],
        lesson_content: Optional[Any],
        course_title: Optional[str],
        difficulty: Optional[str],
        language: str = 'de'
    ) -> str:
        """
        Build method-specific prompt based on learning method type.

        Args:
            method_type: Learning method type ID (e.g., 0 for LM0)
            method_name: Name of learning method
            method_description: Instructions for method
            lesson_title: Lesson title
            lesson_content: Lesson content (JSONB)
            course_title: Course title
            difficulty: Difficulty level
            language: Target language

        Returns:
            Constructed prompt string for AI
        """
        # Extract text content from lesson_content
        content_text = cls._extract_content_text(lesson_content)

        # Build context parts
        context_parts = []
        if course_title:
            context_parts.append(f"Kurs: {course_title}")
        if lesson_title:
            context_parts.append(f"Lektion: {lesson_title}")
        context_str = ", ".join(context_parts) if context_parts else "Allgemeiner Kontext"

        difficulty_str = difficulty or "mittel"

        # Method-specific prompts
        if method_type == 12:  # LM12 = Mathe-Interaktiv
            return cls._prompt_math_interactive(
                context_str, difficulty_str, method_description, content_text
            )
        elif method_type == 0:  # LM0 = Deep Explanation
            return cls._prompt_deep_explanation(
                context_str, method_description, lesson_title, content_text
            )
        elif method_type == 1:  # LM1 = Step-by-Step
            return cls._prompt_step_by_step(
                context_str, method_description, lesson_title, content_text
            )
        elif method_type == 13:  # LM13 = Flashcards
            return cls._prompt_flashcards(context_str, method_description, content_text)
        elif method_type == 19:  # LM19 = IHK-Style
            return cls._prompt_ihk_style(
                context_str, difficulty_str, method_description, content_text
            )
        elif method_type == 22:  # LM22 = Exam Quiz
            return cls._prompt_exam_quiz(context_str, method_description, content_text)
        else:
            return cls._prompt_default(
                method_name, context_str, difficulty_str, method_description,
                lesson_title, content_text
            )

    @classmethod
    def _extract_content_text(cls, lesson_content: Optional[Any]) -> str:
        """Extract text from lesson content (dict or string)."""
        if not lesson_content:
            return ''

        if isinstance(lesson_content, dict):
            for key in ('text', 'content', 'body'):
                if key in lesson_content:
                    return lesson_content[key]
            return json.dumps(lesson_content, ensure_ascii=False, indent=2)
        elif isinstance(lesson_content, str):
            return lesson_content

        return ''

    @staticmethod
    def _prompt_math_interactive(context: str, difficulty: str, task: str, content: str) -> str:
        """Prompt for math interactive method (LM12)."""
        return f"""Du bist ein KI-Tutor für Mathematik und Kalkulationen im Bereich IHK-Prüfungsvorbereitung.

Kontext: {context}
Schwierigkeitsgrad: {difficulty}

Aufgabe: {task}

Basierend auf dem Lektionsinhalt, erstelle eine interaktive Mathematik-Aufgabe.

Lektionsinhalt:
{content[:2000] if content else 'Bezugskalkulation und kaufmännisches Rechnen'}

Erstelle eine Rechenaufgabe mit:
1. Einer klaren Aufgabenstellung
2. Realistischen Zahlen (z.B. Einkaufspreise, Rabatte, Bezugskosten)
3. Schritt-für-Schritt Lösung zum Aufklappen
4. Erklärung des Rechenwegs

Format die Ausgabe als strukturierte Aufgabe mit Lösung."""

    @staticmethod
    def _prompt_deep_explanation(context: str, task: str, lesson: str, content: str) -> str:
        """Prompt for deep explanation method (LM0)."""
        return f"""Du bist ein erfahrener KI-Tutor.

Kontext: {context}
Aufgabe: {task}

Erkläre das Thema "{lesson or 'dieses Konzept'}" tiefgehend mit:
1. Einer klaren Definition
2. Praktischen Beispielen
3. Analogien zum besseren Verständnis
4. Zusammenfassung der Kernpunkte

Lektionsinhalt zur Referenz:
{content[:2000] if content else 'Keine spezifischen Inhalte verfügbar'}"""

    @staticmethod
    def _prompt_step_by_step(context: str, task: str, lesson: str, content: str) -> str:
        """Prompt for step-by-step method (LM1)."""
        return f"""Du bist ein KI-Tutor für schrittweise Erklärungen.

Kontext: {context}
Aufgabe: {task}

Erkläre das Thema "{lesson or 'dieses Konzept'}" in nummerierten Schritten:
1. Beginne mit den Grundlagen
2. Baue systematisch darauf auf
3. Verwende praktische Beispiele
4. Schließe mit einer Zusammenfassung ab

Lektionsinhalt:
{content[:2000] if content else 'Keine spezifischen Inhalte verfügbar'}"""

    @staticmethod
    def _prompt_flashcards(context: str, task: str, content: str) -> str:
        """Prompt for flashcards method (LM13)."""
        return f"""Erstelle Lernkarten (Flashcards) für das Thema.

Kontext: {context}
Aufgabe: {task}

Basierend auf dem Lektionsinhalt, erstelle 5-10 Flashcards im Format:
**Frage:** [Frage hier]
**Antwort:** [Antwort hier]
---

Lektionsinhalt:
{content[:2000] if content else 'Keine spezifischen Inhalte verfügbar'}"""

    @staticmethod
    def _prompt_ihk_style(context: str, difficulty: str, task: str, content: str) -> str:
        """Prompt for IHK-style method (LM19)."""
        return f"""Du bist ein IHK-Prüfungsexperte.

Kontext: {context}
Schwierigkeitsgrad: {difficulty}
Aufgabe: {task}

Erstelle eine prüfungsnahe Aufgabe im IHK-Stil mit:
1. Situationsbeschreibung
2. Konkrete Fragestellung
3. Relevante Daten/Zahlen
4. Musterlösung mit Punkteverteilung

Lektionsinhalt:
{content[:2000] if content else 'Kaufmännische Inhalte'}"""

    @staticmethod
    def _prompt_exam_quiz(context: str, task: str, content: str) -> str:
        """Prompt for exam quiz method (LM22)."""
        return f"""Erstelle ein Quiz zum Thema.

Kontext: {context}
Aufgabe: {task}

Erstelle 5 Multiple-Choice-Fragen mit:
- 4 Antwortmöglichkeiten pro Frage
- Einer korrekten Antwort (markiert)
- Kurzer Erklärung warum die Antwort richtig ist

Lektionsinhalt:
{content[:2000] if content else 'Keine spezifischen Inhalte verfügbar'}"""

    @staticmethod
    def _prompt_default(name: str, context: str, difficulty: str, task: str,
                       lesson: str, content: str) -> str:
        """Default prompt for unknown method types."""
        return f"""Du bist ein KI-Tutor für die Lernmethode "{name}".

Kontext: {context}
Schwierigkeitsgrad: {difficulty}

Aufgabe: {task if task else 'Erstelle eine interaktive Lernaufgabe zum Thema.'}

Thema der Lektion: {lesson or 'Allgemeines Thema'}

Lektionsinhalt:
{content[:2000] if content else 'Erstelle eine passende Aufgabe basierend auf dem Lektionsthema.'}

Erstelle eine strukturierte, interaktive Aufgabe die dem Lernenden hilft, das Thema zu verstehen und zu üben."""
