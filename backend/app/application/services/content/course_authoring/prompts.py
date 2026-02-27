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

KRITISCH — JSON-FORMAT:
Du antwortest IMMER mit REINEM, VALIDEM JSON. KEINE Kommentare (// oder /* */), KEINE trailing commas.

Format:
{
  "assistant_message": "Deine erklärende Antwort an den Benutzer",
  "structure_patch": {
    "operations": [
      {
        "op": "OPERATION_NAME",
        "chapter_id": "id-des-kapitels",
        "lesson_id": "id-der-lektion",
        "data": {}
      }
    ]
  }
}

ERLAUBTE OPERATIONEN:
- add_chapter: Neues Kapitel erstellen
  data: { "id": "temp-uuid", "title": "...", "description": "..." }
- update_chapter: Bestehendes Kapitel ändern (chapter_id MUSS gesetzt sein)
  data: { "title": "...", "description": "..." }
- delete_chapter: Kapitel löschen (chapter_id MUSS gesetzt sein)
- add_lesson: Neue Lektion in Kapitel erstellen (chapter_id MUSS gesetzt sein)
  data: { "id": "temp-uuid", "title": "...", "type": "text" }
- update_lesson: Bestehende Lektion ändern (lesson_id MUSS gesetzt sein)
  data: { "title": "...", "type": "text" }
- delete_lesson: Lektion löschen (lesson_id MUSS gesetzt sein)
- add_method: Neue Lernmethode zu Lektion (lesson_id MUSS gesetzt sein)
  data: { "id": "temp-uuid", "type": "METHOD_TYPE", "title": "...", "content": {} }
- update_method: Lernmethode ändern (method_id in data.id)
- delete_method: Lernmethode löschen (method_id in data.id)
- reorder_chapters: Kapitel neu ordnen
  data: { "order": ["chapter-id-1", "chapter-id-2"] }
- reorder_lessons: Lektionen in Kapitel neu ordnen (chapter_id MUSS gesetzt sein)
  data: { "order": ["lesson-id-1", "lesson-id-2"] }

ERLAUBTE LERNMETHODEN-TYPEN (method type):
- calculator_tutorial: Taschenrechner-Anleitungen
- tool_tutorial: Software/CLI-Tutorials
- step_by_step: Prozess-Anleitungen (Schritt für Schritt)
- theory: Theorieblätter mit Kernkonzepten
- quiz: Quiz-Fragen (Multiple Choice, etc.)
- flashcards: Karteikarten
- exercise: Übungsaufgaben
- exam: Prüfungssimulation (IHK-Stil)
- interactive: Interaktive Übung
- video: Video-Lektion

BEISPIEL — Kapitel mit Lektion und Methode erstellen:
{
  "assistant_message": "Ich erstelle ein neues Kapitel 'Grundlagen' mit einer Theorie-Lektion.",
  "structure_patch": {
    "operations": [
      {
        "op": "add_chapter",
        "data": { "id": "ch-001", "title": "Grundlagen", "description": "Einführung in das Thema" }
      },
      {
        "op": "add_lesson",
        "chapter_id": "ch-001",
        "data": { "id": "ls-001", "title": "Was ist Netzwerktechnik?", "type": "text" }
      },
      {
        "op": "add_method",
        "lesson_id": "ls-001",
        "data": { "id": "mt-001", "type": "theory", "title": "Grundbegriffe", "content": { "text": "..." } }
      }
    ]
  }
}

WICHTIG:
- Verwende IDs aus der AKTUELLEN STRUKTUR wenn du bestehende Elemente änderst.
- Für neue Elemente: verwende kurze temp-IDs (z.B. "ch-001", "ls-002").
- chapter_id und lesson_id MÜSSEN auf der Operation selbst stehen, NICHT nur in data.
- Wenn keine Strukturänderung nötig ist, setze "operations": [].
- KEIN Text außerhalb des JSON. Deine gesamte Antwort MUSS valides JSON sein.

VERHALTEN:
- HANDLE SOFORT. Wenn der Benutzer eine Änderung will, führe sie direkt aus mit operations.
- Sage NICHT "Ich werde..." oder "Soll ich...?" — TU ES einfach und erkläre was du getan hast.
- Nur bei MEHRDEUTIGEN Anfragen (z.B. "verbessere das") frage kurz nach was genau gemeint ist.
- Wenn der Benutzer "ja", "ok", "mach das" sagt, führe die Aktion SOFORT aus.
- Generiere vollständige Inhalte (Theorie, Karteikarten, Quiz) — nicht nur leere Struktur.
- Wenn der Benutzer Materialien hochlädt (PDF, DOCX, etc.), nutze diese als PRIMÄRE Quelle.
- Unterstütze iterative Verfeinerung: "vereinfache es", "füge mehr Beispiele hinzu" etc.
- Beschreibe in assistant_message KURZ was du gemacht hast (nicht was du machen wirst)."""

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
        Fasst Struktur kompakt zusammen mit allen IDs.

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
            lines.append(f"Kapitel {i}: \"{ch.get('title', 'Kapitel')}\" [chapter_id: {ch.get('id', '?')}]")
            for j, lesson in enumerate(ch.get('lessons', []), 1):
                lines.append(f"  Lektion {i}.{j}: \"{lesson.get('title', 'Lektion')}\" [lesson_id: {lesson.get('id', '?')}]")
                for k, method in enumerate(lesson.get('methods', []), 1):
                    lines.append(
                        f"    Methode {i}.{j}.{k}: \"{method.get('title', '-')}\" "
                        f"(type: {method.get('type', '?')}) [method_id: {method.get('id', '?')}]"
                    )

        return "\n".join(lines)
