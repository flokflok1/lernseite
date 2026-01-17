"""
LM Suggestion Service - KI-gestützte Lernmethoden-Vorschläge

Die KI analysiert den Lektionskontext und wählt intelligent passende
Content-Lernmethoden aus den 19 verfügbaren aus.

19 Content-Lernmethoden in 3 Gruppen:
- A: Erklärend (LM00-LM03, LM06) - 5 Methoden
- B: Praxis (LM08, LM12-LM15, LM17) - 6 Methoden
- C: Prüfung (LM18-LM25) - 8 Methoden

System-Features (Tutor, IT-Sandboxes, Kollaboration) sind KEINE Content-LMs
und werden separat behandelt (siehe 02a_System-Features.md).

Kein hardcoded Mapping - die KI entscheidet basierend auf:
- Thema und Inhalt der Lektion
- Lernziele
- Schwierigkeitsgrad
- Bereits vorhandene Methoden
- Didaktische Prinzipien
"""

from typing import List, Dict, Optional
import json
import logging

from app.ai.configuration.learning_method_mapping import (
    LEARNING_METHODS,
    LearningMethodDefinition,
    get_all_methods_as_dict
)
from app.services.ai_adapter import AIAdapter

logger = logging.getLogger(__name__)

# Icons für LM-Gruppen (nur Content-Gruppen A, B, C)
GROUP_ICONS = {
    'A': '📖',  # Erklärend
    'B': '✏️',  # Praxis
    'C': '📝'   # Prüfung
}

# LM-spezifische Icons (nur 19 Content-LMs)
LM_ICONS = {
    # Gruppe A - Erklärend
    0: '📚',   # Tiefgehende Erklärung
    1: '🔢',   # Schritt-für-Schritt
    2: '💡',   # Interaktive Theorie
    3: '📊',   # Diagramm/Visualisierung
    6: '🎭',   # Beispiel-Szenario
    # Gruppe B - Praxis
    8: '🖼️',   # Whiteboard-Aufgabe
    12: '🧮',  # Mathe-Interaktiv
    13: '🃏',  # Flashcards
    14: '🎯',  # Drag & Drop
    15: '📝',  # Lückentext
    17: '🧪',  # Hands-on Lab
    # Gruppe C - Prüfung
    18: '✍️',  # Freitext-Langantwort
    19: '🏆',  # IHK-Stil Aufgaben
    20: '📋',  # Multi-Step Praxisprüfung
    21: '⏱️',  # Zeitlimit-Training
    22: '❓',  # Prüfungs-Quiz
    23: '✅',  # Verständnis-Checks
    24: '🎤',  # Mündliche Erklärung
    25: '🎓'   # Kapitel-Endprüfung
}

# System-Prompt für LM-Auswahl (nur 19 Content-LMs)
LM_SELECTION_SYSTEM_PROMPT = """Du bist ein didaktischer Experte für E-Learning.
Deine Aufgabe ist es, die passendsten Lernmethoden für eine gegebene Lektion auszuwählen.

Du kennst diese 19 Content-Lernmethoden (gruppiert):

GRUPPE A - Erklärend (5 Methoden):
- LM00: Tiefgehende Erklärung - KI-generierte Erklärung mit Beispielen & Analogien
- LM01: Schritt-für-Schritt - Sequenzielle Anleitung in nummerierten Schritten
- LM02: Interaktive Theorie - Theorieblöcke mit eingebetteten Kontrollfragen
- LM03: Diagramm/Visualisierung - Visuelle Modelle (Netzwerk, OSI, ER, Flows)
- LM06: Beispiel-Szenario - Realitätsnahe Case-Erklärung eines Konzepts

GRUPPE B - Praxis (6 Methoden):
- LM08: Whiteboard-Aufgabe - Lernende zeichnen/verbinden Topologien, Skizzen
- LM12: Mathe-Interaktiv - Rechenaufgaben mit Schritt-für-Schritt-Erklärung
- LM13: Flashcards - Karteikarten mit Spaced-Repetition
- LM14: Drag & Drop - Zuordnungs-/Matching-Aufgaben
- LM15: Lückentext - Fill-in-the-blanks in Texten/Configs
- LM17: Hands-on Lab - Virtuelle Umgebung (Terminal/IDE) mit Aufgabe

GRUPPE C - Prüfung (8 Methoden):
- LM18: Freitext-Langantwort - Lange Antworten, KI bewertet mit Rubric
- LM19: IHK-Stil Aufgaben - Prüfungsnahe MC/Lückentext/Szenario
- LM20: Multi-Step Praxisprüfung - Mehrstufige Prüfungsketten
- LM21: Zeitlimit-Training - Aufgaben unter Zeitdruck (Countdown)
- LM22: Prüfungs-Quiz - Quiz mit sofortigem Feedback
- LM23: Verständnis-Checks - Single-Item-Checks nach Lerneinheit
- LM24: Mündliche Erklärung - User erklärt mündlich, KI bewertet
- LM25: Kapitel-Endprüfung - Größere Prüfung am Kapitelende

WICHTIGE REGELN:
1. Wähle 3-6 passende Methoden aus
2. Berücksichtige das Thema (IT, Kaufmännisch, Mathe, etc.)
3. Mische verschiedene Gruppen (Theorie + Praxis + Prüfung)
4. Schließe bereits vorhandene LMs aus
5. Begründe jede Auswahl kurz
6. Nutze NUR diese 19 Content-LMs (keine anderen IDs!)

Antworte NUR mit validem JSON in diesem Format:
{
  "suggestions": [
    {
      "lm_id": 12,
      "reason": "Bezugskalkulation erfordert Berechnungen - Mathe-Interaktiv ist ideal"
    },
    ...
  ]
}"""


class LMSuggestionService:
    """Service für KI-gestützte Lernmethoden-Vorschläge"""

    @staticmethod
    async def get_suggestions_from_ai(
        lesson_title: str,
        lesson_content: str = "",
        chapter_title: str = "",
        course_title: str = "",
        existing_lm_ids: List[int] = None,
        user_id: str = None,
        max_suggestions: int = 6
    ) -> List[Dict]:
        """
        Lässt die KI passende Lernmethoden für die Lektion auswählen.

        Args:
            lesson_title: Titel der Lektion
            lesson_content: Inhalt/Theorie der Lektion
            chapter_title: Titel des Kapitels
            course_title: Titel des Kurses
            existing_lm_ids: Bereits vorhandene LM-IDs
            user_id: User-ID für Token-Tracking
            max_suggestions: Maximale Anzahl Vorschläge

        Returns:
            Liste von LM-Vorschlägen mit Begründung
        """
        existing_lm_ids = existing_lm_ids or []

        # User-Prompt bauen
        user_prompt = f"""Analysiere diese Lektion und wähle passende Lernmethoden:

KURS: {course_title or 'Nicht angegeben'}
KAPITEL: {chapter_title or 'Nicht angegeben'}
LEKTION: {lesson_title}

LEKTIONSINHALT:
{lesson_content[:2000] if lesson_content else 'Kein Inhalt vorhanden'}

BEREITS VORHANDENE LMs (NICHT nochmal vorschlagen): {existing_lm_ids if existing_lm_ids else 'Keine'}

Wähle {max_suggestions} passende Lernmethoden aus und begründe jede Auswahl.
Antworte NUR mit JSON."""

        try:
            # KI-Request
            result = await AIAdapter.generate_async(
                system_prompt=LM_SELECTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                user_id=user_id,
                request_type='lm_suggestion',
                model='claude-3-haiku-20240307',  # Schnelles Modell für Suggestions
                max_tokens=1000
            )

            if not result or not result.get('success'):
                logger.warning("KI-Request für LM-Suggestions fehlgeschlagen")
                return LMSuggestionService._get_fallback_suggestions(
                    lesson_title, existing_lm_ids, max_suggestions
                )

            # JSON parsen
            content = result.get('content', '')
            suggestions = LMSuggestionService._parse_ai_response(content)

            if not suggestions:
                return LMSuggestionService._get_fallback_suggestions(
                    lesson_title, existing_lm_ids, max_suggestions
                )

            # Anreichern mit Methoden-Details
            enriched = []
            for idx, suggestion in enumerate(suggestions[:max_suggestions]):
                lm_id = suggestion.get('lm_id')
                if lm_id not in LEARNING_METHODS:
                    continue
                if lm_id in existing_lm_ids:
                    continue

                method = LEARNING_METHODS[lm_id]
                enriched.append({
                    'lm_id': lm_id,
                    'name': method.name,
                    'group': method.group.value,
                    'method_type': method.method_type.value,
                    'description': method.description,
                    'reason': suggestion.get('reason', 'Passend für diese Lektion'),
                    'priority': idx + 1,
                    'icon': LM_ICONS.get(lm_id, '📋'),
                    'ki_usage': method.ki_usage.value
                })

            return enriched

        except Exception as e:
            logger.error(f"Fehler bei KI-LM-Suggestions: {e}")
            return LMSuggestionService._get_fallback_suggestions(
                lesson_title, existing_lm_ids, max_suggestions
            )

    @staticmethod
    def get_suggestions_sync(
        lesson_title: str,
        lesson_content: str = "",
        chapter_title: str = "",
        course_title: str = "",
        existing_lm_ids: List[int] = None,
        user_id: str = None,
        max_suggestions: int = 6
    ) -> List[Dict]:
        """
        Synchrone Version - nutzt einfache Heuristik wenn keine async möglich.
        Für schnelle Erstvorschläge.
        """
        import asyncio

        try:
            # Versuche async auszuführen
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Fallback wenn bereits in async context
                return LMSuggestionService._get_fallback_suggestions(
                    lesson_title, existing_lm_ids or [], max_suggestions
                )
            return loop.run_until_complete(
                LMSuggestionService.get_suggestions_from_ai(
                    lesson_title, lesson_content, chapter_title,
                    course_title, existing_lm_ids, user_id, max_suggestions
                )
            )
        except Exception:
            return LMSuggestionService._get_fallback_suggestions(
                lesson_title, existing_lm_ids or [], max_suggestions
            )

    @staticmethod
    def _parse_ai_response(content: str) -> List[Dict]:
        """Parst die KI-Antwort und extrahiert Suggestions"""
        try:
            # Versuche direktes JSON-Parsing
            if '{' in content:
                # Finde JSON-Block
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                data = json.loads(json_str)
                return data.get('suggestions', [])
        except json.JSONDecodeError:
            pass

        # Fallback: Versuche Array zu finden
        try:
            if '[' in content:
                start = content.find('[')
                end = content.rfind(']') + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        return []

    @staticmethod
    def _get_fallback_suggestions(
        lesson_title: str,
        existing_lm_ids: List[int],
        max_suggestions: int
    ) -> List[Dict]:
        """
        Fallback-Vorschläge wenn KI nicht verfügbar.
        Einfache Keyword-basierte Heuristik mit 19 Content-LMs.
        """
        title_lower = lesson_title.lower()

        # Keyword-basierte Vorauswahl (nur gültige Content-LM IDs)
        candidates = []

        # Mathe/Kalkulation Keywords
        if any(kw in title_lower for kw in ['kalkulation', 'berechnung', 'rechnung', 'prozent', 'zins']):
            candidates = [12, 19, 15, 1, 22, 8]  # Mathe, IHK, Lückentext, Schritt-für-Schritt
        # IT Keywords (nutzt Content-LMs, nicht IT-System-Features)
        elif any(kw in title_lower for kw in ['netzwerk', 'server', 'code', 'programmierung', 'linux']):
            candidates = [17, 3, 8, 15, 22, 19]  # Hands-on Lab, Diagramm, Whiteboard
        # Prüfung Keywords
        elif any(kw in title_lower for kw in ['prüfung', 'test', 'ihk', 'abschluss']):
            candidates = [19, 22, 21, 25, 20, 18]  # Prüfungs-LMs
        # Default: Mix aus allen Gruppen
        else:
            candidates = [0, 1, 22, 13, 14, 15]  # Erklärung, Schritt, Quiz, Flashcards

        # Filtern und anreichern
        suggestions = []
        for lm_id in candidates:
            if lm_id in existing_lm_ids:
                continue
            if lm_id not in LEARNING_METHODS:
                continue
            if len(suggestions) >= max_suggestions:
                break

            method = LEARNING_METHODS[lm_id]
            suggestions.append({
                'lm_id': lm_id,
                'name': method.name,
                'group': method.group.value,
                'method_type': method.method_type.value,
                'description': method.description,
                'reason': f'Passend für "{lesson_title}"',
                'priority': len(suggestions) + 1,
                'icon': LM_ICONS.get(lm_id, '📋'),
                'ki_usage': method.ki_usage.value
            })

        return suggestions

    @staticmethod
    def get_all_lms_grouped() -> Dict[str, Dict]:
        """
        Gibt alle 19 Content-LMs gruppiert zurück.
        Für manuelle Auswahl wenn User selbst entscheiden will.
        """
        groups = {}

        for method in LEARNING_METHODS.values():
            group_key = method.group.value
            if group_key not in groups:
                groups[group_key] = {
                    'name': {
                        'A': 'Erklärend',
                        'B': 'Praxis',
                        'C': 'Prüfung'
                    }.get(group_key, group_key),
                    'icon': GROUP_ICONS.get(group_key, '📋'),
                    'methods': []
                }

            groups[group_key]['methods'].append({
                'lm_id': method.lm_id,
                'name': method.name,
                'description': method.description,
                'icon': LM_ICONS.get(method.lm_id, '📋'),
                'ki_usage': method.ki_usage.value
            })

        # Sortiere Methoden nach ID
        for group in groups.values():
            group['methods'].sort(key=lambda x: x['lm_id'])

        return groups
