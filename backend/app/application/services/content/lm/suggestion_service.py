"""
LM Suggestion Service - KI-gestützte Lernmethoden-Vorschläge

Die KI analysiert den Lektionskontext und wählt intelligent passende
Content-Lernmethoden aus den 12 verfügbaren aus.

12 Content-Lernmethoden in 3 Gruppen (DB-driven):
- A: Erklärend (LM00-LM04) - 5 Methoden
- B: Praxis (LM05-LM08) - 4 Methoden
- C: Prüfung (LM09-LM11) - 3 Methoden

ALLE Lernmethoden-Definitionen kommen aus der Datenbank (learning_method_types).
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

from app.infrastructure.persistence.repositories.learning_method.config.catalog import LearningMethodCatalogRepository
from app.infrastructure.persistence.repositories.learning_method.config.groups import LearningMethodGroupRepository
from app.application.services.ai.adapter import AIAdapter

logger = logging.getLogger(__name__)

# System-Prompt für LM-Auswahl (12 Content-LMs, DB-driven)
LM_SELECTION_SYSTEM_PROMPT = """Du bist ein didaktischer Experte für E-Learning.
Deine Aufgabe ist es, die passendsten Lernmethoden für eine gegebene Lektion auszuwählen.

Du kennst diese 12 Content-Lernmethoden (gruppiert):

GRUPPE A - Erklärend (5 Methoden):
- LM00: Tiefgehende Erklärung - KI-generierte Erklärung mit Beispielen & Analogien
- LM01: Schritt-für-Schritt - Sequenzielle Anleitung in nummerierten Schritten
- LM02: Interaktive Theorie - Theorie mit interaktiven Frage-Antwort-Elementen
- LM03: Diagramm/Visualisierung - Grafische Darstellung komplexer Konzepte
- LM04: Beispiel-Szenario - Praxisnahes Anwendungsbeispiel mit Kontext

GRUPPE B - Praxis (4 Methoden):
- LM05: Mathe-Interaktiv - Mathematische Aufgaben mit Schritt-Erkennung
- LM06: Flashcards - Digitale Lernkarten für Wiederholung
- LM07: Drag & Drop - Zuordnungsaufgaben per Drag & Drop
- LM08: Lückentext - Lückentexte mit Auto-Korrektur

GRUPPE C - Prüfung (3 Methoden):
- LM09: Freitext-Langantwort - Offene Fragen mit Agent-Bewertung
- LM10: Multiple-Choice Quiz - Multiple-Choice Quiz in Prüfungsformat
- LM11: True/False - Richtig/Falsch Aussagen bewerten

WICHTIGE REGELN:
1. Wähle 2-4 passende Methoden aus (nicht mehr als verfügbar)
2. Berücksichtige das Thema (IT, Kaufmännisch, Mathe, etc.)
3. Mische verschiedene Gruppen wenn möglich (Theorie + Praxis + Prüfung)
4. Schließe bereits vorhandene LMs aus
5. Begründe jede Auswahl kurz
6. Nutze NUR diese 12 Content-LMs (LM00-LM11)!

Antworte NUR mit validem JSON in diesem Format:
{
  "suggestions": [
    {
      "lm_id": 5,
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
{lesson_content if lesson_content else 'Kein Inhalt vorhanden'}

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
                model='claude-3-haiku-20240307'  # Schnelles Modell für Suggestions
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

            # Anreichern mit Methoden-Details (von Database)
            enriched = []
            for idx, suggestion in enumerate(suggestions[:max_suggestions]):
                lm_id = suggestion.get('lm_id')
                if lm_id in existing_lm_ids:
                    continue

                # Query database for method definition
                method_data = LearningMethodCatalogRepository.get_by_type(method_type=lm_id)
                if not method_data:
                    continue

                enriched.append({
                    'lm_id': lm_id,
                    'name': method_data.get('name'),
                    'group': method_data.get('group_code'),
                    'method_type': lm_id,
                    'description': method_data.get('description'),
                    'reason': suggestion.get('reason', 'Passend für diese Lektion'),
                    'priority': idx + 1,
                    'icon': method_data.get('icon', '📋'),  # DB-driven icon
                    'ki_usage': method_data.get('ki_usage', 'intensive')
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
        Einfache Keyword-basierte Heuristik mit 12 Content-LMs (LM00-LM11).
        """
        title_lower = lesson_title.lower()

        # Keyword-basierte Vorauswahl (nur gültige Content-LM IDs: 0-11)
        candidates = []

        # Mathe/Kalkulation Keywords → Group B (Praxis: 5-8)
        if any(kw in title_lower for kw in ['kalkulation', 'berechnung', 'rechnung', 'prozent', 'zins']):
            candidates = [5, 9, 8, 1, 10, 3]  # Mathe, Freitext, Lückentext, Schritt, Quiz, Diagramm
        # IT Keywords → Group B + A (Praxis/Erklärung)
        elif any(kw in title_lower for kw in ['netzwerk', 'server', 'code', 'programmierung', 'linux']):
            candidates = [3, 7, 8, 1, 10, 5]  # Diagramm, Drag&Drop, Lückentext, Schritt, Quiz, Mathe
        # Prüfung Keywords → Group C (Prüfung: 9-11)
        elif any(kw in title_lower for kw in ['prüfung', 'test', 'ihk', 'abschluss']):
            candidates = [9, 10, 11, 8, 1, 5]  # Freitext, Quiz, TrueFalse, Lückentext, Schritt, Mathe
        # Default: Mix aus allen Gruppen
        else:
            candidates = [0, 1, 10, 6, 7, 8]  # Erklärung, Schritt, Quiz, Flashcards, DragDrop, Lückentext

        # Filtern und anreichern (database-driven)
        suggestions = []
        for lm_id in candidates:
            if lm_id in existing_lm_ids:
                continue
            if len(suggestions) >= max_suggestions:
                break

            # Query database for method definition
            method_data = LearningMethodCatalogRepository.get_by_type(method_type=lm_id)
            if not method_data:
                continue

            suggestions.append({
                'lm_id': lm_id,
                'name': method_data.get('name'),
                'group': method_data.get('group_code'),
                'method_type': lm_id,
                'description': method_data.get('description'),
                'reason': f'Passend für "{lesson_title}"',
                'priority': len(suggestions) + 1,
                'icon': method_data.get('icon', '📋'),  # DB-driven icon
                'ki_usage': method_data.get('ki_usage', 'intensive')
            })

        return suggestions

    @staticmethod
    def get_all_lms_grouped() -> Dict[str, Dict]:
        """
        Gibt alle 12 Content-LMs gruppiert zurück (100% database-driven).

        Gruppen und Icons kommen aus der learning_method_groups Tabelle.
        Lernmethoden und Icons kommen aus der learning_method_types Tabelle.

        Für manuelle Auswahl wenn User selbst entscheiden will.

        Returns:
            Dict mit Struktur:
            {
                'A': {
                    'name': 'Erklärend',
                    'icon': '📖',
                    'description': '...',
                    'sort_order': 1,
                    'methods': [...]
                },
                ...
            }
        """
        groups = {}

        # Query database for all active groups
        all_groups = LearningMethodGroupRepository.find_all()

        # Query database for all active learning methods
        catalog = LearningMethodCatalogRepository.get_full_catalog()

        # Build group structure from database
        for group_data in all_groups:
            group_code = group_data.get('group_code')
            groups[group_code] = {
                'name': group_data.get('name'),
                'description': group_data.get('description'),
                'icon': group_data.get('icon'),  # DB-driven icon
                'sort_order': group_data.get('sort_order', 0),
                'methods': []
            }

        # Add methods to their groups
        for method_data in catalog:
            group_key = method_data.get('group_code', 'A')

            # Skip if group doesn't exist (shouldn't happen due to FK constraint)
            if group_key not in groups:
                logger.warning(f"Method {method_data.get('method_type')} references unknown group {group_key}")
                continue

            lm_id = method_data.get('method_type', 0)
            groups[group_key]['methods'].append({
                'lm_id': lm_id,
                'name': method_data.get('name'),
                'description': method_data.get('description'),
                'icon': method_data.get('icon', '📋'),  # DB-driven icon
                'ki_usage': method_data.get('ki_usage', 'intensive')
            })

        # Sortiere Gruppen nach sort_order
        sorted_groups = dict(sorted(
            groups.items(),
            key=lambda x: x[1].get('sort_order', 999)
        ))

        # Sortiere Methoden innerhalb jeder Gruppe nach ID
        for group in sorted_groups.values():
            group['methods'].sort(key=lambda x: x['lm_id'])

        return sorted_groups
