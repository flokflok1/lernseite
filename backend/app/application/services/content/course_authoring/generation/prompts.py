"""
AI prompt generation for course authoring.

Phase D: Prompts optimiert für Tool Calling (Level 2).
Die KI nutzt Tools für Strukturänderungen statt JSON-Text.
Fallback-Kompatibilität mit Text-Parsing bleibt erhalten.
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

TOOLS:
Du hast Tools zur Verfügung um Kursinhalte zu erstellen und zu bearbeiten.
Nutze die Tools um Kapitel, Lektionen und Lernmethoden zu erstellen, ändern oder löschen.
Deine Text-Antwort erklärt dem User was du getan hast.

REGELN FÜR TOOL-NUTZUNG:
- Verwende IDs aus der AKTUELLEN STRUKTUR wenn du bestehende Elemente änderst.
- Für neue Elemente: verwende kurze temp-IDs (z.B. "ch-001", "ls-002", "mt-001").
- Wenn keine Strukturänderung nötig ist, antworte nur mit Text (keine Tool Calls).

INHALT — VOLLSTÄNDIG:
- Generiere VOLLSTÄNDIGE Inhalte — KEINE leeren Platzhalter.
- Theorie-Lektionen: content.raw_text mit ausführlichem Markdown-Text.
- Karteikarten: content.cards mit front/back Paaren (mindestens 5 Karten).
- Quiz: content.questions mit Fragen, Optionen und korrekten Antworten (mindestens 3 Fragen).
- Übungen: content.tasks mit Aufgabenstellung und Lösung.

LEKTION — CONTENT.RAW_TEXT (KRITISCH):
- Bei update_lesson IMMER content.raw_text setzen mit vollständigem Markdown-Theorieblatt.
- Bei add_lesson IMMER content.raw_text setzen.
- Das raw_text ist der Hauptinhalt den der Lernende sieht.
- Formatiere als Markdown: # Überschriften, **Fett**, Listen, Code-Blöcke.

LERNMETHODEN — PFLICHT (KRITISCH):
- Jede Lektion MUSS mindestens 1-2 Lernmethoden (Aufgaben) haben!
- Wenn du eine Lektion erstellst oder aktualisierst, füge IMMER auch add_method Tool Calls hinzu.
- Ohne Lernmethoden sieht der User "Keine Aufgaben verfügbar" — das ist ein schlechtes Erlebnis.
- BEVORZUGE Freitext-Aufgaben (type "exercise") — der Lernende muss aktiv formulieren.
- Pro Lektion: 1-2x Freitext (type "exercise"), optional 1x Quiz oder Karteikarten ergänzend.
- Freitext-Beispiel: type="exercise", content={"question": "Erkläre...", "hints": ["Hinweis 1"]}, solution={"modelAnswer": "...", "keyPoints": ["Punkt 1", "Punkt 2"]}
- Quiz-Beispiel: type="quiz", content={"questions": [{"question": "...", "options": ["A", "B", "C", "D"], "correct": 0}]}
- Karteikarten-Beispiel: type="flashcards", content={"cards": [{"front": "...", "back": "..."}]}

VERHALTEN — STRIKT:
- TU ES SOFORT. Interpretiere die Anfrage bestmöglich und führe aus.
- FRAGE NIEMALS "Soll ich...?", "Möchtest du...?" — HANDLE EINFACH.
- Wenn etwas unklar ist, triff die beste Entscheidung und erkläre was du gemacht hast.
- Deine Text-Antwort beschreibt was du GETAN hast, NICHT was du tun wirst.
- Bei "verbessere das" / "mach es besser": Aktualisiere die Lektion UND füge Lernmethoden hinzu.
- Bei "ja", "ok", "mach das": Führe die zuletzt besprochene Aktion aus."""

        if mode == 'exam':
            base_prompt += """

MODUS: Prüfungsgenerierung
Fokussiere auf die Erstellung von Prüfungsfragen im IHK-Stil.
Nutze add_method mit type "quiz" oder "exam" für Prüfungsinhalte."""

        elif mode == 'calculator':
            base_prompt += """

MODUS: Taschenrechner-Tutorial
Erstelle detaillierte Schritt-für-Schritt-Anleitungen für Taschenrechner.
Nutze add_method mit type "calculator_tutorial" mit:
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

Nutze die verfügbaren Tools um Änderungen vorzunehmen."""

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
