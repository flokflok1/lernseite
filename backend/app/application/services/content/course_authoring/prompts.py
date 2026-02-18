"""
AI prompt generation for course authoring.
"""

from typing import Dict, List, Optional


class PromptGenerator:
    """Generates system and user prompts for course authoring AI."""

    @staticmethod
    def get_system_prompt(mode: Optional[str] = None) -> str:
        """
        Returns system prompt for course authoring.

        Args:
            mode: Optional mode ('exam', 'calculator', etc.)

        Returns:
            System prompt string
        """
        base_prompt = """Du bist der LSX-Kursarchitekt, ein Experte für die Erstellung von Lernmaterialien.

Du hilfst beim Aufbau von Kursen für das LernsystemX. Du kennst:
- IHK-Prüfungsformate (AP1, AP2 für Fachinformatiker)
- Kaufmännische Berufsausbildungen
- Didaktische Best Practices

WICHTIG: Du antwortest IMMER im folgenden JSON-Format:
{
  "assistant_message": "Deine erklärende Antwort an den Benutzer",
  "structure_patch": {
    "operations": [
      {
        "op": "add_chapter|update_chapter|delete_chapter|add_lesson|update_lesson|delete_lesson|add_method|update_method|delete_method",
        "chapter_id": "id oder null",
        "lesson_id": "id oder null",
        "data": { ... }
      }
    ]
  }
}

Verfügbare Lernmethoden-Typen:
- calculator_tutorial: Taschenrechner-Anleitungen (z.B. "So rechne Prozent auf dem Casio fx-991")
- tool_tutorial: Software/CLI-Tutorials (z.B. "pfSense IPsec konfigurieren")
- step_by_step: Prozess-Anleitungen (z.B. "Handelskalkulation Schritt für Schritt")
- theory: Theorieblätter mit Kernkonzepten
- quiz: Quiz-Fragen
- flashcards: Karteikarten
- exercise: Übungsaufgaben

Operationen:
- add_chapter: Neues Kapitel { "id": "temp-uuid", "title": "...", "description": "..." }
- add_lesson: Neue Lektion { "chapter_id": "...", "id": "temp-uuid", "title": "...", "type": "text" }
- add_method: Neue Lernmethode { "lesson_id": "...", "id": "temp-uuid", "type": "calculator_tutorial", "title": "...", "content": {...} }
- update_*: Aktualisiert bestehende Elemente
- delete_*: Löscht Elemente

Wenn keine Strukturänderung nötig ist, setze "operations": []."""

        if mode == 'exam':
            base_prompt += """

MODUS: Prüfungsgenerierung
Fokussiere auf die Erstellung von Prüfungsfragen im IHK-Stil.
Nutze method_type "quiz" oder "exam" für Prüfungsinhalte."""

        elif mode == 'calculator':
            base_prompt += """

MODUS: Taschenrechner-Tutorial
Erstelle detaillierte Schritt-für-Schritt-Anleitungen für Taschenrechner.
Nutze method_type "calculator_tutorial" mit:
- calculator_model: "Casio fx-991" oder "TI-30"
- steps: Array mit Tasteneingaben und Erklärungen"""

        return base_prompt

    @staticmethod
    def build_user_prompt(
        course_info: Dict,
        draft_structure: Dict,
        user_message: str,
        file_context: str,
        history: str,
        mode: Optional[str] = None
    ) -> str:
        """
        Baut User-Prompt für KI.

        Args:
            course_info: Kurs-Informationen
            draft_structure: Aktuelle draft_structure
            user_message: Nachricht vom Benutzer
            file_context: Datei-Kontext
            history: Chat-Verlauf
            mode: Optional mode

        Returns:
            User-Prompt string
        """
        # Struktur kompakt formatieren
        structure_summary = PromptGenerator._summarize_structure(draft_structure)

        prompt = f"""KURS-INFO:
Titel: {course_info.get('title', 'Unbekannt')}
Beschreibung: {course_info.get('description', '-')}
Kategorie: {course_info.get('category', '-')}
Zielgruppe: {course_info.get('target_audience', '-')}

AKTUELLE STRUKTUR:
{structure_summary}

"""
        if file_context:
            prompt += f"""DATEI-KONTEXT (Kursmaterial):
{file_context[:3000]}

"""

        if history and history != "Keine vorherigen Nachrichten.":
            prompt += f"""CHAT-VERLAUF:
{history}

"""

        prompt += f"""BENUTZER-NACHRICHT:
{user_message}

Antworte im JSON-Format mit assistant_message und structure_patch."""

        return prompt

    @staticmethod
    def _summarize_structure(structure: Dict) -> str:
        """
        Fasst Struktur kompakt zusammen.

        Args:
            structure: Draft structure

        Returns:
            Zusammenfassung als String
        """
        chapters = structure.get('chapters', [])
        if not chapters:
            return "Keine Kapitel vorhanden."

        lines = []
        for i, ch in enumerate(chapters, 1):
            lines.append(f"{i}. {ch.get('title', 'Kapitel')} (ID: {ch.get('id', '?')})")
            for j, lesson in enumerate(ch.get('lessons', []), 1):
                methods = lesson.get('methods', [])
                method_types = [m.get('type', '?') for m in methods]
                methods_str = f" [{', '.join(method_types)}]" if methods else ""
                lines.append(f"   {i}.{j} {lesson.get('title', 'Lektion')}{methods_str}")

        return "\n".join(lines)
